"""Main entry point for the RAG application."""

import sys


def main() -> int:
    """Main function to run the RAG application."""
    print("RAG Application v0.1.0")
    print("=" * 50)
    print("\nWelcome to the RAG Application!")
    print("This application provides intelligent document search and Q&A.")
    print("\nTo get started:")
    print("1. Add documents to the data/documents/ directory")
    print("2. Configure your .env file with API keys")
    print("3. Run document ingestion")
    print("4. Start querying your documents")
    print("\nFor more information, see README.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
