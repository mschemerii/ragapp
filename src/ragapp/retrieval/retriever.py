"""Retrieval utilities for finding relevant documents."""

import logging
from typing import List

from langchain_core.documents import Document

from ragapp.retrieval.vector_store import VectorStore

logger = logging.getLogger(__name__)


class DocumentRetriever:
    """Retrieve relevant documents based on queries."""

    def __init__(
        self,
        vector_store: VectorStore,
        max_results: int = 5,
        similarity_threshold: float = 0.7,
    ) -> None:
        """Initialize the document retriever.

        Args:
            vector_store: Vector store instance
            max_results: Maximum number of results to return
            similarity_threshold: Minimum similarity score
        """
        self.vector_store = vector_store
        self.max_results = max_results
        self.similarity_threshold = similarity_threshold

    def retrieve(self, query: str, k: int | None = None) -> List[Document]:
        """Retrieve relevant documents for a query.

        Args:
            query: Search query
            k: Number of results (overrides default max_results)

        Returns:
            List of relevant documents
        """
        num_results = k or self.max_results

        logger.info(f"Retrieving documents for query: {query[:100]}...")

        documents = self.vector_store.similarity_search(
            query=query,
            k=num_results,
            score_threshold=self.similarity_threshold,
        )

        logger.info(f"Retrieved {len(documents)} documents")
        return documents

    def retrieve_with_scores(
        self,
        query: str,
        k: int | None = None,
    ) -> List[tuple[Document, float]]:
        """Retrieve documents with similarity scores.

        Args:
            query: Search query
            k: Number of results

        Returns:
            List of (document, score) tuples
        """
        num_results = k or self.max_results

        if self.vector_store.vector_store is None:
            self.vector_store.create_or_load()

        results = self.vector_store.vector_store.similarity_search_with_relevance_scores(  # type: ignore[union-attr]
            query, k=num_results
        )

        # Filter by threshold
        filtered_results = [
            (doc, score) for doc, score in results if score >= self.similarity_threshold
        ]

        logger.info(
            f"Retrieved {len(filtered_results)} documents with scores above {self.similarity_threshold}"
        )
        return filtered_results

    def format_context(self, documents: List[Document]) -> str:
        """Format retrieved documents into a context string.

        Args:
            documents: List of documents

        Returns:
            Formatted context string
        """
        if not documents:
            return "No relevant documents found."

        context_parts = []
        for idx, doc in enumerate(documents, 1):
            source = doc.metadata.get("source", "Unknown")
            content = doc.page_content.strip()
            context_parts.append(f"[Document {idx}] Source: {source}\n{content}")

        return "\n\n".join(context_parts)
