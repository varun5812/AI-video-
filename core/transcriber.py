import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from pydub import AudioSegment
from groq import Groq
from dotenv import load_dotenv

# ─── Groq Whisper Config ────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_WHISPER_MODEL = "whisper-large-v3"

# ─── Sarvam Config ──────────────────────────────────────────────────────────────
SARVAM_PIECE_SECONDS = 25
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
SARVAM_STT_TRANSLATE_URL = "https://api.sarvam.ai/speech-to-text-translate"
SARVAM_MODEL = os.getenv("SARVAM_STT_MODEL", "saaras:v2.5")


# ─── Groq Whisper Transcription ─────────────────────────────────────────────────
def transcribe_chunk_groq(chunk_path: str) -> str:
    """
    Send a WAV chunk to Groq's Whisper API for transcription.
    Uses whisper-large-v3 — same quality as local Whisper, zero local resources.
    """
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not set in environment / .env")

    client = Groq(api_key=GROQ_API_KEY)

    with open(chunk_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            file=(os.path.basename(chunk_path), audio_file),
            model=GROQ_WHISPER_MODEL,
            response_format="text",
            language="en",
        )

    return transcription.strip() if isinstance(transcription, str) else transcription.text.strip()


# ─── Sarvam (Hinglish) Transcription ────────────────────────────────────────────
def _send_to_sarvam(piece_path: str) -> str:
    """Send one ≤30s WAV file to Sarvam and return the English transcript."""
    headers = {"api-subscription-key": SARVAM_API_KEY}

    with open(piece_path, "rb") as f:
        files = {"file": (os.path.basename(piece_path), f, "audio/wav")}
        data = {"model": SARVAM_MODEL, "with_diarization": "false"}
        response = requests.post(
            SARVAM_STT_TRANSLATE_URL,
            headers=headers,
            files=files,
            data=data,
            timeout=120,
        )

    if not response.ok:
        print(f"\n❌ Sarvam returned {response.status_code}")
        print(f"Response body: {response.text}\n")
        response.raise_for_status()

    return response.json().get("transcript", "")


def transcribe_chunk_sarvam(chunk_path: str) -> str:
    """
    Sarvam sync API only accepts ≤30s audio. We split this chunk into
    25-second pieces, send each separately, and join the transcripts.
    """
    if not SARVAM_API_KEY:
        raise RuntimeError("SARVAM_API_KEY is not set in environment / .env")

    audio = AudioSegment.from_wav(chunk_path)
    piece_ms = SARVAM_PIECE_SECONDS * 1000

    full_text = ""
    total_pieces = (len(audio) + piece_ms - 1) // piece_ms

    for i, start in enumerate(range(0, len(audio), piece_ms)):
        piece = audio[start: start + piece_ms]
        piece_path = f"{chunk_path}_sv_{i}.wav"
        piece.export(piece_path, format="wav")

        try:
            print(f"  → Sarvam piece {i + 1}/{total_pieces} ...")
            full_text += _send_to_sarvam(piece_path) + " "
        finally:
            if os.path.exists(piece_path):
                os.remove(piece_path)

    return full_text.strip()


# ─── Router ─────────────────────────────────────────────────────────────────────
def transcribe_chunk(chunk_path: str, language: str = "english") -> str:
    """
    Route one chunk to Groq Whisper or Sarvam depending on language choice.
    - english  → Groq Whisper API (cloud)
    - hinglish → Sarvam (translates to English while transcribing)
    """
    if language.lower() == "hinglish":
        return transcribe_chunk_sarvam(chunk_path)
    return transcribe_chunk_groq(chunk_path)


def transcribe_all(chunks: list, language: str = "english") -> str:

    engine = "Sarvam AI" if language.lower() == "hinglish" else "Groq Whisper"
    print(f"Using {engine} for transcription.")

    max_workers = min(len(chunks), int(os.getenv("TRANSCRIPTION_WORKERS", "3")))
    transcripts = [""] * len(chunks)

    def transcribe_indexed(index: int, chunk_path: str):
        print(f"Transcribing chunk {index + 1}/{len(chunks)}...")
        return index, transcribe_chunk(chunk_path, language=language)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(transcribe_indexed, i, chunk)
            for i, chunk in enumerate(chunks)
        ]
        for future in as_completed(futures):
            index, text = future.result()
            transcripts[index] = text

    print("Transcription complete.")

    return " ".join(transcripts).strip()
