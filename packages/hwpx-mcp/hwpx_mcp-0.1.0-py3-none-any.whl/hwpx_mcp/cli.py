"""hwpx-mcp 패키지의 CLI 엔트리포인트."""

from __future__ import annotations

import os
import sys
import textwrap
from pathlib import Path
from typing import List, Optional

import anyio
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .server import create_server
from .user_config import (
    UserConfig,
    compute_standard_paths,
    load_user_config,
    save_user_config,
)
from .workspace import WorkspaceService

app = typer.Typer(help="HWPX MCP 서버를 제어하는 CLI")
configure_app = typer.Typer(help="클라이언트 설정 가이드", invoke_without_command=True)
app.add_typer(configure_app, name="configure")

console = Console()


def _resolve_config_path(ctx: typer.Context) -> Optional[Path]:
    data = getattr(ctx, "obj", None) or {}
    return data.get("config_path")


def _store_config_path(ctx: typer.Context, path: Optional[Path]) -> None:
    ctx.obj = {"config_path": path}


@app.callback()
def main(
    ctx: typer.Context,
    config: Optional[Path] = typer.Option(
        None,
        "--config",
        help="사용자 설정 파일 경로(기본: ~/.config/hwpx-mcp/config.toml)",
        envvar="HWPX_MCP_CONFIG_PATH",
    ),
) -> None:
    """전역 옵션을 처리한다."""

    resolved: Optional[Path] = None
    if config is not None:
        resolved = config.expanduser()
        os.environ["HWPX_MCP_CONFIG_PATH"] = str(resolved)
    else:
        env_value = os.getenv("HWPX_MCP_CONFIG_PATH")
        if env_value:
            resolved = Path(env_value).expanduser()
    _store_config_path(ctx, resolved)


def _prompt_for_workspaces() -> list[Path]:
    console.print("[bold]허용할 워크스페이스 디렉터리를 입력하세요.[/bold]")
    console.print("빈 입력을 주면 마법사가 종료됩니다. 여러 경로를 입력하려면 계속 진행하세요.")

    selections: list[Path] = []
    while True:
        value = typer.prompt("허용할 경로", default="")
        if not value:
            break
        candidate = Path(value).expanduser()
        if not candidate.exists():
            create_dir = typer.confirm(f"경로 {candidate} 가 존재하지 않습니다. 생성할까요?", default=True)
            if create_dir:
                candidate.mkdir(parents=True, exist_ok=True)
            else:
                console.print(f"[yellow]{candidate} 경로를 건너뜁니다.[/yellow]")
                continue
        selections.append(candidate.resolve())
        if not typer.confirm("추가 경로를 입력하시겠습니까?", default=False):
            break
    return selections


def _ensure_workspaces(
    workspace_paths: List[Path] | None,
    *,
    config_path: Optional[Path],
    interactive: bool,
) -> UserConfig:
    config = load_user_config(config_path)

    if workspace_paths:
        resolved = [path.expanduser().resolve() for path in workspace_paths]
        config.update_workspaces(resolved)
        save_user_config(config, config_path)
        return config

    if config.allowed_workspaces:
        # 설정 파일에 저장된 경로들을 재정규화한다.
        config.update_workspaces(config.normalized_workspaces())
        save_user_config(config, config_path)
        return config

    if not interactive:
        console.print(
            "[red]허용된 워크스페이스가 없습니다. --workspace 옵션 또는 hwpx-mcp configure 명령을 사용하세요.[/red]"
        )
        raise typer.Exit(code=1)

    selections = _prompt_for_workspaces()
    if not selections:
        console.print("[red]최소 한 개 이상의 워크스페이스가 필요합니다.[/red]")
        raise typer.Exit(code=1)

    config.update_workspaces(selections)
    save_user_config(config, config_path)
    return config


@app.command()
def serve(
    ctx: typer.Context,
    workspace: Optional[List[Path]] = typer.Option(
        None,
        "-w",
        "--workspace",
        help="허용할 워크스페이스 경로(지정 시 설정 파일을 갱신합니다)",
    ),
    transport: str = typer.Option(
        "stdio",
        "-t",
        "--transport",
        help="서버 트랜스포트 (stdio, sse, streamable-http)",
        show_default=True,
    ),
    host: str = typer.Option("127.0.0.1", help="SSE/HTTP 모드에서 사용할 호스트"),
    port: int = typer.Option(8081, help="SSE/HTTP 모드에서 사용할 포트"),
) -> None:
    """MCP 서버를 실행한다."""

    config_path = _resolve_config_path(ctx)
    config = _ensure_workspaces(workspace, config_path=config_path, interactive=sys.stdin.isatty())

    console.print(
        Panel.fit(
            "\n".join(f"• {path}" for path in config.allowed_workspaces) or "(미설정)",
            title="허용된 워크스페이스",
            border_style="cyan",
        )
    )

    server = create_server()
    server.settings.host = host
    server.settings.port = port

    transport_key = transport.lower()
    try:
        if transport_key == "stdio":
            anyio.run(server.run_stdio_async)
        elif transport_key == "sse":
            server.run("sse")
        elif transport_key in {"streamable-http", "http"}:
            server.run("streamable-http")
        else:
            console.print(f"[red]알 수 없는 트랜스포트: {transport}[/red]")
            raise typer.Exit(code=1)
    except KeyboardInterrupt:  # pragma: no cover - 사용자 중단 처리
        console.print("[yellow]서버를 종료합니다.[/yellow]")


