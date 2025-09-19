"""서버 전용 예외 정의."""

from __future__ import annotations


class HwpxMcpError(Exception):
    """도메인 전용 기본 예외."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return self.message


class SessionNotFoundError(HwpxMcpError):
    """요청한 세션이 존재하지 않을 때 발생."""


class DocumentNotFoundError(HwpxMcpError):
    """세션 내에서 문서를 찾을 수 없을 때 발생."""


class InvalidDocumentSourceError(HwpxMcpError):
    """문서 로딩 입력이 유효하지 않을 때 발생."""


class SessionCapacityError(HwpxMcpError):
    """세션 문서 수 한도를 초과했을 때 발생."""


class DocumentSaveError(HwpxMcpError):
    """문서 저장 실패 시 발생."""
