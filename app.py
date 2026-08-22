import os
import re
import tempfile

import streamlit as st
import time
from dotenv import load_dotenv

load_dotenv(override=True)

from utils.audio_processor import (
    get_youtube_transcript,
    get_subtitles_via_extract_info,
    get_youtube_subtitles_ytdlp,
    process_uploaded_file,
)
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_all_insights
from core.rag_engine import build_rag_chain, ask_question
from core.llm_router import MODEL_OPTIONS, DEFAULT_MODEL, get_provider_badge

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VideoAI — Meeting Intelligence",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Clean Light Design System ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap');

/* ══════════════════════════════════════════════════════════
   DESIGN TOKENS
   ══════════════════════════════════════════════════════════ */
:root {
    /* Main area — clean light */
    --bg-main: #f8fafc;
    --bg-main-secondary: #f1f5f9;
    --bg-card: #ffffff;
    --bg-card-hover: #f8fafc;
    --bg-input: #ffffff;
    --bg-input-focus: #ffffff;
    
    /* Sidebar — slightly off-white */
    --bg-sidebar: #ffffff;
    --bg-sidebar-hover: #f1f5f9;
    --bg-sidebar-active: rgba(99,102,241,0.08);
    
    /* Accent — calming blue/soft purple */
    --accent: #6366f1; /* indigo-500 */
    --accent-hover: #818cf8; /* indigo-400 */
    --accent-dark: #4f46e5; /* indigo-600 */
    --accent-glow: rgba(99,102,241,0.15);
    --accent-gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #4f46e5 100%);
    --accent-gradient-soft: linear-gradient(135deg, rgba(99,102,241,0.08), rgba(139,92,246,0.04));
    
    /* Complementary accents */
    --green: #10b981;
    --green-soft: rgba(16,185,129,0.1);
    --blue: #3b82f6;
    --blue-soft: rgba(59,130,246,0.1);
    --amber: #f59e0b;
    --amber-soft: rgba(245,158,11,0.1);
    --rose: #f43f5e;
    --rose-soft: rgba(244,63,94,0.1);
    --cyan: #06b6d4;
    
    /* Text */
    --text-primary: #0f172a;
    --text-secondary: #334155;
    --text-muted: #64748b;
    --text-on-accent: #ffffff;
    
    /* Borders */
    --border: #e2e8f0;
    --border-hover: rgba(99,102,241,0.3);
    
    /* Misc */
    --radius-sm: 10px;
    --radius-md: 14px;
    --radius-lg: 18px;
    --radius-xl: 22px;
    --radius-pill: 100px;
    --shadow-sm: 0 2px 8px rgba(0,0,0,0.04);
    --shadow-md: 0 4px 20px rgba(0,0,0,0.06);
    --shadow-lg: 0 8px 40px rgba(0,0,0,0.08);
    --shadow-glow: 0 0 30px rgba(99,102,241,0.1);
    --transition: 250ms cubic-bezier(0.4,0,0.2,1);
    --transition-spring: 400ms cubic-bezier(0.34,1.56,0.64,1);
}

/* ══════════════════════════════════════════════════════════
   GLOBAL
   ══════════════════════════════════════════════════════════ */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    -webkit-font-smoothing: antialiased;
}

.stApp {
    background: var(--bg-main) !important;
}

/* Animated gradient mesh */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 60% 50% at 15% 15%, rgba(99,102,241,0.04), transparent),
        radial-gradient(ellipse 50% 40% at 85% 25%, rgba(59,130,246,0.03), transparent),
        radial-gradient(ellipse 70% 60% at 50% 90%, rgba(139,92,246,0.04), transparent);
    pointer-events: none;
    z-index: 0;
    animation: meshDrift 25s ease-in-out infinite alternate;
}

@keyframes meshDrift {
    0%   { opacity: 1; }
    50%  { opacity: 0.6; }
    100% { opacity: 1; }
}

/* ══════════════════════════════════════════════════════════
   ANIMATIONS
   ══════════════════════════════════════════════════════════ */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}

@keyframes fadeScale {
    from { opacity: 0; transform: scale(0.92); }
    to   { opacity: 1; transform: scale(1); }
}

@keyframes slideRight {
    from { opacity: 0; transform: translateX(-12px); }
    to   { opacity: 1; transform: translateX(0); }
}

@keyframes pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(99,102,241,0.35); }
    50%      { box-shadow: 0 0 0 6px rgba(99,102,241,0); }
}

@keyframes shimmer {
    0%   { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}

@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50%      { transform: translateY(-8px); }
}

@keyframes gradientFlow {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

@keyframes typing {
    from { width: 0; }
    to   { width: 100%; }
}

@keyframes blink {
    0%, 100% { opacity: 1; }
    50%      { opacity: 0; }
}

@keyframes ripple {
    0%   { transform: scale(0.8); opacity: 1; }
    100% { transform: scale(2.5); opacity: 0; }
}

@keyframes progressShimmer {
    0%   { background-position: -300px 0; }
    100% { background-position: 300px 0; }
}

@keyframes progressGlow {
    0%, 100% { box-shadow: 0 0 8px rgba(99,102,241,0.2), 0 0 20px rgba(99,102,241,0.1); }
    50%      { box-shadow: 0 0 16px rgba(99,102,241,0.4), 0 0 40px rgba(99,102,241,0.15); }
}

@keyframes dotPulse {
    0%, 80%, 100% { transform: scale(0); opacity: 0.5; }
    40% { transform: scale(1); opacity: 1; }
}

/* ══════════════════════════════════════════════════════════
   LOADING / PROGRESS BAR
   ══════════════════════════════════════════════════════════ */
.loading-container {
    max-width: 520px;
    margin: 2rem auto;
    padding: 2rem 2.5rem;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-xl);
    text-align: center;
    animation: fadeScale 0.5s ease-out;
    box-shadow: var(--shadow-lg);
}

.loading-icon {
    font-size: 2.5rem;
    margin-bottom: 0.75rem;
    animation: float 2.5s ease-in-out infinite;
}

