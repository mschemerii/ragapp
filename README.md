# RAG Application

A Retrieval-Augmented Generation (RAG) application for intelligent document search and question answering.

## Overview

This application combines document retrieval with large language models to provide accurate, context-aware responses based on your document collection.

## Features

- **Multi-format Support**: PDF, TXT, DOCX, Markdown
- **Multiple LLM Providers**: OpenAI or Local Ollama models (M4 Max optimized)
- **Multiple Interfaces**: CLI, Streamlit Web UI, FastAPI REST API
- **Semantic Search**: Vector-based similarity search using ChromaDB
- **Configurable Chunking**: Customizable chunk sizes and overlap
- **Streaming Responses**: Real-time answer generation
- **Source Attribution**: Track which documents answers come from
- **Interactive Mode**: Conversational query interface (CLI & Web)
- **Type-Safe**: Full type hints with mypy checking
- **Well-Tested**: Comprehensive test suite with pytest
- **CI/CD Ready**: GitHub Actions workflows included

## Prerequisites

- Python 3.10 or higher
- pip or uv package manager

## Download Pre-Built macOS Application

**For macOS users**: You can download a ready-to-use application without installing Python!

### Option 1: Download from Releases (Recommended)

1. Go to the [Releases page](../../releases)
2. Download the latest `RAG-Application-macOS.dmg` or `RAG-Application-macOS.zip`
3. **DMG**: Open the DMG and drag the app to Applications
4. **ZIP**: Extract and move the app to Applications
5. **First launch**: Right-click the app → "Open" (macOS security)
6. The Streamlit web interface will open in your browser automatically

### Option 2: Build Locally

```bash
# Install build dependencies
pip install -e ".[build,all]"

# Build the application
./build_macos.sh

# The app will be in: dist/RAG Application.app
open "dist/RAG Application.app"
```

**Note**: The macOS app includes the Streamlit web interface. For CLI or API server, use Python installation below.

## Installation (Python)

### Using uv (recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
```

### Using pip

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install core dependencies
pip install -e .

# Install with web UI support (Streamlit + FastAPI)
pip install -e ".[web]"

# Install with development dependencies
pip install -e ".[dev]"

# Install everything
pip install -e ".[all]"
```

## Configuration

Create a `.env` file in the project root with your configuration:

### Using Local Ollama (Default, Recommended for M4 Max)

```env
# LLM Provider Configuration
LLM_PROVIDER=ollama
EMBEDDING_PROVIDER=ollama

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
EMBEDDING_MODEL=nomic-embed-text

# Vector Store Configuration
VECTOR_STORE_PATH=./data/vectorstore

# Document Storage
DOCUMENTS_PATH=./data/documents
```

