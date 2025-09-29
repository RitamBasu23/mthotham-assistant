import os
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

from src.config import settings
from src.loaders import load_local_files, load_site
from src.data_paths import DEFAULT_LOCAL_FILES, list_data_files

#  Local embeddings (no OpenAI needed for ingest)
from langchain_community.embeddings import HuggingFaceEmbeddings

def build_vectorstore(docs: List[Document]) -> None:
    os.makedirs(settings.chroma_dir, exist_ok=True)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,           # slightly smaller chunks = faster local embedding
        chunk_overlap=100,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(docs)

    # Local sentence-transformers model
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=settings.chroma_dir,
        collection_name="mthotham",
    )
    vectordb.persist()

def run_ingest(include_crawl: bool = False, crawl_depth: int = 1, extra_paths: List[str] = None) -> dict:
    documents: List[Document] = []

    # 1) Auto-scan data_files/
    scanned = list_data_files()
    paths = scanned.copy()

    # 2) Backward-compat with DEFAULT_LOCAL_FILES (if pre-populated)
    for p in DEFAULT_LOCAL_FILES:
        if p not in paths:
            paths.append(p)

    # 3) Allow ad-hoc extra paths via API
    if extra_paths:
        for p in extra_paths:
            if p not in paths:
                paths.append(p)

    print(f"Ingesting local files ({len(paths)}): {paths}")
    local_docs = load_local_files(paths)
    documents.extend(local_docs)

    # 4) Optional crawl
    if include_crawl:
        site_docs = load_site(max_depth=crawl_depth)
        documents.extend(site_docs)

    if not documents:
        return {"ok": False, "message": "No documents to ingest (is data_files/ empty?)"}

    build_vectorstore(documents)
    return {"ok": True, "message": f"Ingested {len(documents)} docs into {settings.chroma_dir}."}
