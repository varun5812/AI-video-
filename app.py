import streamlit as st
import time
from dotenv import load_dotenv
from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question

load_dotenv()

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Video Assistant — Meeting Intelligence",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Premium CSS Design System ──────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@300;400;500&display=swap');

/* ══════════════════════════════════════════════════════════
   DESIGN TOKENS
   ══════════════════════════════════════════════════════════ */
:root {
    --bg-primary: #06060a;
    --bg-secondary: #0c0c14;
    --bg-tertiary: #12121e;
    --bg-elevated: #181828;
    --bg-glass: rgba(18, 18, 30, 0.7);
    --border-subtle: rgba(255,255,255,0.06);
    --border-default: rgba(255,255,255,0.09);
    --border-hover: rgba(139,92,246,0.35);
    --accent-primary: #8b5cf6;
    --accent-light: #a78bfa;
    --accent-ultralight: #c4b5fd;
    --accent-glow: rgba(139,92,246,0.5);
    --accent-secondary: #06d6a0;
    --accent-tertiary: #38bdf8;
    --text-primary: #f1f0f5;
    --text-secondary: #a09cb5;
    --text-tertiary: #6b6582;
    --success: #22c55e;
    --success-bg: rgba(34,197,94,0.08);
    --warning: #f59e0b;
    --warning-bg: rgba(245,158,11,0.08);
    --danger: #ef4444;
    --danger-bg: rgba(239,68,68,0.08);
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-xl: 20px;
    --shadow-sm: 0 1px 2px rgba(0,0,0,0.3);
    --shadow-md: 0 4px 12px rgba(0,0,0,0.4);
    --shadow-lg: 0 12px 40px rgba(0,0,0,0.5);
    --shadow-glow: 0 0 30px rgba(139,92,246,0.15);
    --transition-fast: 150ms cubic-bezier(0.4,0,0.2,1);
    --transition-base: 250ms cubic-bezier(0.4,0,0.2,1);
    --transition-slow: 400ms cubic-bezier(0.4,0,0.2,1);
}

/* ══════════════════════════════════════════════════════════
   GLOBAL RESET & BASE
   ══════════════════════════════════════════════════════════ */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

.stApp {
    background: var(--bg-primary) !important;
}

/* Subtle animated mesh gradient background */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background:
        radial-gradient(ellipse 80% 50% at 20% 20%, rgba(139,92,246,0.06), transparent),
        radial-gradient(ellipse 60% 40% at 80% 80%, rgba(6,214,160,0.04), transparent),
        radial-gradient(ellipse 50% 50% at 50% 50%, rgba(56,189,248,0.03), transparent);
    pointer-events: none;
    z-index: 0;
}

/* Subtle grid overlay */
.stApp::after {
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background-image:
        linear-gradient(rgba(255,255,255,0.015) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.015) 1px, transparent 1px);
    background-size: 60px 60px;
    pointer-events: none;
    z-index: 0;
}

/* ══════════════════════════════════════════════════════════
   SIDEBAR
   ══════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border-subtle) !important;
}

[data-testid="stSidebar"] * {
    color: var(--text-primary) !important;
}

[data-testid="stSidebar"] .stMarkdown p {
    color: var(--text-secondary) !important;
}

/* ══════════════════════════════════════════════════════════
   TYPOGRAPHY
   ══════════════════════════════════════════════════════════ */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Inter', sans-serif !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.02em;
}

/* Hero Section */
.hero-container {
    text-align: center;
    padding: 2rem 1rem 1.5rem;
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.35rem 0.9rem;
    background: rgba(139,92,246,0.1);
    border: 1px solid rgba(139,92,246,0.2);
    border-radius: 100px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--accent-light);
    margin-bottom: 1rem;
}

