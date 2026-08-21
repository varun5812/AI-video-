"""
Extracts action items, key decisions, and open questions from a transcript.
Uses a SINGLE combined LLM call to avoid rate-limit issues on free tiers.
"""
import re
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from core.llm_router import get_llm, DEFAULT_MODEL

MAX_TRANSCRIPT_CHARS = 3500


def extract_all_insights(transcript: str, language: str = "English", model: str = DEFAULT_MODEL) -> dict:
    """
    Extract action items, key decisions, and open questions in ONE API call.
    Returns a dict with keys: action_items, key_decisions, open_questions.
    """
    llm = get_llm(model)

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
         "CRITICAL LANGUAGE INSTRUCTION: Always write the extracted content and responses entirely in {language} "
         "(except for the markdown headers '## Action Items', '## Key Decisions', '## Open Questions' "
         "which must remain exactly as written in English)."),
        ("human", "{text}"),
    ])

    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({"text": transcript[:MAX_TRANSCRIPT_CHARS], "language": language})

    parsed = {
        "action_items":  "No specific action items identified.",
        "key_decisions": "No specific key decisions identified.",
        "open_questions": "No specific open questions identified.",
    }

    sections = re.split(r'##\s+', result)
    for section in sections:
        section_lower = section.lower()
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


# Backward compatibility stubs
def extract_action_items(transcript: str, language: str = "English", model: str = DEFAULT_MODEL) -> str:
    return extract_all_insights(transcript, language, model)["action_items"]

def extract_key_decisions(transcript: str, language: str = "English", model: str = DEFAULT_MODEL) -> str:
    return extract_all_insights(transcript, language, model)["key_decisions"]

def extract_questions(transcript: str, language: str = "English", model: str = DEFAULT_MODEL) -> str:
    return extract_all_insights(transcript, language, model)["open_questions"]