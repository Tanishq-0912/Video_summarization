# app.py
import re
import streamlit as st
from diag_transcript import fetch_transcript_from_youtube

st.set_page_config(page_title="YouTube Transcript Fetcher", page_icon="🎬", layout="centered")
st.title("🎬 YouTube Transcript Fetcher")

st.markdown("Paste a YouTube URL or a raw 11-char video ID. "
            "This app first tries the official API, then a resilient fallback scraper.")

def extract_video_id(u: str) -> str | None:
    if not u:
        return None
    u = u.strip()
    # Accept raw 11-char ID
    if re.fullmatch(r"[0-9A-Za-z_-]{11}", u):
        return u
    # Extract from common URL forms
    m = re.search(r"(?:v=|/shorts/|youtu\.be/)([0-9A-Za-z_-]{11})", u)
    return m.group(1) if m else None

url = st.text_input("Enter YouTube URL or ID:")

if st.button("Fetch transcript"):
    vid = extract_video_id(url)
    if not vid:
        st.error("Could not extract a valid 11-character video ID. Check the URL.")
    else:
        st.info(f"Video ID detected: **{vid}**")
        with st.spinner("Retrieving transcript…"):
            text, notes = fetch_transcript_from_youtube(vid, return_notes=True)

        if text:
            st.success("Transcript fetched ✅")
            st.text_area("Transcript (first 4000 chars):", text[:4000], height=300)
        else:
            st.error("❌ Transcript not available for this video.")
            with st.expander("Show diagnostic details"):
                if notes:
                    st.code("\n".join(f"- {n}" for n in notes))
                else:
                    st.write("No diagnostic notes available.")
