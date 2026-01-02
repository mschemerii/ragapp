# RAG Application

A Retrieval-Augmented Generation (RAG) application for intelligent document search and question answering.

## Overview

This application combines document retrieval with large language models to provide accurate, context-aware responses based on your document collection.

## Features

- **Multi-format Support**: PDF, TXT, DOCX, Markdown
- **Semantic Search**: Vector-based similarity search using ChromaDB
- **Configurable Chunking**: Customizable chunk sizes and overlap
- **Streaming Responses**: Real-time answer generation
- **CLI & API**: Both command-line and programmatic interfaces
- **Source Attribution**: Track which documents answers come from
- **Interactive Mode**: Conversational query interface
- **Type-Safe**: Full type hints with mypy checking
- **Well-Tested**: Comprehensive test suite with pytest
- **CI/CD Ready**: GitHub Actions workflows included

## Prerequisites

- Python 3.10 or higher
- pip or uv package manager

## Installation

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

# Install dependencies
pip install -e .
```

## Configuration

Create a `.env` file in the project root with your configuration:

```env
# OpenAI API Key (or other LLM provider)
OPENAI_API_KEY=your-api-key-here

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

3. **Query your documents**:
   ```bash
   python -m ragapp query "What is RAG?"
   ```

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
│  Documents  │      │   Vector    │      │   OpenAI    │
│   Loaders   │      │    Store    │      │     LLM     │
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
- [OpenAI](https://openai.com/) - Language models