.hero-title {
    font-family: 'Inter', sans-serif;
    font-size: clamp(1.8rem, 4.5vw, 3rem);
    font-weight: 800;
    line-height: 1.1;
    margin: 0 0 0.6rem;
    background: linear-gradient(135deg, #ffffff 0%, var(--accent-light) 40%, var(--accent-secondary) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.03em;
}

.hero-subtitle {
    font-size: 0.9rem;
    color: var(--text-tertiary);
    font-weight: 400;
    line-height: 1.5;
    max-width: 480px;
    margin: 0 auto;
}

/* ══════════════════════════════════════════════════════════
   CARDS — Glassmorphism
   ══════════════════════════════════════════════════════════ */
.glass-card {
    background: var(--bg-glass);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
    transition: border-color var(--transition-base), box-shadow var(--transition-base), transform var(--transition-fast);
}

.glass-card:hover {
    border-color: var(--border-hover);
    box-shadow: var(--shadow-glow);
    transform: translateY(-1px);
}

.glass-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 2px;
    background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary), var(--accent-tertiary));
    opacity: 0;
    transition: opacity var(--transition-base);
}

.glass-card:hover::before {
    opacity: 1;
}

.card-header {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 1rem;
}

.card-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border-radius: var(--radius-sm);
    font-size: 0.95rem;
    flex-shrink: 0;
}

.card-icon-purple { background: rgba(139,92,246,0.15); }
.card-icon-green  { background: rgba(34,197,94,0.12); }
.card-icon-blue   { background: rgba(56,189,248,0.12); }
.card-icon-amber  { background: rgba(245,158,11,0.12); }
.card-icon-rose   { background: rgba(244,63,94,0.12); }

.card-label {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-tertiary);
}

.card-body {
    font-size: 0.875rem;
    line-height: 1.75;
    color: var(--text-secondary);
}

/* ══════════════════════════════════════════════════════════
   BADGES / CHIPS
   ══════════════════════════════════════════════════════════ */
.chip {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    padding: 0.25rem 0.65rem;
    border-radius: 100px;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    transition: all var(--transition-fast);
}

.chip-purple  { background: rgba(139,92,246,0.12); color: var(--accent-light); border: 1px solid rgba(139,92,246,0.2); }
.chip-green   { background: rgba(6,214,160,0.1);   color: var(--accent-secondary); border: 1px solid rgba(6,214,160,0.2); }
.chip-blue    { background: rgba(56,189,248,0.1);   color: var(--accent-tertiary); border: 1px solid rgba(56,189,248,0.2); }
.chip-success { background: var(--success-bg);      color: var(--success); border: 1px solid rgba(34,197,94,0.2); }

/* ══════════════════════════════════════════════════════════
   PIPELINE STATUS
   ══════════════════════════════════════════════════════════ */
.pipeline-step {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.6rem 0.9rem;
    background: var(--bg-tertiary);
    border-radius: var(--radius-sm);
    margin: 0.3rem 0;
    border: 1px solid var(--border-subtle);
    font-size: 0.78rem;
    font-weight: 500;
    color: var(--text-secondary);
    transition: all var(--transition-base);
}

.pipeline-step:hover {
    background: var(--bg-elevated);
    border-color: var(--border-default);
}

.step-indicator {
    width: 7px; height: 7px;
    border-radius: 50%;
    flex-shrink: 0;
    transition: all var(--transition-base);
}

.ind-active {
    background: var(--accent-primary);
    box-shadow: 0 0 10px var(--accent-glow), 0 0 4px var(--accent-glow);
    animation: pulseGlow 2s ease-in-out infinite;
}

.ind-done {
    background: var(--success);
    box-shadow: 0 0 6px rgba(34,197,94,0.3);
}

.ind-pending {
    background: var(--text-tertiary);
    opacity: 0.4;
}

@keyframes pulseGlow {
    0%, 100% { opacity: 1; box-shadow: 0 0 10px var(--accent-glow); }
    50%      { opacity: 0.5; box-shadow: 0 0 4px var(--accent-glow); }
}

/* ══════════════════════════════════════════════════════════
   METRIC CARDS
   ══════════════════════════════════════════════════════════ */
.metric-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.75rem;
    margin-bottom: 1.25rem;
}

.metric-card {
    background: var(--bg-tertiary);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    padding: 1rem;
    text-align: center;
    transition: all var(--transition-base);
}

