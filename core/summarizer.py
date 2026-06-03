from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import time
import os


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
        temperature=0.3,
        max_retries=5,
    )


def summarize(transcript: str) -> str:
    """Summarize in a single LLM call by truncating to fit within token limits."""
    llm = get_llm()

    # Truncate to ~4000 chars (~1000 tokens) to stay under free-tier limit
    truncated = transcript[:4000]

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are an expert meeting summarizer. Create a professional, detailed "
         "meeting summary from the transcript below. Use clear bullet points. "
         "Cover all major topics, decisions, and outcomes discussed."),
        ("human", "{text}"),
    ])

    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"text": truncated})


def generate_title(transcript: str) -> str:
    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "Based on the meeting transcript, generate a short professional meeting title "
         "(max 8 words). Only return the title, nothing else."),
        ("human", "{text}"),
    ])

    chain = prompt | llm | StrOutputParser()
    time.sleep(3)  # Rate-limit buffer for Groq free tier
    return chain.invoke({"text": transcript[:1000]})
