import streamlit as st
from pytube import YouTube
import tempfile
import os
import whisper
import subprocess
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

# Download audio using pytube
def download_audio(youtube_url):
    try:
        yt = YouTube(youtube_url)
        stream = yt.streams.filter(only_audio=True).first()
        temp_dir = tempfile.mkdtemp()
        output_path = os.path.join(temp_dir, "audio.mp3")
        stream.download(filename=output_path)
        return output_path
    except Exception as e:
        raise Exception(f"Download failed: {str(e)}")

# Transcribe first 30s using Whisper
def transcribe_audio(audio_path):
    try:
        trimmed_path = audio_path.replace(".mp3", "_trimmed.mp3")
        trim_command = [
            "ffmpeg", "-y", "-i", audio_path,
            "-t", "30",  # only first 30 sec
            "-acodec", "copy", trimmed_path
        ]
        subprocess.run(trim_command, capture_output=True)

        model = whisper.load_model("tiny")
        result = model.transcribe(trimmed_path)

        os.remove(trimmed_path)
        return result["text"]
    except Exception as e:
        raise Exception(f"Transcription failed: {str(e)}")

# Streamlit UI
st.title("🎧 YouTube Video Transcriber")
youtube_url = st.text_input("Enter YouTube video URL")

if st.button("Transcribe"):
    if not youtube_url:
        st.error("Please enter a YouTube URL.")
    else:
        with st.spinner("Downloading audio..."):
            try:
                audio_path = download_audio(youtube_url)
                st.success("Audio downloaded successfully ✅")

                with st.spinner("Transcribing first 30 seconds..."):
                    transcript = transcribe_audio(audio_path)
                    st.success("Transcription complete 🎉")
                    st.text_area("Transcript", transcript, height=400)
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
