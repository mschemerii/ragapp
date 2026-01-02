"""Tests for configuration module."""

import os

from ragapp.config import Settings, get_settings


def test_settings_initialization():
    """Test Settings can be initialized with defaults."""
    settings = Settings()

    # Default provider is Ollama
    assert settings.llm_provider == "ollama"
    assert settings.embedding_provider == "ollama"
    assert settings.ollama_model == "llama3.2"
    assert settings.embedding_model == "nomic-embed-text"
    assert settings.chunk_size == 1000
    assert settings.chunk_overlap == 200
    assert settings.max_results == 5


def test_settings_with_custom_values():
    """Test Settings with custom values."""
    settings = Settings(
        chunk_size=500,
        max_results=10,
        temperature=0.5,
    )

    assert settings.chunk_size == 500
    assert settings.max_results == 10
    assert settings.temperature == 0.5


def test_get_settings():
    """Test get_settings function."""
    settings = get_settings()

    assert isinstance(settings, Settings)
    assert settings.llm_provider in ["openai", "ollama"]


def test_settings_creates_directories(tmp_path):
    """Test that Settings creates necessary directories."""
    vector_path = tmp_path / "vectorstore"
    docs_path = tmp_path / "documents"

    Settings(
        vector_store_path=vector_path,
        documents_path=docs_path,
    )

    assert vector_path.exists()
    assert docs_path.exists()


def test_settings_with_openai_provider():
    """Test Settings with OpenAI provider."""
    os.environ["OPENAI_API_KEY"] = "test-key-123"

    settings = Settings(
        llm_provider="openai",
        embedding_provider="openai",
    )

    assert settings.llm_provider == "openai"
    assert settings.embedding_provider == "openai"
    assert settings.openai_api_key == "test-key-123"


def test_settings_with_ollama_provider():
    """Test Settings with Ollama provider (default)."""
    settings = Settings()

    assert settings.llm_provider == "ollama"
    assert settings.embedding_provider == "ollama"
    assert settings.ollama_model == "llama3.2"
    assert settings.ollama_base_url == "http://localhost:11434"
