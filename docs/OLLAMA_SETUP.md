# Ollama Setup Guide

This guide will help you set up Ollama to run the RAG application with local language models, optimized for Apple Silicon (M4 Max).

## Why Ollama?

- **Privacy**: All data stays on your machine
- **Cost**: No API costs or usage limits
- **Performance**: Optimized for Apple Silicon (M4 Max)
- **Offline**: Works without internet connection

## Installation

### macOS (Recommended for M4 Max)

1. **Download and Install Ollama**:
   ```bash
   # Download from official website
   curl -fsSL https://ollama.ai/install.sh | sh

   # Or install via Homebrew
   brew install ollama
   ```

2. **Verify Installation**:
   ```bash
   ollama --version
   ```

3. **Start Ollama Service**:
   ```bash
   # Ollama runs as a background service automatically
   # Check if it's running:
   curl http://localhost:11434
   ```

### Linux

```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### Windows

Download the installer from [ollama.ai](https://ollama.ai/download) and run it.

## Required Models

### 1. Language Model (for Generation)

Pull the recommended `llama3.2` model:

```bash
ollama pull llama3.2
```

**Alternative models** (if you need different capabilities):

```bash
# Larger, more capable model (requires more RAM)
ollama pull llama3.2:13b

# Smaller, faster model
ollama pull llama3.2:7b

# Code-focused model
ollama pull codellama

# More advanced model
ollama pull llama3.3
```

### 2. Embedding Model (for Vector Search)

Pull the recommended `nomic-embed-text` model:

```bash
ollama pull nomic-embed-text
```

This model is optimized for semantic search and works great with RAG applications.

## Verify Models

Check that both models are installed:

```bash
ollama list
```

You should see both `llama3.2` and `nomic-embed-text` in the list.

## Configuration

Update your `.env` file:

```env
# LLM Provider Configuration
LLM_PROVIDER=ollama
EMBEDDING_PROVIDER=ollama

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
EMBEDDING_MODEL=nomic-embed-text

# Vector Store Configuration
VECTOR_STORE_PATH=./data/vectorstore

# Document Storage
DOCUMENTS_PATH=./data/documents
```

## Testing Your Setup

1. **Test Ollama is Running**:
   ```bash
   curl http://localhost:11434/api/tags
   ```

2. **Test the Language Model**:
   ```bash
   ollama run llama3.2 "What is RAG?"
   ```

3. **Test the RAG Application**:
   ```bash
   # Add some documents to data/documents/
   # Then ingest and query:
   python -m ragapp ingest --reset
   python -m ragapp query "What is this about?"
   ```

## Performance Optimization for M4 Max

### Memory Settings

For optimal performance on M4 Max:

```bash
# Set environment variables for better performance
export OLLAMA_NUM_PARALLEL=4
export OLLAMA_MAX_LOADED_MODELS=2
```

Add these to your shell profile (`~/.zshrc` or `~/.bashrc`):

```bash
echo 'export OLLAMA_NUM_PARALLEL=4' >> ~/.zshrc
echo 'export OLLAMA_MAX_LOADED_MODELS=2' >> ~/.zshrc
source ~/.zshrc
```

### Model Selection for M4 Max

The M4 Max has excellent performance for local LLMs:

- **36GB+ RAM**: Use `llama3.2:13b` or `llama3.3` for best quality
- **24GB RAM**: Use `llama3.2` (default, good balance)
- **16GB RAM**: Use `llama3.2:7b` for faster responses

## Common Issues

### Ollama Not Running

```bash
# Check if service is running
curl http://localhost:11434

# If not, start manually
ollama serve
```

### Model Not Found

```bash
# List installed models
ollama list

# Pull missing models
ollama pull llama3.2
ollama pull nomic-embed-text
```

### Slow Performance

1. **Check system resources**:
   ```bash
   top
   ```

2. **Use a smaller model**:
   ```bash
   ollama pull llama3.2:7b
   ```

   Update `.env`:
   ```env
   OLLAMA_MODEL=llama3.2:7b
   ```

3. **Reduce chunk size** in `.env`:
   ```env
   CHUNK_SIZE=500
   MAX_RESULTS=3
   ```

### Connection Refused

If you get connection errors:

1. **Check Ollama is running**:
   ```bash
   ps aux | grep ollama
   ```

2. **Restart Ollama**:
   ```bash
   killall ollama
   ollama serve
   ```

3. **Check the port**:
   ```bash
   lsof -i :11434
   ```

## Advanced Configuration

### Custom Ollama URL

If running Ollama on a different machine or port:

```env
OLLAMA_BASE_URL=http://your-server:11434
```

### Using Multiple Models

You can switch models by updating `.env`:

```env
# For coding questions
OLLAMA_MODEL=codellama

# For general questions
OLLAMA_MODEL=llama3.2
```

### Temperature and Generation Settings

Adjust in your `.env`:

```env
# More creative (0.0 - 1.0)
TEMPERATURE=0.8

# More focused/deterministic
TEMPERATURE=0.3

# Longer responses
MAX_TOKENS=2000
```

## Switching Between Ollama and OpenAI

You can easily switch between providers by changing `.env`:

**Using Ollama** (local):
```env
LLM_PROVIDER=ollama
EMBEDDING_PROVIDER=ollama
```

**Using OpenAI** (cloud):
```env
LLM_PROVIDER=openai
EMBEDDING_PROVIDER=openai
OPENAI_API_KEY=your-key-here
```

**Mixed** (Ollama for LLM, OpenAI for embeddings):
```env
LLM_PROVIDER=ollama
EMBEDDING_PROVIDER=openai
OPENAI_API_KEY=your-key-here
```

## Resources

- [Ollama Documentation](https://github.com/ollama/ollama)
- [Ollama Model Library](https://ollama.ai/library)
- [LangChain Ollama Integration](https://python.langchain.com/docs/integrations/llms/ollama)
- [Nomic Embed Text](https://ollama.ai/library/nomic-embed-text)

## Next Steps

Once Ollama is set up:

1. ✅ Models are installed (`ollama list`)
2. ✅ Service is running (`curl http://localhost:11434`)
3. ✅ `.env` is configured
4. 📚 Add documents to `data/documents/`
5. 🔄 Run `python -m ragapp ingest --reset`
6. 💬 Query: `python -m ragapp query "your question"`

Enjoy your privacy-focused, local RAG application!
