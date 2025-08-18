import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from diag_transcript import fetch_transcript_from_youtube

def fetch_transcript(video_id):
    transcript_text = fetch_transcript_from_youtube(video_id)
    if transcript_text:
        return transcript_text

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


