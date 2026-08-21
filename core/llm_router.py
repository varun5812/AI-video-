"""
core/llm_router.py
──────────────────
Multi-model LLM router.
Supports Groq (free-tier models), Google Gemini, and OpenAI GPT.
"""
import os
from langchain_core.language_models.chat_models import BaseChatModel


# ── Model catalogue ────────────────────────────────────────────────────────────
MODEL_OPTIONS = {
    "✨ Google — Gemini 2.5 Flash (Free)":   ("google", "gemini-2.5-flash"),
    "🌟 Google — Gemini 2.5 Pro":            ("google", "gemini-2.5-pro"),
    "⚡ Groq — Llama 3 8B (Free)":           ("groq",   "llama3-8b-8192"),
    "🔥 Groq — Mixtral 8x7B (Free)":         ("groq",   "mixtral-8x7b-32768"),
    "🤖 OpenAI — GPT-4o Mini":               ("openai", "gpt-4o-mini"),
    "💡 OpenAI — GPT-4o":                    ("openai", "gpt-4o"),
}

DEFAULT_MODEL = "✨ Google — Gemini 2.5 Flash (Free)"


def get_llm(model_display_name: str = DEFAULT_MODEL) -> BaseChatModel:
    provider, model_id = MODEL_OPTIONS.get(
        model_display_name,
        ("google", "gemini-2.5-flash")
    )

    if provider == "groq":
        from langchain_groq import ChatGroq
        api_key = os.getenv("GROQ_API_KEY", "").strip()
        if not api_key or len(api_key) < 10:
            raise RuntimeError(
                "GROQ_API_KEY is missing or revoked.\n"
                "Get a free key at https://console.groq.com/keys and update your .env file."
            )
        return ChatGroq(model=model_id, api_key=api_key, temperature=0.3, max_retries=3)

    elif provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        api_key = os.getenv("GOOGLE_API_KEY", "").strip()
        if not api_key or len(api_key) < 10:
            raise RuntimeError(
                "GOOGLE_API_KEY is missing.\n"
                "Get a free key at https://aistudio.google.com/apikey and update your .env file."
            )
        return ChatGoogleGenerativeAI(model=model_id, google_api_key=api_key, temperature=0.3)

    elif provider == "openai":
        from langchain_openai import ChatOpenAI
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key or len(api_key) < 10:
            raise RuntimeError(
                "OPENAI_API_KEY is missing.\n"
                "Get a key at https://platform.openai.com/api-keys and update your .env file."
            )
        return ChatOpenAI(model=model_id, api_key=api_key, temperature=0.3)

    else:
        raise ValueError(f"Unknown provider: {provider}")


def get_provider_badge(model_display_name: str) -> str:
    provider, _ = MODEL_OPTIONS.get(model_display_name, ("google", ""))
    badges = {"groq": "🟣 Groq", "google": "🔵 Google", "openai": "🟢 OpenAI"}
    return badges.get(provider, provider)


def check_key_status() -> dict:
    """Quick connectivity check for each provider. Returns dict of provider→(ok, message)."""
    results = {}

    # Google
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        api_key = os.getenv("GOOGLE_API_KEY", "").strip()
        if not api_key or len(api_key) < 10:
            results["google"] = (False, "Key missing")
        else:
            llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key, temperature=0)
            llm.invoke("hi")
            results["google"] = (True, "Connected")
    except Exception as e:
        results["google"] = (False, str(e)[:80])

    # Groq
    try:
        from langchain_groq import ChatGroq
        api_key = os.getenv("GROQ_API_KEY", "").strip()
        if not api_key or len(api_key) < 10:
            results["groq"] = (False, "Key missing")
        else:
            llm = ChatGroq(model="llama3-8b-8192", api_key=api_key, temperature=0, max_retries=1)
            llm.invoke("hi")
            results["groq"] = (True, "Connected")
    except Exception as e:
        results["groq"] = (False, str(e)[:80])

    # OpenAI
    try:
        from langchain_openai import ChatOpenAI
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key or len(api_key) < 10:
            results["openai"] = (False, "Key missing")
        else:
            llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key, temperature=0)
            llm.invoke("hi")
            results["openai"] = (True, "Connected")
    except Exception as e:
        results["openai"] = (False, str(e)[:80])

    return results
