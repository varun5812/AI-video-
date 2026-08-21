"""
core/llm_router.py
──────────────────
Multi-model LLM router.
Supports Groq (Llama), Google Gemini, and OpenAI GPT models.
Model IDs updated August 2026.
"""
import os
from langchain_core.language_models.chat_models import BaseChatModel


# ── Model catalogue ────────────────────────────────────────────────────────────
MODEL_OPTIONS = {
    # Display name                          : (provider,   model_id)
    "⚡ Groq — Llama 3.3 70B (Fast)":       ("groq",   "llama-3.3-70b-versatile"),
    "🦙 Groq — Llama 3 8B":                 ("groq",   "llama3-8b-8192"),
    "✨ Google — Gemini 3.6 Flash":          ("google", "gemini-3.6-flash"),
    "🌟 Google — Gemini 2.5 Pro":            ("google", "gemini-2.5-pro"),
    "🤖 OpenAI — GPT-4o Mini":              ("openai", "gpt-4o-mini"),
    "💡 OpenAI — GPT-4o":                   ("openai", "gpt-4o"),
}

DEFAULT_MODEL = "⚡ Groq — Llama 3.3 70B (Fast)"


def get_llm(model_display_name: str = DEFAULT_MODEL) -> BaseChatModel:
    """
    Return the correct LangChain chat model for the given display name.
    Raises RuntimeError if the required API key is missing.
    """
    provider, model_id = MODEL_OPTIONS.get(
        model_display_name,
        ("groq", "llama-3.3-70b-versatile")
    )

    if provider == "groq":
        from langchain_groq import ChatGroq
        api_key = os.getenv("GROQ_API_KEY", "").strip()
        if not api_key or len(api_key) < 10:
            raise RuntimeError("GROQ_API_KEY is missing. Add it to your .env file or Streamlit secrets.")
        return ChatGroq(model=model_id, api_key=api_key, temperature=0.3, max_retries=5)

    elif provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        api_key = os.getenv("GOOGLE_API_KEY", "").strip()
        if not api_key or len(api_key) < 10:
            raise RuntimeError("GOOGLE_API_KEY is missing. Add it to your .env file or Streamlit secrets.")
        return ChatGoogleGenerativeAI(model=model_id, google_api_key=api_key, temperature=0.3)

    elif provider == "openai":
        from langchain_openai import ChatOpenAI
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key or len(api_key) < 10:
            raise RuntimeError("OPENAI_API_KEY is missing. Add it to your .env file or Streamlit secrets.")
        return ChatOpenAI(model=model_id, api_key=api_key, temperature=0.3)

    else:
        raise ValueError(f"Unknown provider: {provider}")


def get_provider_badge(model_display_name: str) -> str:
    """Return a short badge string for the active model."""
    provider, _ = MODEL_OPTIONS.get(model_display_name, ("groq", ""))
    badges = {"groq": "🟣 Groq", "google": "🔵 Gemini", "openai": "🟢 OpenAI"}
    return badges.get(provider, provider)
