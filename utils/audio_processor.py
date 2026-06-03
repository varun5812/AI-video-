"""
Audio / transcript acquisition utilities.

Strategy for YouTube URLs (in order):
  1. Try youtube-transcript-api to fetch existing captions — instant, no
     download, works on most servers.
  2. Use yt-dlp extract_info to get subtitle URLs from video metadata,
     then fetch subtitle content via requests (CDN URLs are less blocked).
  3. Fall back to yt-dlp subtitle file download (skip_download mode).
  4. Last resort: yt-dlp audio download → Groq Whisper transcription.

For local files the audio-download path is always used.
"""

import os
import re
import requests as _requests
import yt_dlp
from pydub import AudioSegment

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

_BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


# ── YouTube transcript (captions) ─────────────────────────────────────────────

def extract_video_id(url: str) -> str | None:
    """Extract the YouTube video ID from various URL formats."""
    patterns = [
        r"(?:v=|/v/|/shorts/|/live/|youtu\.be/|/embed/)([a-zA-Z0-9_-]{11})",
        r"^([a-zA-Z0-9_-]{11})$",
    ]
    for pat in patterns:
        m = re.search(pat, url)
        if m:
            return m.group(1)
    return None


def get_youtube_transcript(url: str) -> str | None:
    """
    Strategy 1: fetch transcript via youtube-transcript-api.
    Returns the full transcript text, or None if unavailable.
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        print("[Strategy 1] youtube-transcript-api not installed — skipping.")
        return None

    video_id = extract_video_id(url)
    if not video_id:
        print("[Strategy 1] Could not extract video ID from URL.")
        return None

    import requests
    session = requests.Session()
    # Use a modern browser User-Agent and headers to prevent instant YouTube anti-bot blocking
    session.headers.update(_BROWSER_HEADERS)
    ytt_api = YouTubeTranscriptApi(http_client=session)

    # Try multiple language combinations
    language_attempts = [
        ["en"],
        ["en-US", "en-GB", "en-IN"],
        ["hi"],
        ["en", "hi", "en-IN", "en-US"],
    ]

    for langs in language_attempts:
        try:
            fetched = ytt_api.fetch(video_id, languages=langs)
            full_text = " ".join(snippet.text for snippet in fetched).strip()

            if len(full_text) >= 20:
                print(f"[Strategy 1] [SUCCESS] Fetched YouTube captions ({len(full_text)} chars, langs={langs})")
                return full_text

        except Exception as e:
            print(f"[Strategy 1] Caption attempt with {langs} failed: {e}")
            continue

    # Last resort: list all available transcripts and try translate to English
    try:
        transcript_list = ytt_api.list(video_id)
        for t in transcript_list:
            try:
                # If it's already English-ish, fetch directly
                if t.language_code.startswith("en"):
                    fetched = t.fetch()
                    full_text = " ".join(snippet.text for snippet in fetched).strip()
                    if len(full_text) >= 20:
                        print(f"[Strategy 1] [SUCCESS] Fetched captions via list ({len(full_text)} chars, lang={t.language_code})")
                        return full_text
                else:
                    # Try to translate non-English captions to English
                    try:
                        translated = t.translate("en")
                        fetched = translated.fetch()
                        full_text = " ".join(snippet.text for snippet in fetched).strip()
                        if len(full_text) >= 20:
                            print(f"[Strategy 1] [SUCCESS] Fetched translated captions ({len(full_text)} chars, {t.language_code}->en)")
                            return full_text
                    except Exception:
                        print(f"[Strategy 1] Translation from {t.language_code} to English not available.")
                        continue
            except Exception:
                continue
    except Exception as e:
        print(f"[Strategy 1] Listing transcripts also failed: {e}")

    print("[Strategy 1] [FAILED] No usable captions found via youtube-transcript-api.")
    return None


# ── yt-dlp extract_info subtitle URL fetching (Strategy 2) ────────────────────

def get_subtitles_via_extract_info(url: str) -> str | None:
    """
    Strategy 2: use yt-dlp's extract_info(download=False) to get subtitle URLs
    from video metadata, then fetch the subtitle content via requests.

    This works differently from direct caption APIs because:
    - extract_info uses YouTube's innertube API (internal client API)
    - Subtitle content is served from YouTube's CDN, which is less blocked
    - No actual download occurs — just metadata extraction + URL fetch
    """
    video_id = extract_video_id(url)
    if not video_id:
        return None

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web"],
                "skip": ["dash", "hls"],
            }
        },
        "http_headers": _BROWSER_HEADERS,
        # Don't write anything to disk
        "writesubtitles": False,
        "writeautomaticsub": False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("[Strategy 2] Extracting video info via yt-dlp...")
            info = ydl.extract_info(url, download=False)
    except Exception as e:
        print(f"[Strategy 2] [FAILED] extract_info failed: {e}")
        return None

    if not info:
        print("[Strategy 2] [FAILED] extract_info returned empty result.")
        return None

    # Check for subtitles in the metadata
    manual_subs = info.get("subtitles", {}) or {}
    auto_subs = info.get("automatic_captions", {}) or {}

    print(f"[Strategy 2] Found manual subtitle langs: {list(manual_subs.keys())[:5]}")
    print(f"[Strategy 2] Found auto-caption langs: {list(auto_subs.keys())[:5]}")

    preferred_langs = ["en", "en-US", "en-GB", "en-IN", "en-orig", "hi"]
    preferred_formats = ["json3", "vtt", "srv3", "srt", "ttml"]

    # Try manual subs first, then auto-generated
    for subs_source, source_name in [(manual_subs, "manual"), (auto_subs, "auto")]:
        langs = preferred_langs + [lang for lang in subs_source.keys() if lang not in preferred_langs]
        for lang in langs:
            if lang not in subs_source:
                continue

            formats = subs_source[lang]
            ordered_formats = []
            for fmt_pref in preferred_formats:
                ordered_formats.extend([fmt for fmt in formats if fmt.get("ext") == fmt_pref])
            ordered_formats.extend([fmt for fmt in formats if fmt not in ordered_formats])

            for fmt_entry in ordered_formats:
                sub_url = fmt_entry.get("url")
                fmt_ext = fmt_entry.get("ext", "vtt")
                if not sub_url:
                    continue
                try:
                    print(f"[Strategy 2] Fetching {source_name} subtitles ({lang}/{fmt_ext}) from CDN...")
                    resp = _requests.get(sub_url, timeout=20, headers=_BROWSER_HEADERS)
                    if resp.ok and len(resp.text) > 50:
                        text = _parse_subtitle_content(resp.text, fmt_ext)
                        if text and len(text) >= 20:
                            print(f"[Strategy 2] [SUCCESS] Got subtitles via extract_info ({len(text)} chars, {source_name}/{lang}/{fmt_ext})")
                            return text
                except Exception as e:
                    print(f"[Strategy 2] Failed to fetch subtitle URL: {e}")
                    continue

    print("[Strategy 2] [FAILED] No usable subtitles found via extract_info.")
    return None


def _parse_subtitle_content(content: str, fmt: str) -> str:
    """Parse subtitle content (json3/vtt/srv3/srt) into plain text."""
    import json as _json

    if fmt == "json3":
        try:
            data = _json.loads(content)
            events = data.get("events", [])
            lines = []
            for event in events:
                segs = event.get("segs", [])
                for seg in segs:
                    text = seg.get("utf8", "").strip()
                    if text and text != "\n":
                        lines.append(text)
            result = " ".join(lines).strip()
            # Clean up extra whitespace
            result = re.sub(r"\s+", " ", result)
            return result
        except Exception:
            pass

    # For vtt/srt/srv3 — use the file parser
    return _parse_subtitle_text(content)


def _parse_subtitle_text(content: str) -> str:
    """
    Parse VTT or SRT subtitle text and extract plain text.
    Removes timestamps, formatting tags, and duplicate lines.
    """
    # Remove VTT header
    content = re.sub(r"^WEBVTT.*?\n\n", "", content, flags=re.DOTALL)

    # Remove timestamp lines (e.g., "00:00:01.000 --> 00:00:04.000")
    content = re.sub(r"\d{2}:\d{2}:\d{2}[.,]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[.,]\d{3}.*?\n", "", content)

    # Remove SRT sequence numbers (lines that are just digits)
    content = re.sub(r"^\d+\s*$", "", content, flags=re.MULTILINE)

    # Remove HTML-like tags (<c>, </c>, <b>, etc.)
    content = re.sub(r"<[^>]+>", "", content)

    content = (
        content.replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", '"')
        .replace("&#39;", "'")
    )

    # Remove position/alignment tags
    content = re.sub(r"align:.*?position:.*?\n", "", content)

    # Deduplicate consecutive identical lines (common in VTT auto-captions)
    lines = [line.strip() for line in content.split("\n") if line.strip()]
    deduplicated = []
    for line in lines:
        if not deduplicated or line != deduplicated[-1]:
            deduplicated.append(line)

    return " ".join(deduplicated).strip()


# ── yt-dlp subtitle file download (Strategy 3) ────────────────────────────────

def get_youtube_subtitles_ytdlp(url: str) -> str | None:
    """
    Strategy 3: use yt-dlp to download subtitle files (skip video download).
    Returns the transcript text, or None on failure.
    """
    import tempfile
    import glob

    video_id = extract_video_id(url)
    if not video_id:
        return None

    with tempfile.TemporaryDirectory() as tmpdir:
        output_template = os.path.join(tmpdir, "%(id)s.%(ext)s")
        ydl_opts = {
            "skip_download": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": ["en", "en-US", "en-GB", "en-IN", "hi", "all"],
            "subtitlesformat": "json3/vtt/srv3/srt",
            "extractor_args": {
                "youtube": {
                    "player_client": ["android", "web"],
                    "skip": ["dash", "hls"],
                }
            },
            "http_headers": _BROWSER_HEADERS,
            "outtmpl": output_template,
            "quiet": True,
            "no_warnings": True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print("[Strategy 3] Downloading subtitle files via yt-dlp...")
                ydl.download([url])
        except Exception as e:
            print(f"[Strategy 3] [FAILED] yt-dlp subtitle download failed: {e}")
            return None

        # Look for downloaded subtitle files, preferring formats that parse cleanly.
        sub_files = []
        for pattern in ("*.json3", "*.vtt", "*.srv3", "*.srt"):
            sub_files.extend(glob.glob(os.path.join(tmpdir, pattern)))

        if not sub_files:
            print("[Strategy 3] [FAILED] yt-dlp did not produce any subtitle files.")
            return None

        # Parse the first available subtitle file
        try:
            with open(sub_files[0], "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            ext = os.path.splitext(sub_files[0])[1].lstrip(".") or "vtt"
            text = _parse_subtitle_content(content, ext)
            if text and len(text) >= 20:
                print(f"[Strategy 3] [SUCCESS] Got subtitles via yt-dlp file download ({len(text)} chars)")
                return text
        except Exception as e:
            print(f"[Strategy 3] Failed to parse subtitle file: {e}")

    print("[Strategy 3] [FAILED] No usable subtitles from yt-dlp file download.")
    return None


# ── Audio download (yt-dlp) — last resort ─────────────────────────────────────

def download_youtube_audio(url: str) -> str:
    """Download audio from YouTube using yt-dlp and convert to WAV."""
    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        base_filename = ydl.prepare_filename(info)
        filename = os.path.splitext(base_filename)[0] + ".wav"
    return filename


def convert_to_wav(input_path: str) -> str:
    """Convert any audio/video file to WAV format using pydub."""
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000)
    audio.export(output_path, format="wav")
    return output_path


def chunk_audio(wav_path: str, chunk_minutes: int = 5) -> list:
    """Split a WAV file into chunks for the Whisper API (≤25 MB each)."""
    audio = AudioSegment.from_file(wav_path)
    audio = audio.set_channels(1).set_frame_rate(16000)
    chunk_ms = chunk_minutes * 60 * 1000

    chunks = []
    for i, start in enumerate(range(0, len(audio), chunk_ms)):
        chunk = audio[start : start + chunk_ms]
        chunk_path = f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)

    return chunks


def process_input(source: str) -> list:
    """
    Process a YouTube URL or local file path.
    Returns a list of WAV chunk file paths for transcription.
    """
    if source.startswith("http://") or source.startswith("https://"):
        print("Detected YouTube URL. Downloading audio...")
        wav_path = download_youtube_audio(source)
    else:
        print("Detected local file. Converting to WAV...")
        wav_path = convert_to_wav(source)

    print("Chunking audio...")
    chunks = chunk_audio(wav_path)
    print(f"Audio ready — {len(chunks)} chunk(s) created.")
    return chunks