.loading-title {
    font-size: 1.3rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 0.3rem;
    letter-spacing: -0.02em;
}

.loading-percent {
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #6366f1, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem;
    line-height: 1.2;
}

.loading-bar-track {
    width: 100%;
    height: 18px;
    background: #f1f5f9;
    border-radius: 100px;
    overflow: hidden;
    position: relative;
    margin-bottom: 0.85rem;
    border: 1px solid #e2e8f0;
}

.loading-bar-fill {
    height: 100%;
    border-radius: 100px;
    background: linear-gradient(90deg, #6366f1, #8b5cf6, #06b6d4, #6366f1);
    background-size: 300px 100%;
    animation: progressShimmer 2s linear infinite, progressGlow 2s ease-in-out infinite;
    transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
}

.loading-bar-fill::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(
        90deg,
        transparent 0%,
        rgba(255,255,255,0.4) 50%,
        transparent 100%
    );
    background-size: 200px 100%;
    animation: progressShimmer 1.5s linear infinite;
}

.loading-step {
    font-size: 0.82rem;
    font-weight: 500;
    color: var(--text-secondary);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
}

.loading-step-icon {
    font-size: 1rem;
}

.loading-dots {
    display: inline-flex;
    gap: 3px;
    margin-left: 4px;
}

.loading-dots span {
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: var(--accent);
    display: inline-block;
    animation: dotPulse 1.4s ease-in-out infinite;
}

.loading-dots span:nth-child(2) { animation-delay: 0.2s; }
.loading-dots span:nth-child(3) { animation-delay: 0.4s; }

.loading-wait {
    font-size: 0.72rem;
    color: var(--text-muted);
    margin-top: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.03em;
}

/* ══════════════════════════════════════════════════════════
   SIDEBAR
   ══════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border) !important;
}

[data-testid="stSidebar"] * {
    color: var(--text-primary) !important;
}

[data-testid="stSidebar"] .stMarkdown p {
    color: var(--text-secondary) !important;
}

/* Sidebar brand */
.sb-brand {
    display: flex;
    align-items: center;
    gap: 0.65rem;
    padding: 1.25rem 0.25rem;
    margin-bottom: 0.5rem;
}

.sb-brand-logo {
    width: 38px; height: 38px;
    background: var(--accent-gradient);
    border-radius: var(--radius-sm);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.15rem;
    color: white !important;
    box-shadow: 0 4px 12px rgba(99,102,241,0.25);
}

.sb-brand-text {
    font-size: 1.1rem;
    font-weight: 700;
    letter-spacing: -0.02em;
}

.sb-brand-sub {
    font-size: 0.58rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-muted) !important;
    margin-top: 1px;
}

/* New Analysis button */
.sb-new-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    width: 100%;
    padding: 0.7rem;
    background: var(--bg-sidebar-hover);
    border: 1px dashed #cbd5e1;
    border-radius: var(--radius-sm);
    color: var(--text-secondary) !important;
    font-size: 0.82rem;
    font-weight: 500;
    cursor: pointer;
    transition: all var(--transition);
    margin-bottom: 1rem;
}

.sb-new-btn:hover {
    background: var(--bg-sidebar-active);
    border-color: var(--accent);
    color: var(--accent-hover) !important;
}

/* History items */
.sb-section-label {
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--text-muted) !important;
    padding: 0.75rem 0.25rem 0.4rem;
}

.sb-history-item {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.6rem 0.7rem;
    border-radius: var(--radius-sm);
    font-size: 0.78rem;
    font-weight: 500;
    color: var(--text-secondary) !important;
    cursor: pointer;
    transition: all var(--transition);
    margin: 2px 0;
    text-decoration: none;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.sb-history-item:hover {
    background: var(--bg-sidebar-hover);
    color: var(--text-primary) !important;
}

.sb-history-item.active {
    background: var(--bg-sidebar-active);
    color: var(--accent-dark) !important;
}

.sb-history-icon {
    font-size: 0.85rem;
    opacity: 0.8;
    flex-shrink: 0;
}

.sb-history-text {
    overflow: hidden;
    text-overflow: ellipsis;
}

/* Status indicator */
.sb-status {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.55rem 0.7rem;
    background: var(--green-soft);
    border: 1px solid rgba(16,185,129,0.2);
    border-radius: var(--radius-sm);
    margin: 0.3rem 0;
    font-size: 0.72rem;
    font-weight: 600;
    color: var(--green) !important;
}

.sb-status-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--green);
    flex-shrink: 0;
}

/* Pipeline steps in sidebar */
.sb-pipeline {
    padding: 0.25rem 0;
}

.sb-step {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.4rem 0.5rem;
    font-size: 0.72rem;
    font-weight: 500;
    color: var(--text-muted);
    transition: all var(--transition);
}

.sb-step-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    flex-shrink: 0;
}

.sb-step-dot.done { background: var(--green); box-shadow: 0 0 6px rgba(16,185,129,0.3); }
.sb-step-dot.active { background: var(--accent); animation: pulse 2s infinite; }
.sb-step-dot.pending { background: #cbd5e1; opacity: 0.6; }

/* Powered by footer */
.sb-footer {
    text-align: center;
    padding: 1rem 0 0.5rem;
}

.sb-footer-label {
    font-size: 0.55rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--text-muted) !important;
}

.sb-footer-tech {
    font-size: 0.65rem;
    font-weight: 500;
    color: var(--text-secondary) !important;
    margin-top: 0.2rem;
}

/* ══════════════════════════════════════════════════════════
   MAIN — CENTERED CONTENT
   ══════════════════════════════════════════════════════════ */
.main-wrapper {
    max-width: 820px;
    margin: 0 auto;
    padding: 0 1rem;
}

/* Hero */
.hero {
    text-align: center;
    padding: 3.5rem 0 2rem;
    animation: fadeUp 0.7s ease-out;
}

.hero-icon-wrap {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 64px; height: 64px;
    background: var(--accent-gradient);
    border-radius: var(--radius-lg);
    font-size: 1.8rem;
    margin-bottom: 1.25rem;
    box-shadow: 0 8px 32px rgba(99,102,241,0.25);
    animation: float 4s ease-in-out infinite;
}

