# diag_transcript.py
import sys
import re
import json
import html
import requests
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from pytube import YouTube

def extract_video_id(url_or_id: str) -> str:
    # Accept either a full URL or a bare 11-char ID
    url = url_or_id.strip()
    m = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    if m:
        return m.group(1)
    if re.fullmatch(r"[0-9A-Za-z_-]{11}", url):
        return url
    raise ValueError("Could not extract a YouTube video id from input")

def try_youtube_transcript_api(video_id: str):
    print("\n=== Trying youtube_transcript_api.get_transcript ===")
    try:
        ts = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([seg.get("text","") for seg in ts])
        print("SUCCESS: youtube_transcript_api.get_transcript returned text (length {})".format(len(text)))
        print("Preview:", text[:1000])
        return True, text
    except TranscriptsDisabled:
        print("TranscriptsDisabled: uploader disabled transcripts.")
        return False, None
    except NoTranscriptFound:
        print("NoTranscriptFound: API could not find transcripts.")
        return False, None
    except AttributeError as e:
        print("AttributeError (maybe installed package is old/wrong):", e)
        return False, None
    except Exception as e:
        print("Other exception from youtube_transcript_api:", repr(e))
        return False, None

def try_list_transcripts(video_id: str):
    print("\n=== Trying youtube_transcript_api.list_transcripts and friends ===")
    try:
        tl = YouTubeTranscriptApi.list_transcripts(video_id)
        # list languages available:
        try:
            available = []
            # ._manually_created_transcripts may exist; we will attempt to introspect
            # best effort: call .find_transcript languages if present
            # print repr of transcripts object
            print("TranscriptList object repr:", repr(tl)[:400])
        except Exception:
            pass

        # Try to fetch english (manual or generated) using provided helpers:
        for try_langs in (['en'], ['en-US','en-GB','en'], ['hi','en']):
            try:
                print("Attempting find_transcript with languages:", try_langs)
                tr = tl.find_transcript(try_langs)
                fetched = tr.fetch()
                text = " ".join([seg.get("text","") for seg in fetched])
                print("SUCCESS via list_transcripts + find_transcript languages", try_langs)
                print("Preview:", text[:1000])
                return True, text
            except Exception as e:
                print(" - not available for", try_langs, ":", type(e).__name__, str(e)[:200])
        # If none worked:
        print("No transcript found via list_transcripts fallback attempts.")
        return False, None
    except Exception as e:
        print("list_transcripts call failed:", type(e).__name__, str(e)[:400])
        return False, None

def try_pytube_captions(url: str):
    print("\n=== Trying pytube .captions (manual & auto-generated) ===")
    try:
        yt = YouTube(url)
    except Exception as e:
        print("pytube: failed to construct YouTube object:", type(e).__name__, e)
        return False, None

    # show available captions codes
    try:
        captions = yt.captions  # CaptionQuery
        codes = [c.code for c in captions]
        print("pytube: available caption codes:", codes)
    except Exception as e:
        print("pytube: error accessing captions:", type(e).__name__, e)
        codes = []

    # Try common codes for manual and auto-generated captions
    tried_codes = []
    for code in ['en','a.en','en-US','en-GB','a.en-US','a.en-GB']:
        if code in codes:
            try:
                print("Trying caption code:", code)
                cap = captions.get_by_language_code(code)
                if not cap:
                    print("get_by_language_code returned None for", code)
                    continue
                srt = cap.generate_srt_captions()
                # srt to plain text
                text = " ".join(re.sub(r"\d+\n", "", srt).splitlines())
                print("SUCCESS: pytube caption code", code, "yielded text (len {})".format(len(text)))
                print("Preview:", text[:1000])
                return True, text
            except Exception as e:
                print("Error generating SRT for code", code, ":", type(e).__name__, e)
        tried_codes.append(code)

    # If none of the common codes worked, try listing all and attempting each
    if codes:
        for code in codes:
            if code in tried_codes:
                continue
            try:
                print("Trying available caption:", code)
                cap = captions.get_by_language_code(code)
                if cap:
                    srt = cap.generate_srt_captions()
                    text = " ".join(re.sub(r"\d+\n", "", srt).splitlines())
                    print("SUCCESS (via available code):", code)
                    print("Preview:", text[:1000])
                    return True, text
            except Exception as e:
                print("Error with available caption", code, ":", type(e).__name__, str(e)[:200])
    else:
        print("pytube reports no captions available (captions list empty).")

    return False, None

