import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

def fetch_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([entry["text"] for entry in transcript])
        return text
    except TranscriptsDisabled:
        return "❌ Transcript not available (disabled by uploader)."
    except NoTranscriptFound:
        return "❌ No transcript found for this video."
    except Exception as e:
        return f"❌ Error fetching transcript: {e}"

st.title("🎬 YouTube Transcript Fetcher")

url = st.text_input("Enter YouTube URL:")
if url:
    if "v=" in url:
        video_id = url.split("v=")[-1].split("&")[0]
    else:
        video_id = url.split("/")[-1]

    st.write("Video ID:", video_id)

    transcript_text = fetch_transcript(video_id)
    st.text_area("Transcript:", transcript_text, height=300)
