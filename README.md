# RAG Application

A Retrieval-Augmented Generation (RAG) application for intelligent document search and question answering.

## Overview

This application combines document retrieval with large language models to provide accurate, context-aware responses based on your document collection.

## Features

- Document ingestion and processing
- Vector storage for semantic search
- Context-aware question answering
- Support for multiple document formats

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

## Usage

```bash
# Run the application
python -m ragapp

# Or with uv
uv run python -m ragapp
```

## Project Structure

```
ragapp/
├── src/
│   └── ragapp/          # Main application package
│       ├── __init__.py
│       ├── ingestion/   # Document ingestion
│       ├── retrieval/   # Vector search and retrieval
│       └── generation/  # LLM-based generation
├── data/                # Data storage
│   ├── documents/       # Source documents
│   └── vectorstore/     # Vector embeddings
├── tests/               # Test suite
├── .env.example         # Environment variables template
├── .gitignore
├── pyproject.toml
└── README.md
```

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
