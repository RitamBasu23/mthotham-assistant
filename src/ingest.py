import os
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

from src.config import settings
from src.loaders import load_local_files, load_site
from src.data_paths import DEFAULT_LOCAL_FILES, list_data_files


# -------------------------------------------------------------------------
# 🔹 Build Vectorstore (Local FAISS/Chroma)
# -------------------------------------------------------------------------
def build_vectorstore(docs: List[Document]) -> None:
    """
    Splits documents into manageable chunks, embeds them using a local model,
    and saves a persistent Chroma vectorstore.
    """
    os.makedirs(settings.chroma_dir, exist_ok=True)

    print(f"🔹 Splitting {len(docs)} documents into chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(docs)
    print(f"✅ Created {len(chunks)} chunks for embedding.")

    # Local embedding model from config
    print(f"🔹 Loading embedding model: {settings.embedding_model_name}")
    embeddings = HuggingFaceEmbeddings(model_name=settings.embedding_model_name)

    print(f"🔹 Building Chroma vectorstore at {settings.chroma_dir} ...")
    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=settings.chroma_dir,
        collection_name="mthotham",
    )
    vectordb.persist()
    print("✅ Vectorstore successfully built and persisted.")


# -------------------------------------------------------------------------
# 🔹 Main Ingest Function
# -------------------------------------------------------------------------
def run_ingest(
    include_crawl: bool = False, crawl_depth: int = 1, extra_paths: List[str] = None
) -> dict:
    """
    Ingests local and/or crawled data, embeds it, and saves to Chroma.
    """
    documents: List[Document] = []

    # 1️⃣ Auto-scan data_files/ for available data
    scanned = list_data_files()
    paths = scanned.copy()

    # 2️⃣ Include default fallback paths (if defined)
    for p in DEFAULT_LOCAL_FILES:
        if p not in paths:
            paths.append(p)

    # 3️⃣ Include any ad-hoc extra paths
    if extra_paths:
        for p in extra_paths:
            if p not in paths:
                paths.append(p)

    print(f"🔹 Ingesting local files ({len(paths)}): {paths}")
    local_docs = load_local_files(paths)
    documents.extend(local_docs)

    # 4️⃣ Optional crawl (scrape site data)
    if include_crawl:
        print(f"🔹 Crawling ARV / Mt Hotham site data (depth={crawl_depth})...")
        site_docs = load_site(max_depth=crawl_depth)
        documents.extend(site_docs)

    if not documents:
        return {
            "ok": False,
            "message": "No documents to ingest (is data_files/ empty?)",
        }

    # 5️⃣ Build vectorstore
    build_vectorstore(documents)

    return {
        "ok": True,
        "message": f"Ingested {len(documents)} source docs into {settings.chroma_dir}.",
        "model": settings.embedding_model_name,
    }


# -------------------------------------------------------------------------
# 🔹 CLI Entrypoint (optional)
# -------------------------------------------------------------------------
if __name__ == "__main__":
    result = run_ingest(include_crawl=False)
    print(result)
