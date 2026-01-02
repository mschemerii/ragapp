"""Response generation using LLMs."""

import logging
from typing import Literal

from langchain_community.llms import Ollama
from langchain_core.documents import Document
from langchain_core.language_models import BaseLLM
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI

from ragapp.generation.prompts import CONVERSATIONAL_RAG_PROMPT, RAG_CHAT_PROMPT

logger = logging.getLogger(__name__)


class ResponseGenerator:
    """Generate responses using LLMs based on retrieved context."""

    def __init__(
        self,
        provider: Literal["openai", "ollama"] = "ollama",
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = 1000,
        openai_api_key: str | None = None,
        ollama_base_url: str = "http://localhost:11434",
    ) -> None:
        """Initialize the response generator.

        Args:
            provider: LLM provider ("openai" or "ollama")
            model: Model name (provider-specific)
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            openai_api_key: OpenAI API key (required for OpenAI)
            ollama_base_url: Ollama server URL (for Ollama)
        """
        self.provider = provider
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Initialize the appropriate LLM
        if provider == "openai":
            if not model:
                model = "gpt-4-turbo-preview"
            self.llm: BaseLLM = ChatOpenAI(
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                openai_api_key=openai_api_key,
            )
            logger.info(f"Initialized OpenAI generator with model: {model}")

        elif provider == "ollama":
            if not model:
                model = "llama3.2"
            self.llm = Ollama(
                model=model,
                temperature=temperature,
                base_url=ollama_base_url,
            )
            logger.info(
                f"Initialized Ollama generator with model: {model} at {ollama_base_url}"
            )

        else:
            raise ValueError(f"Unsupported provider: {provider}")

        self.model = model

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
            if self.provider == "openai":
                # Use chat prompt for OpenAI
                if chat_history:
                    prompt = CONVERSATIONAL_RAG_PROMPT
                    response = self.llm.invoke(
                        prompt.format_messages(
                            context=context,
                            question=question,
                            chat_history=chat_history,
                        )
                    )
                else:
                    prompt = RAG_CHAT_PROMPT
                    response = self.llm.invoke(
                        prompt.format_messages(
                            context=context,
                            question=question,
                        )
                    )
                answer = response.content

            else:  # Ollama
                # Format prompt as plain text for Ollama
                prompt_text = f"""Context information:
{context}

Question: {question}

Based on the context above, please provide a detailed answer to the question. If the context doesn't contain the information needed to answer the question, please say so."""

                answer = self.llm.invoke(prompt_text)

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
            if self.provider == "openai":
                # Use chat prompt for OpenAI
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

            else:  # Ollama
                # Format prompt as plain text for Ollama
                prompt_text = f"""Context information:
{context}

Question: {question}

Based on the context above, please provide a detailed answer to the question. If the context doesn't contain the information needed to answer the question, please say so."""

                for chunk in self.llm.stream(prompt_text):
                    yield chunk

        except Exception as e:
            logger.error(f"Error streaming response: {e}")
            raise
