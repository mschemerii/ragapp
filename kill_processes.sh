#!/bin/bash
# Emergency cleanup script for orphaned RAG Application processes

echo "Killing all RAG Application processes..."

# Kill by process name
pkill -9 "RAG Application"

# Kill any remaining streamlit processes
pkill -9 streamlit

# Kill Python processes running streamlit
pkill -9 -f "streamlit run"

# Kill by the specific app path
pkill -9 -f "/Users/mschemer/ragapp/dist/RAG Application.app"

# Wait a moment
sleep 1

# Check if any are still running
REMAINING=$(pgrep -c "RAG Application" 2>/dev/null || echo "0")

if [ "$REMAINING" -eq 0 ]; then
    echo "✓ All processes killed successfully"
else
    echo "⚠ Warning: $REMAINING processes still running"
    echo "Try manually in Activity Monitor or run: sudo pkill -9 'RAG Application'"
fi
