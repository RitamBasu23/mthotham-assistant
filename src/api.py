# src/api.py
from fastapi import FastAPI, Body, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from zoneinfo import ZoneInfo

from src.ingest import run_ingest
from src.rag_chain import answer
from src.data_paths import list_data_files
from src.config import settings  # <-- import to show model info in metadata


# -------------------------------------------------------------------
# FastAPI App Configuration
# -------------------------------------------------------------------
app = FastAPI(
    title=f"Mt Hotham Assistant API ({settings.llm_model_name})",
    description="Local RAG pipeline using TinyLlama and Chroma vectorstore. \
Supports ingestion of local CSV/JSON/TXT/MD files plus optional site crawl.",
    version="2.0.0",
)


# -------------------------------------------------------------------
# Data Models
# -------------------------------------------------------------------
class ChatRequest(BaseModel):
    message: str = Field(..., description="User query")
    intent: Optional[str] = Field(None, description="Optional intent override")


class IngestRequest(BaseModel):
    include_crawl: bool = Field(False, description="Also crawl official pages")
    crawl_depth: int = Field(1, description="Crawl depth for site crawling")
    extra_paths: Optional[List[str]] = Field(None, description="Extra files to ingest")


# -------------------------------------------------------------------
# Health Check
# -------------------------------------------------------------------
@app.get("/health")
def health():
    return {
        "ok": True,
        "service": "mthotham-assistant",
        "model": settings.llm_model_name,
        "embedding_model": settings.embedding_model_name,
        "time": datetime.now(ZoneInfo(settings.app_timezone)).isoformat(),
    }


# -------------------------------------------------------------------
# Ingest Endpoints
# -------------------------------------------------------------------
@app.post("/ingest")
def ingest_endpoint(req: IngestRequest):
    print(
        f"📥 Ingest request received. Crawl={req.include_crawl}, depth={req.crawl_depth}"
    )
    res = run_ingest(
        include_crawl=req.include_crawl,
        crawl_depth=req.crawl_depth,
        extra_paths=req.extra_paths,
    )
    return res


@app.get("/ingest/default-files")
def list_default_files():
    return {"scanned_files": list_data_files()}


# -------------------------------------------------------------------
# Chat Endpoints
# -------------------------------------------------------------------
@app.post("/chat")
def chat_endpoint(req: ChatRequest):
    print(f"💬 Chat request: {req.message[:80]}...")
    res = answer(req.message, intent=req.intent)
    # Attach model + timestamp for debugging convenience
    res["served_by"] = settings.llm_model_name
    res["timestamp"] = datetime.now(ZoneInfo(settings.app_timezone)).isoformat()
    return res


# -------------------------------------------------------------------
# Simple GET (for Postman quick tests)
# Example: /GetData?q=where can I buy ski passes?
# -------------------------------------------------------------------
@app.get("/GetData")
def get_data(
    q: str = Query(..., description="Your search query"),
    intent: Optional[str] = Query(None, description="Optional intent override"),
):
    print(f"🔎 GET request: {q[:80]}...")
    res = answer(q, intent=intent)
    res["served_by"] = settings.llm_model_name
    res["timestamp"] = datetime.now(ZoneInfo(settings.app_timezone)).isoformat()
    return res
