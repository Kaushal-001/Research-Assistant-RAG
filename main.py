# main.py
import os
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager
import traceback
import logging

# Import your modules (make sure these functions exist)
from src.ingest import ingest_documents, store_documents
from src.retrieve import retrieve_context
from src.summary import answer_from_sources
from src.arxiv_search import search_arxiv
from src.utils import extract_text_from_pdf  # your PDF text extractor

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("research-assistant")

ROOT = Path(__file__).resolve().parent

# ---------------------------
# FastAPI App (single declaration)
# ---------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: auto-ingest main data folder once. Shutdown: optional cleanup."""
    logger.info("🚀 FastAPI starting — auto-indexing data folder (once)...")
    try:
        result = ingest_documents()
        logger.info("✅ Auto-ingest complete: %s", result)
    except Exception as e:
        logger.exception("❌ Auto-ingest failed at startup: %s", e)
    yield
    logger.info("🛑 FastAPI shutting down...")

app = FastAPI(title="Research Assistant API", version="1.0", lifespan=lifespan)

# CORS for frontend support (React / Streamlit / anything)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Request Models
# ---------------------------

class QueryRequest(BaseModel):
    question: str
    k: Optional[int] = 10        # number of vector results to fetch (optional)

# ---------------------------
# ROUTES
# ---------------------------

@app.get("/")
def home():
    return {"status": "running", "message": "Research Assistant FastAPI backend online!"}


# --------- 1) Upload single PDF and ingest that file only ---------
@app.post("/upload-pdf")
async def upload_pdf(file: Optional[UploadFile] = File(None)):
    """
    Save uploaded PDF into data/uploaded_papers and ingest it immediately (only this file).
    Returns the file path and ingest result.
    """
    if file is None:
        return {"status": "no_file", "message": "No file uploaded."}

    save_dir = ROOT / "data" / "uploaded_papers"
    save_dir.mkdir(parents=True, exist_ok=True)
    file_path = save_dir / file.filename

    try:
        # Save file
        with open(file_path, "wb") as f:
            f.write(await file.read())

        logger.info("Saved uploaded file to %s", file_path)

        # Extract text and ingest only this document
        text = extract_text_from_pdf(str(file_path))
        if not text or len(text.strip()) < 50:
            msg = "Extracted text is empty or too small; skipping ingestion."
            logger.warning("%s for file %s", msg, file_path)
            return {"status": "skipped", "message": msg, "filepath": str(file_path)}

        ingest_result = store_documents(str(file_path), text)
        logger.info("Ingest result for %s: %s", file_path, ingest_result)

        return {"status": "success", "filepath": str(file_path), "ingest": ingest_result}

    except Exception as e:
        logger.exception("Failed to upload/ingest file: %s", e)
        return {"status": "error", "message": str(e), "trace": traceback.format_exc()}


# --------- 2) Ingest all PDFs (manual trigger) ---------
@app.post("/ingest")
def index_all_data():
    """
    Manually trigger a full re-index of configured data directories.
    Use carefully — can be time-consuming.
    """
    try:
        result = ingest_documents()
        return {"status": "completed", "result": result}
    except Exception as e:
        logger.exception("Full ingest failed: %s", e)
        return {"status": "error", "message": str(e), "trace": traceback.format_exc()}


# --------- 3) Chat / Answer Query ---------
@app.post("/chat")
def chat(request: QueryRequest):
    """
    Query the system:
    - retrieve_context(query, k=request.k) returns the vector DB chunks (string or list)
    - search_arxiv(query) returns a list of arXiv paper dicts
    - answer_from_sources(query, context, papers) returns the final LLM answer
    """
    query = request.question
    k = request.k or 10

    try:
        # Retrieve context from vector DB (do not re-ingest here)
        context = retrieve_context(query, k=k)

        # Get arXiv papers as fallback / supplement
        papers = search_arxiv(query, max_results=6)

        # Generate grounded answer using both sources (internal logic decides priority)
        answer = answer_from_sources(query, context, papers)

        return {
            "status": "ok",
            "answer": answer,
            "db_chunks": context,
            "papers": papers,
        }

    except Exception as e:
        logger.exception("Chat failed for query '%s': %s", query, e)
        return {"status": "error", "message": str(e), "trace": traceback.format_exc()}