.metric-card:hover {
    border-color: var(--border-hover);
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}

.metric-value {
    font-size: 1.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, var(--accent-light), var(--accent-secondary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.metric-label {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-tertiary);
    margin-top: 0.25rem;
}

/* ══════════════════════════════════════════════════════════
   TITLE BANNER
   ══════════════════════════════════════════════════════════ */
.title-banner {
    background: linear-gradient(135deg, rgba(139,92,246,0.08) 0%, rgba(6,214,160,0.05) 100%);
    border: 1px solid rgba(139,92,246,0.15);
    border-radius: var(--radius-lg);
    padding: 1.25rem 1.5rem;
    margin-bottom: 1.25rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}

.title-banner-icon {
    width: 42px; height: 42px;
    border-radius: var(--radius-md);
    background: rgba(139,92,246,0.15);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    flex-shrink: 0;
}

.title-banner-text {
    font-family: 'Inter', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.01em;
}

.title-banner-sub {
    font-size: 0.72rem;
    color: var(--text-tertiary);
    margin-top: 0.15rem;
    font-weight: 500;
}

/* ══════════════════════════════════════════════════════════
   TRANSCRIPT BOX
   ══════════════════════════════════════════════════════════ */
.transcript-box {
    background: var(--bg-tertiary);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    padding: 1.25rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    line-height: 1.9;
    max-height: 340px;
    overflow-y: auto;
    color: var(--text-secondary);
    white-space: pre-wrap;
    word-break: break-word;
}

/* ══════════════════════════════════════════════════════════
   CHAT INTERFACE
   ══════════════════════════════════════════════════════════ */
.chat-wrapper {
    background: var(--bg-secondary);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-lg);
    padding: 1.25rem;
    max-height: 440px;
    overflow-y: auto;
    margin-bottom: 0.75rem;
}

.chat-msg {
    margin-bottom: 0.9rem;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    animation: fadeSlideIn 0.3s ease-out;
}

@keyframes fadeSlideIn {
    from { opacity: 0; transform: translateY(6px); }
    to   { opacity: 1; transform: translateY(0); }
}

.chat-label {
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}

.chat-bubble {
    display: inline-block;
    padding: 0.7rem 1rem;
    border-radius: var(--radius-md);
    font-size: 0.84rem;
    line-height: 1.65;
    max-width: 85%;
}

.user-label  { color: var(--accent-light); }
.bot-label   { color: var(--accent-secondary); }

.user-bubble {
    background: rgba(139,92,246,0.1);
    border: 1px solid rgba(139,92,246,0.18);
    align-self: flex-end;
    border-bottom-right-radius: 4px;
}

.bot-bubble {
    background: rgba(6,214,160,0.06);
    border: 1px solid rgba(6,214,160,0.12);
    align-self: flex-start;
    border-bottom-left-radius: 4px;
}

.chat-empty {
    text-align: center;
    padding: 3rem 2rem;
}

.chat-empty-icon {
    font-size: 2.5rem;
    margin-bottom: 0.6rem;
    opacity: 0.6;
}

.chat-empty-text {
    color: var(--text-tertiary);
    font-size: 0.82rem;
    max-width: 300px;
    margin: 0 auto;
    line-height: 1.6;
}

/* ══════════════════════════════════════════════════════════
   STREAMLIT OVERRIDES
   ══════════════════════════════════════════════════════════ */
.stTextInput > div > div > input,
.stSelectbox > div > div {
    background: var(--bg-tertiary) !important;
    border: 1px solid var(--border-default) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
    transition: border-color var(--transition-fast), box-shadow var(--transition-fast) !important;
}

.stTextInput > div > div > input:focus {
    border-color: var(--accent-primary) !important;
    box-shadow: 0 0 0 3px rgba(139,92,246,0.12) !important;
}

.stTextInput > div > div > input::placeholder {
    color: var(--text-tertiary) !important;
    opacity: 0.7 !important;
}

