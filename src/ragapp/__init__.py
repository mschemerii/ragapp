"""RAG Application - Retrieval-Augmented Generation for intelligent document search."""

from ragapp.config import Settings, get_settings
from ragapp.pipeline import RAGPipeline

__version__ = "0.1.0"

__all__ = ["__version__", "RAGPipeline", "Settings", "get_settings"]
