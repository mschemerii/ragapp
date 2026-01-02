"""Advanced programmatic usage of the RAG application."""

import logging
from pathlib import Path

from ragapp import RAGPipeline, Settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Example 1: Custom settings
print("Example 1: Using Custom Settings")
print("=" * 50)

custom_settings = Settings(
    openai_api_key="your-api-key-here",
    openai_model="gpt-4-turbo-preview",
    embedding_model="text-embedding-3-small",
    chunk_size=500,
    chunk_overlap=50,
    max_results=3,
    temperature=0.5,
)

pipeline = RAGPipeline(settings=custom_settings)
logger.info("Pipeline initialized with custom settings")

# Example 2: Ingest specific documents
print("\nExample 2: Ingesting Specific Documents")
print("=" * 50)

documents_path = Path("data/documents")
if documents_path.exists():
    # Get list of files
    files = list(documents_path.glob("*.txt")) + list(documents_path.glob("*.pdf"))

    if files:
        # Ingest the first file as an example
        first_file = files[0]
        logger.info(f"Ingesting: {first_file}")
        chunks = pipeline.ingest_documents(file_path=first_file)
        logger.info(f"Ingested {chunks} chunks from {first_file.name}")
    else:
        logger.warning("No documents found in data/documents/")
else:
    logger.warning("Documents directory does not exist")

# Example 3: Query with detailed analysis
print("\nExample 3: Detailed Query Analysis")
print("=" * 50)

question = "What are the key concepts discussed in the documents?"

# Get answer with sources
answer, sources = pipeline.query(question, return_sources=True)

print(f"\nQuestion: {question}")
print(f"\nAnswer:\n{answer}")
print("\n--- Source Analysis ---")
print(f"Number of sources: {len(sources)}")

for idx, doc in enumerate(sources, 1):
    source_file = doc.metadata.get("source", "Unknown")
    chunk_id = doc.metadata.get("chunk_id", "N/A")
    chunk_size = doc.metadata.get("chunk_size", 0)

    print(f"\n[Source {idx}]")
    print(f"  File: {source_file}")
    print(f"  Chunk ID: {chunk_id}")
    print(f"  Chunk Size: {chunk_size} characters")
    print(f"  Preview: {doc.page_content[:150]}...")

# Example 4: Multiple queries
print("\nExample 4: Batch Queries")
print("=" * 50)

questions = [
    "What is the main topic?",
    "Are there any examples provided?",
    "What are the conclusions?",
]

for i, q in enumerate(questions, 1):
    print(f"\nQuery {i}: {q}")
    answer = pipeline.query(q)
    print(f"Answer: {answer[:200]}..." if len(answer) > 200 else f"Answer: {answer}")

logger.info("All examples completed successfully")
