# diag_transcript.py
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from pytube import YouTube

def fetch_transcript_from_youtube(video_id: str):
    """
    Try to fetch transcript for a given YouTube video ID.
    Falls back gracefully if transcript is disabled or not available.
    """
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["en"])
        return " ".join([t["text"] for t in transcript])
    except (TranscriptsDisabled, NoTranscriptFound):
        return None
    except Exception as e:
        return f"❌ Error while fetching transcript: {str(e)}"
