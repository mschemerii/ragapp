"""Tests for ingestion module."""

from ragapp.ingestion import DocumentLoader, DocumentProcessor


def test_document_loader_initialization(tmp_path):
    """Test DocumentLoader can be initialized."""
    loader = DocumentLoader(tmp_path)
    assert loader.documents_path == tmp_path


def test_document_loader_supported_extensions():
    """Test supported file extensions."""
    expected_extensions = {".txt", ".md", ".pdf", ".docx"}
    assert set(DocumentLoader.SUPPORTED_EXTENSIONS.keys()) == expected_extensions


def test_document_processor_initialization():
    """Test DocumentProcessor can be initialized."""
    processor = DocumentProcessor(chunk_size=1000, chunk_overlap=200)
    assert processor.chunk_size == 1000
    assert processor.chunk_overlap == 200


def test_document_processor_with_empty_list():
    """Test processing empty document list."""
    processor = DocumentProcessor()
    result = processor.process_documents([])
    assert result == []


def test_get_file_count_empty_directory(tmp_path):
    """Test file count in empty directory."""
    loader = DocumentLoader(tmp_path)
    count = loader.get_file_count()
    assert count == 0


def test_get_file_count_with_files(tmp_path):
    """Test file count with supported files."""
    # Create test files
    (tmp_path / "test.txt").write_text("test content")
    (tmp_path / "test.md").write_text("# Test")
    (tmp_path / "test.pdf").write_bytes(b"fake pdf")

    loader = DocumentLoader(tmp_path)
    count = loader.get_file_count()
    assert count == 3
