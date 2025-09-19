"""세션별 HWPX 문서 상태 관리."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path
from threading import RLock
from typing import BinaryIO, Dict, Iterable
from uuid import uuid4

from hwpx.document import HwpxDocument

from .exceptions import (
    DocumentNotFoundError,
    DocumentSaveError,
    SessionCapacityError,
    SessionNotFoundError,
)


def _now_utc() -> datetime:
    """UTC 현재 시간을 반환한다."""

    return datetime.now(UTC)


@dataclass(slots=True)
class DocumentHandle:
    """열린 문서와 부가 정보를 보관."""

    document_id: str
    document: HwpxDocument
    source_path: Path | None = None
    label: str | None = None
    opened_at: datetime = field(default_factory=_now_utc)
    last_saved_path: Path | None = None

    def snapshot_bytes(self) -> bytes:
        """현재 메모리 상태를 HWPX 아카이브 바이트로 직렬화한다."""

        updates = self.document.oxml.serialize()
        blob = self.document.package.save(None, updates)
        if isinstance(blob, bytes):
            return blob
        if hasattr(blob, "getvalue"):
            return blob.getvalue()  # type: ignore[no-any-return]
        raise DocumentSaveError("메모리 스냅샷을 생성할 수 없습니다.")

    def open_stream(self) -> BytesIO:
        """텍스트 추출 도구에 전달할 수 있도록 BytesIO를 반환."""

        return BytesIO(self.snapshot_bytes())

    def save(self, path_or_stream: str | Path | BinaryIO | None = None) -> tuple[str | None, int | None, bytes | None]:
        """문서를 저장하고 경로/크기/바이트 정보를 반환한다."""

        destination = path_or_stream or self.source_path
        try:
            result = self.document.save(destination)
        except Exception as exc:  # pragma: no cover - 외부 I/O 실패 보강
            raise DocumentSaveError(f"문서를 저장하지 못했습니다: {exc}") from exc

        saved_path: str | None = None
        size: int | None = None
        payload: bytes | None = None

        if isinstance(result, (str, Path)):
            path_obj = Path(result)
            saved_path = str(path_obj)
            self.last_saved_path = path_obj
            self.source_path = path_obj
            try:
                size = path_obj.stat().st_size
            except OSError:
                size = None
        elif hasattr(result, "getvalue"):
            payload = result.getvalue()  # type: ignore[assignment]
            size = len(payload)
        elif isinstance(result, bytes):
            payload = result
            size = len(payload)
        else:
            payload = None

        if destination is None and saved_path is None:
            saved_path = "memory"

        return saved_path, size, payload


class SessionState:
    """단일 MCP 세션에서 열린 문서 컨테이너."""

    def __init__(self) -> None:
        self._documents: Dict[str, DocumentHandle] = {}

    def get(self, document_id: str) -> DocumentHandle:
        try:
            return self._documents[document_id]
        except KeyError as exc:
            raise DocumentNotFoundError(f"문서 ID '{document_id}'를 찾을 수 없습니다.") from exc

    def put(self, handle: DocumentHandle, *, limit: int | None = None) -> None:
        if limit is not None and limit > 0 and handle.document_id not in self._documents:
            if len(self._documents) >= limit:
                raise SessionCapacityError("세션 문서 수 한도를 초과했습니다.")
        self._documents[handle.document_id] = handle

    def remove(self, document_id: str) -> None:
        if document_id in self._documents:
            del self._documents[document_id]
        else:
            raise DocumentNotFoundError(f"문서 ID '{document_id}'를 찾을 수 없습니다.")

    def values(self) -> Iterable[DocumentHandle]:
        return self._documents.values()


class DocumentSessionManager:
    """세션별 문서 핸들을 안전하게 관리하는 관리자."""

    def __init__(self, *, max_documents_per_session: int | None = None) -> None:
        self._sessions: Dict[str, SessionState] = {}
        self._lock = RLock()
        self._max_per_session = max_documents_per_session

    @staticmethod
    def generate_document_id() -> str:
        """새 문서 ID를 생성한다."""

        return uuid4().hex

    def _state(self, session_id: str, *, create: bool = False) -> SessionState:
        with self._lock:
            if session_id not in self._sessions:
                if not create:
                    raise SessionNotFoundError("세션이 초기화되지 않았습니다.")
                self._sessions[session_id] = SessionState()
            return self._sessions[session_id]

    def open_session(self, session_id: str) -> None:
        """세션 상태를 미리 생성한다."""

        self._state(session_id, create=True)

    def close_session(self, session_id: str) -> None:
        """세션을 종료하고 문서 캐시를 해제한다."""

        with self._lock:
            self._sessions.pop(session_id, None)

    def register_document(self, session_id: str, handle: DocumentHandle) -> DocumentHandle:
        """세션에 문서를 추가한다."""

        state = self._state(session_id, create=True)
        state.put(handle, limit=self._max_per_session)
        return handle

    def get_document(self, session_id: str, document_id: str) -> DocumentHandle:
        state = self._state(session_id, create=False)
        return state.get(document_id)

    def close_document(self, session_id: str, document_id: str) -> None:
        state = self._state(session_id, create=False)
        state.remove(document_id)

    def iter_documents(self, session_id: str) -> Iterable[DocumentHandle]:
        state = self._state(session_id, create=False)
        return state.values()
