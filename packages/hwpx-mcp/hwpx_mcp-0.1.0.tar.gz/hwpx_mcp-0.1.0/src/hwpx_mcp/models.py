"""도구 입출력에 활용되는 데이터 모델."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from pydantic import BaseModel, ConfigDict, Field


class DocumentSummary(BaseModel):
    """문서 오픈 결과 요약."""

    model_config = ConfigDict(extra="forbid")

    document_id: str = Field(description="세션 내 고유 문서 ID")
    section_count: int = Field(description="섹션 수")
    header_count: int = Field(description="헤더 파트 수")
    memo_count: int = Field(description="메모 개수")
    description: str | None = Field(None, description="추가 설명 또는 라벨")


class PackageOverview(BaseModel):
    """패키지 구조 정보."""

    model_config = ConfigDict(extra="forbid")

    document_id: str
    part_names: Sequence[str]
    section_paths: Sequence[str]
    header_paths: Sequence[str]


class SectionMetadata(BaseModel):
    """섹션 파트 메타데이터."""

    model_config = ConfigDict(extra="forbid")

    index: int
    part_name: str
    paragraph_count: int
    memo_count: int
    has_header: bool
    has_footer: bool
    page_width: int | None
    page_height: int | None


class HeaderMetadata(BaseModel):
    """헤더 파트 메타데이터."""

    model_config = ConfigDict(extra="forbid")

    index: int
    part_name: str
    paragraph_count: int
    style_count: int
    track_change_count: int


class MemoMetadata(BaseModel):
    """메모 요약."""

    model_config = ConfigDict(extra="forbid")

    memo_id: str
    text: str
    section_index: int
    paragraph_count: int


class StyleMetadata(BaseModel):
    """문서 스타일 정의."""

    model_config = ConfigDict(extra="forbid")

    identifier: str = Field(description="문서 내부 참조 문자열")
    style_id: int | None = Field(None, description="정수형 스타일 ID")
    raw_id: str | None = Field(None, description="XML에 정의된 원본 ID")
    type: str | None = Field(None, description="스타일 유형 (PARA/RUN 등)")
    name: str | None = Field(None, description="로컬라이즈된 스타일 이름")
    eng_name: str | None = Field(None, description="영문 스타일 이름")
    para_pr_id_ref: int | None = Field(None, description="문단 서식 참조 ID")
    char_pr_id_ref: int | None = Field(None, description="문자 서식 참조 ID")
    next_style_id_ref: int | None = Field(None, description="다음 스타일 참조 ID")
    lang_id: int | None = Field(None, description="언어 식별자")
    lock_form: bool | None = Field(None, description="스타일 잠금 여부")
    attributes: dict[str, str] = Field(default_factory=dict)


class CharPropertyMetadata(BaseModel):
    """문자 서식 정의."""

    model_config = ConfigDict(extra="forbid")

    identifier: str = Field(description="문서 내부 참조 문자열")
    attributes: dict[str, str] = Field(default_factory=dict)
    child_attributes: dict[str, dict[str, str]] = Field(default_factory=dict)
    text_color: str | None = Field(None, description="텍스트 색상")
    underline_type: str | None = Field(None, description="밑줄 유형")
    underline_color: str | None = Field(None, description="밑줄 색상")


class MemoShapeMetadata(BaseModel):
    """메모 모양 정의."""

    model_config = ConfigDict(extra="forbid")

    identifier: str = Field(description="문서 내부 참조 문자열")
    shape_id: int | None = Field(None, description="정수형 ID")
    width: int | None = Field(None, description="가로 길이 (HWP 단위)")
    line_width: str | None = Field(None, description="외곽선 두께")
    line_type: str | None = Field(None, description="외곽선 유형")
    line_color: str | None = Field(None, description="외곽선 색상")
    fill_color: str | None = Field(None, description="채우기 색상")
    active_color: str | None = Field(None, description="선택 시 색상")
    memo_type: str | None = Field(None, description="메모 모양 타입")
    attributes: dict[str, str] = Field(default_factory=dict)


class GenericElementModel(BaseModel):
    """헤더 참조 목록에서 사용되는 일반 XML 요소."""

    model_config = ConfigDict(extra="forbid")

    name: str
    tag: str | None = None
    attributes: dict[str, str] = Field(default_factory=dict)
    text: str | None = None
    children: list["GenericElementModel"] = Field(default_factory=list)


class BulletParaHeadMetadata(BaseModel):
    """불릿의 단락 머리 정보."""

    model_config = ConfigDict(extra="forbid")

    text: str
    level: int | None = Field(None, description="적용 레벨")
    start: int | None = Field(None, description="시작 번호")
    align: str | None = Field(None, description="정렬 방식")
    use_inst_width: bool | None = Field(None, description="설치 폭 사용 여부")
    auto_indent: bool | None = Field(None, description="자동 들여쓰기 여부")
    width_adjust: int | None = Field(None, description="너비 조정 값")
    text_offset_type: str | None = Field(None, description="텍스트 오프셋 유형")
    text_offset: int | None = Field(None, description="텍스트 오프셋 값")
    attributes: dict[str, str] = Field(default_factory=dict)


class BulletMetadata(BaseModel):
    """불릿 정의."""

    model_config = ConfigDict(extra="forbid")

    identifier: str = Field(description="문서 내부 참조 문자열")
    bullet_id: int | None = Field(None, description="정수형 불릿 ID")
    char: str = Field(description="불릿 문자")
    checked_char: str | None = Field(None, description="체크 상태 문자")
    use_image: bool = Field(description="이미지 불릿 여부")
    para_head: BulletParaHeadMetadata
    image: GenericElementModel | None = None
    attributes: dict[str, str] = Field(default_factory=dict)
    other_children: dict[str, list[GenericElementModel]] = Field(default_factory=dict)


class TrackChangeAuthorMetadata(BaseModel):
    """트랙 변경 작성자 정보."""

    model_config = ConfigDict(extra="forbid")

    identifier: str = Field(description="문서 내부 참조 문자열")
    author_id: int | None = Field(None, description="정수형 작성자 ID")
    name: str | None = Field(None, description="작성자 이름")
    mark: bool | None = Field(None, description="표식 사용 여부")
    color: str | None = Field(None, description="표식 색상")
    attributes: dict[str, str] = Field(default_factory=dict)


class TrackChangeMetadata(BaseModel):
    """트랙 변경 메타데이터."""

    model_config = ConfigDict(extra="forbid")

    identifier: str = Field(description="문서 내부 참조 문자열")
    change_id: int | None = Field(None, description="정수형 변경 ID")
    change_type: str | None = Field(None, description="변경 유형")
    date: str | None = Field(None, description="변경 시각")
    author_id: int | None = Field(None, description="작성자 참조 ID")
    char_shape_id: int | None = Field(None, description="문자 서식 참조 ID")
    para_shape_id: int | None = Field(None, description="문단 서식 참조 ID")
    hide: bool | None = Field(None, description="숨김 여부")
    attributes: dict[str, str] = Field(default_factory=dict)
    author: TrackChangeAuthorMetadata | None = Field(
        None,
        description="변경 작성자 메타데이터",
    )


class HeaderNumberingMetadata(BaseModel):
    """헤더 beginNum 값."""

    model_config = ConfigDict(extra="forbid")

    header_index: int
    part_name: str
    page: int
    footnote: int
    endnote: int
    picture: int
    table: int
    equation: int


class SectionNumberingMetadata(BaseModel):
    """섹션 시작 번호 정보."""

    model_config = ConfigDict(extra="forbid")

    section_index: int
    part_name: str
    page_starts_on: str
    page: int
    picture: int
    table: int
    equation: int


class NumberingMetadata(BaseModel):
    """문서 전체 번호 매김 개요."""

    model_config = ConfigDict(extra="forbid")

    document_id: str
    headers: Sequence[HeaderNumberingMetadata]
    sections: Sequence[SectionNumberingMetadata]


class ParagraphCursor(BaseModel):
    """문단 순회 시 제공할 좌표 정보."""

    model_config = ConfigDict(extra="forbid")

    section_index: int
    paragraph_index: int
    path: str
    tag: str
    is_nested: bool
    ancestors: Sequence[str]
    preview: str


class TextExtractionResult(BaseModel):
    """문단 단위 텍스트 묶음."""

    model_config = ConfigDict(extra="forbid")

    document_id: str
    text: str


class ObjectMatch(BaseModel):
    """XML 요소 검색 결과."""

    model_config = ConfigDict(extra="forbid")

    tag: str
    path: str
    section_index: int
    section_name: str
    attributes: Mapping[str, str]
    text: str | None


class AnnotationResult(BaseModel):
    """주석 정보."""

    model_config = ConfigDict(extra="forbid")

    kind: str
    path: str
    section_index: int
    section_name: str
    value: str | None


class ParagraphInsertionResult(BaseModel):
    """문단 추가 결과."""

    model_config = ConfigDict(extra="forbid")

    document_id: str
    section_index: int
    paragraph_id: str
    text: str
    paragraph_index: int | None = Field(
        None,
        description="섹션 내 문단 인덱스 (중첩 포함)",
    )
    path: str | None = Field(
        None,
        description="텍스트 추출기와 동일한 문단 경로",
    )


class ParagraphUpdateResult(BaseModel):
    """문단 텍스트 갱신 결과."""

    model_config = ConfigDict(extra="forbid")

    document_id: str
    section_index: int
    paragraph_index: int
    paragraph_id: str | None
    path: str
    text: str
    previous_text: str


class ParagraphDeleteResult(BaseModel):
    """문단 삭제 결과."""

    model_config = ConfigDict(extra="forbid")

    document_id: str
    section_index: int
    paragraph_index: int
    paragraph_id: str | None
    path: str
    removed_text: str


class TableInsertionResult(BaseModel):
    """표 추가 결과."""

    model_config = ConfigDict(extra="forbid")

    document_id: str
    section_index: int
    paragraph_id: str
    rows: int
    cols: int


class ShapeInsertionResult(BaseModel):
    """도형 추가 결과."""

    model_config = ConfigDict(extra="forbid")

    document_id: str
    section_index: int
    paragraph_id: str
    shape_type: str
    object_tag: str = Field(description="생성된 도형 XML 태그")
    attributes: dict[str, str] = Field(default_factory=dict)
    run_attributes: dict[str, str] = Field(default_factory=dict)
    char_pr_id_ref: str | None = Field(
        None,
        description="도형이 속한 런의 문자 서식 참조 ID",
    )
    paragraph_index: int | None = Field(
        None,
        description="섹션 내 문단 인덱스 (중첩 포함)",
    )
    path: str | None = Field(
        None,
        description="도형이 삽입된 문단 경로",
    )


class ControlInsertionResult(BaseModel):
    """컨트롤 추가 결과."""

    model_config = ConfigDict(extra="forbid")

    document_id: str
    section_index: int
    paragraph_id: str
    control_type: str | None = Field(
        None,
        description="컨트롤 타입 속성 값",
    )
    object_tag: str = Field(description="생성된 컨트롤 XML 태그")
    attributes: dict[str, str] = Field(default_factory=dict)
    run_attributes: dict[str, str] = Field(default_factory=dict)
    char_pr_id_ref: str | None = Field(
        None,
        description="컨트롤이 속한 런의 문자 서식 참조 ID",
    )
    paragraph_index: int | None = Field(
        None,
        description="섹션 내 문단 인덱스 (중첩 포함)",
    )
    path: str | None = Field(
        None,
        description="컨트롤이 삽입된 문단 경로",
    )


class MemoInsertionResult(BaseModel):
    """메모 추가 결과."""

    model_config = ConfigDict(extra="forbid")

    document_id: str
    memo_id: str
    section_index: int
    paragraph_id: str
    field_value: str


class ReplaceTextResult(BaseModel):
    """텍스트 치환 결과."""

    model_config = ConfigDict(extra="forbid")

    document_id: str
    replaced_count: int


class HeaderFooterUpdateResult(BaseModel):
    """머리말/꼬리말 변경 결과."""

    model_config = ConfigDict(extra="forbid")

    document_id: str
    section_index: int | None
    page_type: str
    status: str


class ValidationIssueModel(BaseModel):
    """문제 지점 정보."""

    model_config = ConfigDict(extra="forbid")

    part_name: str
    message: str
    line: int | None = None
    column: int | None = None


class ValidationReportModel(BaseModel):
    """스키마 검증 결과."""

    model_config = ConfigDict(extra="forbid")

    document_id: str
    ok: bool
    validated_parts: Sequence[str]
    issues: Sequence[ValidationIssueModel]


class SaveResultModel(BaseModel):
    """저장 결과."""

    model_config = ConfigDict(extra="forbid")

    document_id: str
    saved_to: str | None = Field(None, description="저장된 경로 또는 설명")
    size: int | None = Field(None, description="저장된 바이트 크기")
    base64_content: str | None = Field(
        None,
        description="메모리로 받은 경우 Base64 인코딩된 값",
    )
    backup_path: str | None = Field(
        None,
        description="백업 파일 경로 (백업이 생성된 경우)",
    )


JsonMapping = Mapping[str, Any]
"""단순 JSON 매핑 타입 별칭."""