.stButton > button {
    background: linear-gradient(135deg, var(--accent-primary) 0%, #7c3aed 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.03em !important;
    padding: 0.6rem 1.5rem !important;
    transition: all var(--transition-base) !important;
    box-shadow: 0 2px 8px rgba(139,92,246,0.25) !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(139,92,246,0.35) !important;
    filter: brightness(1.08) !important;
}

.stButton > button:active {
    transform: translateY(0) !important;
}

/* Expander */
.streamlit-expanderHeader {
    background: var(--bg-tertiary) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
    font-weight: 600 !important;
}

/* Progress */
.stProgress > div > div > div { background: var(--accent-primary) !important; }
.stSpinner > div { border-top-color: var(--accent-primary) !important; }

/* Labels */
label { color: var(--text-tertiary) !important; font-size: 0.75rem !important; font-weight: 500 !important; }
[data-testid="stMarkdownContainer"] p { color: var(--text-primary) !important; }

/* Divider */
hr {
    border: none !important;
    border-top: 1px solid var(--border-subtle) !important;
    margin: 1.5rem 0 !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border-default); border-radius: 100px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent-primary); }

/* Sidebar branding */
.sidebar-brand {
    padding: 1.25rem 0 0.75rem;
    text-align: center;
}

.sidebar-logo {
    font-size: 1.6rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    background: linear-gradient(135deg, var(--accent-light), var(--accent-secondary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.sidebar-tagline {
    font-size: 0.62rem;
    font-weight: 600;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--text-tertiary);
    margin-top: 0.2rem;
}

.sidebar-divider {
    width: 40px;
    height: 2px;
    background: linear-gradient(90deg, var(--accent-primary), transparent);
    margin: 0.75rem auto;
    border-radius: 2px;
}

/* Empty state */
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 4rem 2rem;
    text-align: center;
    min-height: 50vh;
}

.empty-icon {
    width: 80px;
    height: 80px;
    border-radius: var(--radius-xl);
    background: linear-gradient(135deg, rgba(139,92,246,0.12), rgba(6,214,160,0.08));
    border: 1px solid rgba(139,92,246,0.15);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2.2rem;
    margin-bottom: 1.5rem;
}

.empty-title {
    font-size: 1.3rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
    letter-spacing: -0.02em;
}

.empty-desc {
    color: var(--text-tertiary);
    font-size: 0.85rem;
    max-width: 400px;
    line-height: 1.7;
}

.feature-chips {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    justify-content: center;
    margin-top: 1.5rem;
}

/* Section headers */
.section-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.75rem;
}

.section-title {
    font-family: 'Inter', sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.01em;
}

