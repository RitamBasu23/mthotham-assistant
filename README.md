# Mt Hotham LangChain RAG Chatbot (Postman API Ready)

A local **RAG chatbot** for Mt Hotham content.  
It ingests your CSV/JSON/TXT/MD files from `data_files/`, stores them in a **Chroma** vector DB, and serves answers via **FastAPI**.

## ✨ Features
- Drag-and-drop files into `data_files/` (auto-scanned: `.csv`, `.json`, `.txt`, `.md`)
- Vector DB: Chroma (auto-created at `data/chroma/`)
- Endpoints:
  - `POST /ingest` — build/rebuild vector DB
  - `POST /chat` — ask a question (RAG + optional tools)
  - `GET /GetData` — quick GET for Postman
  - `GET /ingest/default-files` — list scanned files
  - `GET /health` — health check

## ✅ Requirements
- Python 3.9–3.12
- `OPENAI_API_KEY` in `.env`

## 🚀 Quickstart
```bash
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows (PowerShell):
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt
cp .env.example .env
# edit .env and set OPENAI_API_KEY=sk-...

# Put your files into ./data_files/  (csv/json/txt/md)

# Start API
uvicorn src.api:app --reload --port 8001

# Build the vector DB (ingest data_files/)
curl -X POST "http://127.0.0.1:8001/ingest" \
  -H "Content-Type: application/json" \
  -d '{"include_crawl": false}'
