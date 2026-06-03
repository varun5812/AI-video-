from dotenv import load_dotenv

load_dotenv()  # MUST be before core imports

from utils.audio_processor import (
    get_youtube_transcript,
    get_subtitles_via_extract_info,
    get_youtube_subtitles_ytdlp,
    process_uploaded_file,
)
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question


def run_pipeline(source: str, language: str = "english") -> dict:
    print("Starting AI Video Assistant")

    transcript = None

    # If it looks like a YouTube URL, try captions first
    if source.startswith("http") and "youtu" in source:
        print("Detected YouTube URL. Fetching captions...")
        transcript = get_youtube_transcript(source)
        if not transcript:
            transcript = get_subtitles_via_extract_info(source)
        if not transcript:
            transcript = get_youtube_subtitles_ytdlp(source)
        if not transcript:
            print("Could not fetch captions. Please paste transcript manually.")
            return None
    else:
        # Local file — convert and transcribe
        print("Detected local file. Processing audio...")
        chunks = process_uploaded_file(source)
        transcript = transcribe_all(chunks, language)

    print(f"Raw transcription (first 300 chars): {transcript[:300]}")

    title = generate_title(transcript, language)
    summary = summarize(transcript, language)
    action_item = extract_action_items(transcript, language)
    decisions = extract_key_decisions(transcript, language)
    questions = extract_questions(transcript, language)
    rag_chain = build_rag_chain(transcript, language)

    return {
        "title": title,
        "transcript": transcript,
        "summary": summary,
        "action_items": action_item,
        "key_decisions": decisions,
        "open_questions": questions,
        "rag_chain": rag_chain,
    }


if __name__ == "__main__":
    source = input("Enter YouTube URL or local file path: ").strip()
    language = input("Language (english/hinglish): ").strip() or "english"
    result = run_pipeline(source, language)

    if not result:
        print("Failed to process. Exiting.")
        exit(1)

    print("\n" + "=" * 60)
    print(f"[Title] {result['title']}")
    print(f"\n[Summary]\n{result['summary']}")
    print(f"\n[Action Items]\n{result['action_items']}")
    print(f"\n[Key Decisions]\n{result['key_decisions']}")
    print(f"\n[Open Questions]\n{result['open_questions']}")
    print("=" * 60)

    # Chat with your meeting via RAG
    print("\n[Chat with your meeting] (type 'exit' to quit)\n")
    rag_chain = result["rag_chain"]
    while True:
        question = input("You: ").strip()
        if question.lower() in ["exit", "quit", "q"]:
            print("Goodbye!")
            break
        if not question:
            continue
        answer = ask_question(rag_chain, question)
        print(f"\nAssistant: {answer}\n")