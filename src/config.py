import os
from pydantic import BaseModel
from dotenv import load_dotenv

# Load .env file
load_dotenv()


class Settings(BaseModel):
    # Hugging Face
    hf_api_token: str | None = os.getenv("HF_API_TOKEN")
    hf_model: str = os.getenv("HF_MODEL", "tiiuae/falcon-7b-instruct")

    # Paths
    data_dir: str = os.getenv("DATA_DIR", "data")
    chroma_dir: str = os.getenv("CHROMA_DIR", "data/chroma")

    # App
    app_timezone: str = os.getenv("APP_TIMEZONE", "UTC")


# Global settings instance
settings = Settings()