def _interactive_config(config_path: Optional[Path]) -> None:
    console.print(Panel.fit("HWPX MCP 초기 설정", title="Configure", border_style="green"))
    config = load_user_config(config_path)

    selections = _prompt_for_workspaces()
    if not selections:
        console.print("[red]최소 한 개 이상의 워크스페이스가 필요합니다.[/red]")
        raise typer.Exit(code=1)

    config.update_workspaces(selections)
    config.auto_backup = typer.confirm("저장 시 백업 파일을 생성할까요?", default=config.auto_backup)
    language = typer.prompt("기본 언어 코드", default=config.language)
    config.language = language.strip() or config.language
    backup_dir = typer.prompt(
        "백업 파일 저장 디렉터리 (엔터 시 워크스페이스 경로 사용)",
        default=config.backup_dir or "",
    )
    config.backup_dir = (
        str(Path(backup_dir).expanduser().resolve()) if backup_dir.strip() else None
    )
    save_user_config(config, config_path)
    console.print(Panel.fit("설정이 저장되었습니다.", border_style="green"))


@configure_app.callback()
def configure_callback(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is not None:
        return
    parent = ctx.parent or ctx
    config_path = _resolve_config_path(parent)
    _interactive_config(config_path)
    raise typer.Exit()


def _workspace_placeholder(config_path: Optional[Path]) -> str:
    config = load_user_config(config_path)
    if config.allowed_workspaces:
        return config.allowed_workspaces[0]
    return "<워크스페이스 경로>"


@configure_app.command("claude")
def configure_claude(ctx: typer.Context) -> None:
    """Claude Desktop 설정 스니펫을 출력한다."""

    config_path = _resolve_config_path(ctx.parent or ctx)
    workspace_hint = _workspace_placeholder(config_path)
    if "<" in workspace_hint:
        windows_path = "C\\\\경로\\\\hwpx"
    else:
        replaced = workspace_hint.replace("/", "\\")
        windows_path = replaced.replace("\\", "\\\\")

    mac_snippet = textwrap.dedent(
        f"""
        {{
          "mcpServers": {{
            "hwpx-local": {{
              "command": "hwpx-mcp",
              "args": ["serve", "--workspace", "{workspace_hint}"]
            }}
          }}
        }}
        """
    ).strip()
    windows_snippet = textwrap.dedent(
        f"""
        {{
          "mcpServers": {{
            "hwpx-local": {{
              "command": "hwpx-mcp",
              "args": ["serve", "--workspace", "{windows_path}"]
            }}
          }}
        }}
        """
    ).strip()

    console.print("[bold]Claude Desktop 설정 파일 (claude_desktop_config.json) 예시[/bold]")
    console.print("[green]macOS/Linux[/green]")
    console.print(mac_snippet)
    console.print("\n[green]Windows[/green]")
    console.print(windows_snippet)


@configure_app.command("gemini")
def configure_gemini(ctx: typer.Context) -> None:
    """Gemini CLI 설정 예시를 출력한다."""

    config_path = _resolve_config_path(ctx.parent or ctx)
    workspace_hint = _workspace_placeholder(config_path)
    snippet = textwrap.dedent(
        f"""
        [[mcp_servers]]
        name = "hwpx-mcp"
        command = "hwpx-mcp"
        args = ["serve", "--workspace", "{workspace_hint}"]
        """
    ).strip()

    console.print("[bold].gemini-cli/config.toml 설정 예시[/bold]")
    console.print(snippet)


@app.command()
def doctor(ctx: typer.Context) -> None:
    """환경 점검 리포트를 출력한다."""

    config_path = _resolve_config_path(ctx)
    paths = compute_standard_paths(config_path)
    config = load_user_config(config_path)

    table = Table(title="환경 점검", show_lines=True)
    table.add_column("항목", style="cyan", no_wrap=True)
    table.add_column("상태", style="magenta")
    table.add_column("설명", style="white")

    results: list[bool] = []

    def add_row(label: str, ok: bool, detail: str) -> None:
        results.append(ok)
        status = "[green]OK[/green]" if ok else "[red]ERROR[/red]"
        table.add_row(label, status, detail)

    add_row("Python", sys.version_info >= (3, 10), sys.version.split()[0])
    add_row("설정 파일", paths.config_file.exists(), str(paths.config_file))
    workspace_list = ", ".join(config.allowed_workspaces) or "(없음)"
    add_row("워크스페이스 등록", bool(config.allowed_workspaces), workspace_list)

    try:
        import hwpx  # type: ignore

        add_row("python-hwpx", True, getattr(hwpx, "__version__", "installed"))
    except Exception as exc:  # pragma: no cover - 환경별 예외 처리
        add_row("python-hwpx", False, str(exc))

    service = WorkspaceService(config.normalized_workspaces())
    if not service.has_roots:
        add_row("워크스페이스 검사", False, "허용된 경로가 없습니다")
    else:
        for path in service.allowed_paths():
            add_row(f"워크스페이스: {path.name}", path.exists(), str(path))

    console.print(table)
    if not all(results):
        raise typer.Exit(code=1)


__all__ = ["app"]
