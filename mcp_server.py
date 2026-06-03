"""
MCP Server — AI Video Assistant
================================
Exposes the AI Video Assistant's core features as MCP tools so that any
MCP-compatible client (Claude Desktop, Cursor, VS Code Copilot, etc.)
can call them directly.

Run:
    python mcp_server.py            # stdio transport (for Claude Desktop)

Tools:
    1. analyze_youtube_video   — Full pipeline: YouTube URL → title + summary + insights
    2. summarize_transcript    — Summarize any pasted transcript
    3. extract_insights        — Extract action items, key decisions, open questions
    4. chat_with_transcript    — Ask a question about a transcript (RAG)
"""

import os
import sys

# Ensure project root is on the Python path so core/ and utils/ imports work
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv(override=True)

from mcp.server.fastmcp import FastMCP

# ── Import existing core modules (zero duplication) ──────────────────────────
from utils.audio_processor import (
    get_youtube_transcript,
    get_subtitles_via_extract_info,
    get_youtube_subtitles_ytdlp,
)
from core.summarizer import summarize, generate_title
from core.extractor import extract_all_insights
from core.rag_engine import build_rag_chain, ask_question


# ── Create MCP Server ────────────────────────────────────────────────────────
mcp = FastMCP("AI Video Assistant")


# ── Helper: fetch YouTube transcript using strategies 1-3 ────────────────────
def _fetch_youtube_transcript(url: str) -> str:
    """Try all 3 caption strategies and return transcript or raise error."""
    transcript = get_youtube_transcript(url)
    if transcript:
        return transcript

    transcript = get_subtitles_via_extract_info(url)
    if transcript:
        return transcript

    transcript = get_youtube_subtitles_ytdlp(url)
    if transcript:
        return transcript

    raise ValueError(
        f"Could not fetch captions for this video ({url}). "
        "The video may not have captions, or YouTube is blocking this server. "
        "Try using the 'summarize_transcript' tool with a manually pasted transcript instead."
    )


# ══════════════════════════════════════════════════════════════════════════════
# TOOL 1: Full YouTube Video Analysis
# ══════════════════════════════════════════════════════════════════════════════
@mcp.tool()
def analyze_youtube_video(youtube_url: str, language: str = "English") -> str:
    """
    Analyze a YouTube video end-to-end.

    Fetches the transcript from YouTube captions, then generates:
    - A short title
    - A detailed bullet-point summary
    - Action items, key decisions, and open questions

    Args:
        youtube_url: Full YouTube video URL (e.g. https://youtube.com/watch?v=...)
        language: Output language — English, Kannada, Telugu, or Hindi (default: English)

    Returns:
        A formatted report with title, summary, and extracted insights.
    """
    # Step 1: Fetch transcript
    transcript = _fetch_youtube_transcript(youtube_url)

    # Step 2: Generate title
    title = generate_title(transcript, language)

    # Step 3: Summarize
    summary = summarize(transcript, language)

    # Step 4: Extract insights
    insights = extract_all_insights(transcript, language)

    # Format the response
    result = f"""# {title}

## 📋 Summary
{summary}

## ✅ Action Items
{insights['action_items']}

## 🔑 Key Decisions
{insights['key_decisions']}

## ❓ Open Questions
{insights['open_questions']}

---
*Transcript length: {len(transcript.split())} words*
"""
    return result


# ══════════════════════════════════════════════════════════════════════════════
# TOOL 2: Summarize a Pasted Transcript
# ══════════════════════════════════════════════════════════════════════════════
@mcp.tool()
def summarize_transcript(transcript: str, language: str = "English") -> str:
    """
    Summarize a transcript or any text content.

    Generates a short title and a detailed bullet-point summary.
    Use this when you already have the transcript text (e.g. from a meeting,
    lecture, podcast, or manually copied captions).

    Args:
        transcript: The full transcript text to summarize.
        language: Output language — English, Kannada, Telugu, or Hindi (default: English)

    Returns:
        A formatted summary with title.
    """
    title = generate_title(transcript, language)
    summary = summarize(transcript, language)

    return f"""# {title}

## 📋 Summary
{summary}

---
*Transcript length: {len(transcript.split())} words*
"""


# ══════════════════════════════════════════════════════════════════════════════
# TOOL 3: Extract Insights
# ══════════════════════════════════════════════════════════════════════════════
@mcp.tool()
def extract_insights(transcript: str, language: str = "English") -> str:
    """
    Extract structured insights from a transcript.

    Analyzes the text and extracts:
    - Action items (with owners and deadlines if mentioned)
    - Key decisions made
    - Open questions that need follow-up

    Args:
        transcript: The full transcript text to analyze.
        language: Output language — English, Kannada, Telugu, or Hindi (default: English)

    Returns:
        Formatted list of action items, decisions, and open questions.
    """
    insights = extract_all_insights(transcript, language)

    return f"""## ✅ Action Items
{insights['action_items']}

## 🔑 Key Decisions
{insights['key_decisions']}

## ❓ Open Questions
{insights['open_questions']}
"""


# ══════════════════════════════════════════════════════════════════════════════
# TOOL 4: Chat with a Transcript (RAG Q&A)
# ══════════════════════════════════════════════════════════════════════════════
@mcp.tool()
def chat_with_transcript(
    transcript: str,
    question: str,
    language: str = "English",
) -> str:
    """
    Ask a question about a transcript and get an answer using RAG.

    Builds a lightweight retrieval-augmented generation (RAG) index from the
    transcript, finds the most relevant sections, and answers the question
    using Groq LLM.

    Args:
        transcript: The full transcript text to search through.
        question: The question to ask about the transcript content.
        language: Output language — English, Kannada, Telugu, or Hindi (default: English)

    Returns:
        An answer based on the transcript content.
    """
    rag_chain = build_rag_chain(transcript, language)
    answer = ask_question(rag_chain, question)
    return answer


# ── Entry Point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    mcp.run()
