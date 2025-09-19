"""사용자 수준 구성 파일을 관리한다."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from pydantic import BaseModel, Field, ValidationError

try:  # Python 3.11+
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 호환
    import tomli as tomllib  # type: ignore[no-redef]

import tomli_w


_CONFIG_ENV_VAR = "HWPX_MCP_CONFIG_PATH"
_DEFAULT_CONFIG_FILENAME = "config.toml"
_CONFIG_DIR_NAME = "hwpx-mcp"


class UserConfig(BaseModel):
    """사용자별 지속 설정."""

    allowed_workspaces: list[str] = Field(default_factory=list, description="허용된 워크스페이스 경로 목록")
    default_workspace: str | None = Field(default=None, description="기본 워크스페이스 경로")
    language: str = Field(default="ko", description="기본 UI 언어 코드")
    auto_backup: bool = Field(default=True, description="저장 시 백업 파일을 생성할지 여부")
    backup_dir: str | None = Field(default=None, description="백업 파일 저장 디렉터리")
    log_dir: str | None = Field(default=None, description="로그 파일 저장 디렉터리")

    model_config = dict(extra="ignore")

    def normalized_workspaces(self) -> list[Path]:
        """허용 워크스페이스를 정규화된 절대 경로로 반환."""

        return _normalize_paths(self.allowed_workspaces)

    def update_workspaces(self, paths: Sequence[Path]) -> None:
        """워크스페이스 목록을 새 경로들로 교체한다."""

        unique: list[str] = []
        seen: set[str] = set()
        for path in paths:
            value = str(path)
            if value not in seen:
                seen.add(value)
                unique.append(value)
        self.allowed_workspaces = unique
        if unique:
            self.default_workspace = unique[0]


@dataclass(frozen=True, slots=True)
class ConfigPaths:
    """설정/캐시/로그 경로 묶음."""

    config_file: Path
    config_dir: Path
    cache_dir: Path
    log_dir: Path


def resolve_config_path() -> Path:
    """환경 변수 또는 기본 경로에서 설정 파일 위치를 결정한다."""

    env_value = os.getenv(_CONFIG_ENV_VAR)
    if env_value:
        candidate = Path(env_value).expanduser()
        if candidate.is_dir():
            return candidate / _DEFAULT_CONFIG_FILENAME
        return candidate

    base = Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / _CONFIG_DIR_NAME / _DEFAULT_CONFIG_FILENAME


def compute_standard_paths(config_path: Path | None = None) -> ConfigPaths:
    """설정 파일 위치를 기준으로 파생 경로를 반환."""

    cfg_path = config_path or resolve_config_path()
    cfg_dir = cfg_path.parent
    cache_root = Path(os.getenv("XDG_CACHE_HOME", Path.home() / ".cache")) / _CONFIG_DIR_NAME
    log_root = Path(os.getenv("XDG_DATA_HOME", Path.home() / ".local/share")) / _CONFIG_DIR_NAME / "logs"
    return ConfigPaths(config_file=cfg_path, config_dir=cfg_dir, cache_dir=cache_root, log_dir=log_root)


def load_user_config(config_path: Path | None = None) -> UserConfig:
    """설정 파일을 읽어 UserConfig 인스턴스로 반환."""

    cfg_path = config_path or resolve_config_path()
    if not cfg_path.exists():
        return UserConfig()

    try:
        with cfg_path.open("rb") as fp:
            data = tomllib.load(fp)
    except (OSError, tomllib.TOMLDecodeError) as exc:  # type: ignore[attr-defined]
        raise RuntimeError(f"설정 파일을 읽을 수 없습니다: {cfg_path} ({exc})") from exc

    try:
        return UserConfig.model_validate(data)
    except ValidationError as exc:  # pragma: no cover - 방어 로직
        raise RuntimeError(f"설정 파일 형식이 잘못되었습니다: {cfg_path}\n{exc}") from exc


def save_user_config(config: UserConfig, config_path: Path | None = None) -> Path:
    """UserConfig 내용을 TOML 파일로 저장한다."""

    cfg_paths = compute_standard_paths(config_path)
    cfg_paths.config_dir.mkdir(parents=True, exist_ok=True)

    payload = config.model_dump(mode="json", exclude_none=True)
    with cfg_paths.config_file.open("wb") as fp:
        fp.write(tomli_w.dumps(payload).encode("utf-8"))

    return cfg_paths.config_file


def _normalize_paths(paths: Iterable[str]) -> list[Path]:
    normalized: list[Path] = []
    seen: set[str] = set()
    for raw in paths:
        path = Path(raw).expanduser()
        try:
            resolved = path.resolve(strict=False)
        except OSError:
            resolved = path
        key = str(resolved)
        if key not in seen:
            seen.add(key)
            normalized.append(resolved)
    return normalized


__all__ = [
    "UserConfig",
    "ConfigPaths",
    "compute_standard_paths",
    "load_user_config",
    "resolve_config_path",
    "save_user_config",
]
