"""Basic usage example for the RAG application."""

import logging

from ragapp import RAGPipeline

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize the pipeline
pipeline = RAGPipeline()

# Example 1: Ingest documents
print("=" * 50)
print("Example 1: Ingesting Documents")
print("=" * 50)

# Ingest all documents from the data/documents directory
num_chunks = pipeline.ingest_documents(reset=True)
print(f"\nIngested {num_chunks} document chunks")

# Example 2: Get statistics
print("\n" + "=" * 50)
print("Example 2: System Statistics")
print("=" * 50)

stats = pipeline.get_stats()
print(f"\nSource files: {stats['source_files']}")
print(f"Document chunks in vector store: {stats['documents_in_store']}")

# Example 3: Query the system
print("\n" + "=" * 50)
print("Example 3: Querying the System")
print("=" * 50)

question = "What is this document about?"
answer, sources = pipeline.query(question, return_sources=True)

print(f"\nQuestion: {question}")
print(f"\nAnswer: {answer}")
print(f"\nNumber of source documents used: {len(sources)}")

# Example 4: Stream a query
print("\n" + "=" * 50)
print("Example 4: Streaming Query")
print("=" * 50)

question = "Can you summarize the main points?"
print(f"\nQuestion: {question}")
print("\nAnswer (streaming): ", end="", flush=True)

for chunk in pipeline.stream_query(question):
    print(chunk, end="", flush=True)

print("\n")
