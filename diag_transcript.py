# diag_transcript.py
import json
import re
from typing import Tuple, List

import requests
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
)

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

PREFERRED_LANGS = ["en", "en-US", "en-GB", "hi"]


def _join_segments(segments: List[dict]) -> str:
    parts = []
    for seg in segments:
        t = seg.get("text") or seg.get("utf8") or ""
        t = t.replace("\n", " ").strip()
        if t:
            parts.append(t)
    return " ".join(parts)


def _try_yta_list_api(video_id: str, notes: List[str]) -> str:
    """
    Try the official youtube_transcript_api list_transcripts() path:
    1) Prefer manually created transcripts (preferred languages)
    2) Fall back to auto-generated transcripts (preferred languages)
    Returns transcript text or "".
    """
    try:
        listing = YouTubeTranscriptApi.list_transcripts(video_id)

        # 1) Manual first
        for langs in [PREFERRED_LANGS, ["en"], ["hi"]]:
            try:
                tr = listing.find_manually_created_transcript(langs)
                return _join_segments(tr.fetch())
            except Exception as e:
                notes.append(f"manual {langs}: {e}")

        # 2) Auto-generated next
        for langs in [PREFERRED_LANGS, ["en"], ["hi"]]:
            try:
                tr = listing.find_generated_transcript(langs)
                return _join_segments(tr.fetch())
            except Exception as e:
                notes.append(f"auto {langs}: {e}")

    except TranscriptsDisabled:
        notes.append("TranscriptsDisabled")
    except NoTranscriptFound:
        notes.append("NoTranscriptFound")
    except Exception as e:
        notes.append(f"yta list_transcripts error: {e}")

    return ""


def _try_scrape_caption_tracks(video_id: str, notes: List[str]) -> str:
    """
    Fallback: scrape the watch page -> find captionTracks -> fetch JSON3 captions.
    Works for many videos even when other methods are flaky.
    """
    try:
        html = requests.get(
            f"https://www.youtube.com/watch?v={video_id}", headers=UA, timeout=15
        ).text
    except Exception as e:
        notes.append(f"GET watch page failed: {e}")
        return ""

    m = re.search(r'"captionTracks":(\[.*?\])', html)
    if not m:
        notes.append("No captionTracks found in HTML")
        return ""

    try:
        tracks = json.loads(m.group(1))
    except Exception as e:
        notes.append(f"captionTracks JSON parse failed: {e}")
        return ""

    # Pick preferred language, else first available
    track = None
    for t in tracks:
        lang = (t.get("languageCode") or "").lower()
        if lang in [x.lower() for x in PREFERRED_LANGS]:
            track = t
            break
    if track is None and tracks:
        track = tracks[0]
        notes.append("Preferred language not found; using first available track")
    if track is None:
        notes.append("No caption track objects present")
        return ""

    base_url = track.get("baseUrl")
    if not base_url:
        notes.append("Caption track missing baseUrl")
        return ""

    # Ensure JSON3 (richer format)
    if "fmt=" not in base_url:
        sep = "&" if "?" in base_url else "?"
        base_url = base_url + sep + "fmt=json3"

    try:
        j = requests.get(base_url, headers=UA, timeout=15).json()
    except Exception as e:
        notes.append(f"GET caption JSON failed: {e}")
        return ""

    texts = []
    for ev in j.get("events", []):
        if "segs" in ev:
            for s in ev["segs"]:
                t = (s.get("utf8") or "").replace("\n", " ").strip()
                if t:
                    texts.append(t)

    if not texts:
        notes.append("Caption JSON had no text in events/segs")
        return ""
    return " ".join(texts)


def fetch_transcript_from_youtube(video_id: str, return_notes: bool = False) -> Tuple[str, List[str]] | str:
    """
    Try multiple strategies to get a transcript.
    - If return_notes=True, returns (transcript, debug_notes)
    - Else returns transcript string only.
    """
    notes: List[str] = []

    # Strategy A: official API (manual/auto, multiple langs)
    text = _try_yta_list_api(video_id, notes)
    if text:
        return (text, notes) if return_notes else text

    # Strategy B: scrape fallback
    text = _try_scrape_caption_tracks(video_id, notes)
    if text:
        return (text, notes) if return_notes else text

    # Nothing worked
    if return_notes:
        return "", notes
    return ""
