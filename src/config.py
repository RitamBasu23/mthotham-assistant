import os
from pydantic import BaseModel
from dotenv import load_dotenv

# ------------------------------------------------------------
# Load environment variables from .env (if present)
# ------------------------------------------------------------
load_dotenv()


class Settings(BaseModel):
    """
    Configuration class for the Mt Hotham RAG Assistant.
    Handles model settings, data directories, and application preferences.
    """

    # -------------------------------------------------------------------------
    # 🔹 Model Settings
    # -------------------------------------------------------------------------

    # LLM Model (local TinyLlama)
    llm_model_name: str = os.getenv(
        "LLM_MODEL_NAME", "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    )

    # Embedding model (SentenceTransformer for vector store)
    embedding_model_name: str = os.getenv(
        "EMBED_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2"
    )

    # Optional: device setup (use "cuda" if available)
    device: str = os.getenv(
        "DEVICE", "cuda" if os.environ.get("CUDA_VISIBLE_DEVICES") else "cpu"
    )

    # -------------------------------------------------------------------------
    # 🔹 Paths
    # -------------------------------------------------------------------------
    data_dir: str = os.getenv("DATA_DIR", "data")
    chroma_dir: str = os.getenv("CHROMA_DIR", "data/chroma")
    vectorstore_dir: str = os.getenv("VECTORSTORE_DIR", "data/vectorstore")

    # -------------------------------------------------------------------------
    # 🔹 Application Settings
    # -------------------------------------------------------------------------
    app_timezone: str = os.getenv("APP_TIMEZONE", "UTC")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"


# -------------------------------------------------------------------------
# Global settings instance
# -------------------------------------------------------------------------
settings = Settings()

# Optional: print summary for debugging
if settings.debug:
    print(f"✅ Loaded configuration:")
    print(f" - LLM model: {settings.llm_model_name}")
    print(f" - Embedding model: {settings.embedding_model_name}")
    print(f" - Vector store: {settings.vectorstore_dir}")
    print(f" - Device: {settings.device}")
