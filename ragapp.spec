# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for building macOS application.

Usage:
    pyinstaller ragapp.spec
"""

import sys
from pathlib import Path

block_cipher = None

# Collect all package data
a = Analysis(
    ['launch_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('streamlit_app.py', '.'),
        ('api.py', '.'),
        ('static', 'static'),
        ('src/ragapp', 'ragapp'),
        ('.env.example', '.'),
        ('data/documents', 'data/documents'),
        ('docs', 'docs'),
        ('examples', 'examples'),
    ],
    hiddenimports=[
        'streamlit',
        'fastapi',
        'uvicorn',
        'langchain',
        'langchain_community',
        'langchain_openai',
        'chromadb',
        'openai',
        'tiktoken',
        'pydantic',
        'pydantic_settings',
        'pypdf',
        'docx',
        'markdown',
        'bs4',
        'ragapp',
        'ragapp.config',
        'ragapp.pipeline',
        'ragapp.ingestion',
        'ragapp.retrieval',
        'ragapp.generation',
        'sqlite3',
        'pkg_resources.py2_warn',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'PIL',
        'PyQt5',
        'tkinter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='RAG Application',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Set to False for GUI-only mode (no terminal)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='RAG Application',
)

# macOS App Bundle
app = BUNDLE(
    coll,
    name='RAG Application.app',
    icon=None,  # Add icon path if you have one
    bundle_identifier='com.ragapp.application',
    info_plist={
        'CFBundleName': 'RAG Application',
        'CFBundleDisplayName': 'RAG Document Q&A',
        'CFBundleVersion': '0.1.0',
        'CFBundleShortVersionString': '0.1.0',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.13.0',
    },
)
