from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

pytest.importorskip("starlette")

from starlette.testclient import TestClient

from healthyselfjournal.llm import QuestionResponse
from healthyselfjournal.session import SessionManager
from healthyselfjournal.transcription import BackendSelection, TranscriptionResult
from healthyselfjournal.web.app import WebAppConfig, build_app


class StubBackend:
    backend_id = "stub"

    def __init__(self, *_, **__):
        pass

    def transcribe(self, wav_path: Path, *, language: str | None = None) -> TranscriptionResult:
        return TranscriptionResult(
            text="stub transcript",
            raw_response={"text": "stub transcript"},
            model="stub-model",
            backend="stub-backend",
        )


@pytest.fixture()
def web_app(monkeypatch, tmp_path: Path):
    # Force deterministic backend selection without touching real services
    monkeypatch.setattr(
        "healthyselfjournal.web.app.resolve_backend_selection",
        lambda *_, **__: BackendSelection(
            backend_id="stub",
            model="stub-model",
            compute=None,
        ),
    )

    # Avoid spinning background threads in tests
    monkeypatch.setattr(SessionManager, "schedule_summary_regeneration", lambda self: None)

    monkeypatch.setattr(
        "healthyselfjournal.session.create_transcription_backend",
        lambda *args, **kwargs: StubBackend(),
    )

    monkeypatch.setattr(
        "healthyselfjournal.session.generate_followup_question",
        lambda request: QuestionResponse(question="Stub follow-up?", model="stub-llm"),
    )

    config = WebAppConfig(
        sessions_dir=tmp_path,
        static_dir=tmp_path / "static",
    )
    app = build_app(config)
    return app


def test_upload_creates_session_artifacts(tmp_path: Path, web_app):
    client = TestClient(web_app)

    # Landing page should create a new session and expose metadata
    response = client.get("/")
    assert response.status_code == 200
    match = re.search(r"data-session-id=\"([^\"]+)\"", response.text)
    assert match, "session id not found in HTML"
    session_id = match.group(1)

    upload_path = f"/session/{session_id}/upload"
    payload = {
        "duration_ms": "1500",
        "voiced_ms": "900",
        "question": "Opening question?",
    }
    files = {
        "audio": ("clip.webm", b"faux-data", "audio/webm"),
    }

    result = client.post(upload_path, data=payload, files=files)
    assert result.status_code == 201
    data = result.json()
    assert data["status"] == "ok"
    assert data["session_id"] == session_id
    assert data["next_question"] == "Stub follow-up?"
    assert data["segment_label"].startswith("browser-")

    session_dir = tmp_path / session_id
    markdown_path = tmp_path / f"{session_id}.md"
    audio_path = session_dir / "browser-001.webm"
    stt_json = audio_path.with_suffix(".stt.json")

    assert markdown_path.exists()
    assert audio_path.exists()
    assert stt_json.exists()

    body = markdown_path.read_text(encoding="utf-8")
    assert "stub transcript" in body

    stt_payload = json.loads(stt_json.read_text(encoding="utf-8"))
    assert stt_payload["text"] == "stub transcript"
