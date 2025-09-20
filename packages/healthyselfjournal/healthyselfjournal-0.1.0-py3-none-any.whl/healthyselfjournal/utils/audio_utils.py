from __future__ import annotations

"""Audio-related utilities shared across modules."""

from pathlib import Path
from typing import Optional

from ..events import log_event


def maybe_delete_wav_when_safe(wav_path: Path) -> Optional[bool]:
    """Delete WAV if sibling MP3 and STT JSON exist and file still present.

    Returns True if deleted, False if not deleted, or None if an error occurred.
    Emits the existing "audio.wav.deleted" event on success.
    """
    try:
        mp3_path = wav_path.with_suffix(".mp3")
        stt_json = wav_path.with_suffix(".stt.json")
        if mp3_path.exists() and stt_json.exists() and wav_path.exists():
            wav_path.unlink(missing_ok=True)
            try:
                log_event(
                    "audio.wav.deleted",
                    {
                        "wav": wav_path.name,
                        "reason": "safe_delete_after_mp3_and_stt",
                    },
                )
            except Exception:
                pass
            return True
        return False
    except Exception:
        # Defensive: never raise from cleanup path
        return None
