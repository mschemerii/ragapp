# Building macOS Application

This guide explains how to build standalone macOS applications from the RAG Application source code.

## Overview

The RAG Application can be packaged as a standalone macOS app using PyInstaller. This allows users to run the application without installing Python or any dependencies.

## Automated Builds (GitHub Actions)

Every time you create a new release on GitHub, the application is automatically built for macOS.

### How It Works

1. **Trigger**: Create a new release on GitHub
2. **Build Process**: GitHub Actions runs on macOS runners
3. **Outputs**:
   - `RAG-Application-macOS.dmg` - Installer disk image
   - `RAG-Application-macOS.zip` - ZIP archive
   - `ragapp-cli-macOS.zip` - Command-line executable
4. **Distribution**: Files are automatically attached to the release

### Creating a Release

```bash
# Tag your commit
git tag v0.1.0
git push origin v0.1.0

# Or create via GitHub web interface:
# Repository → Releases → Create a new release
```

The build workflow will automatically:
- Install Python 3.11
- Install all dependencies
- Run PyInstaller with `ragapp.spec`
- Create DMG installer using `create-dmg`
- Create ZIP archives as fallback
- Upload artifacts to the release

## Manual Building

### Prerequisites

1. **macOS** (tested on macOS 10.13+)
2. **Python 3.10 or higher**
3. **Homebrew** (for creating DMG)

### Quick Build

```bash
# Install dependencies
pip install -e ".[build,all]"

# Run build script
./build_macos.sh

# Output location
open "dist/RAG Application.app"
```

### Detailed Build Steps

#### 1. Install Dependencies

```bash
# Install Python dependencies
pip install pyinstaller
pip install -e ".[all]"

# Install create-dmg (optional, for DMG creation)
brew install create-dmg
```

#### 2. Build the Application

```bash
# Build using spec file
pyinstaller ragapp.spec
```

This creates:
- `dist/RAG Application.app` - The macOS application bundle

#### 3. Test the Application

```bash
# Launch the app
open "dist/RAG Application.app"
```

The app should:
- Launch the Streamlit web interface
- Open your browser to http://localhost:8501
- Display the RAG Application UI

#### 4. Create DMG Installer (Optional)

```bash
create-dmg \
  --volname "RAG Application" \
  --window-pos 200 120 \
  --window-size 600 400 \
  --icon-size 100 \
  --app-drop-link 450 185 \
  "RAG-Application.dmg" \
  "dist/RAG Application.app"
```

## Build Configuration

### PyInstaller Spec File (`ragapp.spec`)

The spec file controls how PyInstaller builds the application:

```python
# Entry point
['launch_gui.py']

# Data files included
datas=[
    ('streamlit_app.py', '.'),
    ('api.py', '.'),
    ('static', 'static'),
    ('src/ragapp', 'ragapp'),
    ('data/documents', 'data/documents'),
]

# Hidden imports (packages not auto-detected)
hiddenimports=[
    'streamlit',
    'langchain',
    'chromadb',
    # ... etc
]

# Excluded modules (reduce size)
excludes=[
    'matplotlib',
    'PIL',
    'PyQt5',
    'tkinter',
]
```

### Launcher Script (`launch_gui.py`)

The launcher:
1. Locates `streamlit_app.py`
2. Launches Streamlit with `python -m streamlit run`
3. Handles errors gracefully

## Build Variants

### GUI Application (Default)

- Launches Streamlit web interface
- User-friendly for non-technical users
- Built with `ragapp.spec`

### CLI Executable

For users who prefer command-line:

```bash
pyinstaller --onefile \
  --name ragapp-cli \
  --hidden-import ragapp \
  src/ragapp/__main__.py
```

Outputs: `dist/ragapp-cli`

Usage:
```bash
./ragapp-cli ingest --reset
./ragapp-cli query "What is RAG?"
```

## Troubleshooting

### "Application is damaged and can't be opened"

This happens because the app isn't signed with an Apple Developer certificate.

