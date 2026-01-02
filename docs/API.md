# API Reference

## RAGPipeline

The main interface for the RAG application.

### Constructor

```python
RAGPipeline(settings: Optional[Settings] = None)
```

Initialize the RAG pipeline with optional custom settings.

**Parameters**:
- `settings` (Optional[Settings]): Custom configuration. If not provided, loads from environment.

**Example**:
```python
from ragapp import RAGPipeline, Settings

# Use default settings
pipeline = RAGPipeline()

# Use custom settings
custom_settings = Settings(chunk_size=500, max_results=10)
pipeline = RAGPipeline(settings=custom_settings)
```

### Methods

#### ingest_documents

```python
def ingest_documents(
    file_path: Optional[Path] = None,
    reset: bool = False,
) -> int
```

Ingest documents into the vector store.

**Parameters**:
- `file_path` (Optional[Path]): Specific file to ingest. If None, ingests all documents in configured directory.
- `reset` (bool): If True, clears vector store before ingestion.

**Returns**:
- `int`: Number of document chunks ingested.

**Example**:
```python
# Ingest all documents
count = pipeline.ingest_documents()

# Ingest specific file
from pathlib import Path
count = pipeline.ingest_documents(file_path=Path("data/documents/myfile.pdf"))

# Reset and ingest
count = pipeline.ingest_documents(reset=True)
```

#### query

```python
def query(
    question: str,
    chat_history: Optional[List[BaseMessage]] = None,
    return_sources: bool = False,
) -> str | tuple[str, List[Document]]
```

Query the RAG system and get an answer.

**Parameters**:
- `question` (str): The question to ask.
- `chat_history` (Optional[List[BaseMessage]]): Conversation history for context.
- `return_sources` (bool): If True, returns (answer, sources) tuple.

**Returns**:
- `str`: Generated answer (if return_sources=False)
- `tuple[str, List[Document]]`: Answer and source documents (if return_sources=True)

**Example**:
```python
# Simple query
answer = pipeline.query("What is RAG?")
print(answer)

# Query with sources
answer, sources = pipeline.query("What is RAG?", return_sources=True)
print(f"Answer: {answer}")
print(f"Based on {len(sources)} sources")

# Query with chat history
from langchain_core.messages import HumanMessage, AIMessage

history = [
    HumanMessage(content="What is RAG?"),
    AIMessage(content="RAG is Retrieval-Augmented Generation..."),
]
answer = pipeline.query("Can you explain more?", chat_history=history)
```

#### stream_query

```python
def stream_query(
    question: str,
    chat_history: Optional[List[BaseMessage]] = None,
)
```

Stream the response generation (generator function).

**Parameters**:
- `question` (str): The question to ask.
- `chat_history` (Optional[List[BaseMessage]]): Conversation history.

**Yields**:
- `str`: Chunks of the generated response.

**Example**:
```python
# Stream response
for chunk in pipeline.stream_query("Explain vector embeddings"):
    print(chunk, end="", flush=True)
print()
```

#### get_stats

```python
def get_stats() -> dict[str, int]
```

Get system statistics.

**Returns**:
- `dict[str, int]`: Dictionary with statistics:
  - `documents_in_store`: Number of chunks in vector store
  - `source_files`: Number of source files in documents directory

**Example**:
```python
stats = pipeline.get_stats()
print(f"Vector store: {stats['documents_in_store']} chunks")
print(f"Source files: {stats['source_files']}")
```

#### reset_vector_store

```python
def reset_vector_store() -> None
```

Delete all data from the vector store.

**Example**:
```python
pipeline.reset_vector_store()
```

## Settings

Configuration management using Pydantic settings.

### Constructor

```python
Settings(**kwargs)
```

**Parameters** (all optional, loaded from `.env` if not provided):

**OpenAI Configuration**:
- `openai_api_key` (str): OpenAI API key (**required**)
- `openai_model` (str): Model for generation (default: "gpt-4-turbo-preview")
- `embedding_model` (str): Model for embeddings (default: "text-embedding-3-small")

**Vector Store**:
- `vector_store_path` (Path): Path to vector store (default: "./data/vectorstore")
- `collection_name` (str): ChromaDB collection name (default: "documents")

**Documents**:
- `documents_path` (Path): Path to documents directory (default: "./data/documents")
- `chunk_size` (int): Text chunk size (default: 1000, range: 100-4000)
- `chunk_overlap` (int): Chunk overlap (default: 200, range: 0-1000)

**Retrieval**:
- `max_results` (int): Max documents to retrieve (default: 5, range: 1-20)
- `similarity_threshold` (float): Min similarity score (default: 0.7, range: 0.0-1.0)

