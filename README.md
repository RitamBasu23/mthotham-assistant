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


curl -X POST http://127.0.0.1:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"query": cl}'




     🧠 3. Five Solid Chatbot Test Questions

Q1 — Historical Trend Query (Reasoning + Numeric Extraction)

“How has Mt Hotham’s winter visitation changed between 2019 and 2024, and what factors mentioned by Alpine Resorts Victoria contributed to this change?”

🧩 Tests: multi-year numeric reasoning + causal reference retrieval from ARV site text (e.g., COVID impact, economic recovery).

⸻

Q2 — Seasonal Definition & Data Source Validation

“According to Alpine Resorts Victoria, how are winter and summer visitation periods defined, and which agencies have historically collected this data?”

🧩 Tests: factual recall and document grounding using text_content.json definitions.

⸻

Q3 — Event & Snow-Data Fusion

“What major snow event occurred at Mt Hotham in August 2025, and how did it impact resort operations such as lift openings?”

🧩 Tests: cross-file reasoning — combine hotham_snow.csv + Mt Hotham site text (“77 cm storm”, “all lifts spinning”).

⸻

Q4 — Data Interpretation + Context Awareness

“What does the 58% increase above the 10-year average in ARV visitation statistics indicate about Victoria’s alpine tourism recovery?”

🧩 Tests: contextual summarization + ability to interpret statistical statements.

⸻

Q5 — Comparative Query Across Resorts

“Compare Mt Hotham’s 2021 and 2022 visitation numbers with other ARV resorts. Which resort showed the greatest recovery after COVID-19 restrictions?”

🧩 Tests: multi-table lookup and comparative reasoning using historic-visitation-data_table.json series.

⸻

✅ 4. Next Steps (for integration & testing)
	•	Save these questions in your evaluation_questions.json under your RAG evaluation folder.
	•	When testing your /chat or /qa endpoint:
	•	Use the “message” key (not “query”) in your POST payload.
	•	Expected answer types:
	•	Q1, Q5 → numerical + descriptive
	•	Q2 → factual paragraph
	•	Q3 → event narrative
	•	Q4 → interpretation summary
	•	Use these for RAGAS faithfulness + context precision scoring later.

⸻
