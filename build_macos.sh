#!/bin/bash
# Build script for macOS application

set -e

echo "Building RAG Application for macOS..."

# Install dependencies
echo "Installing dependencies..."
pip install pyinstaller
pip install -e ".[all]"

# Build the application
echo "Building with PyInstaller..."
pyinstaller ragapp.spec

echo ""
echo "Build complete!"
echo "Application location: dist/RAG Application.app"
echo ""
echo "To test the app:"
echo "  open 'dist/RAG Application.app'"
echo ""
echo "To create a DMG installer, install create-dmg:"
echo "  brew install create-dmg"
echo "  create-dmg --volname 'RAG Application' 'RAG-Application.dmg' 'dist/RAG Application.app'"
