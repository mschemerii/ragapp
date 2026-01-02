"""Response generation using LLMs."""

import logging

from langchain_core.documents import Document
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI

from ragapp.generation.prompts import CONVERSATIONAL_RAG_PROMPT, RAG_CHAT_PROMPT

logger = logging.getLogger(__name__)


class ResponseGenerator:
    """Generate responses using LLMs based on retrieved context."""

    def __init__(
        self,
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.7,
        max_tokens: int | None = 1000,
        openai_api_key: str | None = None,
    ) -> None:
        """Initialize the response generator.

        Args:
            model: OpenAI model name
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            openai_api_key: OpenAI API key
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            openai_api_key=openai_api_key,
        )

        logger.info(f"Initialized generator with model: {model}")

    def generate(
        self,
        question: str,
        context: str,
        chat_history: list[BaseMessage] | None = None,
    ) -> str:
        """Generate a response based on context.

        Args:
            question: User's question
            context: Retrieved context from documents
            chat_history: Optional chat history for conversational context

        Returns:
            Generated response
        """
        try:
            if chat_history:
                # Use conversational prompt with history
                prompt = CONVERSATIONAL_RAG_PROMPT
                response = self.llm.invoke(
                    prompt.format_messages(
                        context=context,
                        question=question,
                        chat_history=chat_history,
                    )
                )
            else:
                # Use standard RAG prompt
                prompt = RAG_CHAT_PROMPT
                response = self.llm.invoke(
                    prompt.format_messages(
                        context=context,
                        question=question,
                    )
                )

            answer = response.content
            logger.info(f"Generated response of length: {len(str(answer))}")
            return str(answer)

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise

    def generate_from_documents(
        self,
        question: str,
        documents: list[Document],
        chat_history: list[BaseMessage] | None = None,
    ) -> str:
        """Generate a response from retrieved documents.

        Args:
            question: User's question
            documents: Retrieved documents
            chat_history: Optional chat history

        Returns:
            Generated response
        """
        # Format documents into context
        context = self._format_documents(documents)

        return self.generate(question, context, chat_history)

    def _format_documents(self, documents: list[Document]) -> str:
        """Format documents into a context string.

        Args:
            documents: List of documents

        Returns:
            Formatted context string
        """
        if not documents:
            return "No relevant information found in the knowledge base."

        context_parts = []
        for idx, doc in enumerate(documents, 1):
            source = doc.metadata.get("source", "Unknown")
            content = doc.page_content.strip()
            context_parts.append(f"--- Document {idx} (Source: {source}) ---\n{content}")

        return "\n\n".join(context_parts)

    def stream_generate(
        self,
        question: str,
        context: str,
        chat_history: list[BaseMessage] | None = None,
    ):
        """Stream generate a response (generator function).

        Args:
            question: User's question
            context: Retrieved context
            chat_history: Optional chat history

        Yields:
            Chunks of the generated response
        """
        try:
            if chat_history:
                prompt = CONVERSATIONAL_RAG_PROMPT
                messages = prompt.format_messages(
                    context=context,
                    question=question,
                    chat_history=chat_history,
                )
            else:
                prompt = RAG_CHAT_PROMPT
                messages = prompt.format_messages(
                    context=context,
                    question=question,
                )

            for chunk in self.llm.stream(messages):
                if chunk.content:
                    yield chunk.content

        except Exception as e:
            logger.error(f"Error streaming response: {e}")
            raise
