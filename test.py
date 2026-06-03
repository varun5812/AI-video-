from dotenv import load_dotenv
load_dotenv(override=True)   # MUST be before any core/ imports

from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions


source = "https://www.youtube.com/watch?v=_Q-e_nczWqM&t=223s"
language = "english"   # "english" → Whisper, "hinglish" → Sarvam



chunks = process_input(source)


transcript = transcribe_all(chunks, language=language)
print("\n" + "=" * 60)
print("TRANSCRIPT")
print("=" * 60)
print(transcript[:500] + "..." if len(transcript) > 500 else transcript)


title = generate_title(transcript)
summary = summarize(transcript)

print("\n" + "=" * 60)
print(f"TITLE: {title}")
print("=" * 60)
print("\nSUMMARY")
print("-" * 60)
print(summary)



from core.extractor import extract_all_insights

insights = extract_all_insights(transcript)
action_items = insights["action_items"]
decisions = insights["key_decisions"]
questions = insights["open_questions"]

print("\n" + "=" * 60)
print("ACTION ITEMS")
print("=" * 60)
print(action_items)

print("\n" + "=" * 60)
print("KEY DECISIONS")
print("=" * 60)
print(decisions)

print("\n" + "=" * 60)
print("OPEN QUESTIONS")
print("=" * 60)
print(questions)