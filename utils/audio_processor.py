"""
Audio / transcript acquisition utilities.

Strategy for YouTube URLs (in order):
  1. Try youtube-transcript-api to fetch existing captions — instant, no
     download, works on all cloud servers (no bot detection issues).
  2. Fall back to yt-dlp audio download → Groq Whisper transcription if
     captions are unavailable.

For local files the audio-download path is always used.
"""

import os
import re
import yt_dlp
from pydub import AudioSegment

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


# ── YouTube transcript (captions) ─────────────────────────────────────────────

def extract_video_id(url: str) -> str | None:
    """Extract the YouTube video ID from various URL formats."""
    patterns = [
        r"(?:v=|/v/|youtu\.be/|/embed/)([a-zA-Z0-9_-]{11})",
        r"^([a-zA-Z0-9_-]{11})$",
    ]
    for pat in patterns:
        m = re.search(pat, url)
        if m:
            return m.group(1)
    return None


def get_youtube_transcript(url: str) -> str | None:
    """
    Try to fetch the transcript via YouTube's caption system.
    Returns the full transcript text, or None if captions are not available.
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        print("youtube-transcript-api not installed — skipping caption fetch.")
        return None

    video_id = extract_video_id(url)
    if not video_id:
        print("Could not extract video ID from URL.")
        return None

    ytt_api = YouTubeTranscriptApi()

    # Try multiple language combinations — most YouTube videos have at least one
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
                print(f"Fetched YouTube captions ({len(full_text)} chars, langs={langs})")
                return full_text

        except Exception as e:
            print(f"Caption attempt with {langs} failed: {e}")
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
                        print(f"Fetched captions via list ({len(full_text)} chars, lang={t.language_code})")
                        return full_text
                else:
                    # Try to translate non-English captions to English
                    try:
                        translated = t.translate("en")
                        fetched = translated.fetch()
                        full_text = " ".join(snippet.text for snippet in fetched).strip()
                        if len(full_text) >= 20:
                            print(f"Fetched translated captions ({len(full_text)} chars, {t.language_code}->en)")
                            return full_text
                    except Exception:
                        # Translation not available — skip this one
                        print(f"Translation from {t.language_code} to English not available.")
                        continue
            except Exception:
                continue
    except Exception as e:
        print(f"Listing transcripts also failed: {e}")

    print("No usable captions found for this video.")
    return None


# ── Audio download (yt-dlp) — fallback ────────────────────────────────────────

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
