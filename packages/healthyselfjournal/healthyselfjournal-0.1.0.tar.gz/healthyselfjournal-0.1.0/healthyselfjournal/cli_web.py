from __future__ import annotations

"""Typer command that launches the FastHTML web server."""

from pathlib import Path

import typer
from rich.console import Console

from .config import CONFIG
from .web.app import WebAppConfig, run_app


console = Console()


def web(
    sessions_dir: Path = typer.Option(
        CONFIG.recordings_dir,
        "--sessions-dir",
        help="Directory where session markdown and audio artifacts are stored.",
    ),
    host: str = typer.Option(
        "127.0.0.1",
        "--host",
        help="Interface to bind the development server to.",
    ),
    port: int = typer.Option(
        8765,
        "--port",
        help="Port to serve the web interface on.",
    ),
    reload: bool = typer.Option(
        False,
        "--reload/--no-reload",
        help="Enable FastHTML/uvicorn autoreload (development only).",
    ),
) -> None:
    """Launch the FastHTML-powered web interface."""

    config = WebAppConfig(
        sessions_dir=sessions_dir,
        host=host,
        port=port,
        reload=reload,
    )
    console.print(
        f"[green]Starting Healthy Self Journal web server on {host}:{port}[/]"
    )
    console.print(
        f"Sessions directory: [cyan]{config.sessions_dir.expanduser()}[/]"
    )

    try:
        run_app(config)
    except KeyboardInterrupt:  # pragma: no cover - direct CLI interrupt
        console.print("\n[cyan]Server stopped.[/]")

