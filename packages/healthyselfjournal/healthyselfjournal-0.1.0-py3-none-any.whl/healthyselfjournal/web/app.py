from __future__ import annotations

"""FastHTML application setup for the web journaling interface."""

from dataclasses import dataclass, field
import logging
from pathlib import Path

from fasthtml import FastHTML
from starlette.datastructures import UploadFile
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse
from starlette.staticfiles import StaticFiles

from ..audio import AudioCaptureResult
from ..config import CONFIG
from ..events import log_event
from ..session import SessionConfig, SessionManager
from ..transcription import BackendNotAvailableError, resolve_backend_selection


_LOGGER = logging.getLogger(__name__)

_PACKAGE_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_STATIC_DIR = _PACKAGE_ROOT / "static"


@dataclass(slots=True)
class WebAppConfig:
    """Runtime configuration for the FastHTML web server."""

    sessions_dir: Path
    static_dir: Path = field(default=DEFAULT_STATIC_DIR)
    host: str = "127.0.0.1"
    port: int = 8765
    reload: bool = False

    def resolved(self) -> "WebAppConfig":
        """Return a copy with absolute paths for filesystem access."""

        return WebAppConfig(
            sessions_dir=self.sessions_dir.expanduser().resolve(),
            static_dir=self.static_dir.expanduser().resolve(),
            host=self.host,
            port=self.port,
            reload=self.reload,
        )


@dataclass(slots=True)
class WebSessionState:
    """Book-keeping for an active web session."""

    manager: SessionManager
    current_question: str

    @property
    def session_id(self) -> str:
        state = self.manager.state
        if state is None:  # pragma: no cover - defensive guard
            raise RuntimeError("Session state not initialised")
        return state.session_id


