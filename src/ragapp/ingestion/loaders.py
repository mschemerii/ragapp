"""Document loaders for various file formats."""

import logging
from pathlib import Path

from langchain_community.document_loaders import (
    DirectoryLoader,
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
)
from langchain_community.document_loaders.word_document import Docx2txtLoader
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class DocumentLoader:
    """Load documents from various file formats."""

    SUPPORTED_EXTENSIONS = {
        ".txt": TextLoader,
        ".md": UnstructuredMarkdownLoader,
        ".pdf": PyPDFLoader,
        ".docx": Docx2txtLoader,
    }

    def __init__(self, documents_path: Path) -> None:
        """Initialize the document loader.

        Args:
            documents_path: Path to the documents directory
        """
        self.documents_path = documents_path

    def load_document(self, file_path: Path) -> list[Document]:
        """Load a single document.

        Args:
            file_path: Path to the document file

        Returns:
            List of loaded documents

        Raises:
            ValueError: If file format is not supported
        """
        suffix = file_path.suffix.lower()

        if suffix not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file format: {suffix}. "
                f"Supported formats: {list(self.SUPPORTED_EXTENSIONS.keys())}"
            )

        loader_class = self.SUPPORTED_EXTENSIONS[suffix]
        loader = loader_class(str(file_path))

        try:
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} documents from {file_path}")
            return documents
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            raise

    def load_directory(self) -> list[Document]:
        """Load all supported documents from a directory.

        Returns:
            List of all loaded documents
        """
        all_documents: list[Document] = []

        for extension, loader_class in self.SUPPORTED_EXTENSIONS.items():
            try:
                pattern = f"**/*{extension}"
                loader = DirectoryLoader(
                    str(self.documents_path),
                    glob=pattern,
                    loader_cls=loader_class,
                    show_progress=True,
                    use_multithreading=True,
                )
                documents = loader.load()
                all_documents.extend(documents)
                logger.info(f"Loaded {len(documents)} documents with extension {extension}")
            except Exception as e:
                logger.warning(f"Error loading {extension} files: {e}")
                continue

        logger.info(f"Total documents loaded: {len(all_documents)}")
        return all_documents

    def get_file_count(self) -> int:
        """Get the count of supported files in the documents directory.

        Returns:
            Number of supported files
        """
        count = 0
        for extension in self.SUPPORTED_EXTENSIONS:
            count += len(list(self.documents_path.glob(f"**/*{extension}")))
        return count