**Solution for users**:
```bash
# Remove quarantine flag
xattr -cr "/Applications/RAG Application.app"
```

**Or**: Right-click → "Open" instead of double-clicking

### Missing Dependencies

If the app crashes on launch:

1. **Check Console.app** for errors
2. **Verify hidden imports** in `ragapp.spec`
3. **Add missing packages** to `hiddenimports` list

Example:
```python
hiddenimports=[
    'missing_package',  # Add here
]
```

### Large App Size

The app bundle is large (~500MB) because it includes:
- Python interpreter
- All dependencies (LangChain, ChromaDB, etc.)
- Data files

To reduce size:
1. Exclude unnecessary packages in spec file
2. Use `--exclude-module` flag
3. Enable UPX compression (already enabled)

### ChromaDB Database Errors

The app creates its database in:
```
~/Library/Application Support/RAG Application/data/vectorstore/
```

To reset:
```bash
rm -rf ~/Library/Application\ Support/RAG\ Application/
```

## Code Signing (Optional)

For distribution outside GitHub:

### 1. Get Apple Developer Certificate

- Enroll in Apple Developer Program ($99/year)
- Download certificates in Xcode

### 2. Sign the Application

```bash
codesign --force --deep --sign "Developer ID Application: Your Name" \
  "dist/RAG Application.app"
```

### 3. Notarize (macOS 10.14.5+)

```bash
# Create ZIP for notarization
ditto -c -k --keepParent "dist/RAG Application.app" "RAG-App.zip"

# Submit for notarization
xcrun notarytool submit RAG-App.zip \
  --apple-id "your@email.com" \
  --team-id "TEAMID" \
  --password "app-specific-password" \
  --wait

# Staple the notarization
xcrun stapler staple "dist/RAG Application.app"
```

## GitHub Actions Workflow

Located at: `.github/workflows/build-macos.yml`

### Key Steps

1. **Checkout**: Get latest code
2. **Setup Python**: Install Python 3.11
3. **Install deps**: `pip install pyinstaller` + all dependencies
4. **Build**: Run `pyinstaller ragapp.spec`
5. **Create DMG**: Use `create-dmg` to make installer
6. **Create ZIP**: Fallback for DMG issues
7. **Upload artifacts**: Make available for download
8. **Attach to release**: If triggered by release event

### Triggering Manually

You can trigger the build without creating a release:

1. Go to **Actions** tab on GitHub
2. Select **Build macOS Application**
3. Click **Run workflow**
4. Download artifacts from the workflow run

## Distribution

### Via GitHub Releases (Recommended)

Users download from:
```
https://github.com/yourusername/ragapp/releases/latest
```

### Via Direct Link

Link to specific release:
```
https://github.com/yourusername/ragapp/releases/download/v0.1.0/RAG-Application-macOS.dmg
```

### Self-Hosting

Host the DMG/ZIP on your own server:
```bash
# Upload to server
scp RAG-Application-macOS.dmg user@yourserver.com:/var/www/downloads/

# Users download
wget https://yourserver.com/downloads/RAG-Application-macOS.dmg
```

## Future Improvements

### Planned Enhancements

- [ ] Windows build support (PyInstaller works on Windows too)
- [ ] Linux AppImage builds
- [ ] Smaller app size optimizations
- [ ] Auto-update functionality
- [ ] App icon design
- [ ] Menu bar integration
- [ ] Native macOS UI (SwiftUI wrapper)

### Contributing

To improve the build process:

1. Edit `ragapp.spec` for build configuration
2. Update `.github/workflows/build-macos.yml` for CI/CD
3. Modify `build_macos.sh` for local builds
4. Test on different macOS versions

## Resources

- [PyInstaller Documentation](https://pyinstaller.org/)
- [create-dmg GitHub](https://github.com/create-dmg/create-dmg)
- [Apple Code Signing Guide](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution)
- [GitHub Actions Runners](https://docs.github.com/en/actions/using-github-hosted-runners/about-github-hosted-runners)
