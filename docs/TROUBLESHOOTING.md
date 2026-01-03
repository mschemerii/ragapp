# macOS App Troubleshooting Guide

This guide helps resolve common issues with the RAG Application macOS app.

## Issue: App Won't Close / Processes Keep Running

### Symptoms
- App window closes but processes remain running
- Multiple processes visible in Activity Monitor
- Need to force quit processes
- High CPU usage after closing app

### Root Cause
The Streamlit server spawns multiple child processes that weren't being properly cleaned up when the app closed.

### Solution (Fixed in Latest Version)

The latest version includes proper process management:
- Process groups are used to track all child processes
- Signal handlers (SIGTERM, SIGINT) properly cleanup processes
- `atexit` handler ensures cleanup even on unexpected exits
- Both graceful (SIGTERM) and forced (SIGKILL) cleanup

### If You're Still Experiencing Issues

#### Method 1: Kill Processes via Activity Monitor
1. Open **Activity Monitor** (Applications → Utilities → Activity Monitor)
2. Search for "RAG Application" or "streamlit"
3. Select all related processes
4. Click the ⓧ button and choose "Force Quit"

#### Method 2: Kill Processes via Terminal

```bash
# Kill all Streamlit processes
pkill -9 streamlit

# Kill all Python processes running Streamlit
pkill -9 -f "streamlit run"

# Kill all processes related to RAG Application
pkill -9 -f "RAG Application"

# Nuclear option: Kill all Python processes (use with caution!)
# pkill -9 python
```

#### Method 3: Find and Kill by Port

If Streamlit is running on port 8501:

```bash
# Find process using port 8501
lsof -ti:8501

# Kill it
lsof -ti:8501 | xargs kill -9
```

### Prevention

**Always close the app properly:**
1. Use **Cmd+Q** to quit the application
2. Or click the app name in menu bar → "Quit RAG Application"
3. Wait 2-3 seconds for cleanup to complete
4. Don't force quit unless necessary

**Rebuild with latest fixes:**
```bash
cd /path/to/ragapp
git pull
./build_macos.sh
```

## Issue: App Won't Start

### Check Ollama is Running

The app requires Ollama to be running:

```bash
# Check if Ollama is running
curl http://localhost:11434

# If not, start it
ollama serve
```

### Check Required Models

```bash
# List installed models
ollama list

# Install required models if missing
ollama pull llama3.2
ollama pull nomic-embed-text
```

### Check Logs

Run the app from Terminal to see error messages:

```bash
# Navigate to the app
cd "/Applications/RAG Application.app/Contents/MacOS"

# Run the executable
./RAG\ Application
```

## Issue: Port Already in Use

If you get "Port 8501 already in use":

```bash
# Kill process on port 8501
lsof -ti:8501 | xargs kill -9

# Wait a few seconds, then restart the app
```

## Issue: Slow Performance

### On M4 Max Mac

The default configuration is optimized for M4 Max, but you can further tune:

1. **Use larger model** (if 36GB+ RAM):
   ```bash
   ollama pull llama3.2:13b
   ```

   Update `.env`:
   ```
   OLLAMA_MODEL=llama3.2:13b
   ```

2. **Set environment variables**:
   ```bash
   export OLLAMA_NUM_PARALLEL=4
   export OLLAMA_MAX_LOADED_MODELS=2
   ```

3. **Reduce chunk processing**:
   Edit `.env`:
   ```
   CHUNK_SIZE=500
   MAX_RESULTS=3
   ```

## Issue: "Apple could not verify..." Warning

This is expected for unsigned apps. See [../BUILDING.md](BUILDING.md) for code signing instructions.

**Workaround:**
1. Right-click the app
2. Select "Open"
3. Click "Open" in the security dialog

Or via Terminal:
```bash
xattr -cr "/Applications/RAG Application.app"
open "/Applications/RAG Application.app"
```

## Getting Help

If issues persist:

1. **Check logs**: Look for error messages in Terminal when running the app
2. **Verify installation**:
   ```bash
   ollama list
   curl http://localhost:11434
   ```
3. **Report issue**: https://github.com/mschemerii/ragapp/issues
   - Include macOS version
   - Include error messages
   - Include steps to reproduce

## Clean Reinstall

To completely reset the app:

```bash
# 1. Kill all running processes
pkill -9 -f "RAG Application"
pkill -9 streamlit

# 2. Remove app
rm -rf "/Applications/RAG Application.app"

# 3. Remove app data
rm -rf ~/Library/Application\ Support/RAG\ Application
rm -rf ~/Library/Caches/RAG\ Application

# 4. Rebuild and reinstall
cd ~/ragapp
git pull
./build_macos.sh

# 5. Install fresh
cp -r "dist/RAG Application.app" /Applications/
```

## Development Mode Alternative

Instead of using the packaged app, run directly:

```bash
cd ~/ragapp
uv sync
uv run streamlit run streamlit_app.py
```

This provides:
- Better error messages
- Easier debugging
- Automatic code reloading
- No process management issues
