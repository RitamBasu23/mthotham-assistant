# src/main.py
from src.ingest import run_ingest

if __name__ == "__main__":
    print(" Ingesting from data_files/ ...")
    result = run_ingest(include_crawl=False, crawl_depth=1, extra_paths=None)
    print(" Done:", result)
