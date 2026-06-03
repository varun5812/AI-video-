"""
Extracts action items, key decisions, and open questions from a transcript.
Uses a SINGLE combined LLM call to avoid rate-limit issues on Groq free tier.
"""
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
import re

MAX_TRANSCRIPT_CHARS = 3500


def get_llm():
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key or api_key == "GROQ_API_KEY" or len(api_key) < 10:
        raise RuntimeError(
            "GROQ_API_KEY is missing or invalid. "
            "Set it in Render Dashboard → Environment Variables, or in the local .env file."
        )
    return ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=api_key,
        temperature=0.2,
        max_retries=5,
    )


def extract_all_insights(transcript: str, language: str = "English") -> dict:
    """
    Extract action items, key decisions, and open questions in ONE API call.
    Returns a dict with keys: action_items, key_decisions, open_questions.
    """
    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are an expert meeting analyst. Analyze the meeting transcript and extract THREE categories of insights.\n\n"
         "Return your response in EXACTLY this format with these three sections:\n\n"
         "## Action Items\n"
         "- [action item 1 with owner and deadline if mentioned]\n"
         "- [action item 2]\n"
         "(If none found, write: No specific action items identified in this content.)\n\n"
         "## Key Decisions\n"
         "- [decision 1]\n"
         "- [decision 2]\n"
         "(If none found, write: No specific key decisions identified in this content.)\n\n"
         "## Open Questions\n"
         "- [question 1]\n"
         "- [question 2]\n"
         "(If none found, write: No specific open questions identified in this content.)\n\n"
         "IMPORTANT: Always provide thoughtful analysis. Even for informal content, identify implied action items, "
         "decisions or topics discussed, and questions raised or left unanswered. Be thorough.\n\n"
         "CRITICAL LANGUAGE INSTRUCTION: Always write the extracted content and responses entirely in {language} (except for the markdown headers '## Action Items', '## Key Decisions', '## Open Questions' which must remain exactly as written in English)."),
        ("human", "{text}"),
    ])

    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({"text": transcript[:MAX_TRANSCRIPT_CHARS], "language": language})

    # Parse the sections
    parsed = {
        "action_items": "No specific action items identified.",
        "key_decisions": "No specific key decisions identified.",
        "open_questions": "No specific open questions identified.",
    }

    sections = re.split(r'##\s+', result)
    for section in sections:
        section_lower = section.lower()
        # Get the content after the header line
        lines = section.strip().split('\n', 1)
        content = lines[1].strip() if len(lines) > 1 else ""

        if content:
            if 'action item' in section_lower:
                parsed["action_items"] = content
            elif 'key decision' in section_lower:
                parsed["key_decisions"] = content
            elif 'open question' in section_lower:
                parsed["open_questions"] = content

    return parsed


# Keep individual functions for backward compatibility
def extract_action_items(transcript: str, language: str = "English") -> str:
    """Kept for compatibility — use extract_all_insights() instead."""
    return extract_all_insights(transcript, language)["action_items"]


def extract_key_decisions(transcript: str, language: str = "English") -> str:
    """Kept for compatibility — use extract_all_insights() instead."""
    return extract_all_insights(transcript, language)["key_decisions"]


def extract_questions(transcript: str, language: str = "English") -> str:
    """Kept for compatibility — use extract_all_insights() instead."""
    return extract_all_insights(transcript, language)["open_questions"]