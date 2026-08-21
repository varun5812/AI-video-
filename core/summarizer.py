import time
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from core.llm_router import get_llm, DEFAULT_MODEL


def summarize(transcript: str, language: str = "English", model: str = DEFAULT_MODEL) -> str:
    """Summarize in a single LLM call by truncating to fit within token limits."""
    llm = get_llm(model)
    truncated = transcript[:4000]

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are an expert meeting summarizer. Create a professional, detailed "
         "meeting summary from the transcript below. Use clear bullet points. "
         "Cover all major topics, decisions, and outcomes discussed.\n\n"
         "IMPORTANT: Always output your complete response in {language}."),
        ("human", "{text}"),
    ])

    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"text": truncated, "language": language})


def generate_title(transcript: str, language: str = "English", model: str = DEFAULT_MODEL) -> str:
    llm = get_llm(model)

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "Based on the meeting transcript, generate a short professional meeting title "
         "(max 8 words). Only return the title, nothing else.\n\n"
         "IMPORTANT: Always output your response in {language}."),
        ("human", "{text}"),
    ])

    chain = prompt | llm | StrOutputParser()
    time.sleep(2)  # Rate-limit buffer for free-tier APIs
    return chain.invoke({"text": transcript[:1000], "language": language})