**Note**: You need to have [Ollama](https://ollama.ai) installed and running. See the [Ollama Setup Guide](docs/OLLAMA_SETUP.md) for details.

### Using OpenAI

```env
# LLM Provider Configuration
LLM_PROVIDER=openai
EMBEDDING_PROVIDER=openai

# OpenAI API Key
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-4-turbo-preview
EMBEDDING_MODEL=text-embedding-3-small

# Vector Store Configuration
VECTOR_STORE_PATH=./data/vectorstore

# Document Storage
DOCUMENTS_PATH=./data/documents
```

## Quick Start

1. **Add your documents** to the `data/documents/` directory (supports .txt, .pdf, .docx, .md)

2. **Ingest documents** into the vector store:
   ```bash
   python -m ragapp ingest --reset
   ```

3. **Choose your interface**:

   **CLI (Command Line)**:
   ```bash
   python -m ragapp query "What is RAG?"
   ```

   **Streamlit Web UI**:
   ```bash
   pip install -e ".[web]"
   streamlit run streamlit_app.py
   # Opens browser at http://localhost:8501
   ```

   **FastAPI + Web Frontend**:
   ```bash
   pip install -e ".[web]"
   uvicorn api:app --reload
   # Opens browser at http://localhost:8000
   ```

## User Interfaces

This application provides **three different interfaces** to suit your needs:

### 1. Command-Line Interface (CLI)

The simplest way to use the application from the terminal.

**Best for**: Scripts, automation, quick queries

### 2. Streamlit Web UI

A beautiful, interactive web interface built with Streamlit.

**Best for**: Internal tools, data science teams, quick demos

**Run it:**
```bash
pip install -e ".[web]"
streamlit run streamlit_app.py
```

Then open http://localhost:8501 in your browser.

**Features**:
- Interactive query interface
- Real-time statistics display
- Source document viewer
- Streaming response support
- Clean, modern UI

### 3. FastAPI REST API + Web Frontend

A production-ready REST API with a responsive web frontend.

**Best for**: Production deployments, integration with other services, custom frontends

**Run it:**
```bash
pip install -e ".[web]"
uvicorn api:app --reload
```

Then open http://localhost:8000 in your browser.

**Features**:
- RESTful API with OpenAPI documentation
- Interactive web interface at `/`
- API docs at `/docs`
- Streaming support
- CORS enabled for external integrations
- Background task support

**API Endpoints**:
- `POST /query` - Query the RAG system
- `POST /query/stream` - Stream query response
- `GET /stats` - Get system statistics
- `POST /ingest` - Ingest documents
- `DELETE /vector-store` - Reset vector store
- `GET /health` - Health check

## Usage

### CLI Commands

#### Ingest Documents
```bash
# Ingest all documents from data/documents/
python -m ragapp ingest

# Ingest a specific file
python -m ragapp ingest --file path/to/document.pdf

# Reset vector store and ingest
python -m ragapp ingest --reset
```

#### Query
```bash
# Ask a question
python -m ragapp query "What is this about?"

# Stream the response
python -m ragapp query "Explain the main concepts" --stream

# Show source documents
python -m ragapp query "What is RAG?" --show-sources
```

#### Interactive Mode
```bash
# Start an interactive session
python -m ragapp interactive
```

#### Statistics
```bash
# View system statistics
python -m ragapp stats
```

### Programmatic Usage

```python
from ragapp import RAGPipeline

# Initialize pipeline
pipeline = RAGPipeline()

# Ingest documents
count = pipeline.ingest_documents()
print(f"Ingested {count} chunks")

# Query
answer = pipeline.query("What is RAG?")
print(answer)

# Query with sources
answer, sources = pipeline.query("What is RAG?", return_sources=True)
print(f"Answer: {answer}")
print(f"Based on {len(sources)} sources")

# Stream response
for chunk in pipeline.stream_query("Explain vector embeddings"):
    print(chunk, end="", flush=True)
```

See [examples/](examples/) for more detailed usage examples.

## Architecture

This RAG application follows a modular architecture:

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│  Ingestion  │─────▶│  Retrieval  │─────▶│ Generation  │
│   Pipeline  │      │   System    │      │   Engine    │
└─────────────┘      └─────────────┘      └─────────────┘
      │                     │                     │
      ▼                     ▼                     ▼
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│  Documents  │      │   Vector    │      │  Ollama or  │
│   Loaders   │      │    Store    │      │   OpenAI    │
└─────────────┘      └─────────────┘      └─────────────┘
```

**Components**:
- `config.py`: Centralized configuration with Pydantic
- `ingestion/`: Document loading and chunking
- `retrieval/`: Vector storage and semantic search
- `generation/`: LLM-based response generation
- `pipeline.py`: Orchestrates the entire RAG flow

For detailed architecture information, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Documentation

- [Architecture Guide](docs/ARCHITECTURE.md) - System design and components
- [API Reference](docs/API.md) - Complete API documentation
- [Examples](examples/) - Usage examples and code samples

## Development

### Running Tests

```bash
# With pytest
pytest

# With coverage
pytest --cov=ragapp tests/
```

### Code Quality

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Type checking
mypy src/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Acknowledgments

Built with:
- [LangChain](https://python.langchain.com/) - LLM framework
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [Ollama](https://ollama.ai/) - Local language models (default)
- [OpenAI](https://openai.com/) - Cloud language models (optional)
