# 🎧 YouTube Video Transcriber

YouTube Video Transcriber & Summarizer

A streamlined Streamlit-based app that quickly downloads, transcribes, and summarizes YouTube video audio using OpenAI’s Whisper model. Designed for lightning-fast deployment on Streamlit Cloud.

Features

Paste a YouTube URL and get a transcription of the first 30 seconds of audio.

Uses yt-dlp to download the best-quality audio efficiently.

Leverages ffmpeg to trim audio, ensuring faster processing.

Powered by OpenAI Whisper (tiny model)—CPU-compatible, no GPU required.

Sleek, user-friendly Streamlit interface, perfect for rapid prototyping and deployment.

Optional: extend to full-length transcription or include video summarization.

Installation & Setup

Clone this repository

git clone https://github.com/Tanishq-0912/Video_summarization.git
cd Video_summarization


Create and activate a virtual environment (recommended)

python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install dependencies

pip install -r requirements.txt


(Optional) If using packages.txt, install system-level dependencies (like ffmpeg):

sudo apt update
sudo apt install ffmpeg


Launch the app

streamlit run app.py


Deploy on Streamlit Cloud: Push to your GitHub repo and connect it in Streamlit Cloud for instant deployment.

How It Works (Architecture)

User Input: Paste a YouTube URL into the app.

Audio Download: yt-dlp fetches the highest-quality audio.

Audio Trimming: ffmpeg isolates the first 30 seconds for fast transcription.

Transcription: Whisper (tiny model) processes the trimmed audio and generates text.

Output: The app displays the transcribed text for the user.

(Extendable to summaries or full transcripts.)

Project Structure

app.py: Streamlit interface and orchestration logic.

summarizer.py: Core transcription (and optional summarization) functionality.

diag_transcript.py: (Optional) Diagnostic tools for transcript analysis.

requirements.txt & packages.txt: Python and system dependency lists.

readme.md: Project overview (you’re here!).

Skills & Tools Used

Python

Streamlit for building the web app

yt-dlp for downloading YouTube audio

ffmpeg for audio processing

OpenAI Whisper for transcription (tiny model)

Cloud Deployment: Easily deployable on Streamlit Cloud

Usage Tips & Extensions

Transcribe full videos by modifying the ffmpeg trimming logic.

Add a summarization step using NLP models like OpenAI’s GPT or BART to generate concise summaries.

Include a QA chatbot that uses embeddings to allow users to query video content interactively.

Support batch processing for multiple video transcripts at once.

License & Credits

License: MIT (or your preferred license).

Acknowledgments:

OpenAI Whisper

yt-dlp

ffmpeg

Streamlit