.section-line {
    flex: 1;
    height: 1px;
    background: var(--border-subtle);
}
</style>
""", unsafe_allow_html=True)

# ─── Session State Init ──────────────────────────────────────────────────────────
for key, default in {
    "result": None,
    "chat_history": [],
    "processing": False,
    "pipeline_done": False,
    "pipeline_steps": {},
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─── Helpers ────────────────────────────────────────────────────────────────────
def step_indicator_class(steps: dict, key: str) -> str:
    s = steps.get(key, "pending")
    if s == "active":  return "ind-active"
    if s == "done":    return "ind-done"
    return "ind-pending"

def render_pipeline_step(label: str, key: str, icon: str):
    css = step_indicator_class(st.session_state.pipeline_steps, key)
    st.markdown(f"""
    <div class="pipeline-step">
        <div class="step-indicator {css}"></div>
        <span>{icon}&ensp;{label}</span>
    </div>""", unsafe_allow_html=True)

def count_words(text: str) -> int:
    return len(text.split()) if text else 0

# ─── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div class="sidebar-logo">🎬 VideoAI</div>
        <div class="sidebar-tagline">Meeting Intelligence</div>
        <div class="sidebar-divider"></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<span class="chip chip-purple">🎤 Input Source</span>', unsafe_allow_html=True)
    source = st.text_input(
        "YouTube URL or File Path",
        placeholder="https://youtube.com/watch?v=...",
        help="Paste a YouTube link or enter a local file path"
    )

    language = st.selectbox("🌐 Language", ["english", "hinglish"], index=0)

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    run_btn = st.button("⚡  Analyse Video", use_container_width=True)

    if st.session_state.pipeline_done:
        st.markdown("---")
        st.markdown('<span class="chip chip-success">✓ Pipeline Complete</span>', unsafe_allow_html=True)
        st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)
        for step, icon, label in [
            ("audio",      "🔊", "Audio Processing"),
            ("transcript", "📝", "Transcription"),
            ("title",      "🏷️", "Title Generation"),
            ("summary",    "📋", "Summarisation"),
            ("extract",    "🔍", "Extraction"),
            ("rag",        "🧠", "RAG Engine"),
        ]:
            render_pipeline_step(label, step, icon)

    st.markdown("---")
    st.markdown("""
    <div style="text-align:center;padding:0.5rem 0">
        <div style="font-size:0.6rem;color:var(--text-tertiary);letter-spacing:0.08em;text-transform:uppercase;font-weight:600">
            Powered by
        </div>
        <div style="font-size:0.7rem;color:var(--text-secondary);margin-top:0.2rem">
            Groq Whisper · Mistral AI · LangChain
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─── Main Content ───────────────────────────────────────────────────────────────
# Hero
st.markdown("""
<div class="hero-container">
    <div class="hero-badge">🚀 AI-Powered Analysis</div>
    <div class="hero-title">AI Video Assistant</div>
    <div class="hero-subtitle">
        Transform any video or meeting into structured insights — transcripts, summaries, action items, and an interactive Q&A chatbot.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ─── Run Pipeline ───────────────────────────────────────────────────────────────
if run_btn:
    if not source.strip():
        st.error("⚠️ Please enter a YouTube URL or file path in the sidebar.")
    else:
        st.session_state.pipeline_done = False
        st.session_state.result = None
        st.session_state.chat_history = []
        st.session_state.pipeline_steps = {}

        progress_placeholder = st.empty()

        def update_step(key, state):
            st.session_state.pipeline_steps[key] = state

        try:
            with progress_placeholder.container():
                st.info("⚙️ Processing your video — pipeline is running…")

            update_step("audio", "active")
            chunks = process_input(source)
            update_step("audio", "done")

            update_step("transcript", "active")
            transcript = transcribe_all(chunks, language)
            update_step("transcript", "done")

            update_step("title", "active")
            title = generate_title(transcript)
            update_step("title", "done")

            update_step("summary", "active")
            summary = summarize(transcript)
            update_step("summary", "done")

            update_step("extract", "active")
            action_items  = extract_action_items(transcript)
            decisions     = extract_key_decisions(transcript)
            questions     = extract_questions(transcript)
            update_step("extract", "done")

            update_step("rag", "active")
            rag_chain = build_rag_chain(transcript)
            update_step("rag", "done")

            st.session_state.result = {
                "title": title,
                "transcript": transcript,
                "summary": summary,
                "action_items": action_items,
                "key_decisions": decisions,
                "open_questions": questions,
                "rag_chain": rag_chain,
            }
            st.session_state.pipeline_done = True
            progress_placeholder.success("✅ Analysis complete! Scroll down to see your results.")
            time.sleep(0.8)
            progress_placeholder.empty()
            st.rerun()

        except Exception as e:
            for k in ["audio","transcript","title","summary","extract","rag"]:
                if st.session_state.pipeline_steps.get(k) == "active":
                    st.session_state.pipeline_steps[k] = "pending"
            progress_placeholder.error(f"❌ Error: {e}")

# ─── Results ────────────────────────────────────────────────────────────────────
if st.session_state.result:
    r = st.session_state.result

    # Title Banner
    st.markdown(f"""
    <div class="title-banner">
        <div class="title-banner-icon">📌</div>
        <div>
            <div class="title-banner-text">{r['title']}</div>
            <div class="title-banner-sub">Generated meeting title</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Metrics row
    word_count = count_words(r['transcript'])
    duration_est = max(1, word_count // 150)
    chunk_count = len(r['transcript'].split('.'))
    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card">
            <div class="metric-value">{word_count:,}</div>
            <div class="metric-label">Words Transcribed</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">~{duration_est} min</div>
            <div class="metric-label">Estimated Duration</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{chunk_count}</div>
            <div class="metric-label">Sentences</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Summary + Transcript row
    col1, col2 = st.columns([3, 2], gap="medium")

    with col1:
        st.markdown(f"""
        <div class="glass-card">
            <div class="card-header">
                <div class="card-icon card-icon-purple">📋</div>
                <div class="card-label">Summary</div>
            </div>
            <div class="card-body">{r['summary']}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        with st.expander("📝 Full Transcript", expanded=False):
            st.markdown(f'<div class="transcript-box">{r["transcript"]}</div>', unsafe_allow_html=True)

    # Extraction cards row
    st.markdown("""
    <div class="section-header">
        <span class="section-title">🔍 Extracted Insights</span>
        <div class="section-line"></div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        st.markdown(f"""
        <div class="glass-card">
            <div class="card-header">
                <div class="card-icon card-icon-green">✅</div>
                <div class="card-label">Action Items</div>
            </div>
            <div class="card-body">{r['action_items']}</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="glass-card">
            <div class="card-header">
                <div class="card-icon card-icon-blue">🔑</div>
                <div class="card-label">Key Decisions</div>
            </div>
            <div class="card-body">{r['key_decisions']}</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="glass-card">
            <div class="card-header">
                <div class="card-icon card-icon-amber">❓</div>
                <div class="card-label">Open Questions</div>
            </div>
            <div class="card-body">{r['open_questions']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── RAG Chat ──────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="section-header">
        <span class="section-title">💬 Chat with Your Meeting</span>
        <div class="section-line"></div>
    </div>
    """, unsafe_allow_html=True)

    # Chat history display
    if st.session_state.chat_history:
        chat_html = '<div class="chat-wrapper">'
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                chat_html += f"""
                <div class="chat-msg" style="align-items:flex-end">
                    <span class="chat-label user-label">You</span>
                    <div class="chat-bubble user-bubble">{msg['content']}</div>
                </div>"""
            else:
                chat_html += f"""
                <div class="chat-msg" style="align-items:flex-start">
                    <span class="chat-label bot-label">🤖 Assistant</span>
                    <div class="chat-bubble bot-bubble">{msg['content']}</div>
                </div>"""
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="glass-card chat-empty">
            <div class="chat-empty-icon">💬</div>
            <div class="chat-empty-text">
                Ask anything about your meeting — decisions, action items, specific topics, or quotes from participants.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Chat input
    chat_col1, chat_col2 = st.columns([5, 1], gap="small")
    with chat_col1:
        user_input = st.text_input(
            "Your question",
            placeholder="What were the main decisions made?",
            label_visibility="collapsed"
        )
    with chat_col2:
        send_btn = st.button("Send →", use_container_width=True)

    if send_btn and user_input.strip():
        with st.spinner("🤔 Thinking…"):
            answer = ask_question(r["rag_chain"], user_input.strip())
        st.session_state.chat_history.append({"role": "user",      "content": user_input.strip()})
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()

    if st.session_state.chat_history:
        if st.button("🗑️  Clear Chat", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()

else:
    # ── Empty State ──────────────────────────────────────────────────────────
    st.markdown("""
    <div class="empty-state">
        <div class="empty-icon">🎬</div>
        <div class="empty-title">Ready to Analyse</div>
        <div class="empty-desc">
            Paste a YouTube URL or file path in the sidebar, select your language,
            and hit <strong>Analyse Video</strong> to unlock AI-powered meeting intelligence.
        </div>
        <div class="feature-chips">
            <span class="chip chip-purple">📝 Transcription</span>
            <span class="chip chip-green">📋 Summarisation</span>
            <span class="chip chip-blue">💬 RAG Chat</span>
        </div>
    </div>
    """, unsafe_allow_html=True)