**Application**:
- `log_level` (str): Logging level (default: "INFO")
- `temperature` (float): LLM temperature (default: 0.7, range: 0.0-2.0)
- `max_tokens` (Optional[int]): Max tokens to generate (default: 1000)

**Example**:
```python
from ragapp import Settings

settings = Settings(
    openai_api_key="sk-...",
    chunk_size=500,
    max_results=10,
    temperature=0.5,
)
```

## Component APIs

### DocumentLoader

```python
from ragapp.ingestion import DocumentLoader

loader = DocumentLoader(documents_path=Path("data/documents"))

# Load single document
docs = loader.load_document(Path("file.pdf"))

# Load directory
docs = loader.load_directory()

# Get file count
count = loader.get_file_count()
```

### DocumentProcessor

```python
from ragapp.ingestion import DocumentProcessor

processor = DocumentProcessor(chunk_size=1000, chunk_overlap=200)

# Process documents
chunks = processor.process_documents(documents)
```

### VectorStore

```python
from ragapp.retrieval import VectorStore

vector_store = VectorStore(
    store_path=Path("data/vectorstore"),
    collection_name="docs",
    embedding_model="text-embedding-3-small",
    openai_api_key="sk-...",
)

# Create or load
vector_store.create_or_load()

# Add documents
vector_store.add_documents(documents)

# Search
results = vector_store.similarity_search(query="What is RAG?", k=5)

# Get count
count = vector_store.get_document_count()
```

### DocumentRetriever

```python
from ragapp.retrieval import DocumentRetriever

retriever = DocumentRetriever(
    vector_store=vector_store,
    max_results=5,
    similarity_threshold=0.7,
)

# Retrieve documents
docs = retriever.retrieve("What is RAG?")

# Retrieve with scores
docs_with_scores = retriever.retrieve_with_scores("What is RAG?")

# Format context
context = retriever.format_context(docs)
```

### ResponseGenerator

```python
from ragapp.generation import ResponseGenerator

generator = ResponseGenerator(
    model="gpt-4-turbo-preview",
    temperature=0.7,
    max_tokens=1000,
    openai_api_key="sk-...",
)

# Generate response
answer = generator.generate(question="What is RAG?", context=context)

# Generate from documents
answer = generator.generate_from_documents(question="What is RAG?", documents=docs)

# Stream response
for chunk in generator.stream_generate(question="What is RAG?", context=context):
    print(chunk, end="")
```

## CLI Reference

### Commands

#### ingest

Ingest documents into the vector store.

```bash
python -m ragapp ingest [OPTIONS]
```

**Options**:
- `--file FILE`, `-f FILE`: Specific file to ingest
- `--reset`, `-r`: Reset vector store before ingesting
- `--log-level LEVEL`: Set logging level (DEBUG, INFO, WARNING, ERROR)

**Examples**:
```bash
# Ingest all documents
python -m ragapp ingest

# Ingest specific file
python -m ragapp ingest --file data/documents/myfile.pdf

# Reset and ingest
python -m ragapp ingest --reset
```

#### query

Query the RAG system.

```bash
python -m ragapp query QUESTION [OPTIONS]
```

**Arguments**:
- `QUESTION`: The question to ask

**Options**:
- `--stream`, `-s`: Stream the response
- `--show-sources`: Show source documents
- `--verbose`, `-v`: Show verbose output
- `--log-level LEVEL`: Set logging level

**Examples**:
```bash
# Simple query
python -m ragapp query "What is RAG?"

# Stream response
python -m ragapp query "What is RAG?" --stream

# Show sources
python -m ragapp query "What is RAG?" --show-sources

# Verbose with sources
python -m ragapp query "What is RAG?" --show-sources --verbose
```

#### interactive

Start interactive query mode.

```bash
python -m ragapp interactive [OPTIONS]
```

**Options**:
- `--log-level LEVEL`: Set logging level

**Example**:
```bash
python -m ragapp interactive
```

#### stats

Show system statistics.

```bash
python -m ragapp stats [OPTIONS]
```

**Options**:
- `--log-level LEVEL`: Set logging level

**Example**:
```bash
python -m ragapp stats
```

## Environment Variables

All settings can be configured via environment variables or `.env` file:

```bash
# Required
OPENAI_API_KEY=sk-...

# Optional (with defaults shown)
OPENAI_MODEL=gpt-4-turbo-preview
EMBEDDING_MODEL=text-embedding-3-small
VECTOR_STORE_PATH=./data/vectorstore
COLLECTION_NAME=documents
DOCUMENTS_PATH=./data/documents
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_RESULTS=5
SIMILARITY_THRESHOLD=0.7
LOG_LEVEL=INFO
TEMPERATURE=0.7
MAX_TOKENS=1000
```
