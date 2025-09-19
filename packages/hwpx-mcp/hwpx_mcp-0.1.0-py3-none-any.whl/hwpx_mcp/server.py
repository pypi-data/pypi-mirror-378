"""Smithery FastMCP 서버 구현."""

from __future__ import annotations

import base64
from typing import Any, Mapping, Sequence

from mcp.server.fastmcp import Context, FastMCP
from pydantic import ValidationError

from smithery.decorators import smithery

from .config import ServerSettings, SessionConfig
from .exceptions import InvalidDocumentSourceError
from .logging_utils import configure_logging
from .services.document_service import DocumentService
from .session import DocumentSessionManager
from .user_config import load_user_config
from .workspace import WorkspaceResourceManager, WorkspaceService


def _decode_base64(value: str | None) -> bytes | None:
    if value is None:
        return None
    try:
        return base64.b64decode(value)
    except Exception as exc:  # pragma: no cover - 잘못된 인코딩 보호
        raise InvalidDocumentSourceError("Base64 디코딩에 실패했습니다.") from exc


def _session_info(ctx: Context | None) -> tuple[str, SessionConfig]:
    if ctx is None:
        raise InvalidDocumentSourceError("세션 컨텍스트가 필요합니다.")

    def _from_session_obj(session: Any) -> str | None:
        if session is None:
            return None
        for attr in ("id", "session_id", "sessionId"):
            value = getattr(session, attr, None)
            if value:
                return str(value)
        transport = getattr(session, "transport", None)
        if transport is not None:
            for attr in ("mcp_session_id", "session_id"):
                value = getattr(transport, attr, None)
                if value:
                    return str(value)
        return None

    session_id: str | None = None

    root_session_id = getattr(ctx, "root_session_id", None)
    if root_session_id:
        session_id = str(root_session_id)

    if session_id is None:
        try:
            session_id = _from_session_obj(getattr(ctx, "session"))
        except (AttributeError, ValueError):
            session_id = None

    if session_id is None:
        request_context = getattr(ctx, "request_context", None)
        if request_context is not None:
            session_id = _from_session_obj(getattr(request_context, "session", None))
            if session_id is None:
                request = getattr(request_context, "request", None)
                if request is not None:
                    headers = getattr(request, "headers", None)
                    if headers is not None:
                        session_id = headers.get("mcp-session-id") or headers.get("mcp_session_id")
                    if not session_id:
                        scope = getattr(request, "scope", None)
                        if scope is not None:
                            session_id = scope.get("mcp-session-id") or scope.get("mcp_session_id")
                    if session_id:
                        session_id = str(session_id)

    if session_id is None:
        session_id = getattr(ctx, "session_id", None)
        if session_id is not None:
            session_id = str(session_id)

    if not session_id:
        raise InvalidDocumentSourceError("세션 식별자를 확인할 수 없습니다.")

    session_config = getattr(ctx, "session_config", None) or SessionConfig()
    if not isinstance(session_config, SessionConfig):
        try:
            session_config = SessionConfig.model_validate(session_config)
        except ValidationError as exc:  # pragma: no cover - 방어 로직
            raise InvalidDocumentSourceError(f"세션 설정이 올바르지 않습니다: {exc}") from exc
    return session_id, session_config