def build_app(config: WebAppConfig) -> FastHTML:
    """Construct and configure a FastHTML app instance."""

    resolved = config.resolved()
    resolved.sessions_dir.mkdir(parents=True, exist_ok=True)
    resolved.static_dir.mkdir(parents=True, exist_ok=True)

    app = FastHTML()
    app.state.config = resolved
    app.state.sessions: dict[str, WebSessionState] = {}

    # Serve static files (JS, CSS, media) under /static/
    app.mount(
        "/static",
        StaticFiles(directory=str(resolved.static_dir), check_dir=False),
        name="static",
    )

    @app.route("/")
    def index() -> HTMLResponse:
        """Landing page that boots a brand-new session."""

        try:
            state = _start_session(app)
        except Exception as exc:  # pragma: no cover - surface to browser
            _LOGGER.exception("Failed to start web session")
            return HTMLResponse(
                """
                <!doctype html>
                <html lang=\"en\">
                  <head>
                    <meta charset=\"utf-8\" />
                    <title>Healthy Self Journal (Web)</title>
                  </head>
                  <body>
                    <main style=\"max-width:600px;margin:3rem auto;font-family:system-ui\">
                      <h1>Healthy Self Journal</h1>
                      <p>Sorry, the web interface could not start: check your STT/LLM configuration.</p>
                    </main>
                  </body>
                </html>
                """,
                status_code=500,
            )

        body = _render_session_shell(state)
        return HTMLResponse(body)

    @app.post("/session/{session_id}/upload")
    async def upload(session_id: str, request: Request) -> JSONResponse:
        state = app.state.sessions.get(session_id)
        if state is None:
            return JSONResponse(
                {"status": "error", "error": "unknown_session"}, status_code=404
            )

        form = await request.form()
        upload = form.get("audio")
        if upload is None:
            return JSONResponse(
                {"status": "error", "error": "missing_audio"}, status_code=400
            )
        if not isinstance(upload, UploadFile):
            return JSONResponse(
                {"status": "error", "error": "invalid_payload"}, status_code=400
            )

        # Metadata provided by the browser recorder
        mime = (form.get("mime") or upload.content_type or "audio/webm").lower()
        try:
            duration_ms = float(form.get("duration_ms", "0") or 0.0)
        except (TypeError, ValueError):
            duration_ms = 0.0
        try:
            voiced_ms = float(form.get("voiced_ms", duration_ms) or duration_ms)
        except (TypeError, ValueError):
            voiced_ms = duration_ms

        # Persist uploaded audio to the active session directory
        session_state = state.manager.state
        if session_state is None:
            return JSONResponse(
                {"status": "error", "error": "inactive_session"}, status_code=409
            )

        target_dir = session_state.audio_dir
        target_dir.mkdir(parents=True, exist_ok=True)

        next_index = session_state.response_index + 1
        extension = _extension_for_mime(mime, upload.filename)
        segment_basename = _build_segment_basename(next_index)
        target_path = target_dir / f"{segment_basename}{extension}"
        while target_path.exists():  # Defensive: avoid accidental overwrite
            next_index += 1
            segment_basename = _build_segment_basename(next_index)
            target_path = target_dir / f"{segment_basename}{extension}"

        blob = await upload.read()
        if not blob:
            return JSONResponse(
                {"status": "error", "error": "empty_audio"}, status_code=400
            )

        target_path.write_bytes(blob)
        duration_seconds = max(duration_ms, 0.0) / 1000.0
        voiced_seconds = max(voiced_ms, 0.0) / 1000.0

        capture = AudioCaptureResult(
            wav_path=target_path,
            mp3_path=None,
            duration_seconds=duration_seconds,
            voiced_seconds=voiced_seconds,
            cancelled=False,
            quit_after=False,
            discarded_short_answer=False,
        )

        log_event(
            "web.upload.received",
            {
                "session_id": session_id,
                "filename": target_path.name,
                "content_type": mime,
                "bytes": len(blob),
                "duration_seconds": round(duration_seconds, 2),
            },
        )

        try:
            exchange = state.manager.process_uploaded_exchange(
                state.current_question,
                capture,
                segment_label=target_path.name,
            )
        except Exception as exc:  # pragma: no cover - runtime path
            _LOGGER.exception("Failed to process uploaded exchange")
            return JSONResponse(
                {
                    "status": "error",
                    "error": "processing_failed",
                    "detail": str(exc),
                },
                status_code=500,
            )

        summary_scheduled = True
        try:
            state.manager.schedule_summary_regeneration()
        except Exception as exc:  # pragma: no cover - best-effort logging
            summary_scheduled = False
            _LOGGER.exception("Summary scheduling failed: %s", exc)

        try:
            next_question = state.manager.generate_next_question(exchange.transcript)
            state.current_question = next_question.question
        except Exception as exc:  # pragma: no cover - runtime path
            _LOGGER.exception("Next question generation failed")
            return JSONResponse(
                {
                    "status": "error",
                    "error": "question_failed",
                    "detail": str(exc),
                },
                status_code=502,
            )

        log_event(
            "web.upload.processed",
            {
                "session_id": session_id,
                "segment_label": target_path.name,
                "transcript_chars": len(exchange.transcript),
                "next_question_chars": len(state.current_question or ""),
            },
        )

        response_payload = {
            "status": "ok",
            "session_id": session_id,
            "segment_label": target_path.name,
            "duration_seconds": round(exchange.audio.duration_seconds, 2),
            "transcript": exchange.transcript,
            "next_question": state.current_question,
            "llm_model": getattr(next_question, "model", None),
            "summary_scheduled": summary_scheduled,
        }
        return JSONResponse(response_payload, status_code=201)

    return app


def run_app(config: WebAppConfig) -> None:
    """Run the FastHTML development server."""

    app = build_app(config)
    # FastHTML exposes a convenience runner that wraps uvicorn.
    app.run(host=config.host, port=config.port, reload=config.reload)


