"""서버 및 세션 설정 스키마 정의."""

from __future__ import annotations

import os
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class SessionConfig(BaseModel):
    """클라이언트 세션별 실행 옵션."""


    # Smithery 테스트 프로필 등에서 추가 메타데이터를 전달해도
    # 무시하고 기본값을 적용할 수 있도록 extra를 허용한다.
    model_config = ConfigDict(extra="ignore")


    autosave_on_modify: bool = Field(
        False,
        description="도구 호출로 문서를 수정한 뒤 자동으로 저장할지 여부",
    )
    include_nested_paragraphs: bool = Field(
        True,
        description="문단 순회 시 표·도형 등 내부 문단을 포함할지 여부",
    )
    object_placeholder: str | None = Field(
        None,
        description="텍스트 추출 시 객체를 대체할 문자열 (None이면 무시)",
    )
    annotation_mode: Literal["ignore", "summary", "inline"] = Field(
        "summary",
        description="주석 정보를 어떻게 표현할지 선택 (ignore/summary/inline)",
    )
    preserve_line_breaks: bool = Field(
        True,
        description="텍스트 추출 시 줄바꿈을 유지할지 여부",
    )
    max_items: int = Field(
        200,
        ge=1,
        le=1000,
        description="목록형 도구가 반환할 최대 항목 수 (안정성 한도)",
    )


class ServerSettings(BaseModel):
    """프로세스 전역 설정 값."""

    model_config = ConfigDict(extra="ignore")

    log_level: str = Field("INFO", description="루트 로거 로그 레벨")
    max_documents_per_session: int = Field(
        8,
        ge=1,
        le=64,
        description="세션 당 동시 오픈 가능한 문서 수 한도",
    )
    default_encoding: str = Field(
        "utf-8",
        description="파일 경로 해석 시 기본 사용할 문자 인코딩",
    )

    @classmethod
    def from_env(cls) -> "ServerSettings":
        """환경 변수 값을 반영해 설정 인스턴스를 생성한다."""

        raw = {
            "log_level": os.getenv("HWPX_MCP_LOG_LEVEL"),
            "max_documents_per_session": os.getenv("HWPX_MCP_MAX_DOCUMENTS"),
            "default_encoding": os.getenv("HWPX_MCP_DEFAULT_ENCODING"),
        }

        data: dict[str, object] = {}
        for key, value in raw.items():
            if value is None or value == "":
                continue
            if key == "max_documents_per_session":
                try:
                    data[key] = int(value)
                except ValueError:
                    raise ValidationError(
                        [
                            {
                                "loc": (key,),
                                "msg": "정수로 변환할 수 없는 값입니다.",
                                "type": "type_error.integer",
                            }
                        ],
                        cls,
                    ) from None
            else:
                data[key] = value

        return cls(**data)
