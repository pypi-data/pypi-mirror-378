"""문서 조작 로직 집합."""

from __future__ import annotations

import base64
from dataclasses import dataclass
from io import BytesIO
from logging import Logger
from pathlib import Path
from typing import Iterable, Mapping, Sequence
from xml.etree.ElementTree import Element
from zipfile import BadZipFile

from hwpx import ObjectFinder, TextExtractor
from hwpx.document import HwpxDocument, blank_document_bytes
from hwpx.oxml import GenericElement
from hwpx.oxml.document import HwpxOxmlParagraph
from hwpx.tools.text_extractor import (
    AnnotationOptions,
    ParagraphInfo,
    DEFAULT_NAMESPACES,
    build_parent_map,
    describe_element_path,
)
from hwpx.tools.validator import ValidationReport, validate_document

from ..config import ServerSettings, SessionConfig
from ..exceptions import DocumentSaveError, HwpxMcpError, InvalidDocumentSourceError
from ..models import (
    AnnotationResult,
    BulletMetadata,
    BulletParaHeadMetadata,
    CharPropertyMetadata,
    ControlInsertionResult,
    DocumentSummary,
    HeaderFooterUpdateResult,
    HeaderMetadata,
    HeaderNumberingMetadata,
    MemoInsertionResult,
    MemoMetadata,
    MemoShapeMetadata,
    NumberingMetadata,
    ObjectMatch,
    PackageOverview,
    ParagraphCursor,
    ParagraphInsertionResult,
    ParagraphDeleteResult,
    ParagraphUpdateResult,
    ReplaceTextResult,
    SectionNumberingMetadata,
    SaveResultModel,
    SectionMetadata,
    ShapeInsertionResult,
    StyleMetadata,
    TableInsertionResult,
    TextExtractionResult,
    TrackChangeAuthorMetadata,
    TrackChangeMetadata,
    ValidationIssueModel,
    ValidationReportModel,
    GenericElementModel,
)
from ..session import DocumentHandle, DocumentSessionManager
from ..user_config import UserConfig
from ..workspace import WorkspaceService, make_backup


def _annotation_from_mode(mode: str) -> AnnotationOptions:
    """세션/요청 모드에 따른 AnnotationOptions 매핑."""

    mode = mode.lower()
    if mode == "inline":
        return AnnotationOptions(
            highlight="markers",
            footnote="inline",
            endnote="inline",
            hyperlink="target",
            control="nested",
        )
    if mode == "summary":
        return AnnotationOptions(
            highlight="markers",
            footnote="placeholder",
            endnote="placeholder",
            hyperlink="placeholder",
            control="placeholder",
        )
    return AnnotationOptions()


def _encode_base64(data: bytes | None) -> str | None:
    if data is None:
        return None
    return base64.b64encode(data).decode("ascii")


def _paragraph_preview(info: ParagraphInfo, *, config: SessionConfig, object_behavior: str | None) -> str:
    behavior = object_behavior or ("skip" if config.object_placeholder is None else "placeholder")
    return info.text(
        object_behavior=behavior,
        object_placeholder=config.object_placeholder,
        preserve_breaks=config.preserve_line_breaks,
        annotations=_annotation_from_mode(config.annotation_mode),
    )


def _stringify_mapping(values: Mapping[str, object] | None) -> dict[str, str]:
    mapping: dict[str, str] = {}
    if not values:
        return mapping
    for key, value in values.items():
        if value is None:
            continue
        mapping[str(key)] = str(value)
    return mapping


def _convert_generic(element: GenericElement | None) -> GenericElementModel | None:
    if element is None:
        return None
    children = [_convert_generic(child) for child in element.children]
    return GenericElementModel(
        name=element.name,
        tag=element.tag,
        attributes=dict(element.attributes),
        text=element.text,
        children=children,
    )


def _resolve_limit(config: SessionConfig, limit: int | None) -> int:
    if limit is None or limit <= 0:
        return config.max_items
    return min(limit, config.max_items)


@dataclass(slots=True)
class _ParagraphEntry:
    index: int
    element: Element
    path: str
    parent: Element


@dataclass(slots=True)
class _ResolvedParagraph:
    paragraph: HwpxOxmlParagraph
    section_index: int
    paragraph_index: int
    path: str
    parent: Element


