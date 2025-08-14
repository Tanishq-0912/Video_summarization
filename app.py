import streamlit as st
import subprocess
import os
import tempfile
import whisper
import warnings

# Suppress FP16 warning
warnings.filterwarnings("ignore", category=UserWarning)

# Normalize YouTube URL
def normalize_url(url):
    return url.replace("m.youtube.com", "www.youtube.com")

# Download audio using yt-dlp
def download_audio(youtube_url):
    try:
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
    except Exception as e:
        raise Exception(f"Download failed: {str(e)}")

# Transcribe audio using Whisper (tiny model, limited duration)
def transcribe_audio(audio_path):
    try:
        # Trim first 30 seconds using ffmpeg
        trimmed_path = audio_path.replace(".mp3", "_trimmed.mp3")
        trim_command = [
            "ffmpeg", "-y", "-i", audio_path,
            "-t", "30",  # duration in seconds
            "-acodec", "copy", trimmed_path
        ]
        subprocess.run(trim_command, capture_output=True)

        # Load Whisper model
        model = whisper.load_model("tiny")
        result = model.transcribe(trimmed_path)

        # Clean up trimmed file
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
                st.success("Audio downloaded successfully.")

                with st.spinner("Transcribing first 30 seconds..."):
                    transcript = transcribe_audio(audio_path)
                    st.success("Transcription complete.")
                    st.text_area("Transcript", transcript, height=400)
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
