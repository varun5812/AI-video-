"""
core/llm_router.py
──────────────────
Multi-model LLM router — 2 active models only.
"""
import os
from langchain_core.language_models.chat_models import BaseChatModel

MODEL_OPTIONS = {
    "✨ Google — Gemini 3.6 Flash": ("google", "gemini-3.6-flash"),
    "🧠 Groq — Qwen 3.6 27B":      ("groq",   "qwen/qwen3.6-27b"),
}

DEFAULT_MODEL = "✨ Google — Gemini 3.6 Flash"


def get_llm(model_display_name: str = DEFAULT_MODEL) -> BaseChatModel:
    provider, model_id = MODEL_OPTIONS.get(
        model_display_name,
        ("google", "gemini-3.6-flash")
    )

    if provider == "groq":
        from langchain_groq import ChatGroq
        api_key = os.getenv("GROQ_API_KEY", "").strip()
        if not api_key or len(api_key) < 10:
            raise RuntimeError("GROQ_API_KEY missing. Get one free at https://console.groq.com/keys")
        return ChatGroq(model=model_id, api_key=api_key, temperature=0.3, max_retries=3)

    elif provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        api_key = os.getenv("GOOGLE_API_KEY", "").strip()
        if not api_key or len(api_key) < 10:
            raise RuntimeError("GOOGLE_API_KEY missing. Get one free at https://aistudio.google.com/apikey")
        return ChatGoogleGenerativeAI(model=model_id, google_api_key=api_key, temperature=0.3)

    else:
        raise ValueError(f"Unknown provider: {provider}")


def get_provider_badge(model_display_name: str) -> str:
    provider, _ = MODEL_OPTIONS.get(model_display_name, ("google", ""))
    return {"groq": "🟣 Groq", "google": "🔵 Google"}.get(provider, provider)
