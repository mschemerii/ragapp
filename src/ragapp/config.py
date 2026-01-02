"""Configuration management for the RAG application."""

from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # OpenAI Configuration
    openai_api_key: str = Field(..., description="OpenAI API key")
    openai_model: str = Field(
        default="gpt-4-turbo-preview",
        description="OpenAI model to use for generation",
    )

    # Embedding Configuration
    embedding_model: str = Field(
        default="text-embedding-3-small",
        description="OpenAI embedding model",
    )

    # Vector Store Configuration
    vector_store_path: Path = Field(
        default=Path("./data/vectorstore"),
        description="Path to vector store directory",
    )
    collection_name: str = Field(
        default="documents",
        description="ChromaDB collection name",
    )

    # Document Configuration
    documents_path: Path = Field(
        default=Path("./data/documents"),
        description="Path to documents directory",
    )
    chunk_size: int = Field(
        default=1000,
        description="Size of text chunks for processing",
        ge=100,
        le=4000,
    )
    chunk_overlap: int = Field(
        default=200,
        description="Overlap between chunks",
        ge=0,
        le=1000,
    )

    # Retrieval Configuration
    max_results: int = Field(
        default=5,
        description="Maximum number of results to retrieve",
        ge=1,
        le=20,
    )
    similarity_threshold: float = Field(
        default=0.7,
        description="Minimum similarity score for retrieval",
        ge=0.0,
        le=1.0,
    )

    # Application Settings
    log_level: str = Field(
        default="INFO",
        description="Logging level",
    )
    temperature: float = Field(
        default=0.7,
        description="LLM temperature for generation",
        ge=0.0,
        le=2.0,
    )
    max_tokens: Optional[int] = Field(
        default=1000,
        description="Maximum tokens for generation",
        ge=1,
    )

    def __init__(self, **kwargs):  # type: ignore[no-untyped-def]
        """Initialize settings and create necessary directories."""
        super().__init__(**kwargs)
        self.vector_store_path.mkdir(parents=True, exist_ok=True)
        self.documents_path.mkdir(parents=True, exist_ok=True)


def get_settings() -> Settings:
    """Get application settings singleton."""
    return Settings()