class DocumentService:
    """세션 관리자를 감싸는 고수준 비즈니스 로직."""

    def __init__(
        self,
        manager: DocumentSessionManager,
        settings: ServerSettings,
        logger: Logger,
        workspace: WorkspaceService | None = None,
        user_config: UserConfig | None = None,
    ) -> None:
        self._manager = manager
        self._settings = settings
        self._logger = logger
        self._workspace = workspace
        self._user_config = user_config

    # ------------------------------------------------------------------
    # 기본 관리 기능
    # ------------------------------------------------------------------
    def load_document(
        self,
        session_id: str,
        *,
        path: str | None = None,
        content: bytes | None = None,
        document_id: str | None = None,
        label: str | None = None,
    ) -> DocumentSummary:
        """문서를 열어 세션에 등록한다."""

        if path and content:
            raise InvalidDocumentSourceError("파일 경로와 바이너리를 동시에 지정할 수 없습니다.")
        if not path and content is None:
            raise InvalidDocumentSourceError("파일 경로나 바이너리를 제공해야 합니다.")

        if path:
            if self._workspace is None or not self._workspace.has_roots:
                raise InvalidDocumentSourceError(
                    "파일 경로를 사용하려면 hwpx-mcp configure 명령으로 워크스페이스를 등록해 주세요."
                )
            source_path = self._workspace.ensure_readable(path)
            self._logger.info("문서를 경로에서 로드합니다: session=%s path=%s", session_id, source_path)
            try:
                document = HwpxDocument.open(str(source_path))
            except (OSError, BadZipFile, KeyError, ValueError, RuntimeError) as exc:
                raise InvalidDocumentSourceError(
                    "지정한 파일을 찾거나 읽을 수 없습니다. 경로를 다시 확인하거나 base64_content를 제공해 주세요."
                ) from exc
        else:
            assert content is not None
            document = HwpxDocument.open(content)
            source_path = None

        doc_id = document_id or self._manager.generate_document_id()
        handle = DocumentHandle(doc_id, document, source_path=source_path, label=label)
        if source_path is not None:
            handle.last_saved_path = source_path
        self._manager.register_document(session_id, handle)
        self._logger.info("문서 로딩: session=%s id=%s", session_id, doc_id)
        return self._summarize(handle)

    def new_document(
        self,
        session_id: str,
        *,
        document_id: str | None = None,
        label: str | None = None,
        include_template: bool = False,
    ) -> tuple[DocumentSummary, str | None]:
        """새 빈 문서를 생성한다."""

        document = HwpxDocument.new()
        doc_id = document_id or self._manager.generate_document_id()
        handle = DocumentHandle(doc_id, document, source_path=None, label=label)
        self._manager.register_document(session_id, handle)
        template_b64 = _encode_base64(blank_document_bytes()) if include_template else None
        self._logger.info("새 문서 생성: session=%s id=%s", session_id, doc_id)
        return self._summarize(handle), template_b64

    def save_document(
        self,
        session_id: str,
        document_id: str,
        *,
        path: str | None = None,
        return_base64: bool = False,
    ) -> SaveResultModel:
        """문서를 저장하고 결과를 반환한다."""

        handle = self._manager.get_document(session_id, document_id)
        destination: Path | None = None
        if path:
            if self._workspace is None or not self._workspace.has_roots:
                raise InvalidDocumentSourceError(
                    "파일로 저장하려면 hwpx-mcp configure 명령으로 워크스페이스를 등록해 주세요."
                )
            destination = self._workspace.ensure_writable(path)
        elif handle.source_path is not None:
            destination = handle.source_path
            if self._workspace and self._workspace.has_roots:
                try:
                    destination = self._workspace.ensure_writable(destination)
                except InvalidDocumentSourceError:
                    # 설정에서 제거된 경로는 자동 저장 대상에서 제외한다.
                    self._logger.warning(
                        "저장 경로가 더 이상 허용되지 않아 메모리에만 저장합니다: session=%s id=%s path=%s",
                        session_id,
                        document_id,
                        destination,
                    )
                    destination = None

        backup_path: Path | None = None
        if destination and destination.exists() and self._user_config and self._user_config.auto_backup:
            backup_dir = (
                Path(self._user_config.backup_dir).expanduser()
                if self._user_config.backup_dir
                else None
            )
            try:
                backup_path = make_backup(destination, backup_dir)
                self._logger.info(
                    "저장 전에 백업 파일을 생성했습니다: session=%s id=%s backup=%s",
                    session_id,
                    document_id,
                    backup_path,
                )
            except Exception as exc:  # pragma: no cover - I/O 실패 방어
                self._logger.warning(
                    "백업 파일 생성 실패: session=%s id=%s error=%s",
                    session_id,
                    document_id,
                    exc,
                )

        saved_to, size, payload = handle.save(destination)
        if return_base64 and payload is None:
            payload = handle.snapshot_bytes()
            size = len(payload)
        encoded = _encode_base64(payload)
        self._logger.info(
            "문서 저장: session=%s id=%s target=%s", session_id, document_id, saved_to or "memory"
        )
        return SaveResultModel(
            document_id=document_id,
            saved_to=saved_to,
            size=size,
            base64_content=encoded,
            backup_path=str(backup_path) if backup_path else None,
        )

    def close_document(self, session_id: str, document_id: str) -> None:
        """문서를 닫아 세션 캐시에서 제거한다."""

        self._manager.close_document(session_id, document_id)
        self._logger.info("문서 종료: session=%s id=%s", session_id, document_id)

    # ------------------------------------------------------------------
    # 구조 탐색
    # ------------------------------------------------------------------
    def inspect_package(self, session_id: str, document_id: str) -> PackageOverview:
        handle = self._manager.get_document(session_id, document_id)
        package = handle.document.package
        return PackageOverview(
            document_id=document_id,
            part_names=list(package.part_names()),
            section_paths=package.section_paths(),
            header_paths=package.header_paths(),
        )

    def list_sections(self, session_id: str, document_id: str) -> list[SectionMetadata]:
        handle = self._manager.get_document(session_id, document_id)
        sections: list[SectionMetadata] = []
        for index, section in enumerate(handle.document.sections):
            properties = section.properties
            page_size = getattr(properties, "page_size", None)
            has_header = properties.get_header("BOTH") is not None if hasattr(properties, "get_header") else False
            has_footer = properties.get_footer("BOTH") is not None if hasattr(properties, "get_footer") else False
            sections.append(
                SectionMetadata(
                    index=index,
                    part_name=section.part_name,
                    paragraph_count=len(section.paragraphs),
                    memo_count=len(section.memos),
                    has_header=has_header,
                    has_footer=has_footer,
                    page_width=getattr(page_size, "width", None),
                    page_height=getattr(page_size, "height", None),
                )
            )
        return sections

    def list_headers(self, session_id: str, document_id: str) -> list[HeaderMetadata]:
        handle = self._manager.get_document(session_id, document_id)
        result: list[HeaderMetadata] = []
        for index, header in enumerate(handle.document.headers):
            paragraph_count = len(header.element.findall(".//hp:p", namespaces=DEFAULT_NAMESPACES))
            result.append(
                HeaderMetadata(
                    index=index,
                    part_name=header.part_name,
                    paragraph_count=paragraph_count,
                    style_count=len(header.styles),
                    track_change_count=len(header.track_changes),
                )
            )
        return result

    def list_memos(self, session_id: str, document_id: str) -> list[MemoMetadata]:
        handle = self._manager.get_document(session_id, document_id)
        document = handle.document
        items: list[MemoMetadata] = []
        for memo in document.memos:
            section = memo.group.section
            section_index = document.sections.index(section) if section in document.sections else -1
            items.append(
                MemoMetadata(
                    memo_id=str(memo.id),
                    text=memo.text or "",
                    section_index=section_index,
                    paragraph_count=len(memo.paragraphs),
                )
            )
        return items

    def list_styles(
        self,
        session_id: str,
        document_id: str,
        config: SessionConfig,
        *,
        style_type: str | None = None,
        name_contains: str | None = None,
        limit: int | None = None,
    ) -> list[StyleMetadata]:
        handle = self._manager.get_document(session_id, document_id)
        document = handle.document
        resolved_limit = _resolve_limit(config, limit)
        collected: list[StyleMetadata] = []
        type_filter = style_type.lower() if style_type else None
        name_filter = name_contains.lower() if name_contains else None
        for identifier, style in document.styles.items():
            if type_filter and (style.type or "").lower() != type_filter:
                continue
            if name_filter and name_filter not in (style.name or "").lower():
                continue
            collected.append(
                StyleMetadata(
                    identifier=identifier,
                    style_id=style.id,
                    raw_id=style.raw_id,
                    type=style.type,
                    name=style.name,
                    eng_name=style.eng_name,
                    para_pr_id_ref=style.para_pr_id_ref,
                    char_pr_id_ref=style.char_pr_id_ref,
                    next_style_id_ref=style.next_style_id_ref,
                    lang_id=style.lang_id,
                    lock_form=style.lock_form,
                    attributes=dict(style.attributes),
                )
            )
            if len(collected) >= resolved_limit:
                break
        return collected

    def list_char_properties(
        self,
        session_id: str,
        document_id: str,
        config: SessionConfig,
        *,
        text_color: str | None = None,
        underline_type: str | None = None,
        underline_color: str | None = None,
        limit: int | None = None,
    ) -> list[CharPropertyMetadata]:
        handle = self._manager.get_document(session_id, document_id)
        document = handle.document
        resolved_limit = _resolve_limit(config, limit)
        collected: list[CharPropertyMetadata] = []
        color_filter = text_color.lower() if text_color else None
        underline_type_filter = underline_type.lower() if underline_type else None
        underline_color_filter = underline_color.lower() if underline_color else None
        for identifier, char_prop in document.char_properties.items():
            current_color = (char_prop.text_color() or "").lower()
            current_underline_type = (char_prop.underline_type() or "").lower()
            current_underline_color = (char_prop.underline_color() or "").lower()
            if color_filter and current_color != color_filter:
                continue
            if underline_type_filter and current_underline_type != underline_type_filter:
                continue
            if underline_color_filter and current_underline_color != underline_color_filter:
                continue
            child_attrs = {key: dict(value) for key, value in char_prop.child_attributes.items()}
            collected.append(
                CharPropertyMetadata(
                    identifier=identifier,
                    attributes=dict(char_prop.attributes),
                    child_attributes=child_attrs,
                    text_color=char_prop.text_color(),
                    underline_type=char_prop.underline_type(),
                    underline_color=char_prop.underline_color(),
                )
            )
            if len(collected) >= resolved_limit:
                break
        return collected

    def list_memo_shapes(
        self,
        session_id: str,
        document_id: str,
        config: SessionConfig,
        *,
        memo_type: str | None = None,
        limit: int | None = None,
    ) -> list[MemoShapeMetadata]:
        handle = self._manager.get_document(session_id, document_id)
        document = handle.document
        resolved_limit = _resolve_limit(config, limit)
        type_filter = memo_type.lower() if memo_type else None
        collected: list[MemoShapeMetadata] = []
        for identifier, shape in document.memo_shapes.items():
            if type_filter and (shape.memo_type or "").lower() != type_filter:
                continue
            collected.append(
                MemoShapeMetadata(
                    identifier=identifier,
                    shape_id=shape.id,
                    width=shape.width,
                    line_width=shape.line_width,
                    line_type=shape.line_type,
                    line_color=shape.line_color,
                    fill_color=shape.fill_color,
                    active_color=shape.active_color,
                    memo_type=shape.memo_type,
                    attributes=dict(shape.attributes),
                )
            )
            if len(collected) >= resolved_limit:
                break
        return collected

    def list_bullets(
        self,
        session_id: str,
        document_id: str,
        config: SessionConfig,
        *,
        level: int | None = None,
        use_image: bool | None = None,
        char_contains: str | None = None,
        limit: int | None = None,
    ) -> list[BulletMetadata]:
        handle = self._manager.get_document(session_id, document_id)
        document = handle.document
        resolved_limit = _resolve_limit(config, limit)
        char_filter = char_contains.lower() if char_contains else None
        collected: list[BulletMetadata] = []
        for identifier, bullet in document.bullets.items():
            if level is not None and bullet.para_head.level != level:
                continue
            if use_image is not None and bool(bullet.use_image) != bool(use_image):
                continue
            if char_filter and char_filter not in (bullet.char or "").lower():
                continue
            para_head = bullet.para_head
            para_head_model = BulletParaHeadMetadata(
                text=para_head.text,
                level=para_head.level,
                start=para_head.start,
                align=para_head.align,
                use_inst_width=para_head.use_inst_width,
                auto_indent=para_head.auto_indent,
                width_adjust=para_head.width_adjust,
                text_offset_type=para_head.text_offset_type,
                text_offset=para_head.text_offset,
                attributes=dict(para_head.attributes),
            )
            other_children = {
                name: [_convert_generic(child) for child in children]
                for name, children in bullet.other_children.items()
            }
            collected.append(
                BulletMetadata(
                    identifier=identifier,
                    bullet_id=bullet.id,
                    char=bullet.char,
                    checked_char=bullet.checked_char,
                    use_image=bool(bullet.use_image),
                    para_head=para_head_model,
                    image=_convert_generic(bullet.image),
                    attributes=dict(bullet.attributes),
                    other_children=other_children,
                )
            )
            if len(collected) >= resolved_limit:
                break
        return collected

    def list_track_changes(
        self,
        session_id: str,
        document_id: str,
        config: SessionConfig,
        *,
        change_type: str | None = None,
        author_id: int | None = None,
        include_hidden: bool = True,
        limit: int | None = None,
    ) -> list[TrackChangeMetadata]:
        handle = self._manager.get_document(session_id, document_id)
        document = handle.document
        resolved_limit = _resolve_limit(config, limit)
        type_filter = change_type.lower() if change_type else None
        collected: list[TrackChangeMetadata] = []
        for identifier, change in document.track_changes.items():
            if type_filter and (change.change_type or "").lower() != type_filter:
                continue
            if author_id is not None and change.author_id != author_id:
                continue
            if not include_hidden and change.hide:
                continue
            author_model: TrackChangeAuthorMetadata | None = None
            author = document.track_change_author(change.author_id)
            if author is not None:
                author_identifier = author.raw_id or (str(author.id) if author.id is not None else "")
                author_model = TrackChangeAuthorMetadata(
                    identifier=author_identifier,
                    author_id=author.id,
                    name=author.name,
                    mark=author.mark,
                    color=author.color,
                    attributes=dict(author.attributes),
                )
            collected.append(
                TrackChangeMetadata(
                    identifier=identifier,
                    change_id=change.id,
                    change_type=change.change_type,
                    date=change.date,
                    author_id=change.author_id,
                    char_shape_id=change.char_shape_id,
                    para_shape_id=change.para_shape_id,
                    hide=change.hide,
                    attributes=dict(change.attributes),
                    author=author_model,
                )
            )
            if len(collected) >= resolved_limit:
                break
        return collected

    def describe_numberings(
        self,
        session_id: str,
        document_id: str,
    ) -> NumberingMetadata:
        handle = self._manager.get_document(session_id, document_id)
        document = handle.document
        header_items: list[HeaderNumberingMetadata] = []
        for index, header in enumerate(document.headers):
            begin = header.begin_numbering
            header_items.append(
                HeaderNumberingMetadata(
                    header_index=index,
                    part_name=header.part_name,
                    page=begin.page,
                    footnote=begin.footnote,
                    endnote=begin.endnote,
                    picture=begin.picture,
                    table=begin.table,
                    equation=begin.equation,
                )
            )
        section_items: list[SectionNumberingMetadata] = []
        for index, section in enumerate(document.sections):
            numbering = section.properties.start_numbering
            section_items.append(
                SectionNumberingMetadata(
                    section_index=index,
                    part_name=section.part_name,
                    page_starts_on=numbering.page_starts_on,
                    page=numbering.page,
                    picture=numbering.picture,
                    table=numbering.table,
                    equation=numbering.equation,
                )
            )
        return NumberingMetadata(
            document_id=document_id,
            headers=header_items,
            sections=section_items,
        )

    def iter_paragraphs(
        self,
        session_id: str,
        document_id: str,
        config: SessionConfig,
        *,
        section_indexes: Sequence[int] | None = None,
        limit: int | None = None,
        object_behavior: str | None = None,
    ) -> list[ParagraphCursor]:
        handle = self._manager.get_document(session_id, document_id)
        stream = handle.open_stream()
        limit = limit or config.max_items
        collector: list[ParagraphCursor] = []
        with TextExtractor(stream) as extractor:
            iterator: Iterable[ParagraphInfo] = extractor.iter_document_paragraphs(
                include_nested=config.include_nested_paragraphs,
            )
            for info in iterator:
                if section_indexes is not None and info.section.index not in section_indexes:
                    continue
                preview = _paragraph_preview(info, config=config, object_behavior=object_behavior)
                collector.append(
                    ParagraphCursor(
                        section_index=info.section.index,
                        paragraph_index=info.index,
                        path=info.path,
                        tag=info.tag,
                        is_nested=info.is_nested,
                        ancestors=list(info.ancestors),
                        preview=preview,
                    )
                )
                if len(collector) >= limit:
                    break
        return collector

    def extract_text(
        self,
        session_id: str,
        document_id: str,
        config: SessionConfig,
        *,
        object_behavior: str | None = None,
        preserve_breaks: bool | None = None,
        annotation_mode: str | None = None,
    ) -> TextExtractionResult:
        handle = self._manager.get_document(session_id, document_id)
        stream = handle.open_stream()
        annotations = _annotation_from_mode(annotation_mode or config.annotation_mode)
        with TextExtractor(stream) as extractor:
            text = extractor.extract_text(
                object_behavior=object_behavior or ("skip" if config.object_placeholder is None else "placeholder"),
                object_placeholder=config.object_placeholder,
                preserve_breaks=config.preserve_line_breaks if preserve_breaks is None else preserve_breaks,
                annotations=annotations,
            )
        return TextExtractionResult(document_id=document_id, text=text)

    def find_objects(
        self,
        session_id: str,
        document_id: str,
        config: SessionConfig,
        *,
        tag: str | Sequence[str] | None = None,
        xpath: str | None = None,
        attributes: Mapping[str, str] | None = None,
        limit: int | None = None,
    ) -> list[ObjectMatch]:
        handle = self._manager.get_document(session_id, document_id)
        stream = handle.open_stream()
        limit = limit or config.max_items
        finder = ObjectFinder(stream)
        matches = finder.find_all(tag=tag, xpath=xpath, attrs=attributes, limit=limit)
        result: list[ObjectMatch] = []
        for found in matches:
            result.append(
                ObjectMatch(
                    tag=found.tag,
                    path=found.path,
                    section_index=found.section.index,
                    section_name=found.section.name,
                    attributes=dict(found.element.attrib),
                    text=found.text,
                )
            )
        return result

    def list_annotations(
        self,
        session_id: str,
        document_id: str,
        config: SessionConfig,
        *,
        kinds: Sequence[str] | None = None,
        preserve_breaks: bool | None = None,
        limit: int | None = None,
    ) -> list[AnnotationResult]:
        handle = self._manager.get_document(session_id, document_id)
        stream = handle.open_stream()
        finder = ObjectFinder(stream)
        annotations = _annotation_from_mode(config.annotation_mode)
        limit = limit or config.max_items
        collected: list[AnnotationResult] = []
        for item in finder.iter_annotations(
            kinds=kinds,
            options=annotations,
            preserve_breaks=config.preserve_line_breaks if preserve_breaks is None else preserve_breaks,
        ):
            collected.append(
                AnnotationResult(
                    kind=item.kind,
                    path=item.element.path,
                    section_index=item.element.section.index,
                    section_name=item.element.section.name,
                    value=item.value,
                )
            )
            if len(collected) >= limit:
                break
        return collected

    # ------------------------------------------------------------------
    # 편집 기능
    # ------------------------------------------------------------------
    def add_paragraph(
        self,
        session_id: str,
        document_id: str,
        config: SessionConfig,
        *,
        text: str,
        section_index: int | None = None,
        para_pr_id_ref: str | int | None = None,
        style_id_ref: str | int | None = None,
        char_pr_id_ref: str | int | None = None,
        run_attributes: Mapping[str, str] | None = None,
    ) -> ParagraphInsertionResult:
        handle = self._manager.get_document(session_id, document_id)
        section = handle.document.sections[section_index] if section_index is not None else None
        paragraph = handle.document.add_paragraph(
            text,
            section=section,
            para_pr_id_ref=para_pr_id_ref,
            style_id_ref=style_id_ref,
            char_pr_id_ref=char_pr_id_ref,
            run_attributes=dict(run_attributes or {}),
        )
        self._autosave_if_requested(config, handle)
        resolved_section = paragraph.section
        if resolved_section is not None:
            resolved_index, resolved_path = self._describe_paragraph(paragraph)
            resolved_section_index = (
                section_index
                if section_index is not None
                else handle.document.sections.index(resolved_section)
            )
        else:
            resolved_section_index = section_index if section_index is not None else -1
            resolved_index = None
            resolved_path = None
        return ParagraphInsertionResult(
            document_id=document_id,
            section_index=resolved_section_index,
            paragraph_id=paragraph.element.get("id", ""),
            text=text,
            paragraph_index=resolved_index,
            path=resolved_path,
        )

    def update_paragraph_text(
        self,
        session_id: str,
        document_id: str,
        config: SessionConfig,
        *,
        text: str,
        path: str | None = None,
        section_index: int | None = None,
        paragraph_index: int | None = None,
    ) -> ParagraphUpdateResult:
        handle = self._manager.get_document(session_id, document_id)
        resolved = self._resolve_paragraph(
            handle,
            path=path,
            section_index=section_index,
            paragraph_index=paragraph_index,
        )
        previous_text = resolved.paragraph.text
        resolved.paragraph.text = text
        self._autosave_if_requested(config, handle)
        return ParagraphUpdateResult(
            document_id=document_id,
            section_index=resolved.section_index,
            paragraph_index=resolved.paragraph_index,
            paragraph_id=resolved.paragraph.element.get("id"),
            path=resolved.path,
            text=text,
            previous_text=previous_text,
        )

    def insert_paragraph_at(
        self,
        session_id: str,
        document_id: str,
        config: SessionConfig,
        *,
        text: str,
        path: str | None = None,
        section_index: int | None = None,
        paragraph_index: int | None = None,
        after: bool = False,
        para_pr_id_ref: str | int | None = None,
        style_id_ref: str | int | None = None,
        char_pr_id_ref: str | int | None = None,
        run_attributes: Mapping[str, str] | None = None,
    ) -> ParagraphInsertionResult:
        handle = self._manager.get_document(session_id, document_id)
        resolved = self._resolve_paragraph(
            handle,
            path=path,
            section_index=section_index,
            paragraph_index=paragraph_index,
        )
        section = resolved.paragraph.section
        if section is None:
            raise HwpxMcpError("문단이 속한 섹션을 확인하지 못했습니다.")
        new_paragraph = section.add_paragraph(
            text,
            para_pr_id_ref=para_pr_id_ref,
            style_id_ref=style_id_ref,
            char_pr_id_ref=char_pr_id_ref,
            run_attributes=dict(run_attributes or {}),
        )
        section.element.remove(new_paragraph.element)
        siblings = list(resolved.parent)
        try:
            anchor_index = siblings.index(resolved.paragraph.element)
        except ValueError as exc:  # pragma: no cover - 방어적 코드
            raise HwpxMcpError("문단 기준 위치를 찾지 못했습니다.") from exc
        insert_index = anchor_index + 1 if after else anchor_index
        resolved.parent.insert(insert_index, new_paragraph.element)
        section.mark_dirty()
        new_index, new_path = self._describe_paragraph(new_paragraph)
        self._autosave_if_requested(config, handle)
        return ParagraphInsertionResult(
            document_id=document_id,
            section_index=resolved.section_index,
            paragraph_id=new_paragraph.element.get("id", ""),
            text=text,
            paragraph_index=new_index,
            path=new_path,
        )

    def delete_paragraph(
        self,
        session_id: str,
        document_id: str,
        config: SessionConfig,
        *,
        path: str | None = None,
        section_index: int | None = None,
        paragraph_index: int | None = None,
    ) -> ParagraphDeleteResult:
        handle = self._manager.get_document(session_id, document_id)
        resolved = self._resolve_paragraph(
            handle,
            path=path,
            section_index=section_index,
            paragraph_index=paragraph_index,
        )
        paragraph = resolved.paragraph
        section = paragraph.section
        if section is None:
            raise HwpxMcpError("문단이 속한 섹션을 확인하지 못했습니다.")
        removed_text = paragraph.text
        try:
            resolved.parent.remove(paragraph.element)
        except ValueError as exc:  # pragma: no cover - 방어적 코드
            raise HwpxMcpError("문단 삭제에 실패했습니다.") from exc
        section.mark_dirty()
        self._autosave_if_requested(config, handle)
        return ParagraphDeleteResult(
            document_id=document_id,
            section_index=resolved.section_index,
            paragraph_index=resolved.paragraph_index,
            paragraph_id=paragraph.element.get("id"),
            path=resolved.path,
            removed_text=removed_text,
        )

    def add_table(
        self,
        session_id: str,
        document_id: str,
        config: SessionConfig,
        *,
        rows: int,
        cols: int,
        section_index: int | None = None,
        width: int | None = None,
        height: int | None = None,
        border_fill_id_ref: str | int = "0",
    ) -> TableInsertionResult:
        handle = self._manager.get_document(session_id, document_id)
        section = handle.document.sections[section_index] if section_index is not None else None
        table = handle.document.add_table(
            rows,
            cols,
            section=section,
            width=width,
            height=height,
            border_fill_id_ref=border_fill_id_ref,
        )
        self._autosave_if_requested(config, handle)
        paragraph = table.paragraph
        section_idx = section_index or (handle.document.sections.index(paragraph.section) if paragraph.section else -1)
        return TableInsertionResult(
            document_id=document_id,
            section_index=section_idx,
            paragraph_id=paragraph.element.get("id", ""),
            rows=table.row_count,
            cols=table.column_count,
        )

    def add_shape(
        self,
        session_id: str,
        document_id: str,
        config: SessionConfig,
        *,
        shape_type: str,
        section_index: int | None = None,
        attributes: Mapping[str, object] | None = None,
        para_pr_id_ref: str | int | None = None,
        style_id_ref: str | int | None = None,
        char_pr_id_ref: str | int | None = None,
        run_attributes: Mapping[str, object] | None = None,
        paragraph_attributes: Mapping[str, object] | None = None,
    ) -> ShapeInsertionResult:
        handle = self._manager.get_document(session_id, document_id)
        section = handle.document.sections[section_index] if section_index is not None else None
        inline = handle.document.add_shape(
            shape_type,
            section=section,
            section_index=section_index,
            attributes=_stringify_mapping(attributes),
            para_pr_id_ref=para_pr_id_ref,
            style_id_ref=style_id_ref,
            char_pr_id_ref=char_pr_id_ref,
            run_attributes=_stringify_mapping(run_attributes),
            **_stringify_mapping(paragraph_attributes),
        )
        paragraph = inline.paragraph
        if paragraph.section is not None:
            resolved_section_index = (
                section_index
                if section_index is not None
                else handle.document.sections.index(paragraph.section)
            )
            paragraph_index, path = self._describe_paragraph(paragraph)
        else:
            resolved_section_index = section_index if section_index is not None else -1
            paragraph_index = None
            path = None
        run_attributes_result: dict[str, str] = {}
        char_ref: str | None = None
        if paragraph.runs:
            run = paragraph.runs[-1]
            run_attributes_result = dict(run.element.attrib)
            char_ref = run.char_pr_id_ref
        self._autosave_if_requested(config, handle)
        return ShapeInsertionResult(
            document_id=document_id,
            section_index=resolved_section_index,
            paragraph_id=paragraph.element.get("id", ""),
            shape_type=shape_type,
            object_tag=inline.tag,
            attributes=dict(inline.attributes),
            run_attributes=run_attributes_result,
            char_pr_id_ref=char_ref,
            paragraph_index=paragraph_index,
            path=path,
        )

    def add_control(
        self,
        session_id: str,
        document_id: str,
        config: SessionConfig,
        *,
        section_index: int | None = None,
        attributes: Mapping[str, object] | None = None,
        control_type: str | None = None,
        para_pr_id_ref: str | int | None = None,
        style_id_ref: str | int | None = None,
        char_pr_id_ref: str | int | None = None,
        run_attributes: Mapping[str, object] | None = None,
        paragraph_attributes: Mapping[str, object] | None = None,
    ) -> ControlInsertionResult:
        handle = self._manager.get_document(session_id, document_id)
        section = handle.document.sections[section_index] if section_index is not None else None
        inline = handle.document.add_control(
            section=section,
            section_index=section_index,
            attributes=_stringify_mapping(attributes),
            control_type=control_type,
            para_pr_id_ref=para_pr_id_ref,
            style_id_ref=style_id_ref,
            char_pr_id_ref=char_pr_id_ref,
            run_attributes=_stringify_mapping(run_attributes),
            **_stringify_mapping(paragraph_attributes),
        )
        paragraph = inline.paragraph
        if paragraph.section is not None:
            resolved_section_index = (
                section_index
                if section_index is not None
                else handle.document.sections.index(paragraph.section)
            )
            paragraph_index, path = self._describe_paragraph(paragraph)
        else:
            resolved_section_index = section_index if section_index is not None else -1
            paragraph_index = None
            path = None
        run_attributes_result: dict[str, str] = {}
        char_ref: str | None = None
        if paragraph.runs:
            run = paragraph.runs[-1]
            run_attributes_result = dict(run.element.attrib)
            char_ref = run.char_pr_id_ref
        self._autosave_if_requested(config, handle)
        return ControlInsertionResult(
            document_id=document_id,
            section_index=resolved_section_index,
            paragraph_id=paragraph.element.get("id", ""),
            control_type=inline.get_attribute("type"),
            object_tag=inline.tag,
            attributes=dict(inline.attributes),
            run_attributes=run_attributes_result,
            char_pr_id_ref=char_ref,
            paragraph_index=paragraph_index,
            path=path,
        )

    def add_memo_with_anchor(
        self,
        session_id: str,
        document_id: str,
        config: SessionConfig,
        *,
        text: str,
        section_index: int | None = None,
        paragraph_text: str | None = None,
        memo_shape_id_ref: str | int | None = None,
        memo_id: str | None = None,
        author: str | None = None,
        number: int = 1,
    ) -> MemoInsertionResult:
        handle = self._manager.get_document(session_id, document_id)
        section = handle.document.sections[section_index] if section_index is not None else None
        memo, paragraph, field_value = handle.document.add_memo_with_anchor(
            text,
            section=section,
            paragraph_text=paragraph_text,
            memo_shape_id_ref=memo_shape_id_ref,
            memo_id=memo_id,
            author=author,
            number=number,
        )
        self._autosave_if_requested(config, handle)
        section_idx = section_index or (handle.document.sections.index(paragraph.section) if paragraph.section else -1)
        return MemoInsertionResult(
            document_id=document_id,
            memo_id=str(memo.id),
            section_index=section_idx,
            paragraph_id=paragraph.element.get("id", ""),
            field_value=field_value,
        )

    def replace_text(
        self,
        session_id: str,
        document_id: str,
        config: SessionConfig,
        *,
        search: str,
        replacement: str,
        text_color: str | None = None,
        underline_type: str | None = None,
        underline_color: str | None = None,
        style_id: str | None = None,
        char_pr_id_ref: str | int | None = None,
        max_replacements: int | None = None,
    ) -> ReplaceTextResult:
        handle = self._manager.get_document(session_id, document_id)
        resolved_char: str | int | None = char_pr_id_ref
        if resolved_char is None and style_id is not None:
            resolved_char = style_id
        replaced = handle.document.replace_text_in_runs(
            search,
            replacement,
            text_color=text_color,
            underline_type=underline_type,
            underline_color=underline_color,
            char_pr_id_ref=resolved_char,
            limit=max_replacements,
        )
        self._autosave_if_requested(config, handle)
        return ReplaceTextResult(document_id=document_id, replaced_count=replaced)

    def set_header_text(
        self,
        session_id: str,
        document_id: str,
        config: SessionConfig,
        *,
        text: str,
        section_index: int | None = None,
        page_type: str = "BOTH",
    ) -> HeaderFooterUpdateResult:
        handle = self._manager.get_document(session_id, document_id)
        section = handle.document.sections[section_index] if section_index is not None else None
        handle.document.set_header_text(text, section=section, section_index=section_index, page_type=page_type)
        self._autosave_if_requested(config, handle)
        return HeaderFooterUpdateResult(
            document_id=document_id,
            section_index=section_index,
            page_type=page_type,
            status="header-set",
        )

    def set_footer_text(
        self,
        session_id: str,
        document_id: str,
        config: SessionConfig,
        *,
        text: str,
        section_index: int | None = None,
        page_type: str = "BOTH",
    ) -> HeaderFooterUpdateResult:
        handle = self._manager.get_document(session_id, document_id)
        section = handle.document.sections[section_index] if section_index is not None else None
        handle.document.set_footer_text(text, section=section, section_index=section_index, page_type=page_type)
        self._autosave_if_requested(config, handle)
        return HeaderFooterUpdateResult(
            document_id=document_id,
            section_index=section_index,
            page_type=page_type,
            status="footer-set",
        )

    def remove_header(
        self,
        session_id: str,
        document_id: str,
        config: SessionConfig,
        *,
        section_index: int | None = None,
        page_type: str = "BOTH",
    ) -> HeaderFooterUpdateResult:
        handle = self._manager.get_document(session_id, document_id)
        section = handle.document.sections[section_index] if section_index is not None else None
        handle.document.remove_header(section=section, section_index=section_index, page_type=page_type)
        self._autosave_if_requested(config, handle)
        return HeaderFooterUpdateResult(
            document_id=document_id,
            section_index=section_index,
            page_type=page_type,
            status="header-removed",
        )

    def remove_footer(
        self,
        session_id: str,
        document_id: str,
        config: SessionConfig,
        *,
        section_index: int | None = None,
        page_type: str = "BOTH",
    ) -> HeaderFooterUpdateResult:
        handle = self._manager.get_document(session_id, document_id)
        section = handle.document.sections[section_index] if section_index is not None else None
        handle.document.remove_footer(section=section, section_index=section_index, page_type=page_type)
        self._autosave_if_requested(config, handle)
        return HeaderFooterUpdateResult(
            document_id=document_id,
            section_index=section_index,
            page_type=page_type,
            status="footer-removed",
        )

    # ------------------------------------------------------------------
    # 검증
    # ------------------------------------------------------------------
    def validate_document(
        self,
        session_id: str,
        document_id: str,
    ) -> ValidationReportModel:
        handle = self._manager.get_document(session_id, document_id)
        payload = BytesIO(handle.snapshot_bytes())
        report: ValidationReport = validate_document(payload)
        issues = [
            ValidationIssueModel(
                part_name=issue.part_name,
                message=issue.message,
                line=issue.line,
                column=issue.column,
            )
            for issue in report.issues
        ]
        return ValidationReportModel(
            document_id=document_id,
            ok=report.ok,
            validated_parts=list(report.validated_parts),
            issues=issues,
        )

    # ------------------------------------------------------------------
    # 내부 도우미
    # ------------------------------------------------------------------
    def _enumerate_section_paragraphs(self, section) -> list[_ParagraphEntry]:
        root = section.element
        parent_map = build_parent_map(root)
        elements = root.findall(".//hp:p", namespaces=DEFAULT_NAMESPACES)
        entries: list[_ParagraphEntry] = []
        for index, element in enumerate(elements):
            path = describe_element_path(element, parent_map)
            parent = parent_map.get(element, root)
            entries.append(_ParagraphEntry(index=index, element=element, path=path, parent=parent))
        return entries

    def _resolve_paragraph(
        self,
        handle: DocumentHandle,
        *,
        path: str | None = None,
        section_index: int | None = None,
        paragraph_index: int | None = None,
    ) -> _ResolvedParagraph:
        if path is None and (section_index is None or paragraph_index is None):
            raise HwpxMcpError("문단 위치를 지정하려면 path 또는 section_index/paragraph_index를 제공해야 합니다.")

        document = handle.document
        if section_index is not None:
            try:
                sections = [(section_index, document.sections[section_index])]
            except IndexError as exc:
                raise HwpxMcpError(f"섹션 인덱스 {section_index}가 범위를 벗어났습니다.") from exc
        else:
            sections = list(enumerate(document.sections))
            if not sections:
                raise HwpxMcpError("문서에 섹션이 존재하지 않습니다.")

        matches: list[_ResolvedParagraph] = []

        for sec_idx, section in sections:
            entries = self._enumerate_section_paragraphs(section)
            if path is None:
                assert paragraph_index is not None
                if paragraph_index < 0 or paragraph_index >= len(entries):
                    raise HwpxMcpError(
                        f"섹션 {sec_idx}에서 문단 인덱스 {paragraph_index}를 찾을 수 없습니다."
                    )
                entry = entries[paragraph_index]
                paragraph = HwpxOxmlParagraph(entry.element, section)
                return _ResolvedParagraph(
                    paragraph=paragraph,
                    section_index=sec_idx,
                    paragraph_index=entry.index,
                    path=entry.path,
                    parent=entry.parent,
                )

            for entry in entries:
                if entry.path == path:
                    paragraph = HwpxOxmlParagraph(entry.element, section)
                    matches.append(
                        _ResolvedParagraph(
                            paragraph=paragraph,
                            section_index=sec_idx,
                            paragraph_index=entry.index,
                            path=entry.path,
                            parent=entry.parent,
                        )
                    )
            if matches and section_index is not None:
                break

        if path is not None:
            if not matches:
                location = f"섹션 {section_index}" if section_index is not None else "문서 전체"
                raise HwpxMcpError(f"{location}에서 경로 '{path}' 문단을 찾을 수 없습니다.")
            if len(matches) > 1:
                raise HwpxMcpError(
                    f"경로 '{path}'에 해당하는 문단이 여러 섹션에서 발견되었습니다. section_index를 함께 지정하세요."
                )
            return matches[0]

        raise HwpxMcpError("문단 선택 정보가 부족합니다.")

    def _describe_paragraph(self, paragraph: HwpxOxmlParagraph) -> tuple[int, str]:
        section = paragraph.section
        if section is None:
            raise HwpxMcpError("문단이 속한 섹션을 확인하지 못했습니다.")
        entries = self._enumerate_section_paragraphs(section)
        for entry in entries:
            if entry.element is paragraph.element:
                return entry.index, entry.path
        raise HwpxMcpError("문단 경로를 계산하지 못했습니다.")

    def _summarize(self, handle: DocumentHandle) -> DocumentSummary:
        document = handle.document
        description = handle.label
        if description is None and handle.source_path is not None:
            description = str(handle.source_path)
        return DocumentSummary(
            document_id=handle.document_id,
            section_count=len(document.sections),
            header_count=len(document.headers),
            memo_count=len(document.memos),
            description=description,
        )

    def _autosave_if_requested(self, config: SessionConfig, handle: DocumentHandle) -> None:
        if not config.autosave_on_modify:
            return
        target = handle.source_path or handle.last_saved_path
        if target is None:
            self._logger.warning("자동 저장을 건너뜁니다 (경로 없음): id=%s", handle.document_id)
            return
        if self._workspace is None or not self._workspace.has_roots:
            self._logger.warning(
                "자동 저장을 건너뜁니다 (워크스페이스 미구성): id=%s", handle.document_id
            )
            return
        try:
            writable = self._workspace.ensure_writable(target)
        except InvalidDocumentSourceError as exc:
            self._logger.warning(
                "자동 저장 경로가 허용되지 않습니다: id=%s error=%s", handle.document_id, exc
            )
            return
        try:
            handle.save(writable)
        except DocumentSaveError as exc:  # pragma: no cover - 예외 경로
            self._logger.error("자동 저장 실패: id=%s error=%s", handle.document_id, exc)

