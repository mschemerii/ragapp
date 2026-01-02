# RAG Application Architecture

## Overview

This document describes the architecture and design of the RAG (Retrieval-Augmented Generation) application.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      RAG Application                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────┐      ┌────────────┐      ┌────────────┐   │
│  │ Ingestion  │─────▶│ Retrieval  │─────▶│ Generation │   │
│  │  Pipeline  │      │   System   │      │   Engine   │   │
│  └────────────┘      └────────────┘      └────────────┘   │
│         │                   │                    │          │
│         ▼                   ▼                    ▼          │
│  ┌────────────┐      ┌────────────┐      ┌────────────┐   │
│  │  Document  │      │   Vector   │      │    LLM     │   │
│  │  Loaders   │      │   Store    │      │   (OpenAI) │   │
│  └────────────┘      └────────────┘      └────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Configuration (`config.py`)

**Purpose**: Centralized configuration management using Pydantic settings.

**Key Features**:
- Environment variable loading from `.env` files
- Type-safe settings with validation
- Default values for all configuration options
- Automatic directory creation

**Configuration Categories**:
- OpenAI settings (API key, model selection)
- Embedding configuration
- Vector store settings
- Document processing parameters
- Retrieval settings
- Application behavior

### 2. Ingestion Pipeline (`ingestion/`)

**Purpose**: Load, process, and prepare documents for vector storage.

#### DocumentLoader (`loaders.py`)

**Responsibilities**:
- Support multiple document formats (TXT, PDF, DOCX, Markdown)
- Load individual files or entire directories
- Progress tracking for batch operations
- Error handling and logging

**Supported Formats**:
- `.txt`: Plain text files
- `.pdf`: PDF documents (via PyPDF)
- `.docx`: Word documents (via docx2txt)
- `.md`: Markdown files (via UnstructuredMarkdownLoader)

#### DocumentProcessor (`processor.py`)

**Responsibilities**:
- Text chunking with configurable size and overlap
- Document cleaning and normalization
- Metadata enrichment
- Recursive character splitting for natural breaks

**Chunking Strategy**:
- Splits on natural boundaries: `\n\n` → `\n` → `. ` → ` `
- Configurable chunk size (default: 1000 characters)
- Configurable overlap (default: 200 characters)
- Preserves context across chunks

### 3. Retrieval System (`retrieval/`)

**Purpose**: Store embeddings and retrieve relevant documents based on queries.

#### VectorStore (`vector_store.py`)

**Responsibilities**:
- Manage ChromaDB vector database
- Generate embeddings using OpenAI models
- Persist vector data to disk
- Batch processing for efficiency

**Key Operations**:
- `create_or_load()`: Initialize or load existing database
- `add_documents()`: Add new documents with embeddings
- `similarity_search()`: Find similar documents
- `delete_collection()`: Clear all data

**Technology Stack**:
- **Vector DB**: ChromaDB (local, persistent)
- **Embeddings**: OpenAI text-embedding-3-small (or configurable)
- **Similarity Metric**: Cosine similarity

#### DocumentRetriever (`retriever.py`)

**Responsibilities**:
- Query the vector store
- Filter results by similarity threshold
- Format context for generation
- Provide relevance scores

**Retrieval Process**:
1. Convert query to embedding
2. Perform k-nearest neighbors search
3. Filter by similarity threshold
4. Return ranked documents

### 4. Generation Engine (`generation/`)

**Purpose**: Generate natural language responses using LLMs.

#### Prompts (`prompts.py`)

**Templates Provided**:
- `RAG_SYSTEM_PROMPT`: System-level instructions
- `RAG_PROMPT`: Standard RAG prompt template
- `RAG_CHAT_PROMPT`: Chat-based prompt with system message
- `CONVERSATIONAL_RAG_PROMPT`: Multi-turn conversation support

**Prompt Design Principles**:
- Clear instructions to use provided context
- Guidance on handling missing information
- Emphasis on accuracy and source attribution
- Structured context presentation

#### ResponseGenerator (`generator.py`)

**Responsibilities**:
- Interface with OpenAI LLM API
- Format retrieved context
- Support both streaming and non-streaming responses
- Handle conversation history

**Features**:
- Temperature control for response variability
- Token limit configuration
- Streaming support for real-time responses
- Error handling and retry logic

### 5. RAG Pipeline (`pipeline.py`)

**Purpose**: Orchestrate all components into a cohesive system.

**Key Methods**:

