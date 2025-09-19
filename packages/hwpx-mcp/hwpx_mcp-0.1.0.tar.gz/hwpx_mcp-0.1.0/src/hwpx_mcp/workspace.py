"""허용된 워크스페이스 경로와 리소스를 관리한다."""

from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from datetime import UTC, datetime
from logging import Logger, getLogger
from pathlib import Path
from typing import Sequence
from urllib.parse import quote

from mcp.server.fastmcp.resources import FunctionResource, Resource

from .exceptions import InvalidDocumentSourceError


@dataclass(slots=True)
class WorkspaceRoot:
    """사용자가 허용한 루트 디렉터리 정보."""

    key: str
    path: Path
    display_name: str


@dataclass(slots=True)
class WorkspaceDocument:
    """워크스페이스 내부 문서 메타데이터."""

    workspace: WorkspaceRoot
    uri: str
    absolute_path: Path
    relative_path: Path
    display_name: str
    size: int | None
    modified: datetime | None

    @property
    def description(self) -> str:
        parts = [self.workspace.display_name, self.relative_path.as_posix()]
        if self.size is not None:
            parts.append(f"{self.size} bytes")
        if self.modified is not None:
            parts.append(self.modified.isoformat())
        return " · ".join(parts)


@dataclass(slots=True)
class WorkspaceIndex:
    """워크스페이스 단위 문서 목록 리소스."""

    workspace: WorkspaceRoot
    uri: str
    payload: str


@dataclass(slots=True)
class WorkspaceSnapshot:
    """현재 워크스페이스 내 문서/인덱스 스냅샷."""

    documents: list[WorkspaceDocument]
    indexes: list[WorkspaceIndex]


class WorkspaceService:
    """허용된 디렉터리에 대한 접근과 리소스 생성을 담당한다."""

    def __init__(
        self,
        allowed: Sequence[Path],
        *,
        logger: Logger | None = None,
        patterns: Sequence[str] | None = None,
        max_documents_per_root: int = 200,
    ) -> None:
        self._logger = logger or getLogger("hwpx_mcp.workspace")
        self._roots: list[WorkspaceRoot] = []
        self._patterns = tuple(patterns or ("*.hwpx", "*.hwpxz"))
        self._max_per_root = max_documents_per_root
        self._doc_cache: dict[str, WorkspaceDocument] = {}
        self._index_cache: dict[str, WorkspaceIndex] = {}

        for idx, raw in enumerate(allowed):
            path = raw.expanduser()
            try:
                resolved = path.resolve(strict=False)
            except OSError:
                resolved = path
            if not resolved.exists():
                self._logger.debug("워크스페이스 경로가 존재하지 않음: %s", resolved)
            key = self._make_key(resolved, idx)
            display = resolved.name or key
            self._roots.append(WorkspaceRoot(key=key, path=resolved, display_name=display))

    @property
    def has_roots(self) -> bool:
        return bool(self._roots)

    def allowed_paths(self) -> list[Path]:
        return [root.path for root in self._roots]

    def _make_key(self, path: Path, index: int) -> str:
        slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", path.name or f"workspace-{index}").strip("-")
        if not slug:
            slug = f"workspace-{index}"
        base = slug.lower()
        existing = {root.key for root in self._roots}
        candidate = base
        counter = 1
        while candidate in existing:
            counter += 1
            candidate = f"{base}-{counter}"
        return candidate

    def snapshot(self) -> WorkspaceSnapshot:
        """허용된 워크스페이스를 스캔해 리소스 스냅샷을 생성한다."""

        documents: list[WorkspaceDocument] = []
        indexes: list[WorkspaceIndex] = []
        self._doc_cache.clear()
        self._index_cache.clear()

        for root in self._roots:
            if not root.path.exists():
                self._logger.warning("워크스페이스 경로가 존재하지 않습니다: %s", root.path)
                continue
            if not root.path.is_dir():
                self._logger.warning("워크스페이스가 디렉터리가 아닙니다: %s", root.path)
                continue

            collected: list[WorkspaceDocument] = []
            for pattern in self._patterns:
                for candidate in sorted(root.path.rglob(pattern)):
                    if not candidate.is_file():
                        continue
                    try:
                        stat = candidate.stat()
                        size = stat.st_size
                        modified = datetime.fromtimestamp(stat.st_mtime, UTC)
                    except OSError:
                        size = None
                        modified = None
                    relative = candidate.relative_to(root.path)
                    encoded = quote(relative.as_posix(), safe="")
                    uri = f"hwpx-doc://{root.key}/{encoded}"
                    doc = WorkspaceDocument(
                        workspace=root,
                        uri=uri,
                        absolute_path=candidate,
                        relative_path=relative,
                        display_name=candidate.name,
                        size=size,
                        modified=modified,
                    )
                    documents.append(doc)
                    collected.append(doc)
                    self._doc_cache[uri] = doc
                    if len(collected) >= self._max_per_root:
                        break
                if len(collected) >= self._max_per_root:
                    break

            payload = {
                "workspace": root.display_name,
                "root": str(root.path),
                "documents": [
                    {
                        "uri": doc.uri,
                        "relative_path": doc.relative_path.as_posix(),
                        "size": doc.size,
                        "modified": doc.modified.isoformat() if doc.modified else None,
                    }
                    for doc in collected
                ],
            }
            index_uri = f"hwpx-index://{root.key}/documents"
            index = WorkspaceIndex(workspace=root, uri=index_uri, payload=json.dumps(payload, ensure_ascii=False, indent=2))
            indexes.append(index)
            self._index_cache[index_uri] = index

        return WorkspaceSnapshot(documents=documents, indexes=indexes)

    def ensure_readable(self, path: str | Path) -> Path:
        """읽기 가능한 경로인지 확인하고 정규화된 Path를 반환한다."""

        resolved = self._resolve(path)
        if not resolved.exists():
            raise InvalidDocumentSourceError("지정한 파일을 찾을 수 없습니다. 허용된 워크스페이스 경로를 확인하세요.")
        self._assert_within_root(resolved)
        return resolved

    def ensure_writable(self, path: str | Path) -> Path:
        """쓰기 가능한 경로인지 검증한다."""

        resolved = self._resolve(path)
        parent = resolved.parent
        self._assert_within_root(parent)
        parent.mkdir(parents=True, exist_ok=True)
        return resolved

    def lookup_document(self, uri: str) -> WorkspaceDocument | None:
        if uri in self._doc_cache:
            return self._doc_cache[uri]
        snapshot = self.snapshot()
        mapping = {doc.uri: doc for doc in snapshot.documents}
        self._doc_cache.update(mapping)
        return self._doc_cache.get(uri)

    def lookup_index(self, uri: str) -> WorkspaceIndex | None:
        if uri in self._index_cache:
            return self._index_cache[uri]
        snapshot = self.snapshot()
        mapping = {index.uri: index for index in snapshot.indexes}
        self._index_cache.update(mapping)
        return self._index_cache.get(uri)

    def create_document_resource(self, doc: WorkspaceDocument) -> Resource:
        """문서를 읽어들일 FunctionResource를 생성한다."""

        def reader(path: Path = doc.absolute_path) -> bytes:
            try:
                return path.read_bytes()
            except OSError as exc:
                raise InvalidDocumentSourceError(f"문서를 읽지 못했습니다: {path}") from exc

        return FunctionResource.from_function(
            reader,
            uri=doc.uri,
            name=f"{doc.workspace.key}:{doc.relative_path.as_posix()}",
            title=doc.display_name,
            description=doc.description,
            mime_type="application/octet-stream",
        )

    def create_index_resource(self, index: WorkspaceIndex) -> Resource:
        """문서 목록을 반환하는 FunctionResource를 생성한다."""

        def reader(payload: str = index.payload) -> str:
            return payload

        return FunctionResource.from_function(
            reader,
            uri=index.uri,
            name=f"{index.workspace.key}-index",
            title=f"{index.workspace.display_name} 문서 목록",
            description=f"{index.workspace.path}",
            mime_type="application/json",
        )

    def _resolve(self, path: str | Path) -> Path:
        candidate = Path(path).expanduser()
        try:
            return candidate.resolve(strict=False)
        except OSError:
            return candidate

    def _assert_within_root(self, candidate: Path) -> None:
        for root in self._roots:
            try:
                candidate.relative_to(root.path)
                return
            except ValueError:
                continue
        raise InvalidDocumentSourceError(
            "허용된 워크스페이스 밖 경로입니다. configure 명령으로 경로를 추가해 주세요."
        )


