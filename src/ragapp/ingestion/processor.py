"""Document processing and chunking utilities."""

import logging
from typing import List

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Process and chunk documents for vector storage."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200) -> None:
        """Initialize the document processor.

        Args:
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def process_documents(self, documents: List[Document]) -> List[Document]:
        """Process and chunk documents.

        Args:
            documents: List of documents to process

        Returns:
            List of processed and chunked documents
        """
        if not documents:
            logger.warning("No documents to process")
            return []

        # Clean documents
        cleaned_docs = self._clean_documents(documents)

        # Split into chunks
        chunked_docs = self.text_splitter.split_documents(cleaned_docs)

        # Add metadata
        processed_docs = self._add_chunk_metadata(chunked_docs)

        logger.info(
            f"Processed {len(documents)} documents into {len(processed_docs)} chunks"
        )
        return processed_docs

    def _clean_documents(self, documents: List[Document]) -> List[Document]:
        """Clean document content.

        Args:
            documents: Documents to clean

        Returns:
            Cleaned documents
        """
        cleaned = []
        for doc in documents:
            # Remove excessive whitespace
            content = " ".join(doc.page_content.split())

            # Skip empty documents
            if not content.strip():
                logger.debug(f"Skipping empty document: {doc.metadata.get('source')}")
                continue

            doc.page_content = content
            cleaned.append(doc)

        return cleaned

    def _add_chunk_metadata(self, documents: List[Document]) -> List[Document]:
        """Add chunk-specific metadata to documents.

        Args:
            documents: Documents to add metadata to

        Returns:
            Documents with added metadata
        """
        for idx, doc in enumerate(documents):
            doc.metadata["chunk_id"] = idx
            doc.metadata["chunk_size"] = len(doc.page_content)

        return documents
