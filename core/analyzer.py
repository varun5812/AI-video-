import json
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

MAX_ANALYSIS_CHARS = 8000


def get_llm():
    return ChatGroq(
        model=os.getenv("GROQ_ANALYSIS_MODEL", "llama-3.1-8b-instant"),
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.2,
    )


def _fallback_analysis(transcript: str) -> dict:
    title = "Video Analysis"
    return {
        "title": title,
        "summary": "Analysis could not be parsed cleanly. Please use the transcript and chat view.",
        "action_items": "No action items found.",
        "key_decisions": "No key decisions found.",
        "open_questions": "No open questions found.",
    }


def _parse_json_response(raw: str, transcript: str) -> dict:
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.removeprefix("json").strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1:
            return _fallback_analysis(transcript)
        try:
            data = json.loads(cleaned[start : end + 1])
        except json.JSONDecodeError:
            return _fallback_analysis(transcript)

    fallback = _fallback_analysis(transcript)
    return {
        "title": str(data.get("title") or fallback["title"]).strip(),
        "summary": str(data.get("summary") or fallback["summary"]).strip(),
        "action_items": str(data.get("action_items") or fallback["action_items"]).strip(),
        "key_decisions": str(data.get("key_decisions") or fallback["key_decisions"]).strip(),
        "open_questions": str(data.get("open_questions") or fallback["open_questions"]).strip(),
    }


def analyze_transcript(transcript: str) -> dict:
    """Generate all meeting insights in one Groq call instead of five sequential calls."""
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are an expert meeting and video analyst.
Return only valid JSON with these string fields:
title, summary, action_items, key_decisions, open_questions.

Rules:
- title: professional, max 8 words.
- summary: concise but useful bullet points.
- action_items: numbered list with owner and deadline when available.
- key_decisions: numbered list, or "No key decisions found."
- open_questions: numbered list, or "No open questions found."
- Do not include markdown fences or extra commentary.""",
            ),
            ("human", "{text}"),
        ]
    )

    chain = prompt | llm | StrOutputParser()
    raw = chain.invoke({"text": transcript[:MAX_ANALYSIS_CHARS]})
    return _parse_json_response(raw, transcript)
