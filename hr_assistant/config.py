import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DOCUMENTS_DIR = "resumes"
    COLLECTION_NAME = "CVs"
    PERSISTENT_DIR = "data/chromadb"

    # Embeddings con Ollama
    EMBEDDING_PROVIDER = "ollama"
    EMBEDDING_MODEL = "nomic-embed-text"

    # OpenAI
    OPENAI_KEY = os.getenv("OPENAI_API_KEY")
    LLM_MODEL = "gpt-4.1-mini"