.hero h1 {
    font-size: clamp(1.7rem, 4vw, 2.6rem) !important;
    font-weight: 800 !important;
    letter-spacing: -0.04em !important;
    line-height: 1.15 !important;
    margin: 0 0 0.4rem !important;
    color: var(--text-primary) !important;
}

.hero-gradient-text {
    background: linear-gradient(135deg, #4f46e5, #06b6d4, #4f46e5);
    background-size: 200% 200%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: gradientFlow 5s ease infinite;
}

.hero-sub {
    font-size: 0.95rem;
    color: var(--text-muted);
    line-height: 1.6;
    max-width: 480px;
    margin: 0.6rem auto 0;
}

/* CTA Input Bar */
.cta-bar {
    max-width: 640px;
    margin: 0 auto;
    background: var(--bg-input);
    border: 1px solid var(--border);
    border-radius: var(--radius-xl);
    padding: 0.5rem;
    display: flex;
    gap: 0.5rem;
    transition: all var(--transition);
    animation: fadeUp 0.7s ease-out 0.3s both;
    box-shadow: var(--shadow-sm);
}

.cta-bar:focus-within {
    border-color: var(--accent);
    box-shadow: 0 0 0 4px rgba(99,102,241,0.1), var(--shadow-md);
}

/* How it works — Horizontal Flow */
.flow-container {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.4rem;
    margin: 2.5rem auto 1.5rem;
    max-width: 680px;
    animation: fadeUp 0.7s ease-out 0.5s both;
}

.flow-step {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.4rem;
    padding: 0.85rem 0.6rem;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    flex: 1;
    transition: all var(--transition);
    min-width: 0;
    box-shadow: var(--shadow-sm);
}

.flow-step:hover {
    background: var(--bg-card-hover);
    border-color: var(--border-hover);
    transform: translateY(-3px);
    box-shadow: var(--shadow-md);
}

.flow-step-icon {
    width: 36px; height: 36px;
    border-radius: var(--radius-sm);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
}

.flow-step-icon.purple { background: rgba(139,92,246,0.1); color: #7c3aed; }
.flow-step-icon.blue   { background: rgba(59,130,246,0.1); color: #2563eb; }
.flow-step-icon.green  { background: rgba(16,185,129,0.1); color: #059669; }
.flow-step-icon.cyan   { background: rgba(6,182,212,0.1); color: #0891b2; }

.flow-step-label {
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--text-primary);
    text-align: center;
}

.flow-arrow {
    color: #cbd5e1;
    font-size: 0.85rem;
    flex-shrink: 0;
}

/* Capability chips */
.cap-row {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 0.5rem;
    margin-top: 1.5rem;
    animation: fadeUp 0.7s ease-out 0.7s both;
}

.cap-chip {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.4rem 0.85rem;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-pill);
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--text-secondary);
    transition: all var(--transition);
    box-shadow: var(--shadow-sm);
}

.cap-chip:hover {
    border-color: var(--accent);
    color: var(--accent-dark);
    transform: translateY(-1px);
    box-shadow: var(--shadow-md);
}

/* ══════════════════════════════════════════════════════════
   RESULT CARDS
   ══════════════════════════════════════════════════════════ */
/* Title Banner */
.res-title {
    background: var(--accent-gradient-soft);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: var(--radius-lg);
    padding: 1.2rem 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1.25rem;
    animation: fadeUp 0.5s ease-out;
}

.res-title-icon {
    width: 44px; height: 44px;
    border-radius: var(--radius-md);
    background: var(--accent-gradient);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    flex-shrink: 0;
    color: white !important;
    box-shadow: 0 4px 12px rgba(99,102,241,0.25);
}

.res-title-text {
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.01em;
}

.res-title-sub {
    font-size: 0.72rem;
    color: var(--text-muted);
    margin-top: 2px;
    font-weight: 500;
}

/* Metric strip */
.metric-strip {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.7rem;
    margin-bottom: 1.25rem;
}

.metric-box {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 1rem;
    text-align: center;
    transition: all var(--transition);
    animation: fadeScale 0.4s ease-out both;
    box-shadow: var(--shadow-sm);
}

.metric-box:nth-child(2) { animation-delay: 0.08s; }
.metric-box:nth-child(3) { animation-delay: 0.16s; }

.metric-box:hover {
    border-color: var(--border-hover);
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}

.metric-num {
    font-size: 1.4rem;
    font-weight: 800;
    background: linear-gradient(135deg, var(--accent-dark), var(--cyan));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.metric-lbl {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-top: 0.2rem;
}

/* Glass cards */
.g-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.4rem;
    margin-bottom: 0.85rem;
    position: relative;
    overflow: hidden;
    transition: all var(--transition);
    animation: fadeUp 0.45s ease-out both;
    box-shadow: var(--shadow-sm);
}

.g-card:hover {
    border-color: var(--border-hover);
    box-shadow: var(--shadow-md);
    transform: translateY(-2px);
}

/* Gradient top bar on hover */
.g-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 3px;
    background: var(--accent-gradient);
    opacity: 0;
    transition: opacity var(--transition);
}
.g-card:hover::after { opacity: 1; }

.g-card-head {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 0.85rem;
}

.g-card-icon {
    width: 34px; height: 34px;
    border-radius: var(--radius-sm);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.95rem;
    flex-shrink: 0;
    transition: transform var(--transition-spring);
}

.g-card:hover .g-card-icon { transform: scale(1.12) rotate(-4deg); }

.g-card-icon.purple { background: rgba(139,92,246,0.1); color: #7c3aed; }
.g-card-icon.green  { background: var(--green-soft); color: #059669; }
.g-card-icon.blue   { background: var(--blue-soft); color: #2563eb; }
.g-card-icon.amber  { background: var(--amber-soft); color: #d97706; }

.g-card-label {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-secondary);
}

.g-card-body {
    font-size: 0.88rem;
    line-height: 1.8;
    color: var(--text-secondary);
}

/* Transcript */
.transcript-box {
    background: #f8fafc;
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 1.1rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    line-height: 1.85;
    max-height: 350px;
    overflow-y: auto;
    color: var(--text-secondary);
    white-space: pre-wrap;
    word-break: break-word;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
}

/* Section divider */
.sec-head {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin: 1.5rem 0 0.85rem;
    animation: fadeUp 0.4s ease-out;
}

.sec-title {
    font-size: 1rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.01em;
    white-space: nowrap;
}

.sec-line {
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, var(--border), transparent);
}

/* ══════════════════════════════════════════════════════════
   CHAT
   ══════════════════════════════════════════════════════════ */
.chat-area {
    background: #f8fafc;
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.2rem;
    max-height: 420px;
    overflow-y: auto;
    margin-bottom: 0.75rem;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
}

.chat-msg {
    display: flex;
    gap: 0.7rem;
    margin-bottom: 1rem;
    animation: fadeUp 0.3s ease-out;
}

.chat-avatar {
    width: 30px; height: 30px;
    border-radius: var(--radius-sm);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.85rem;
    flex-shrink: 0;
    margin-top: 2px;
}

.chat-avatar.user { background: var(--accent-gradient); color: white; }
.chat-avatar.bot  { background: var(--green-soft); color: #059669; }

.chat-content {
    flex: 1;
    min-width: 0;
}

.chat-name {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 0.25rem;
}

.chat-name.user { color: var(--accent-dark); }
.chat-name.bot  { color: #059669; }

.chat-text {
    font-size: 0.88rem;
    line-height: 1.7;
    color: var(--text-secondary);
    padding: 0.6rem 0.9rem;
    border-radius: var(--radius-md);
    max-width: 90%;
    box-shadow: var(--shadow-sm);
}

.chat-text.user {
    background: var(--bg-card);
    border: 1px solid rgba(99,102,241,0.2);
}

.chat-text.bot {
    background: var(--bg-card);
    border: 1px solid var(--border);
}

.chat-empty {
    text-align: center;
    padding: 2.5rem 1.5rem;
}

.chat-empty-icon {
    font-size: 2.2rem;
    margin-bottom: 0.5rem;
    opacity: 0.4;
}

.chat-empty-text {
    color: var(--text-muted);
    font-size: 0.88rem;
    max-width: 300px;
    margin: 0 auto;
    line-height: 1.6;
}

/* ══════════════════════════════════════════════════════════
   STREAMLIT OVERRIDES
   ══════════════════════════════════════════════════════════ */
.stTextInput > div > div > input,
.stSelectbox > div > div {
    background: var(--bg-input) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
    transition: all var(--transition) !important;
    box-shadow: var(--shadow-sm) !important;
}

.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
    background: var(--bg-input-focus) !important;
}

.stTextInput > div > div > input::placeholder {
    color: #94a3b8 !important;
}

/* Button */
.stButton > button {
    background: var(--accent-gradient) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 0.6rem 1.4rem !important;
    transition: all var(--transition) !important;
    box-shadow: 0 4px 14px rgba(99,102,241,0.25) !important;
    position: relative !important;
    overflow: hidden !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(99,102,241,0.35) !important;
}

.stButton > button:active {
    transform: translateY(0) !important;
}

/* Expander */
.streamlit-expanderHeader {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
    font-weight: 600 !important;
}

/* Progress */
.stProgress > div > div > div { background: var(--accent-gradient) !important; border-radius: 100px !important; }

/* Labels */
label { color: var(--text-secondary) !important; font-size: 0.8rem !important; font-weight: 600 !important; }
[data-testid="stMarkdownContainer"] p { color: var(--text-secondary) !important; }

/* Divider */
hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, var(--border), transparent) !important;
    margin: 1.75rem 0 !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.2); border-radius: 100px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }

h1, h2, h3, h4, h5, h6 {
    color: var(--text-primary) !important;
    letter-spacing: -0.02em;
}

@media (max-width: 768px) {
    .metric-strip { grid-template-columns: 1fr; }
    .flow-container { flex-direction: column; }
    .flow-arrow { transform: rotate(90deg); }
}

/* Modern segmented control tabs */
div[data-baseweb="tab-list"] {
    gap: 8px !important;
    justify-content: center !important;
    background-color: #f1f5f9 !important;
    padding: 5px !important;
    border-radius: 12px !important;
    border: 1px solid #e2e8f0 !important;
    max-width: 280px !important;
    margin: 1.5rem auto 1rem !important;
}
div[data-baseweb="tab"] {
    background-color: transparent !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 6px 18px !important;
    color: #64748b !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    transition: all 0.2s ease !important;
}
div[data-baseweb="tab"][aria-selected="true"] {
    background-color: #ffffff !important;
    color: #6366f1 !important;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.1) !important;
}
div[data-baseweb="tab-border-line"] {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

# ─── Session State ───────────────────────────────────────────────────────────────
for key, default in {
    "result": None,
    "chat_history": [],
    "processing": False,
    "pipeline_done": False,
    "pipeline_steps": {},
    "analysis_history": [],  # Store previous analyses
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─── Helpers ────────────────────────────────────────────────────────────────────
def count_words(text: str) -> int:
    return len(text.split()) if text else 0

def save_uploaded_media(uploaded_file) -> str:
    """Persist an uploaded media file temporarily so pydub/ffmpeg can read it."""
    os.makedirs("downloads", exist_ok=True)
    _, ext = os.path.splitext(uploaded_file.name or "")
    safe_ext = re.sub(r"[^a-zA-Z0-9.]", "", ext) or ".mp4"
    with tempfile.NamedTemporaryFile(delete=False, suffix=safe_ext, dir="downloads") as tmp:
        tmp.write(uploaded_file.getbuffer())
        return tmp.name

def render_loading(percent, step_icon, step_text, placeholder):
    """Render a smooth animated loading bar with percentage and step label."""
    placeholder.markdown(f"""
    <div class="loading-container">
        <div class="loading-icon">🧠</div>
        <div class="loading-title">Analyzing Your Transcript</div>
        <div class="loading-percent">{percent}%</div>
        <div class="loading-bar-track">
            <div class="loading-bar-fill" style="width: {percent}%;"></div>
        </div>
        <div class="loading-step">
            <span class="loading-step-icon">{step_icon}</span>
            {step_text}
            <span class="loading-dots"><span></span><span></span><span></span></span>
        </div>
        <div class="loading-wait">Please wait — this usually takes 15-30 seconds</div>
    </div>
    """, unsafe_allow_html=True)

# ─── Sidebar — Compact Single-Screen Design ─────────────────────────────────────
with st.sidebar:
    # ── Brand (compact) ──
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;padding:4px 0 10px;">
        <div style="background:linear-gradient(135deg,#6366f1,#8b5cf6);width:34px;height:34px;
            border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0;">🎬</div>
        <div>
            <div style="font-weight:800;font-size:1rem;color:#1e1b4b;line-height:1.1;">VideoAI</div>
            <div style="font-size:0.62rem;color:#6366f1;font-weight:600;letter-spacing:0.06em;text-transform:uppercase;">Meeting Intelligence</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Model + Language in one compact row ──
    mc, lc = st.columns(2)
    with mc:
        selected_model = st.selectbox(
            "🤖 Model",
            list(MODEL_OPTIONS.keys()),
            index=0,
            key="model_selector_top",
            help="AI model used for analysis and chat."
        )
    with lc:
        language = st.selectbox(
            "🌐 Language",
            ["English", "Kannada", "Telugu", "Hindi"],
            index=0,
        )

    badge = get_provider_badge(selected_model)
    st.markdown(
        f"<div style='font-size:0.68rem;color:#6366f1;margin:-6px 0 8px;'>Active: {badge}</div>",
        unsafe_allow_html=True
    )

    # ── ⚡ Analyse Video — prominent CTA ──
    run_btn = st.button("⚡  Analyse Video", use_container_width=True, key="run_btn_top")

    st.markdown("<div style='margin:10px 0 6px;border-top:1px solid #e2e8f0;'></div>", unsafe_allow_html=True)

    # ── Input source — tabbed so all 3 fit without scrolling ──
    st.markdown("<div style='font-size:0.72rem;font-weight:700;color:#64748b;letter-spacing:0.06em;text-transform:uppercase;margin-bottom:6px;'>📥 Input Source</div>", unsafe_allow_html=True)
    tab_yt, tab_up, tab_paste = st.tabs(["🎥 YouTube", "📁 Upload", "📝 Paste"])

    with tab_yt:
        source = st.text_input(
            "YouTube URL",
            placeholder="https://youtube.com/watch?v=...",
            label_visibility="collapsed",
            help="Paste a YouTube link — captions fetched automatically.",
        )

    with tab_up:
        uploaded_media = st.file_uploader(
            "Audio/Video file",
            type=["mp3", "mp4", "m4a", "wav", "webm", "mov", "aac", "ogg"],
            label_visibility="collapsed",
            help="Upload a file — Groq Whisper will transcribe it.",
        )

    with tab_paste:
        pasted_transcript = st.text_area(
            "Paste transcript",
            placeholder="Paste captions or transcript here...",
            height=80,
            label_visibility="collapsed",
        )

    st.markdown("<div style='margin:8px 0 4px;border-top:1px solid #e2e8f0;'></div>", unsafe_allow_html=True)

    # ── API Key status — compact inline dots ──
    keys_info = [
        ("GOOGLE_API_KEY", "Gemini"),
        ("GROQ_API_KEY",   "Groq"),
    ]
    dots_html = "<div style='display:flex;gap:12px;align-items:center;padding:4px 0;'>"
    for env_var, label in keys_info:
        key = os.getenv(env_var, "").strip()
        ok = bool(key and len(key) > 10)
        color = "#10b981" if ok else "#ef4444"
        dots_html += (
            f"<div style='display:flex;align-items:center;gap:4px;'>"
            f"<div style='width:7px;height:7px;border-radius:50%;background:{color};'></div>"
            f"<span style='font-size:0.7rem;color:#64748b;'>{label}</span>"
            f"</div>"
        )
    dots_html += "</div>"
    st.markdown(dots_html, unsafe_allow_html=True)

    # ── Pipeline status (shown only after analysis) ──
    if st.session_state.pipeline_done:
        st.markdown("<div style='margin:6px 0 4px;border-top:1px solid #e2e8f0;'></div>", unsafe_allow_html=True)
        steps_html = '<div style="display:flex;flex-wrap:wrap;gap:4px;">'
        for key, icon, label in [
            ("audio","🔊","Audio"),("transcript","📝","Transcript"),
            ("title","🏷️","Title"),("summary","📋","Summary"),
            ("extract","🔍","Insights"),("rag","🧠","RAG"),
        ]:
            s = st.session_state.pipeline_steps.get(key, "pending")
            bg = "#d1fae5" if s=="done" else "#fef3c7" if s=="active" else "#f1f5f9"
            tc = "#065f46" if s=="done" else "#92400e" if s=="active" else "#64748b"
            steps_html += f'<div style="background:{bg};color:{tc};font-size:0.65rem;font-weight:600;padding:2px 7px;border-radius:100px;">{icon} {label}</div>'
        steps_html += '</div>'
        st.markdown(steps_html, unsafe_allow_html=True)

    # ── Previous analyses ──
    if st.session_state.analysis_history:
        st.markdown("<div style='margin:8px 0 4px;border-top:1px solid #e2e8f0;'></div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:0.68rem;font-weight:700;color:#64748b;letter-spacing:0.06em;text-transform:uppercase;margin-bottom:4px;'>📂 Recent</div>", unsafe_allow_html=True)
        for i, item in enumerate(reversed(st.session_state.analysis_history[:3])):
            st.markdown(
                f"<div style='font-size:0.75rem;color:#334155;padding:3px 0;white-space:nowrap;"
                f"overflow:hidden;text-overflow:ellipsis;'>🎬 {item['title']}</div>",
                unsafe_allow_html=True
            )

# ─── Main Content — Centered ────────────────────────────────────────────────────
st.markdown('<div class="main-wrapper">', unsafe_allow_html=True)

# ─── Session state init ──────────────────────────────────────────────────────────
if "ai_chat_history" not in st.session_state:
    st.session_state.ai_chat_history = []

# Persist model across reruns
st.session_state["active_model"] = selected_model

# ─── Two main tabs ───────────────────────────────────────────────────────────────
tab_video, tab_chat = st.tabs(["🎬  Video AI", "💬  AI Chat"])

# ══════════════════════════════════════════════════════════════════════════════════
# TAB 1 — VIDEO AI
# ══════════════════════════════════════════════════════════════════════════════════
with tab_video:
    # Hero
    if not st.session_state.pipeline_done:
        st.markdown("""
        <div class="hero">
            <div class="hero-icon-wrap">🎬</div>
            <h1>What video do you want<br><span class="hero-gradient-text">to understand today?</span></h1>
            <div class="hero-sub">
                Drop a YouTube URL, upload a media file, or paste a transcript — AI extracts summaries, action items, decisions and lets you chat with the content.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # How it works
        st.markdown("""
        <div style="display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap;margin:0 0 24px;">
            <div style="background:#f0f4ff;border:1px solid #c7d2fe;border-radius:12px;padding:10px 16px;text-align:center;min-width:100px;">
                <div style="font-size:1.4rem;">🎥</div>
                <div style="font-size:0.72rem;font-weight:700;color:#4338ca;margin-top:4px;">Paste URL</div>
            </div>
            <div style="color:#94a3b8;font-size:1rem;">→</div>
            <div style="background:#f0f4ff;border:1px solid #c7d2fe;border-radius:12px;padding:10px 16px;text-align:center;min-width:100px;">
                <div style="font-size:1.4rem;">📝</div>
                <div style="font-size:0.72rem;font-weight:700;color:#4338ca;margin-top:4px;">Transcribe</div>
            </div>
            <div style="color:#94a3b8;font-size:1rem;">→</div>
            <div style="background:#f0f4ff;border:1px solid #c7d2fe;border-radius:12px;padding:10px 16px;text-align:center;min-width:100px;">
                <div style="font-size:1.4rem;">🧠</div>
                <div style="font-size:0.72rem;font-weight:700;color:#4338ca;margin-top:4px;">Analyse</div>
            </div>
            <div style="color:#94a3b8;font-size:1rem;">→</div>
            <div style="background:#f0f4ff;border:1px solid #c7d2fe;border-radius:12px;padding:10px 16px;text-align:center;min-width:100px;">
                <div style="font-size:1.4rem;">💬</div>
                <div style="font-size:0.72rem;font-weight:700;color:#4338ca;margin-top:4px;">Chat</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════════
# TAB 2 — AI CHAT (Separate & Persistent general assistant)
# ══════════════════════════════════════════════════════════════════════════════════
with tab_chat:
    # Header with floating clear button
    hc1, hc2 = st.columns([5, 1.2])
    with hc1:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
            <div style="font-size:24px;">💬</div>
            <div>
                <div style="font-size:1.05rem;font-weight:800;color:#1e1b4b;">AI Chat Assistant</div>
                <div style="font-size:0.75rem;color:#6366f1;font-weight:500;">Ask general questions to your selected model</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with hc2:
        # Floating clear button at top right
        if st.session_state.ai_chat_history:
            if st.button("🗑️ Clear Chat", key="ai_clear_chat", use_container_width=True, type="secondary"):
                st.session_state.ai_chat_history = []
                st.rerun()

    # ── Scrollable Chat History Container ──
    chat_area = st.container(height=480, border=False)
    with chat_area:
        if not st.session_state.ai_chat_history:
            st.markdown("""
            <div style="text-align:center;padding:80px 20px;">
                <div style="font-size:2.5rem;margin-bottom:12px;">🤖</div>
                <div style="font-size:1rem;font-weight:700;color:#1e1b4b;margin-bottom:6px;">Start a conversation</div>
                <div style="font-size:0.85rem;color:#64748b;">Ask me anything — I'll give you a clear, structured answer.</div>
                <div style="display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin-top:20px;">
                    <div style="background:#f0f4ff;border:1px solid #c7d2fe;border-radius:100px;padding:6px 14px;font-size:0.78rem;color:#4338ca;">💡 Explain machine learning</div>
                    <div style="background:#f0f4ff;border:1px solid #c7d2fe;border-radius:100px;padding:6px 14px;font-size:0.78rem;color:#4338ca;">📊 What is RAG?</div>
                    <div style="background:#f0f4ff;border:1px solid #c7d2fe;border-radius:100px;padding:6px 14px;font-size:0.78rem;color:#4338ca;">🚀 How does LangChain work?</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in st.session_state.ai_chat_history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"], unsafe_allow_html=True)

    # ── Native bottom-pinned Chat Input ──
    # st.chat_input places the input box beautifully at the bottom of the page
    ai_question = st.chat_input("Type your message here...", key="ai_chat_input_val")
    
    if ai_question and ai_question.strip():
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        from core.llm_router import get_llm, DEFAULT_MODEL
        import re as _re

        user_q = ai_question.strip()
        st.session_state.ai_chat_history.append({"role": "user", "content": user_q})
        active_model = st.session_state.get("active_model", DEFAULT_MODEL)

        with st.spinner("Thinking..."):
            try:
                llm = get_llm(active_model)
                prompt = ChatPromptTemplate.from_messages([
                    ("system",
                     "You are a helpful, knowledgeable AI assistant. "
                     "Always respond in a clear, structured way:\n"
                     "- Start with a direct concise answer\n"
                     "- Use bullet points or numbered lists for multi-part answers\n"
                     "- Use **bold** to highlight key terms\n"
                     "- Keep paragraphs short and scannable\n"
                     "Be friendly, precise and professional."),
                    ("human", "{question}"),
                ])
                chain = prompt | llm | StrOutputParser()
                answer = chain.invoke({"question": user_q})
                
                # Format response nicely
                answer_html = _re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", answer)
                answer_html = answer_html.replace("\n", "<br>")
                st.session_state.ai_chat_history.append({"role": "assistant", "content": answer_html})
            except Exception as e:
                st.session_state.ai_chat_history.append({
                    "role": "assistant",
                    "content": f"⚠️ {str(e)}"
                })
        st.rerun()

with tab_video:
    # ─── Pipeline ───────────────────────────────────────────────────────────────────
    if run_btn:
        pasted_transcript = (pasted_transcript or "").strip()
        if not source.strip() and uploaded_media is None and not pasted_transcript:
            st.error("Please enter a YouTube URL, upload a media file, or paste a transcript.")
        else:
            groq_key = os.getenv("GROQ_API_KEY", "").strip()
            if not groq_key or groq_key == "GROQ_API_KEY" or len(groq_key) < 10:
                st.error(
                    "🔑 **GROQ_API_KEY is missing or invalid.** "
                    "Please set your Groq API key in the platform's environment/secrets, "
                    "or in the local `.env` file. Get a free key at https://console.groq.com"
                )
            else:
                st.session_state.pipeline_done = False
                st.session_state.result = None
                st.session_state.chat_history = []
                st.session_state.pipeline_steps = {}

                progress_placeholder = st.empty()

                def update_step(key, state):
                    st.session_state.pipeline_steps[key] = state

                try:
                    source_to_process = source.strip()
                    is_youtube = source_to_process.startswith("http") and ("youtu" in source_to_process)
                    transcript = pasted_transcript or None

                    if transcript:
                        # User pasted a transcript directly
                        render_loading(20, "📝", "Using pasted transcript", progress_placeholder)
                        update_step("audio", "done")
                        update_step("transcript", "done")

                    elif uploaded_media is not None:
                        # User uploaded an audio/video file → Groq Whisper
                        render_loading(5, "🔊", "Processing uploaded file", progress_placeholder)
                        update_step("audio", "active")
                        saved_path = save_uploaded_media(uploaded_media)
                        chunks = process_uploaded_file(saved_path)
                        update_step("audio", "done")

                        render_loading(20, "📝", "Transcribing audio with Groq Whisper", progress_placeholder)
                        update_step("transcript", "active")
                        transcript = transcribe_all(chunks, language)
                        update_step("transcript", "done")

                    elif is_youtube:
                        # YouTube URL → try caption strategies 1-3 (no audio download)
                        render_loading(5, "📝", "Fetching YouTube captions", progress_placeholder)
                        update_step("audio", "active")
                        update_step("transcript", "active")
                        transcript = get_youtube_transcript(source_to_process)

                        if not transcript:
                            render_loading(12, "📝", "Extracting subtitles from video metadata", progress_placeholder)
                            transcript = get_subtitles_via_extract_info(source_to_process)

                        if not transcript:
                            render_loading(18, "📝", "Trying subtitle file download", progress_placeholder)
                            transcript = get_youtube_subtitles_ytdlp(source_to_process)

                        if transcript:
                            update_step("audio", "done")
                            update_step("transcript", "done")
                        else:
                            raise RuntimeError(
                                "Could not fetch captions for this video. "
                                "This video may not have captions, or YouTube is blocking this server. "
                                "Please upload the audio/video file or paste the transcript instead."
                            )
                    else:
                        st.error("Please enter a valid YouTube URL, upload a file, or paste a transcript.")
                        st.stop()

                    # Step: Title generation
                    render_loading(40, "🏷️", "Generating title", progress_placeholder)
                    update_step("title", "active")
                    title = generate_title(transcript, language, selected_model)
                    update_step("title", "done")

                    # Step: Summarization
                    render_loading(55, "📋", "Creating intelligent summary", progress_placeholder)
                    update_step("summary", "active")
                    summary = summarize(transcript, language, selected_model)
                    update_step("summary", "done")

                    # Step: Insight extraction
                    render_loading(70, "🔍", "Extracting insights & action items", progress_placeholder)
                    update_step("extract", "active")
                    insights = extract_all_insights(transcript, language, selected_model)
                    action_items = insights["action_items"]
                    decisions    = insights["key_decisions"]
                    questions    = insights["open_questions"]
                    update_step("extract", "done")

                    # Step: RAG engine
                    render_loading(90, "🧠", "Building knowledge engine", progress_placeholder)
                    update_step("rag", "active")
                    rag_chain = build_rag_chain(transcript, language, selected_model)
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

                    st.session_state.analysis_history.append({
                        "title": title[:50],
                        "words": count_words(transcript),
                    })

                    render_loading(100, "✅", "Analysis complete!", progress_placeholder)
                    time.sleep(0.8)
                    progress_placeholder.empty()
                    st.rerun()

                except Exception as e:
                    for k in ["audio","transcript","title","summary","extract","rag"]:
                        if st.session_state.pipeline_steps.get(k) == "active":
                            st.session_state.pipeline_steps[k] = "pending"

                    error_msg = str(e)
                    if "rate_limit" in error_msg or "429" in error_msg or "tokens per minute" in error_msg.lower():
                        progress_placeholder.error(
                            "⏳ **Rate limit reached.** Please wait 1-2 minutes and try again, or try a shorter video."
                        )
                    elif "413" in error_msg or "Request too large" in error_msg:
                        progress_placeholder.error(
                            "📏 **File too large for free tier.** Please try a shorter video (under 5 minutes)."
                        )
                    elif ("GROQ_API_KEY" in error_msg or "api_key" in error_msg.lower()) and "yt-dlp" not in error_msg.lower():
                        progress_placeholder.error(
                            "🔑 **GROQ_API_KEY is missing or invalid.** "
                            "Set it in your platform's environment/secrets, or in the `.env` file."
                        )
                    elif "Could not fetch" in error_msg or "captions" in error_msg.lower():
                        progress_placeholder.error(
                            f"📝 **Transcript Error:** {e}\n\n"
                            "Try a video with captions enabled, upload the media file directly, or paste the transcript."
                        )
                    else:
                        progress_placeholder.error(f"❌ Error: {e}")

    # ─── Results ────────────────────────────────────────────────────────────────────
    if st.session_state.result:
        r = st.session_state.result

        st.markdown("---")

        # Title Banner
        st.markdown(f"""
        <div class="res-title">
            <div class="res-title-icon">📌</div>
            <div>
                <div class="res-title-text">{r['title']}</div>
                <div class="res-title-sub">AI-generated meeting title</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Metrics
        wc = count_words(r['transcript'])
        dur = max(1, wc // 150)
        sents = len([s for s in r['transcript'].split('.') if s.strip()])
        st.markdown(f"""
        <div class="metric-strip">
            <div class="metric-box">
                <div class="metric-num">{wc:,}</div>
                <div class="metric-lbl">Words</div>
            </div>
            <div class="metric-box">
                <div class="metric-num">~{dur} min</div>
                <div class="metric-lbl">Duration</div>
            </div>
            <div class="metric-box">
                <div class="metric-num">{sents}</div>
                <div class="metric-lbl">Sentences</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Summary + Chat
        col1, col2 = st.columns([1.1, 1], gap="large")

        with col1:
            st.markdown(f"""
            <div class="g-card">
                <div class="g-card-head">
                    <div class="g-card-icon purple">📋</div>
                    <div class="g-card-label">Summary</div>
                </div>
                <div class="g-card-body">{r['summary']}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
            with st.expander("📝 Full Transcript", expanded=False):
                st.markdown(f'<div class="transcript-box">{r["transcript"]}</div>', unsafe_allow_html=True)

        with col2:
            # ─── Chat ────────────────────────────────────────────
            st.markdown("""
            <div class="sec-head" style="margin-top: 0;">
                <span class="sec-title">💬 Chat with Your Meeting</span>
                <div class="sec-line"></div>
            </div>
            """, unsafe_allow_html=True)

            if st.session_state.chat_history:
                chat_html = '<div class="chat-area" style="max-height: 450px;">'
                for msg in st.session_state.chat_history:
                    if msg["role"] == "user":
                        chat_html += f"""
                        <div class="chat-msg">
                            <div class="chat-avatar user">👤</div>
                            <div class="chat-content">
                                <div class="chat-name user">You</div>
                                <div class="chat-text user">{msg['content']}</div>
                            </div>
                        </div>"""
                    else:
                        chat_html += f"""
                        <div class="chat-msg">
                            <div class="chat-avatar bot">🤖</div>
                            <div class="chat-content">
                                <div class="chat-name bot">VideoAI</div>
                                <div class="chat-text bot">{msg['content']}</div>
                            </div>
                        </div>"""
                chat_html += '</div>'
                st.markdown(chat_html, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="g-card chat-empty" style="margin-bottom: 1rem;">
                    <div class="chat-empty-icon">💬</div>
                    <div class="chat-empty-text">
                        Ask anything about your meeting — decisions, action items, or specific topics.
                    </div>
                </div>
                """, unsafe_allow_html=True)

            cc1, cc2 = st.columns([4, 1], gap="small")
            with cc1:
                user_input = st.text_input("Ask", placeholder="What were the main takeaways?", label_visibility="collapsed")
            with cc2:
                send_btn = st.button("Send →", use_container_width=True)

            if send_btn and user_input.strip():
                with st.spinner("🤔 Thinking…"):
                    answer = ask_question(r["rag_chain"], user_input.strip())
                st.session_state.chat_history.append({"role": "user", "content": user_input.strip()})
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
                st.rerun()

            if st.session_state.chat_history:
                if st.button("🗑️  Clear Chat", type="secondary"):
                    st.session_state.chat_history = []
                    st.rerun()

        # ─── Insights (MOVED BELOW Chat) ────────────────────────────────────────────
        st.markdown("""
        <div class="sec-head">
            <span class="sec-title">🔍 Extracted Insights</span>
            <div class="sec-line"></div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3, gap="medium")

        with c1:
            st.markdown(f"""
            <div class="g-card">
                <div class="g-card-head">
                    <div class="g-card-icon green">✅</div>
                    <div class="g-card-label">Action Items</div>
                </div>
                <div class="g-card-body">{r['action_items']}</div>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown(f"""
            <div class="g-card">
                <div class="g-card-head">
                    <div class="g-card-icon blue">🔑</div>
                    <div class="g-card-label">Key Decisions</div>
                </div>
                <div class="g-card-body">{r['key_decisions']}</div>
            </div>
            """, unsafe_allow_html=True)

        with c3:
            st.markdown(f"""
            <div class="g-card">
                <div class="g-card-head">
                    <div class="g-card-icon amber">❓</div>
                    <div class="g-card-label">Open Questions</div>
                </div>
                <div class="g-card-body">{r['open_questions']}</div>
            </div>
            """, unsafe_allow_html=True)

    else:
        # Empty state — How it works flow
        st.markdown("""
        <div class="flow-container">
            <div class="flow-step">
                <div class="flow-step-icon purple">🔗</div>
                <div class="flow-step-label">Paste URL</div>
            </div>
            <span class="flow-arrow">→</span>
            <div class="flow-step">
                <div class="flow-step-icon blue">🎤</div>
                <div class="flow-step-label">Transcribe</div>
            </div>
            <span class="flow-arrow">→</span>
            <div class="flow-step">
                <div class="flow-step-icon green">🧠</div>
                <div class="flow-step-label">Analyse</div>
            </div>
            <span class="flow-arrow">→</span>
            <div class="flow-step">
                <div class="flow-step-icon cyan">💬</div>
                <div class="flow-step-label">Chat</div>
            </div>
        </div>

        <div class="cap-row">
            <div class="cap-chip">📝 Transcription</div>
            <div class="cap-chip">📋 Summary</div>
            <div class="cap-chip">✅ Action Items</div>
            <div class="cap-chip">🔑 Decisions</div>
            <div class="cap-chip">💬 AI Chat</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
