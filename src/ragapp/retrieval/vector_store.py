"""Vector store management using ChromaDB."""

import logging
from pathlib import Path
from typing import List, Optional

from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings

logger = logging.getLogger(__name__)


class VectorStore:
    """Manage vector storage and retrieval using ChromaDB."""

    def __init__(
        self,
        store_path: Path,
        collection_name: str,
        embedding_model: str = "text-embedding-3-small",
        openai_api_key: Optional[str] = None,
    ) -> None:
        """Initialize the vector store.

        Args:
            store_path: Path to store vector database
            collection_name: Name of the ChromaDB collection
            embedding_model: OpenAI embedding model name
            openai_api_key: OpenAI API key
        """
        self.store_path = store_path
        self.collection_name = collection_name

        # Initialize embeddings
        self.embeddings: Embeddings = OpenAIEmbeddings(
            model=embedding_model,
            openai_api_key=openai_api_key,
        )

        # Initialize or load vector store
        self.vector_store: Optional[Chroma] = None

    def create_or_load(self) -> Chroma:
        """Create a new vector store or load existing one.

        Returns:
            ChromaDB vector store instance
        """
        try:
            self.vector_store = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=str(self.store_path),
            )
            count = self.get_document_count()
            logger.info(f"Loaded vector store with {count} documents")
            return self.vector_store
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            raise

    def add_documents(
        self,
        documents: List[Document],
        batch_size: int = 100,
    ) -> None:
        """Add documents to the vector store.

        Args:
            documents: List of documents to add
            batch_size: Number of documents to process in each batch
        """
        if not documents:
            logger.warning("No documents to add")
            return

        if self.vector_store is None:
            self.create_or_load()

        try:
            # Process in batches to avoid memory issues
            for i in range(0, len(documents), batch_size):
                batch = documents[i : i + batch_size]
                self.vector_store.add_documents(batch)  # type: ignore[union-attr]
                logger.info(f"Added batch {i // batch_size + 1} ({len(batch)} docs)")

            logger.info(f"Successfully added {len(documents)} documents to vector store")
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise

    def similarity_search(
        self,
        query: str,
        k: int = 5,
        score_threshold: Optional[float] = None,
    ) -> List[Document]:
        """Search for similar documents.

        Args:
            query: Search query
            k: Number of results to return
            score_threshold: Minimum similarity score (0-1)

        Returns:
            List of similar documents
        """
        if self.vector_store is None:
            self.create_or_load()

        try:
            if score_threshold is not None:
                # Use similarity search with score threshold
                results = self.vector_store.similarity_search_with_relevance_scores(  # type: ignore[union-attr]
                    query, k=k
                )
                # Filter by threshold
                filtered_results = [
                    doc for doc, score in results if score >= score_threshold
                ]
                logger.info(
                    f"Found {len(filtered_results)} documents above threshold {score_threshold}"
                )
                return filtered_results
            else:
                # Standard similarity search
                results = self.vector_store.similarity_search(query, k=k)  # type: ignore[union-attr]
                logger.info(f"Found {len(results)} similar documents")
                return results
        except Exception as e:
            logger.error(f"Error during similarity search: {e}")
            raise

    def get_document_count(self) -> int:
        """Get the total number of documents in the vector store.

        Returns:
            Number of documents
        """
        if self.vector_store is None:
            return 0

        try:
            collection = self.vector_store._collection
            return collection.count()
        except Exception as e:
            logger.warning(f"Could not get document count: {e}")
            return 0

    def delete_collection(self) -> None:
        """Delete the entire collection."""
        if self.vector_store is not None:
            try:
                self.vector_store.delete_collection()
                logger.info(f"Deleted collection: {self.collection_name}")
                self.vector_store = None
            except Exception as e:
                logger.error(f"Error deleting collection: {e}")
                raise

    def reset(self) -> None:
        """Reset the vector store by deleting and recreating."""
        self.delete_collection()
        self.create_or_load()
        logger.info("Vector store reset complete")