def _start_session(app: FastHTML) -> WebSessionState:
    """Initialise a new journaling session for the web client."""

    resolved: WebAppConfig = app.state.config

    try:
        selection = resolve_backend_selection(
            CONFIG.stt_backend,
            CONFIG.model_stt,
            CONFIG.stt_compute,
        )
    except (ValueError, BackendNotAvailableError) as exc:
        raise RuntimeError(f"Unable to configure STT backend: {exc}") from exc

    CONFIG.model_stt = selection.model
    CONFIG.stt_backend = selection.backend_id
    CONFIG.stt_compute = selection.compute

    session_cfg = SessionConfig(
        base_dir=resolved.sessions_dir,
        llm_model=CONFIG.model_llm,
        stt_model=selection.model,
        stt_backend=selection.backend_id,
        stt_compute=selection.compute,
        opening_question=CONFIG.opening_question,
        language="en",
        stt_formatting=CONFIG.stt_formatting,
        stt_backend_requested=CONFIG.stt_backend,
        stt_model_requested=CONFIG.model_stt,
        stt_compute_requested=CONFIG.stt_compute,
        stt_auto_private_reason=selection.reason,
        stt_backend_selection=selection,
        stt_warnings=selection.warnings,
    )

    manager = SessionManager(session_cfg)
    state = manager.start()
    current_question = session_cfg.opening_question

    web_state = WebSessionState(manager=manager, current_question=current_question)
    app.state.sessions[state.session_id] = web_state

    log_event(
        "web.session.started",
        {
            "session_id": state.session_id,
            "markdown_path": state.markdown_path.name,
            "audio_dir": str(state.audio_dir),
        },
    )
    return web_state


def _build_segment_basename(index: int) -> str:
    return f"browser-{index:03d}"


def _extension_for_mime(mime: str, filename: str | None) -> str:
    """Infer a file extension from the supplied MIME type/filename."""

    if mime.startswith("audio/webm"):
        return ".webm"
    if mime in {"audio/ogg", "application/ogg"}:
        return ".ogg"
    if mime in {"audio/mpeg", "audio/mp3"}:
        return ".mp3"
    if mime == "audio/wav" or mime == "audio/x-wav":
        return ".wav"
    if filename and "." in filename:
        return "." + filename.rsplit(".", 1)[-1]
    return ".bin"


def _render_session_shell(state: WebSessionState) -> str:
    """Return the base HTML shell; dynamic behaviour handled client-side."""

    session_id = state.session_id
    question = state.current_question
    short_duration = CONFIG.short_answer_duration_seconds
    short_voiced = CONFIG.short_answer_voiced_seconds
    return f"""
    <!doctype html>
    <html lang=\"en\">
      <head>
        <meta charset=\"utf-8\" />
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
        <title>Healthy Self Journal (Web)</title>
        <link rel=\"stylesheet\" href=\"/static/css/app.css\" />
      </head>
      <body data-session-id=\"{session_id}\"
            data-upload-url=\"/session/{session_id}/upload\"
            data-short-duration=\"{short_duration}\"
            data-short-voiced=\"{short_voiced}\">\n
        <main class=\"hsj-container\">
          <header class=\"hsj-header\">
            <h1>Healthy Self Journal</h1>
            <p class=\"hsj-session-id\">Session {session_id}</p>
          </header>

          <section class=\"hsj-question\">
            <h2>Current prompt</h2>
            <p id=\"current-question\">{question}</p>
          </section>

          <section class=\"hsj-controls\">
            <button id=\"record-button\" data-state=\"idle\">Start recording</button>
            <div id=\"level-meter\" aria-hidden=\"true\">
              <div class=\"bar\"></div>
            </div>
            <p id=\"status-text\">Click start to begin recording.</p>
          </section>

          <section class=\"hsj-history\">
            <h2>Session history</h2>
            <div id=\"history-list\"></div>
          </section>
        </main>

        <script type=\"module\" src=\"/static/js/app.js\"></script>
      </body>
    </html>
    """
