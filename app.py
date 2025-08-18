# app.py — Streamlit app (cloud-friendly, no heavy deps)
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from pytube import YouTube
import tempfile, os, shutil, re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
import math

# Ensure nltk packages (download at runtime if needed)
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

st.set_page_config(page_title="YouTube Summarizer (light)", layout="wide")
st.title("🎬 YouTube Summarizer — Cloud-friendly")

def extract_video_id(url: str) -> str:
    """Extract YouTube video id from a URL or accept an ID directly."""
    if not url:
        return None
    # common patterns
    m = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    if m:
        return m.group(1)
    # if user pasted only id
    if re.fullmatch(r"[0-9A-Za-z_-]{11}", url.strip()):
        return url.strip()
    return None

def fetch_transcript_from_youtube(video_id: str):
    """Try to obtain a transcript using youtube_transcript_api."""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([seg["text"] for seg in transcript_list if seg.get("text")])
        return text
    except TranscriptsDisabled:
        raise Exception("Transcripts are disabled for this video.")
    except NoTranscriptFound:
        raise Exception("No transcript found for this video.")
    except Exception as e:
        raise Exception(f"Transcript fetch error: {e}")

def download_audio_with_pytube(url: str):
    """Download audio with pytube (will only be used for local testing — Cloud transcription is not included)."""
    temp_dir = tempfile.mkdtemp()
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(only_audio=True).first()
        output_path = os.path.join(temp_dir, "audio.mp4")
        stream.download(filename=output_path)
        return output_path, temp_dir
    except Exception as e:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise Exception(f"Pytube download failed: {e}")

# Lightweight frequency-based summarizer (no heavy libs)
def summarize_text_freq(text: str, num_sentences: int = 5):
    if not text or not text.strip():
        return "No text to summarize."
    # tokenize sentences
    sentences = sent_tokenize(text)
    if len(sentences) <= num_sentences:
        return text  # short text, return as-is

    # build word frequency
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text.lower())
    freq = {}
    for w in words:
        if w.isalpha() and w not in stop_words:
            freq[w] = freq.get(w, 0) + 1

    if not freq:
        # fallback: return first few sentences
        return " ".join(sentences[:num_sentences])

    # normalize frequencies
    max_freq = max(freq.values())
    for w in freq:
        freq[w] = freq[w] / max_freq

    # score sentences
    sent_scores = []
    for i, sent in enumerate(sentences):
        sent_words = word_tokenize(sent.lower())
        score = 0
        count = 0
        for w in sent_words:
            if w.isalpha():
                score += freq.get(w, 0)
                count += 1
        # average to prefer shorter useful sentences
        sent_scores.append((i, score / (count+1e-9)))

    # pick top N by score, keep original order
    sent_scores.sort(key=lambda x: x[1], reverse=True)
    selected_idx = sorted([idx for idx, _ in sent_scores[:num_sentences]])
    summary = " ".join([sentences[i] for i in selected_idx])
    return summary

# UI
st.markdown("Paste a YouTube video URL (or just the video id). This app fetches the transcript (if available) and gives a lightweight summary.")
input_url = st.text_input("YouTube URL or ID")

col1, col2 = st.columns(2)
with col1:
    n_sent = st.number_input("Number of sentences in summary", min_value=1, max_value=10, value=5, step=1)

with col2:
    run_btn = st.button("Fetch transcript & Summarize")

if run_btn:
    if not input_url:
        st.error("Please enter a YouTube URL or video id.")
    else:
        video_id = extract_video_id(input_url.strip())
        if not video_id:
            st.error("Could not extract video id. Paste a full YouTube URL or the 11-char id.")
        else:
            st.info(f"Trying to fetch transcript for video id: {video_id}")
            try:
                transcript = fetch_transcript_from_youtube(video_id)
                st.success("Transcript fetched ✅")
                st.subheader("Transcript (first 2000 chars):")
                st.text_area("Transcript", transcript[:2000], height=200)
                st.subheader("Summary:")
                summary = summarize_text_freq(transcript, num_sentences=n_sent)
                st.write(summary)
            except Exception as e:
                st.error(f"❌ {str(e)}")
                st.write("---")
                st.info("If the video doesn't have captions, try running the project locally (PyCharm) and use a local Whisper/ffmpeg flow to transcribe audio.")

# small footer
st.markdown("---")
st.caption("This lightweight app summarizes videos that already have captions. For videos without captions, run local transcription (Whisper) on your machine.")


