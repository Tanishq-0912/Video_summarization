import re
import streamlit as st
from diag_transcript import fetch_transcript_from_youtube

st.set_page_config(page_title="YouTube Transcript Fetcher", page_icon="🎬", layout="centered")

st.title("🎬 YouTube Transcript Fetcher")

# Input box for YouTube URL
url = st.text_input("Enter YouTube URL:")

if url:
    # Extract video ID (works for youtube.com and youtu.be)
    match = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", url)
    if match:
        video_id = match.group(1)
        st.write(f"✅ Video ID: **{video_id}**")

        # Fetch transcript from diag_transcript.py
        transcript_text = fetch_transcript_from_youtube(video_id)

        if transcript_text:
            st.success("Transcript fetched successfully! 🎉")
            st.text_area("Transcript:", transcript_text, height=400)
        else:
            st.error("❌ Transcript not available for this video.")
    else:
        st.error("⚠️ Could not extract a valid video ID from the URL. Please check the link.")
