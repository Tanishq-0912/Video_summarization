import os
import yt_dlp
import whisper
import gradio as gr

# Path to your ffmpeg/bin folder
FFMPEG_BIN_PATH = r"C:\Users\Admin\Downloads\ffmpeg-6.1.1-full_build\bin"

def download_audio(url):
    """Download YouTube video audio as MP3"""
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "audio.%(ext)s",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192"
            }
        ],
        "ffmpeg_location": FFMPEG_BIN_PATH
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return "audio.mp3"


def transcribe_and_summarize(url):
    try:
        # Step 1: Download audio
        audio_path = download_audio(url)

        # Step 2: Load Whisper model
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)

        transcript = result["text"]

        # Step 3: Very simple summarization (first 500 chars)
        summary = transcript[:500] + "..." if len(transcript) > 500 else transcript

        return transcript, summary
    except Exception as e:
        return f"Error: {str(e)}", ""


# Gradio Web Interface
with gr.Blocks() as demo:
    gr.Markdown("## 🎥 YouTube Video Transcriber & Summarizer")
    url_input = gr.Textbox(label="YouTube URL")
    transcript_output = gr.Textbox(label="Transcript", lines=10)
    summary_output = gr.Textbox(label="Summary", lines=5)
    run_button = gr.Button("Transcribe & Summarize")

    run_button.click(
        fn=transcribe_and_summarize,
        inputs=url_input,
        outputs=[transcript_output, summary_output]
    )

if __name__ == "__main__":
    os.environ["PATH"] += os.pathsep + FFMPEG_BIN_PATH
    demo.launch()
