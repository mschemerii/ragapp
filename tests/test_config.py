"""Tests for configuration module."""

import os

from ragapp.config import Settings, get_settings


def test_settings_initialization():
    """Test Settings can be initialized with defaults."""
    # Set required environment variable
    os.environ["OPENAI_API_KEY"] = "test-key-123"

    settings = Settings()

    assert settings.openai_api_key == "test-key-123"
    assert settings.openai_model == "gpt-4-turbo-preview"
    assert settings.chunk_size == 1000
    assert settings.chunk_overlap == 200
    assert settings.max_results == 5


def test_settings_with_custom_values():
    """Test Settings with custom values."""
    os.environ["OPENAI_API_KEY"] = "custom-key"

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
    os.environ["OPENAI_API_KEY"] = "test-key"

    settings = get_settings()

    assert isinstance(settings, Settings)
    assert settings.openai_api_key == "test-key"


def test_settings_creates_directories(tmp_path):
    """Test that Settings creates necessary directories."""
    os.environ["OPENAI_API_KEY"] = "test-key"

    vector_path = tmp_path / "vectorstore"
    docs_path = tmp_path / "documents"

    Settings(
        vector_store_path=vector_path,
        documents_path=docs_path,
    )

    assert vector_path.exists()
    assert docs_path.exists()
