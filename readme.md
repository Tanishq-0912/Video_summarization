# 🎧 YouTube Video Transcriber

A simple **Streamlit** app that downloads audio from a YouTube video and transcribes the **first 30 seconds** using OpenAI's Whisper model.  
Optimized for quick deployment on **Streamlit Cloud**.

---

## 🚀 Features
- Paste any YouTube URL and get a transcript of the first 30 seconds.
- Uses `yt-dlp` to download the best-quality audio.
- Audio trimming with `ffmpeg` for faster transcription.
- Transcription powered by **OpenAI Whisper (tiny model)**.
- Works on CPU — no GPU required.
- Clean, minimal **Streamlit** UI.

---

## 📦 Installation

Clone this repository:

```bash
git clone https://github.com/yourusername/youtube-video-transcriber.git
cd youtube-video-transcriber
