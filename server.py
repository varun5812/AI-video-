"""
server.py
─────────
FastAPI Backend for the Premium VideoAI & Chat Platform.
Exposes endpoints for chat, video analysis, credentials status checking, and serves the static React build.
"""
import os
import sys
import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Add project root to python path for core/utils imports
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv(override=True)

from core.llm_router import get_llm, DEFAULT_MODEL
from core.summarizer import summarize, generate_title
from core.extractor import extract_all_insights
from core.rag_engine import build_rag_chain, ask_question
from utils.audio_processor import (
    get_youtube_transcript,
    get_subtitles_via_extract_info,
    get_youtube_subtitles_ytdlp,
    process_uploaded_file,
)

app = FastAPI(title="VideoAI Platform Backend", version="1.0.0")

# Enable CORS for frontend Vite development server (port 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request Models ────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    question: str
    model: str = DEFAULT_MODEL


class VideoChatRequest(BaseModel):
    transcript: str
    question: str
    model: str = DEFAULT_MODEL


# ── API Endpoints ─────────────────────────────────────────────────────────────
@app.get("/api/status")
def get_status():
    """Verify active API key presence for credentials status pills."""
    google_key = os.getenv("GOOGLE_API_KEY", "").strip()
    groq_key = os.getenv("GROQ_API_KEY", "").strip()
    return {
        "google_ok": bool(google_key and len(google_key) > 10),
        "groq_ok": bool(groq_key and len(groq_key) > 10),
    }


@app.post("/api/chat")
async def chat_ai(payload: ChatRequest):
    """Handle general AI Assistant conversation."""
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    
    try:
        llm = get_llm(payload.model)
        # Use simple structured prompt
        prompt = f"You are a helpful, knowledgeable AI assistant. Please respond to the user query in a clear, structured way (using bold text and bullet points where appropriate):\n\nQuery: {payload.question}"
        response = llm.invoke(prompt)
        # Convert response content to string format
        answer = response.content if hasattr(response, "content") else str(response)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/video/analyze")
async def analyze_video(
    source: str = Form(""),
    language: str = Form("English"),
    model: str = Form(DEFAULT_MODEL),
    file: UploadFile = File(None)
):
    """Run full Video Analysis Pipeline (fetches transcript, title, summary, insights)."""
    transcript = ""
    filename = ""
    
    try:
        # Scenario A: User uploaded local media file
        if file is not None:
            filename = file.filename
            # Save upload to a temp path
            temp_path = os.path.join("downloads", filename)
            os.makedirs("downloads", exist_ok=True)
            with open(temp_path, "wb") as f:
                f.write(await file.read())
            
            # Process & Transcribe
            chunks = process_uploaded_file(temp_path)
            from core.transcriber import transcribe_all
            transcript = transcribe_all(chunks, language)
            
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)

        # Scenario B: User pasted a YouTube URL
        elif source.strip():
            filename = f"YouTube Video ({source})"
            # Try fetching captions using the 3 fallback levels
            transcript = get_youtube_transcript(source)
            if not transcript:
                transcript = get_subtitles_via_extract_info(source)
            if not transcript:
                transcript = get_youtube_subtitles_ytdlp(source)
            
            if not transcript:
                raise ValueError("Could not extract captions/subtitles for this YouTube video.")
        else:
            raise HTTPException(status_code=400, detail="Please upload a file or submit a YouTube URL.")

        # Pipeline Operations
        title = generate_title(transcript, language, model)
        sum_short = summarize(transcript, language, model) # standard summarization
        insights = extract_all_insights(transcript, language, model)
        
        # Prepare structured dashboard data
        return {
            "title": title,
            "filename": filename,
            "transcript": transcript,
            "summary_short": sum_short,
            "action_items": insights.get("action_items", ""),
            "key_decisions": insights.get("key_decisions", ""),
            "open_questions": insights.get("open_questions", ""),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/video/chat")
async def chat_video(payload: VideoChatRequest):
    """RAG-based chat with a video's transcript."""
    if not payload.transcript.strip() or not payload.question.strip():
        raise HTTPException(status_code=400, detail="Transcript and question are required.")
    
    try:
        rag_chain = build_rag_chain(payload.transcript, "English", payload.model)
        answer = ask_question(rag_chain, payload.question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Serve Built React Frontend Static Files ────────────────────────────────────
frontend_dist = os.path.join(PROJECT_ROOT, "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")

if __name__ == "__main__":
    # Start uvicorn server on port 8000
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
