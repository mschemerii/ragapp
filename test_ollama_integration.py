#!/usr/bin/env python
"""
Integration test script for Ollama support.
This script validates the configuration and module structure without requiring
actual dependencies or running models.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_imports():
    """Test that all modules can be imported."""
    print("Testing module imports...")

    try:
        from ragapp.config import Settings
        print("  ✓ Config module imported")

        from ragapp.generation.generator import ResponseGenerator
        print("  ✓ Generator module imported")

        from ragapp.retrieval.vector_store import VectorStore
        print("  ✓ VectorStore module imported")

        from ragapp.pipeline import RAGPipeline
        print("  ✓ Pipeline module imported")

        return True
    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        return False


def test_config_validation():
    """Test configuration with both providers."""
    print("\nTesting configuration...")

    try:
        from ragapp.config import Settings

        # Test Ollama configuration (default)
        print("  Testing Ollama configuration:")
        settings = Settings()
        assert settings.llm_provider == "ollama", "Default LLM provider should be ollama"
        assert settings.embedding_provider == "ollama", "Default embedding provider should be ollama"
        assert settings.ollama_model == "llama3.2", "Default Ollama model should be llama3.2"
        assert settings.embedding_model == "nomic-embed-text", "Default embedding model should be nomic-embed-text"
        print("    ✓ Ollama defaults correct")

        # Test OpenAI configuration
        print("  Testing OpenAI configuration:")
        import os
        os.environ["OPENAI_API_KEY"] = "test-key-123"
        settings_openai = Settings(
            llm_provider="openai",
            embedding_provider="openai",
        )
        assert settings_openai.llm_provider == "openai"
        assert settings_openai.embedding_provider == "openai"
        assert settings_openai.openai_api_key == "test-key-123"
        print("    ✓ OpenAI configuration works")

        return True
    except Exception as e:
        print(f"  ✗ Configuration test failed: {e}")
        return False


def test_generator_initialization():
    """Test ResponseGenerator can be initialized with both providers."""
    print("\nTesting ResponseGenerator initialization...")

    try:
        from ragapp.generation.generator import ResponseGenerator

        # Test Ollama initialization
        print("  Testing Ollama generator:")
        gen_ollama = ResponseGenerator(
            provider="ollama",
            model="llama3.2",
            ollama_base_url="http://localhost:11434",
        )
        assert gen_ollama.provider == "ollama"
        assert gen_ollama.model == "llama3.2"
        print("    ✓ Ollama generator initialized")

        # Test OpenAI initialization
        print("  Testing OpenAI generator:")
        gen_openai = ResponseGenerator(
            provider="openai",
            model="gpt-4-turbo-preview",
            openai_api_key="test-key",
        )
        assert gen_openai.provider == "openai"
        assert gen_openai.model == "gpt-4-turbo-preview"
        print("    ✓ OpenAI generator initialized")

        return True
    except Exception as e:
        print(f"  ✗ Generator initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_vector_store_params():
    """Test VectorStore accepts both provider parameters."""
    print("\nTesting VectorStore parameters...")

    try:
        from ragapp.retrieval.vector_store import VectorStore
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            # Test Ollama embeddings
            print("  Testing Ollama embeddings params:")
            vs_ollama = VectorStore(
                store_path=Path(tmpdir) / "ollama",
                collection_name="test",
                embedding_provider="ollama",
                embedding_model="nomic-embed-text",
                ollama_base_url="http://localhost:11434",
            )
            assert vs_ollama.embedding_provider == "ollama"
            print("    ✓ Ollama VectorStore parameters accepted")

            # Test OpenAI embeddings
            print("  Testing OpenAI embeddings params:")
            vs_openai = VectorStore(
                store_path=Path(tmpdir) / "openai",
                collection_name="test",
                embedding_provider="openai",
                embedding_model="text-embedding-3-small",
                openai_api_key="test-key",
            )
            assert vs_openai.embedding_provider == "openai"
            print("    ✓ OpenAI VectorStore parameters accepted")

        return True
    except Exception as e:
        print(f"  ✗ VectorStore test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pipeline_integration():
    """Test RAGPipeline passes parameters correctly."""
    print("\nTesting RAGPipeline integration...")

    try:
        from ragapp.pipeline import RAGPipeline
        from ragapp.config import Settings
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            # Test with Ollama settings
            print("  Testing pipeline with Ollama:")
            settings_ollama = Settings(
                llm_provider="ollama",
                embedding_provider="ollama",
                vector_store_path=Path(tmpdir) / "vectorstore",
                documents_path=Path(tmpdir) / "documents",
            )

            pipeline = RAGPipeline(settings=settings_ollama)
            assert pipeline.generator.provider == "ollama"
            assert pipeline.vector_store.embedding_provider == "ollama"
            print("    ✓ Pipeline initialized with Ollama")

        return True
    except Exception as e:
        print(f"  ✗ Pipeline integration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Ollama Integration Test Suite")
    print("=" * 60)

    results = []

    # Run tests
    results.append(("Module Imports", test_imports()))
    results.append(("Configuration", test_config_validation()))
    results.append(("Generator Init", test_generator_initialization()))
    results.append(("VectorStore Params", test_vector_store_params()))
    results.append(("Pipeline Integration", test_pipeline_integration()))

    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name:.<40} {status}")

    print("=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
