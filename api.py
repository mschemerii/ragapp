"""FastAPI backend for the RAG application.

Run with: uvicorn api:app --reload
"""

import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from ragapp import RAGPipeline

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="RAG Document Q&A API",
    description="API for Retrieval-Augmented Generation document question answering",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for web UI
static_path = Path(__file__).parent / "static"
static_path.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Initialize RAG pipeline
try:
    pipeline = RAGPipeline()
    logger.info("RAG pipeline initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize RAG pipeline: {e}")
    pipeline = None


# Request/Response models
class QueryRequest(BaseModel):
    """Request model for query endpoint."""

    question: str = Field(..., description="Question to ask", min_length=1)
    return_sources: bool = Field(
        default=False,
        description="Whether to return source documents",
    )
    max_sources: int = Field(
        default=5,
        description="Maximum number of source documents to return",
        ge=1,
        le=20,
    )


class SourceDocument(BaseModel):
    """Model for source document information."""

    source: str = Field(..., description="Source file path")
    content: str = Field(..., description="Document content")
    chunk_id: int | None = Field(None, description="Chunk ID")
    chunk_size: int | None = Field(None, description="Chunk size in characters")


class QueryResponse(BaseModel):
    """Response model for query endpoint."""

    answer: str = Field(..., description="Generated answer")
    sources: list[SourceDocument] | None = Field(
        None,
        description="Source documents used for the answer",
    )
    question: str = Field(..., description="Original question")


class StatsResponse(BaseModel):
    """Response model for stats endpoint."""

    documents_in_store: int = Field(..., description="Number of document chunks in vector store")
    source_files: int = Field(..., description="Number of source files")


class IngestRequest(BaseModel):
    """Request model for ingest endpoint."""

    file_path: str | None = Field(None, description="Specific file to ingest")
    reset: bool = Field(False, description="Reset vector store before ingesting")


class IngestResponse(BaseModel):
    """Response model for ingest endpoint."""

    chunks_ingested: int = Field(..., description="Number of chunks ingested")
    message: str = Field(..., description="Status message")


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str = Field(..., description="Health status")
    pipeline_initialized: bool = Field(..., description="Whether pipeline is initialized")


# Endpoints
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the web UI."""
    html_path = static_path / "index.html"
    if html_path.exists():
        return html_path.read_text()
    return """
    <html>
        <head><title>RAG API</title></head>
        <body>
            <h1>RAG Document Q&A API</h1>
            <p>API is running. Visit <a href="/docs">/docs</a> for API documentation.</p>
            <p>Web UI is available at <a href="/static/index.html">/static/index.html</a></p>
        </body>
    </html>
    """


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy" if pipeline is not None else "unhealthy",
        pipeline_initialized=pipeline is not None,
    )


@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get system statistics."""
    if pipeline is None:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")

    try:
        stats = pipeline.get_stats()
        return StatsResponse(
            documents_in_store=stats["documents_in_store"],
            source_files=stats["source_files"],
        )
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}") from e


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """Query the RAG system."""
    if pipeline is None:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")

    try:
        logger.info(f"Processing query: {request.question[:100]}...")

        if request.return_sources:
            answer, sources = pipeline.query(
                request.question,
                return_sources=True,
            )

            source_docs = [
                SourceDocument(
                    source=doc.metadata.get("source", "Unknown"),
                    content=doc.page_content,
                    chunk_id=doc.metadata.get("chunk_id"),
                    chunk_size=doc.metadata.get("chunk_size"),
                )
                for doc in sources[: request.max_sources]
            ]

            return QueryResponse(
                answer=answer,
                sources=source_docs,
                question=request.question,
            )
        else:
            answer = pipeline.query(request.question)
            return QueryResponse(
                answer=answer,
                sources=None,
                question=request.question,
            )

    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}") from e


@app.post("/query/stream")
async def query_stream(request: QueryRequest):
    """Stream query response."""
    if pipeline is None:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")

    async def generate():
        try:
            for chunk in pipeline.stream_query(request.question):
                yield chunk
        except Exception as e:
            logger.error(f"Error streaming query: {e}")
            yield f"\n\nError: {str(e)}"

    return StreamingResponse(generate(), media_type="text/plain")


@app.post("/ingest", response_model=IngestResponse)
async def ingest_documents(request: IngestRequest):
    """Ingest documents into the vector store."""
    if pipeline is None:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")

    try:
        file_path = Path(request.file_path) if request.file_path else None

        # Run ingestion
        count = pipeline.ingest_documents(
            file_path=file_path,
            reset=request.reset,
        )

        message = f"Successfully ingested {count} document chunks"
        if request.reset:
            message += " (vector store was reset)"

        logger.info(message)

        return IngestResponse(
            chunks_ingested=count,
            message=message,
        )

    except Exception as e:
        logger.error(f"Error ingesting documents: {e}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}") from e


@app.delete("/vector-store")
async def reset_vector_store():
    """Reset the vector store (delete all data)."""
    if pipeline is None:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")

    try:
        pipeline.reset_vector_store()
        return {"message": "Vector store reset successfully"}
    except Exception as e:
        logger.error(f"Error resetting vector store: {e}")
        raise HTTPException(status_code=500, detail=f"Reset failed: {str(e)}") from e


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
