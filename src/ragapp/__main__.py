"""Main entry point for the RAG application."""

import argparse
import logging
import sys
from pathlib import Path

from ragapp import __version__
from ragapp.pipeline import RAGPipeline


def setup_logging(level: str = "INFO") -> None:
    """Configure logging for the application.

    Args:
        level: Logging level
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def cmd_ingest(args: argparse.Namespace) -> int:
    """Run document ingestion command.

    Args:
        args: Command arguments

    Returns:
        Exit code
    """
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)

    try:
        pipeline = RAGPipeline()

        file_path = Path(args.file) if args.file else None
        count = pipeline.ingest_documents(file_path=file_path, reset=args.reset)

        logger.info(f"Successfully ingested {count} document chunks")
        stats = pipeline.get_stats()
        logger.info(f"Vector store now contains {stats['documents_in_store']} chunks")

        return 0

    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        return 1


def cmd_query(args: argparse.Namespace) -> int:
    """Run query command.

    Args:
        args: Command arguments

    Returns:
        Exit code
    """
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)

    try:
        pipeline = RAGPipeline()

        if args.stream:
            # Stream response
            print("\nAnswer: ", end="", flush=True)
            for chunk in pipeline.stream_query(args.question):
                print(chunk, end="", flush=True)
            print("\n")
        else:
            # Regular response
            answer, sources = pipeline.query(args.question, return_sources=True)
            print(f"\nQuestion: {args.question}")
            print(f"\nAnswer: {answer}")

            if args.show_sources:
                print("\n--- Sources ---")
                for idx, doc in enumerate(sources, 1):
                    source = doc.metadata.get("source", "Unknown")
                    print(f"\n[{idx}] {source}")
                    if args.verbose:
                        print(f"Content: {doc.page_content[:200]}...")

        return 0

    except Exception as e:
        logger.error(f"Query failed: {e}")
        return 1


def cmd_stats(args: argparse.Namespace) -> int:
    """Show statistics command.

    Args:
        args: Command arguments

    Returns:
        Exit code
    """
    setup_logging(args.log_level)

    try:
        pipeline = RAGPipeline()
        stats = pipeline.get_stats()

        print("\n=== RAG Application Statistics ===")
        print(f"Source files in directory: {stats['source_files']}")
        print(f"Document chunks in vector store: {stats['documents_in_store']}")
        print()

        return 0

    except Exception as e:
        print(f"Error getting stats: {e}")
        return 1


def cmd_interactive(args: argparse.Namespace) -> int:
    """Run interactive query mode.

    Args:
        args: Command arguments

    Returns:
        Exit code
    """
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)

    try:
        pipeline = RAGPipeline()
        stats = pipeline.get_stats()

        print("\n=== RAG Application Interactive Mode ===")
        print(f"Vector store contains {stats['documents_in_store']} document chunks")
        print("Type 'quit' or 'exit' to leave\n")

        while True:
            try:
                question = input("Question: ").strip()

                if question.lower() in ["quit", "exit", "q"]:
                    print("Goodbye!")
                    break

                if not question:
                    continue

                print("\nAnswer: ", end="", flush=True)
                for chunk in pipeline.stream_query(question):
                    print(chunk, end="", flush=True)
                print("\n")

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except EOFError:
                break

        return 0

    except Exception as e:
        logger.error(f"Interactive mode failed: {e}")
        return 1


def main() -> int:
    """Main function to run the RAG application."""
    parser = argparse.ArgumentParser(
        description="RAG Application - Retrieval-Augmented Generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Set logging level",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Ingest command
    ingest_parser = subparsers.add_parser("ingest", help="Ingest documents into vector store")
    ingest_parser.add_argument(
        "--file", "-f", help="Specific file to ingest (ingests all if not specified)"
    )
    ingest_parser.add_argument(
        "--reset", "-r", action="store_true", help="Reset vector store before ingesting"
    )
    ingest_parser.set_defaults(func=cmd_ingest)

    # Query command
    query_parser = subparsers.add_parser("query", help="Query the RAG system")
    query_parser.add_argument("question", help="Question to ask")
    query_parser.add_argument("--stream", "-s", action="store_true", help="Stream the response")
    query_parser.add_argument("--show-sources", action="store_true", help="Show source documents")
    query_parser.add_argument("--verbose", "-v", action="store_true", help="Show verbose output")
    query_parser.set_defaults(func=cmd_query)

    # Interactive command
    interactive_parser = subparsers.add_parser("interactive", help="Start interactive query mode")
    interactive_parser.set_defaults(func=cmd_interactive)

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show system statistics")
    stats_parser.set_defaults(func=cmd_stats)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