```python
ingest_documents(file_path, reset)
# Load and process documents into vector store

query(question, chat_history, return_sources)
# Retrieve context and generate answer

stream_query(question, chat_history)
# Stream response generation

get_stats()
# System statistics and health
```

**Workflow**:
1. **Ingestion**: Documents → Chunks → Embeddings → Vector Store
2. **Query**: Question → Query Embedding → Similarity Search → Context
3. **Generation**: Context + Question → LLM → Answer

## Data Flow

### Ingestion Flow

```
Document Files
    ↓
DocumentLoader (load files)
    ↓
Raw Documents
    ↓
DocumentProcessor (chunk & clean)
    ↓
Processed Chunks
    ↓
VectorStore (generate embeddings)
    ↓
ChromaDB (persist)
```

### Query Flow

```
User Question
    ↓
VectorStore (generate query embedding)
    ↓
Similarity Search (k-NN)
    ↓
Retrieved Documents
    ↓
DocumentRetriever (format context)
    ↓
ResponseGenerator (LLM call)
    ↓
Generated Answer
```

## Design Decisions

### 1. Why ChromaDB?

- **Lightweight**: Easy to set up, no separate server required
- **Persistent**: Stores data locally on disk
- **Python-native**: Excellent integration with Python ecosystem
- **Feature-rich**: Supports filtering, metadata, and hybrid search

### 2. Why Chunking?

- **Context Windows**: LLMs have limited context windows
- **Retrieval Precision**: Smaller chunks = more precise matches
- **Cost Efficiency**: Only relevant chunks are sent to LLM
- **Semantic Coherence**: Chunks represent coherent concepts

### 3. Why OpenAI Embeddings?

- **Quality**: State-of-the-art semantic understanding
- **Consistency**: Same model family for embeddings and generation
- **Dimensionality**: Optimized vector sizes (1536 dimensions)
- **Speed**: Fast embedding generation

### 4. Modular Design

Each component is:
- **Independently testable**: Clear interfaces and responsibilities
- **Swappable**: Easy to replace (e.g., swap ChromaDB for Pinecone)
- **Configurable**: Settings-driven behavior
- **Reusable**: Can be used in different contexts

## Scalability Considerations

### Current Limitations

- **Single Machine**: Designed for local deployment
- **In-Memory**: Limited by available RAM
- **Sequential Processing**: Single-threaded ingestion
- **Local Storage**: Disk space constraints

### Future Improvements

1. **Distributed Vector Store**: Pinecone, Weaviate, or Qdrant
2. **Batch Processing**: Parallel document ingestion
3. **Caching Layer**: Redis for frequent queries
4. **API Server**: FastAPI or Flask REST API
5. **Monitoring**: Prometheus metrics and logging
6. **Queue System**: Celery for async processing

## Security Considerations

1. **API Keys**: Stored in environment variables, never committed
2. **Input Validation**: Pydantic models validate all inputs
3. **Error Handling**: Graceful degradation, no sensitive data in errors
4. **Sandboxing**: No arbitrary code execution
5. **Rate Limiting**: Respect LLM API rate limits

## Performance Optimization

### Current Optimizations

- Batch document processing (100 docs per batch)
- Persistent vector storage (no recomputation)
- Streaming responses (lower latency perception)
- Configurable chunk sizes (balance quality/cost)

### Recommended Settings

**For Quality**:
- Chunk size: 1000-1500 characters
- Max results: 5-10 documents
- Temperature: 0.3-0.5 (more deterministic)

**For Speed**:
- Chunk size: 500-800 characters
- Max results: 3-5 documents
- Use streaming responses

**For Cost**:
- Smaller chunk sizes
- Fewer retrieved documents
- Lower max_tokens for generation

## Testing Strategy

1. **Unit Tests**: Individual components (loaders, processors, etc.)
2. **Integration Tests**: Full pipeline end-to-end
3. **Performance Tests**: Latency and throughput benchmarks
4. **Quality Tests**: Retrieval precision and answer accuracy

## Monitoring and Observability

**Recommended Metrics**:
- Ingestion throughput (documents/second)
- Query latency (p50, p95, p99)
- Retrieval precision (relevant docs retrieved)
- LLM token usage (cost tracking)
- Error rates by component

**Logging Levels**:
- `DEBUG`: Detailed component operations
- `INFO`: Pipeline events and statistics
- `WARNING`: Degraded performance or issues
- `ERROR`: Component failures
