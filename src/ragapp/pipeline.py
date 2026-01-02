"""RAG Pipeline orchestration."""

import logging
from pathlib import Path

from langchain_core.documents import Document
from langchain_core.messages import BaseMessage

from ragapp.config import Settings, get_settings
from ragapp.generation import ResponseGenerator
from ragapp.ingestion import DocumentLoader, DocumentProcessor
from ragapp.retrieval import DocumentRetriever, VectorStore

logger = logging.getLogger(__name__)


class RAGPipeline:
    """Complete RAG pipeline for document ingestion, retrieval, and generation."""

    def __init__(self, settings: Settings | None = None) -> None:
        """Initialize the RAG pipeline.

        Args:
            settings: Application settings (uses defaults if not provided)
        """
        self.settings = settings or get_settings()

        # Initialize components
        self.document_loader = DocumentLoader(self.settings.documents_path)
        self.document_processor = DocumentProcessor(
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
        )
        self.vector_store = VectorStore(
            store_path=self.settings.vector_store_path,
            collection_name=self.settings.collection_name,
            embedding_model=self.settings.embedding_model,
            openai_api_key=self.settings.openai_api_key,
        )
        self.retriever = DocumentRetriever(
            vector_store=self.vector_store,
            max_results=self.settings.max_results,
            similarity_threshold=self.settings.similarity_threshold,
        )
        self.generator = ResponseGenerator(
            model=self.settings.openai_model,
            temperature=self.settings.temperature,
            max_tokens=self.settings.max_tokens,
            openai_api_key=self.settings.openai_api_key,
        )

        logger.info("RAG Pipeline initialized")

    def ingest_documents(
        self,
        file_path: Path | None = None,
        reset: bool = False,
    ) -> int:
        """Ingest documents into the vector store.

        Args:
            file_path: Optional specific file to ingest (ingests all if None)
            reset: Whether to reset the vector store before ingestion

        Returns:
            Number of document chunks ingested
        """
        logger.info("Starting document ingestion...")

        # Reset vector store if requested
        if reset:
            logger.info("Resetting vector store...")
            self.vector_store.reset()

        # Load documents
        if file_path:
            logger.info(f"Loading document: {file_path}")
            documents = self.document_loader.load_document(file_path)
        else:
            logger.info(f"Loading all documents from {self.settings.documents_path}")
            documents = self.document_loader.load_directory()

        if not documents:
            logger.warning("No documents found to ingest")
            return 0

        # Process documents
        processed_docs = self.document_processor.process_documents(documents)

        # Add to vector store
        self.vector_store.add_documents(processed_docs)

        logger.info(f"Ingestion complete: {len(processed_docs)} chunks added")
        return len(processed_docs)

    def query(
        self,
        question: str,
        chat_history: list[BaseMessage] | None = None,
        return_sources: bool = False,
    ) -> str | tuple[str, list[Document]]:
        """Query the RAG system.

        Args:
            question: User's question
            chat_history: Optional conversation history
            return_sources: Whether to return source documents

        Returns:
            Generated answer, or (answer, sources) if return_sources is True
        """
        logger.info(f"Processing query: {question[:100]}...")

        # Retrieve relevant documents
        documents = self.retriever.retrieve(question)

        if not documents:
            response = "I couldn't find any relevant information to answer your question."
            return (response, []) if return_sources else response

        # Generate response
        response = self.generator.generate_from_documents(
            question=question,
            documents=documents,
            chat_history=chat_history,
        )

        if return_sources:
            return response, documents
        return response

    def stream_query(
        self,
        question: str,
        chat_history: list[BaseMessage] | None = None,
    ):
        """Stream query response.

        Args:
            question: User's question
            chat_history: Optional conversation history

        Yields:
            Chunks of the generated response
        """
        logger.info(f"Streaming query: {question[:100]}...")

        # Retrieve relevant documents
        documents = self.retriever.retrieve(question)

        if not documents:
            yield "I couldn't find any relevant information to answer your question."
            return

        # Format context
        context = self.retriever.format_context(documents)

        # Stream response
        yield from self.generator.stream_generate(
            question=question,
            context=context,
            chat_history=chat_history,
        )

    def get_stats(self) -> dict[str, int]:
        """Get statistics about the RAG system.

        Returns:
            Dictionary with system statistics
        """
        return {
            "documents_in_store": self.vector_store.get_document_count(),
            "source_files": self.document_loader.get_file_count(),
        }

    def reset_vector_store(self) -> None:
        """Reset the vector store (delete all data)."""
        logger.warning("Resetting vector store - all data will be deleted")
        self.vector_store.reset()
        logger.info("Vector store reset complete")