def try_scrape_player_response(url: str):
    """
    Try to parse ytInitialPlayerResponse/captionTracks from the watch HTML page.
    If found, download first captionTrack baseUrl.
    """
    print("\n=== Trying to scrape YouTube page for captionTracks (what the browser uses) ===")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    try:
        r = requests.get(url, headers=headers, timeout=15)
    except Exception as e:
        print("HTTP fetch error for YouTube watch page:", type(e).__name__, e)
        return False, None

    if r.status_code != 200:
        print("Watch page returned status", r.status_code)
        return False, None

    html_text = r.text

    # Find "captionTracks": [ ... ] JSON block
    idx = html_text.find('"captionTracks":')
    if idx == -1:
        print("No 'captionTracks' key found in page HTML. Captions may be embedded differently or blocked.")
        return False, None

    # locate the JSON array starting at the '[' after "captionTracks":
    start = html_text.find('[', idx)
    if start == -1:
        print("Found 'captionTracks' but couldn't find '['")
        return False, None

    # find the matching closing bracket for this array (naive bracket matching)
    depth = 0
    end = None
    for i in range(start, len(html_text)):
        ch = html_text[i]
        if ch == '[':
            depth += 1
        elif ch == ']':
            depth -= 1
            if depth == 0:
                end = i
                break
    if end is None:
        print("Could not extract captionTracks JSON (malformed page).")
        return False, None

    json_text = html_text[start:end+1]
    try:
        ct_list = json.loads(json_text)
        print("Found captionTracks entries:", len(ct_list))
    except Exception as e:
        print("Failed to parse captionTracks JSON:", type(e).__name__, e)
        # as fallback, try unescaping then parse
        try:
            json_text2 = html.unescape(json_text)
            ct_list = json.loads(json_text2)
            print("Parsed after unescape")
        except Exception as e2:
            print("Still failed to parse captionTracks JSON:", type(e2).__name__, e2)
            return False, None

    # pick best English track if available
    chosen = None
    for track in ct_list:
        lang = track.get('languageCode') or track.get('language')
        name = track.get('name', {}).get('simpleText') if track.get('name') else None
        print(" - track language:", lang, "kind:", track.get('kind'), "name:", name)
        if lang and lang.startswith('en'):
            chosen = track
            break
    if not chosen and ct_list:
        chosen = ct_list[0]

    base_url = chosen.get('baseUrl') if chosen else None
    if not base_url:
        print("No baseUrl found for chosen caption track.")
        return False, None

    # fetch caption xml (base_url usually returns XML)
    try:
        r2 = requests.get(base_url, headers=headers, timeout=15)
        if r2.status_code != 200:
            print("Failed to fetch caption xml, status:", r2.status_code)
            return False, None
        content = r2.text
        # remove tags, keep text nodes inside <text>...</text>
        texts = re.findall(r'<text[^>]*>(.*?)</text>', content, flags=re.DOTALL)
        if not texts:
            print("Found caption XML but no <text> tags.")
            return False, None
        # unescape and join
        cleaned = " ".join([html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', t))) for t in texts])
        print("SUCCESS: fetched captions from captionTracks. Preview:", cleaned[:1000])
        return True, cleaned
    except Exception as e:
        print("Error fetching caption xml:", type(e).__name__, e)
        return False, None

def diagnostic(url_or_id: str):
    try:
        video_id = extract_video_id(url_or_id)
    except Exception as e:
        print("ERROR extracting video id:", e)
        return

    watch_url = f"https://www.youtube.com/watch?v={video_id}"
    print("Video id:", video_id)
    print("Watch URL:", watch_url)

    # 1) youtube_transcript_api.get_transcript
    ok, text = try_youtube_transcript_api(video_id)
    if ok:
        return

    # 2) list_transcripts fallback
    ok, text = try_list_transcripts(video_id)
    if ok:
        return

    # 3) pytube captions
    ok, text = try_pytube_captions(watch_url)
    if ok:
        return

    # 4) scrape player_response captionTracks
    ok, text = try_scrape_player_response(watch_url)
    if ok:
        return

    print("\nRESULT: No transcript could be fetched by any method. Possible reasons:")
    print(" - The uploader disabled transcripts (TranscriptsDisabled).")
    print(" - The video captions are region-restricted or require authentication.")
    print(" - Captions are available only as " "embedded in the player but not exposed to APIs.")
    print(" - YouTube changed its page structure and our scraper couldn't find captionTracks (rare).")
    print("\nIf you want guaranteed transcription for any video, the robust fallback is:")
    print(" - download audio locally (pytube/yt-dlp) and run Whisper locally to produce transcript (works offline).")
    print("If you want, run this script locally and paste output here so I can inspect and guide next steps.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python diag_transcript.py <youtube_url_or_id>")
    else:
        diagnostic(sys.argv[1])
