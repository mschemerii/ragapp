"""Prompt templates for RAG generation."""

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

# System prompt for RAG
RAG_SYSTEM_PROMPT = """You are a helpful AI assistant that answers questions based on the provided context.

Your guidelines:
1. Answer questions using ONLY the information from the provided context
2. If the context doesn't contain enough information to answer the question, say so
3. Be concise but thorough in your responses
4. Cite specific parts of the context when relevant
5. If asked about something not in the context, clearly state that you don't have that information

Always maintain accuracy and never make up information not present in the context."""

# RAG prompt template
RAG_PROMPT_TEMPLATE = """Context information:
{context}

Question: {question}

Based on the context above, please provide a detailed answer to the question. If the context doesn't contain the information needed to answer the question, please say so."""

# Create prompt templates
RAG_PROMPT = PromptTemplate(
    template=RAG_PROMPT_TEMPLATE,
    input_variables=["context", "question"],
)

RAG_CHAT_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", RAG_SYSTEM_PROMPT),
        ("user", RAG_PROMPT_TEMPLATE),
    ]
)

# Conversational RAG prompt (with chat history)
CONVERSATIONAL_RAG_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", RAG_SYSTEM_PROMPT),
        ("placeholder", "{chat_history}"),
        ("user", RAG_PROMPT_TEMPLATE),
    ]
)
