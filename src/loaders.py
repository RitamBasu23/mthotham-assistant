from typing import List, Iterable
from pathlib import Path
from bs4 import SoupStrainer
from langchain_core.documents import Document
import json
import pandas as pd

from langchain_community.document_loaders import RecursiveUrlLoader

# Optional crawler (kept for future use)
from langchain_community.document_loaders import RecursiveUrlLoader

DEFAULT_URLS = [
    "https://www.mthotham.com.au/",
    "https://www.mthotham.com.au/discover/accommodation",
    "https://www.mthotham.com.au/plan-and-book/lift-passes",
    "https://www.mthotham.com.au/discover/getting-here",
    "https://www.mthotham.com.au/discover/eat-drink",
    "https://www.mthotham.com.au/on-the-mountain/safety",
]

def load_site(urls: List[str] = None, max_depth: int = 1) -> List[Document]:
    urls = urls or DEFAULT_URLS
    docs_all: List[Document] = []
    for u in urls:
        loader = RecursiveUrlLoader(
            url=u,
            max_depth=max_depth,
            use_async=True,
            extractor=lambda x: SoupStrainer(["article","main","section","div","p","li","h1","h2","h3"]),
        )
        docs = loader.load()
        seen = set()
        for d in docs:
            key = (d.metadata.get("source",""), d.page_content.strip())
            if key in seen:
                continue
            seen.add(key)
            docs_all.append(d)
    return docs_all

# ----- Local files (CSV / JSON / TXT / MD) -----

def _rows_to_docs(rows: Iterable[dict], source: str, doc_tag: str) -> List[Document]:
    out: List[Document] = []
    for i, row in enumerate(rows):
        text = "\n".join(f"{k}: {v}" for k, v in row.items())
        out.append(Document(page_content=text, metadata={"source": source, "row_index": i, "doc_type": doc_tag}))
    return out

def load_local_files(paths: List[str]) -> List[Document]:
    out: List[Document] = []
    for p in paths:
        path = Path(p)
        if not path.exists():
            print(f"[load_local_files] WARNING: file not found, skipping: {p}")
            continue
        src = str(path.resolve())
        suff = path.suffix.lower()
        try:
            if suff == ".csv":
                df = pd.read_csv(path)
                out.extend(_rows_to_docs(df.to_dict(orient="records"), src, "csv"))
            elif suff == ".json":
                data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
                if isinstance(data, list):
                    out.extend(_rows_to_docs(data, src, "json"))
                elif isinstance(data, dict):
                    out.append(Document(page_content=json.dumps(data, ensure_ascii=False, indent=2),
                                        metadata={"source": src, "doc_type": "json"}))
                    for k, v in data.items():
                        out.append(Document(
                            page_content=f"key: {k}\nvalue: {json.dumps(v, ensure_ascii=False)}",
                            metadata={"source": src, "json_key": k, "doc_type": "json"}
                        ))
                else:
                    out.append(Document(page_content=str(data), metadata={"source": src, "doc_type": "json"}))
            elif suff in {".txt", ".md"}:
                out.append(Document(page_content=path.read_text(encoding="utf-8", errors="ignore"),
                                    metadata={"source": src, "doc_type": "text"}))
            else:
                print(f"[load_local_files] NOTE: unsupported type {suff} for {p}, skipping.")
        except Exception as e:
            print(f"[load_local_files] ERROR reading {p}: {e}")
    return out
