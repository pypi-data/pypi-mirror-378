"""로깅 초기화 도우미."""

from __future__ import annotations

import logging
from logging import Logger


def _resolve_level(level: str) -> int:
    candidate = logging.getLevelName(level.upper())
    if isinstance(candidate, int):
        return candidate
    return logging.INFO


def configure_logging(level: str) -> Logger:
    """루트 로거를 초기화하고 패키지 전용 로거를 반환한다."""

    logging.basicConfig(
        level=_resolve_level(level),
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )
    return logging.getLogger("hwpx_mcp")
