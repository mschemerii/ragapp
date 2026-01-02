# Getting Started with RAG Applications

## Quick Start Guide

This guide will help you get up and running with a RAG application in just a few steps.

### Prerequisites

Before you begin, ensure you have:

- Python 3.10 or higher installed
- An OpenAI API key (or alternative LLM provider)
- Basic familiarity with command line tools

### Installation Steps

1. **Install the package**
   ```bash
   pip install -e .
   ```

2. **Set up environment variables**
   Create a `.env` file with your configuration:
   ```
   OPENAI_API_KEY=your-key-here
   OPENAI_MODEL=gpt-4-turbo-preview
   ```

3. **Add your documents**
   Place documents in the `data/documents/` directory. Supported formats include:
   - Plain text (.txt)
   - PDF (.pdf)
   - Word documents (.docx)
   - Markdown (.md)

4. **Ingest documents**
   ```bash
   python -m ragapp ingest --reset
   ```

5. **Start querying**
   ```bash
   python -m ragapp query "What is RAG?"
   ```

### Usage Examples

#### Command Line Interface

Check statistics:
```bash
python -m ragapp stats
```

Interactive mode:
```bash
python -m ragapp interactive
```

Query with source attribution:
```bash
python -m ragapp query "Explain vector embeddings" --show-sources
```

#### Programmatic Usage

```python
from ragapp import RAGPipeline

# Initialize the pipeline
pipeline = RAGPipeline()

# Ingest documents
pipeline.ingest_documents()

# Query the system
answer = pipeline.query("What are the benefits of RAG?")
print(answer)
```

### Tips for Success

1. **Document Quality**: Ensure your documents are well-formatted and contain accurate information
2. **Chunking**: Experiment with different chunk sizes for optimal retrieval
3. **Prompts**: Customize prompts to match your specific use case
4. **Evaluation**: Test with a variety of queries to ensure good performance

### Troubleshooting

**No documents found:**
- Verify documents are in `data/documents/`
- Check file extensions are supported

**Low quality answers:**
- Try adjusting similarity threshold
- Increase number of retrieved documents
- Improve document quality and structure

**API errors:**
- Verify your API key is correctly set
- Check your API rate limits and quotas

For more detailed information, refer to the full documentation.
