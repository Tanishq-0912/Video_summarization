import streamlit as st
import subprocess
import os
import tempfile
import whisper
import warnings
import shutil

# Suppress FP16 warning
warnings.filterwarnings("ignore", category=UserWarning)

# Cache Whisper model to avoid reloading every button click
@st.cache_resource
def load_whisper_model():
    return whisper.load_model("tiny")  # can change to "base" if you want better quality

# Normalize YouTube URL
def normalize_url(url: str) -> str:
    return url.replace("m.youtube.com", "www.youtube.com")

# Download audio using yt-dlp
def download_audio(youtube_url: str) -> str:
    clean_url = normalize_url(youtube_url)
    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, "audio.mp3")

    command = [
        "yt-dlp",
        "-f", "bestaudio",
        "--extract-audio",
        "--audio-format", "mp3",
        "-o", output_path,
        clean_url
    ]

    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"yt-dlp error: {result.stderr}")

    return output_path

# Transcribe audio using Whisper (first 30s only)
def transcribe_audio(audio_path: str, model):
    trimmed_path = audio_path.replace(".mp3", "_trimmed.mp3")
    trim_command = [
        "ffmpeg", "-y", "-i", audio_path,
        "-t", "30",  # only first 30 seconds
        "-acodec", "copy", trimmed_path
    ]
    subprocess.run(trim_command, capture_output=True)

    result = model.transcribe(trimmed_path)

    # Clean up temporary files
    try:
        os.remove(trimmed_path)
        os.remove(audio_path)
        shutil.rmtree(os.path.dirname(audio_path), ignore_errors=True)
    except:
        pass

    return result["text"]

# ---------------- STREAMLIT UI ---------------- #
st.set_page_config(page_title="🎧 YouTube Transcriber", layout="wide")
st.title("🎧 YouTube Video Transcriber")

youtube_url = st.text_input("Enter YouTube video URL")

if st.button("Transcribe"):
    if not youtube_url:
        st.error("Please enter a YouTube URL.")
    else:
        with st.spinner("Loading Whisper model..."):
            model = load_whisper_model()

        with st.spinner("Downloading audio..."):
            try:
                audio_path = download_audio(youtube_url)
                st.success("✅ Audio downloaded.")

                with st.spinner("Transcribing first 30 seconds..."):
                    transcript = transcribe_audio(audio_path, model)
                    st.success("✅ Transcription complete.")
                    st.text_area("Transcript", transcript, height=300)

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
