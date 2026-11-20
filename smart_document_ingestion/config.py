import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
STORAGE_DIR = PROJECT_ROOT / "storage"
CHROMA_DIR = STORAGE_DIR / "chroma"

load_dotenv(PROJECT_ROOT / ".env")


def get_api_key() -> str:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is empty. Add your OpenAI API key to the project .env file."
        )
    return api_key


def get_embedding_model_name() -> str:
    return os.getenv("OPENAI_EMBEDDING_MODEL", "").strip() or "text-embedding-3-small"


def get_llm_model_name() -> str:
    return os.getenv("OPENAI_LLM_MODEL", "").strip() or "gpt-4.1-nano"
