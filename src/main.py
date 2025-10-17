# src/main.py
import argparse
import uvicorn
from src.api import app
from src.ingest import run_ingest
from src.config import settings


def main():
    parser = argparse.ArgumentParser(
        description="Mt Hotham Assistant - RAG Pipeline Launcher"
    )
    parser.add_argument(
        "--ingest",
        action="store_true",
        help="Rebuild the Chroma vectorstore from data_files/",
    )
    parser.add_argument(
        "--crawl",
        action="store_true",
        help="Also crawl ARV/Mt Hotham websites during ingestion",
    )
    args = parser.parse_args()

    if args.ingest:
        print("📥 Starting ingestion process...")
        result = run_ingest(include_crawl=args.crawl, crawl_depth=1, extra_paths=None)
        print("✅ Ingestion complete:", result)
    else:
        print(f"🚀 Launching FastAPI app with model: {settings.llm_model_name}")
        uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
