from fastapi import FastAPI, Body, Query
from pydantic import BaseModel, Field
from typing import List, Optional

from src.ingest import run_ingest
from src.rag_chain import answer
from src.data_paths import list_data_files


app = FastAPI(
    title="Mt Hotham Assistant API",
    description="LangChain RAG over local CSV/JSON/TXT/MD (+ optional crawl). Weather/search tools are optional.",
    version="1.0.0",
)

# ---------- Models ----------

class ChatRequest(BaseModel):
    message: str = Field(..., description="User query")
    intent: Optional[str] = Field(None, description="Optional intent override")

class IngestRequest(BaseModel):
    include_crawl: bool = Field(False, description="Also crawl official pages")
    crawl_depth: int = Field(1, description="Crawl depth")
    extra_paths: Optional[List[str]] = Field(None, description="Extra files to ingest")

# ---------- Health ----------

@app.get("/health")
def health():
    return {"ok": True, "service": "mthotham-assistant"}

# ---------- Ingest endpoints ----------

@app.post("/ingest")
def ingest_endpoint(req: IngestRequest):
    res = run_ingest(include_crawl=req.include_crawl, crawl_depth=req.crawl_depth, extra_paths=req.extra_paths)
    return res

@app.get("/ingest/default-files")
def list_default_files():
    return {"scanned_files": list_data_files()}

# ---------- Chat ----------

@app.post("/chat")
def chat_endpoint(req: ChatRequest):
    return answer(req.message, intent=req.intent)

# ---------- Simple GET for Postman quick test ----------
# e.g. GET /GetData?q=where can I buy ski passes?
@app.get("/GetData")
def get_data(q: str = Query(..., description="Your search query"),
             intent: Optional[str] = Query(None, description="Optional intent override")):
    return answer(q, intent=intent)
