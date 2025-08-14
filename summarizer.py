# summarizer.py
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline
import re

def get_video_id(url):
    """
    Extract the video ID from a YouTube URL.
    """
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    if not match:
        raise ValueError("Invalid YouTube URL")
    return match.group(1)

def fetch_transcript(url):
    """
    Fetch the transcript from a YouTube video.
    """
    video_id = get_video_id(url)
    transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
    transcript_text = " ".join([item['text'] for item in transcript_data])
    return transcript_text

def summarize_text(text, max_length=150, min_length=50):
    """
    Summarize long text using Hugging Face transformers.
    """
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
    return summary[0]['summary_text']

def summarize_youtube_video(url):
    """
    Full process: fetch transcript → summarize → return result.
    """
    transcript = fetch_transcript(url)
    return summarize_text(transcript)