@smithery.server(config_schema=SessionConfig)
def create_server() -> FastMCP:
    """FastMCP 서버를 생성한다."""

    settings = ServerSettings.from_env()
    logger = configure_logging(settings.log_level)
    user_config = load_user_config()
    workspace = WorkspaceService(user_config.normalized_workspaces(), logger=logger)
    if workspace.has_roots:
        logger.info(
            "허용된 워크스페이스: %s",
            ", ".join(str(path) for path in workspace.allowed_paths()),
        )
    else:
        logger.warning("허용된 워크스페이스가 설정되지 않았습니다. configure 명령을 먼저 실행하세요.")
    manager = DocumentSessionManager(max_documents_per_session=settings.max_documents_per_session)
    service = DocumentService(manager, settings, logger, workspace, user_config)

    server = FastMCP("HWPX 문서 자동화")
    server._resource_manager = WorkspaceResourceManager(server._resource_manager, workspace, logger)

    # --------------------------------------------------------------
    # 문서 관리
    # --------------------------------------------------------------
    @server.tool()
    def load_document(
        document_id: str | None = None,
        path: str | None = None,
        base64_content: str | None = None,
        label: str | None = None,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        session_id, _ = _session_info(ctx)
        content = _decode_base64(base64_content)
        summary = service.load_document(
            session_id,
            path=path,
            content=content,
            document_id=document_id,
            label=label,
        )
        return summary.model_dump()

    @server.tool()
    def new_document(
        document_id: str | None = None,
        label: str | None = None,
        include_template: bool = False,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        session_id, _ = _session_info(ctx)
        summary, template = service.new_document(
            session_id,
            document_id=document_id,
            label=label,
            include_template=include_template,
        )
        payload = summary.model_dump()
        if template is not None:
            payload["blank_document_base64"] = template
        return payload

    @server.tool()
    def save_document(
        document_id: str,
        path: str | None = None,
        return_base64: bool = False,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        session_id, _ = _session_info(ctx)
        result = service.save_document(
            session_id,
            document_id,
            path=path,
            return_base64=return_base64,
        )
        return result.model_dump()

    @server.tool()
    def close_document(document_id: str, ctx: Context | None = None) -> dict[str, str]:
        session_id, _ = _session_info(ctx)
        service.close_document(session_id, document_id)
        return {"status": "closed", "document_id": document_id}

    # --------------------------------------------------------------
    # 구조 탐색
    # --------------------------------------------------------------
    @server.tool()
    def inspect_package(document_id: str, ctx: Context | None = None) -> dict[str, Any]:
        session_id, _ = _session_info(ctx)
        overview = service.inspect_package(session_id, document_id)
        return overview.model_dump()

    @server.tool()
    def list_sections(document_id: str, ctx: Context | None = None) -> list[dict[str, Any]]:
        session_id, _ = _session_info(ctx)
        sections = service.list_sections(session_id, document_id)
        return [section.model_dump() for section in sections]

    @server.tool()
    def list_headers(document_id: str, ctx: Context | None = None) -> list[dict[str, Any]]:
        session_id, _ = _session_info(ctx)
        headers = service.list_headers(session_id, document_id)
        return [header.model_dump() for header in headers]

    @server.tool()
    def list_memos(document_id: str, ctx: Context | None = None) -> list[dict[str, Any]]:
        session_id, _ = _session_info(ctx)
        memos = service.list_memos(session_id, document_id)
        return [memo.model_dump() for memo in memos]

    @server.tool()
    def list_styles(
        document_id: str,
        style_type: str | None = None,
        name_contains: str | None = None,
        limit: int | None = None,
        ctx: Context | None = None,
    ) -> list[dict[str, Any]]:
        session_id, session_config = _session_info(ctx)
        styles = service.list_styles(
            session_id,
            document_id,
            session_config,
            style_type=style_type,
            name_contains=name_contains,
            limit=limit,
        )
        return [style.model_dump() for style in styles]

    @server.tool()
    def list_char_properties(
        document_id: str,
        text_color: str | None = None,
        underline_type: str | None = None,
        underline_color: str | None = None,
        limit: int | None = None,
        ctx: Context | None = None,
    ) -> list[dict[str, Any]]:
        session_id, session_config = _session_info(ctx)
        char_props = service.list_char_properties(
            session_id,
            document_id,
            session_config,
            text_color=text_color,
            underline_type=underline_type,
            underline_color=underline_color,
            limit=limit,
        )
        return [item.model_dump() for item in char_props]

    @server.tool()
    def list_memo_shapes(
        document_id: str,
        memo_type: str | None = None,
        limit: int | None = None,
        ctx: Context | None = None,
    ) -> list[dict[str, Any]]:
        session_id, session_config = _session_info(ctx)
        shapes = service.list_memo_shapes(
            session_id,
            document_id,
            session_config,
            memo_type=memo_type,
            limit=limit,
        )
        return [shape.model_dump() for shape in shapes]

    @server.tool()
    def list_bullets(
        document_id: str,
        level: int | None = None,
        use_image: bool | None = None,
        char_contains: str | None = None,
        limit: int | None = None,
        ctx: Context | None = None,
    ) -> list[dict[str, Any]]:
        session_id, session_config = _session_info(ctx)
        bullets = service.list_bullets(
            session_id,
            document_id,
            session_config,
            level=level,
            use_image=use_image,
            char_contains=char_contains,
            limit=limit,
        )
        return [bullet.model_dump() for bullet in bullets]

    @server.tool()
    def list_track_changes(
        document_id: str,
        change_type: str | None = None,
        author_id: int | None = None,
        include_hidden: bool = True,
        limit: int | None = None,
        ctx: Context | None = None,
    ) -> list[dict[str, Any]]:
        session_id, session_config = _session_info(ctx)
        changes = service.list_track_changes(
            session_id,
            document_id,
            session_config,
            change_type=change_type,
            author_id=author_id,
            include_hidden=include_hidden,
            limit=limit,
        )
        return [change.model_dump() for change in changes]

    @server.tool()
    def describe_numberings(document_id: str, ctx: Context | None = None) -> dict[str, Any]:
        session_id, _ = _session_info(ctx)
        metadata = service.describe_numberings(session_id, document_id)
        return metadata.model_dump()

    @server.tool()
    def iter_paragraphs(
        document_id: str,
        section_indexes: Sequence[int] | None = None,
        limit: int | None = None,
        object_behavior: str | None = None,
        ctx: Context | None = None,
    ) -> list[dict[str, Any]]:
        session_id, session_config = _session_info(ctx)
        paragraphs = service.iter_paragraphs(
            session_id,
            document_id,
            session_config,
            section_indexes=section_indexes,
            limit=limit,
            object_behavior=object_behavior,
        )
        return [item.model_dump() for item in paragraphs]

    @server.tool()
    def extract_text(
        document_id: str,
        object_behavior: str | None = None,
        preserve_breaks: bool | None = None,
        annotation_mode: str | None = None,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        session_id, session_config = _session_info(ctx)
        result = service.extract_text(
            session_id,
            document_id,
            session_config,
            object_behavior=object_behavior,
            preserve_breaks=preserve_breaks,
            annotation_mode=annotation_mode,
        )
        return result.model_dump()

    @server.tool()
    def find_objects(
        document_id: str,
        tag: str | Sequence[str] | None = None,
        xpath: str | None = None,
        attributes: Mapping[str, str] | None = None,
        limit: int | None = None,
        ctx: Context | None = None,
    ) -> list[dict[str, Any]]:
        session_id, session_config = _session_info(ctx)
        matches = service.find_objects(
            session_id,
            document_id,
            session_config,
            tag=tag,
            xpath=xpath,
            attributes=attributes,
            limit=limit,
        )
        return [match.model_dump() for match in matches]

    @server.tool()
    def list_annotations(
        document_id: str,
        kinds: Sequence[str] | None = None,
        preserve_breaks: bool | None = None,
        limit: int | None = None,
        ctx: Context | None = None,
    ) -> list[dict[str, Any]]:
        session_id, session_config = _session_info(ctx)
        items = service.list_annotations(
            session_id,
            document_id,
            session_config,
            kinds=kinds,
            preserve_breaks=preserve_breaks,
            limit=limit,
        )
        return [item.model_dump() for item in items]

    # --------------------------------------------------------------
    # 편집 도구
    # --------------------------------------------------------------
    @server.tool()
    def add_paragraph(
        document_id: str,
        text: str,
        section_index: int | None = None,
        para_pr_id_ref: str | None = None,
        style_id_ref: str | None = None,
        char_pr_id_ref: str | None = None,
        run_attributes: Mapping[str, str] | None = None,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        session_id, session_config = _session_info(ctx)
        result = service.add_paragraph(
            session_id,
            document_id,
            session_config,
            text=text,
            section_index=section_index,
            para_pr_id_ref=para_pr_id_ref,
            style_id_ref=style_id_ref,
            char_pr_id_ref=char_pr_id_ref,
            run_attributes=run_attributes,
        )
        return result.model_dump()

    @server.tool()
    def edit_paragraph(
        document_id: str,
        text: str,
        path: str | None = None,
        section_index: int | None = None,
        paragraph_index: int | None = None,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        session_id, session_config = _session_info(ctx)
        result = service.update_paragraph_text(
            session_id,
            document_id,
            session_config,
            text=text,
            path=path,
            section_index=section_index,
            paragraph_index=paragraph_index,
        )
        return result.model_dump()

    @server.tool()
    def insert_paragraph_at(
        document_id: str,
        text: str,
        path: str | None = None,
        section_index: int | None = None,
        paragraph_index: int | None = None,
        after: bool = False,
        para_pr_id_ref: str | None = None,
        style_id_ref: str | None = None,
        char_pr_id_ref: str | None = None,
        run_attributes: Mapping[str, str] | None = None,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        session_id, session_config = _session_info(ctx)
        result = service.insert_paragraph_at(
            session_id,
            document_id,
            session_config,
            text=text,
            path=path,
            section_index=section_index,
            paragraph_index=paragraph_index,
            after=after,
            para_pr_id_ref=para_pr_id_ref,
            style_id_ref=style_id_ref,
            char_pr_id_ref=char_pr_id_ref,
            run_attributes=run_attributes,
        )
        return result.model_dump()

    @server.tool()
    def delete_paragraph(
        document_id: str,
        path: str | None = None,
        section_index: int | None = None,
        paragraph_index: int | None = None,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        session_id, session_config = _session_info(ctx)
        result = service.delete_paragraph(
            session_id,
            document_id,
            session_config,
            path=path,
            section_index=section_index,
            paragraph_index=paragraph_index,
        )
        return result.model_dump()

    @server.tool()
    def add_table(
        document_id: str,
        rows: int,
        cols: int,
        section_index: int | None = None,
        width: int | None = None,
        height: int | None = None,
        border_fill_id_ref: str | int = "0",
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        session_id, session_config = _session_info(ctx)
        result = service.add_table(
            session_id,
            document_id,
            session_config,
            rows=rows,
            cols=cols,
            section_index=section_index,
            width=width,
            height=height,
            border_fill_id_ref=border_fill_id_ref,
        )
        return result.model_dump()

    @server.tool()
    def add_shape(
        document_id: str,
        shape_type: str,
        section_index: int | None = None,
        attributes: Mapping[str, Any] | None = None,
        para_pr_id_ref: str | None = None,
        style_id_ref: str | None = None,
        char_pr_id_ref: str | None = None,
        run_attributes: Mapping[str, Any] | None = None,
        paragraph_attributes: Mapping[str, Any] | None = None,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        session_id, session_config = _session_info(ctx)
        result = service.add_shape(
            session_id,
            document_id,
            session_config,
            shape_type=shape_type,
            section_index=section_index,
            attributes=attributes,
            para_pr_id_ref=para_pr_id_ref,
            style_id_ref=style_id_ref,
            char_pr_id_ref=char_pr_id_ref,
            run_attributes=run_attributes,
            paragraph_attributes=paragraph_attributes,
        )
        return result.model_dump()

    @server.tool()
    def add_control(
        document_id: str,
        section_index: int | None = None,
        attributes: Mapping[str, Any] | None = None,
        control_type: str | None = None,
        para_pr_id_ref: str | None = None,
        style_id_ref: str | None = None,
        char_pr_id_ref: str | None = None,
        run_attributes: Mapping[str, Any] | None = None,
        paragraph_attributes: Mapping[str, Any] | None = None,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        session_id, session_config = _session_info(ctx)
        result = service.add_control(
            session_id,
            document_id,
            session_config,
            section_index=section_index,
            attributes=attributes,
            control_type=control_type,
            para_pr_id_ref=para_pr_id_ref,
            style_id_ref=style_id_ref,
            char_pr_id_ref=char_pr_id_ref,
            run_attributes=run_attributes,
            paragraph_attributes=paragraph_attributes,
        )
        return result.model_dump()

    @server.tool()
    def add_memo_with_anchor(
        document_id: str,
        text: str,
        section_index: int | None = None,
        paragraph_text: str | None = None,
        memo_shape_id_ref: str | None = None,
        memo_id: str | None = None,
        author: str | None = None,
        number: int = 1,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        session_id, session_config = _session_info(ctx)
        result = service.add_memo_with_anchor(
            session_id,
            document_id,
            session_config,
            text=text,
            section_index=section_index,
            paragraph_text=paragraph_text,
            memo_shape_id_ref=memo_shape_id_ref,
            memo_id=memo_id,
            author=author,
            number=number,
        )
        return result.model_dump()

    @server.tool()
    def replace_text(
        document_id: str,
        search: str,
        replacement: str,
        text_color: str | None = None,
        underline_type: str | None = None,
        underline_color: str | None = None,
        style_id: str | None = None,
        char_pr_id_ref: str | None = None,
        max_replacements: int | None = None,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        session_id, session_config = _session_info(ctx)
        result = service.replace_text(
            session_id,
            document_id,
            session_config,
            search=search,
            replacement=replacement,
            text_color=text_color,
            underline_type=underline_type,
            underline_color=underline_color,
            style_id=style_id,
            char_pr_id_ref=char_pr_id_ref,
            max_replacements=max_replacements,
        )
        return result.model_dump()

    @server.tool()
    def set_header_text(
        document_id: str,
        text: str,
        section_index: int | None = None,
        page_type: str = "BOTH",
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        session_id, session_config = _session_info(ctx)
        result = service.set_header_text(
            session_id,
            document_id,
            session_config,
            text=text,
            section_index=section_index,
            page_type=page_type,
        )
        return result.model_dump()

    @server.tool()
    def set_footer_text(
        document_id: str,
        text: str,
        section_index: int | None = None,
        page_type: str = "BOTH",
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        session_id, session_config = _session_info(ctx)
        result = service.set_footer_text(
            session_id,
            document_id,
            session_config,
            text=text,
            section_index=section_index,
            page_type=page_type,
        )
        return result.model_dump()

    @server.tool()
    def remove_header(
        document_id: str,
        section_index: int | None = None,
        page_type: str = "BOTH",
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        session_id, session_config = _session_info(ctx)
        result = service.remove_header(
            session_id,
            document_id,
            session_config,
            section_index=section_index,
            page_type=page_type,
        )
        return result.model_dump()

    @server.tool()
    def remove_footer(
        document_id: str,
        section_index: int | None = None,
        page_type: str = "BOTH",
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        session_id, session_config = _session_info(ctx)
        result = service.remove_footer(
            session_id,
            document_id,
            session_config,
            section_index=section_index,
            page_type=page_type,
        )
        return result.model_dump()

    # --------------------------------------------------------------
    # 검증
    # --------------------------------------------------------------
    @server.tool()
    def validate_document(document_id: str, ctx: Context | None = None) -> dict[str, Any]:
        session_id, _ = _session_info(ctx)
        report = service.validate_document(session_id, document_id)
        return report.model_dump()

    return server