class WorkspaceResourceManager:
    """워크스페이스 문서를 FastMCP 리소스로 노출한다."""

    def __init__(self, base_manager, workspace: WorkspaceService, logger: Logger | None = None) -> None:
        self._base = base_manager
        self._workspace = workspace
        self._logger = logger or getLogger("hwpx_mcp.workspace")
        self._document_resources: dict[str, Resource] = {}
        self._index_resources: dict[str, Resource] = {}

    @property
    def warn_on_duplicate_resources(self) -> bool:  # pragma: no cover - FastMCP 호환용
        return getattr(self._base, "warn_on_duplicate_resources", True)

    # ------------------------------------------------------------------
    # FastMCP ResourceManager 호환 API
    # ------------------------------------------------------------------
    def add_resource(self, resource: Resource) -> Resource:
        return self._base.add_resource(resource)

    def add_template(self, *args, **kwargs):  # pragma: no cover - 기존 동작 위임
        return self._base.add_template(*args, **kwargs)

    async def get_resource(self, uri, context=None):
        try:
            return await self._base.get_resource(uri, context=context)
        except Exception:
            uri_str = str(uri)
            self._refresh()
            if uri_str in self._document_resources:
                return self._document_resources[uri_str]
            if uri_str in self._index_resources:
                return self._index_resources[uri_str]
            raise

    def list_resources(self) -> list[Resource]:
        resources = list(self._base.list_resources())
        self._refresh()
        resources.extend(self._document_resources.values())
        resources.extend(self._index_resources.values())
        return resources

    def list_templates(self):  # pragma: no cover - 기존 동작 위임
        return self._base.list_templates()

    # ------------------------------------------------------------------

    def _refresh(self) -> None:
        snapshot = self._workspace.snapshot()
        self._document_resources = {
            doc.uri: self._workspace.create_document_resource(doc) for doc in snapshot.documents
        }
        self._index_resources = {
            index.uri: self._workspace.create_index_resource(index) for index in snapshot.indexes
        }


def make_backup(original: Path, destination_dir: Path | None = None) -> Path:
    """원본 파일의 백업을 생성한다."""

    dest_dir = destination_dir or original.parent
    timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    backup_name = f"{original.name}.{timestamp}.bak"
    backup_path = dest_dir / backup_name
    dest_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(original, backup_path)
    return backup_path


__all__ = [
    "WorkspaceDocument",
    "WorkspaceIndex",
    "WorkspaceResourceManager",
    "WorkspaceRoot",
    "WorkspaceService",
    "WorkspaceSnapshot",
    "make_backup",
]
