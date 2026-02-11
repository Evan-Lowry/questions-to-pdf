# Installation Guide

## Prerequisites

### 1. Python 3.8+
Check your Python version:
```bash
python3 --version
```

### 2. LaTeX Distribution
**Required for PDF generation with proper mathematical notation**

#### macOS:
Choose one option:

**Option A: BasicTeX (Recommended - Smaller download)**
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install BasicTeX (smaller, ~100MB)
brew install --cask basictex

# Add to PATH
eval "$(/usr/libexec/path_helper)"

# Update LaTeX packages
sudo tlmgr update --self
sudo tlmgr install collection-fontsrecommended
```

**Option B: MacTeX (Full distribution - Larger download ~4GB)**
```bash
brew install --cask mactex-no-gui
```

#### Linux:
```bash
# Ubuntu/Debian
sudo apt-get install texlive-latex-base texlive-latex-extra

# Fedora
sudo dnf install texlive-scheme-basic
```

#### Windows:
Download and install MiKTeX or TeX Live:
- MiKTeX: https://miktex.org/download
- TeX Live: https://www.tug.org/texlive/

## Installation Steps

### 1. Clone or Download the Repository
```bash
cd /path/to/your/projects
git clone https://github.com/yourusername/questions-to-pdf.git
cd questions-to-pdf/math-worksheet-generator
```

### 2. Install Python Dependencies
```bash
pip3 install -r requirements.txt
```

Or install individually:
```bash
pip3 install PyQt5>=5.15.0
pip3 install PyPDF2>=3.0.0
pip3 install pdfplumber>=0.9.0
```

### 3. Verify Installation
```bash
# Test Python imports
python3 -c "from PyQt5 import QtWidgets; print('✅ PyQt5 OK')"
python3 -c "import pdfplumber; print('✅ pdfplumber OK')"

# Test LaTeX
pdflatex --version
```

### 4. Run the Application
```bash
# Option 1: Using the shell script
chmod +x run.sh
./run.sh

# Option 2: Direct Python
python3 src/main.py
```

## Troubleshooting Installation

### Python Package Issues
```bash
# Upgrade pip first
python3 -m pip install --upgrade pip

# Install in user space if permission denied
pip3 install --user -r requirements.txt
```

### LaTeX Issues

#### "pdflatex not found"
Make sure LaTeX bin directory is in your PATH:

**macOS (after installing BasicTeX):**
```bash
# Add to ~/.zshrc or ~/.bash_profile
export PATH="/Library/TeX/texbin:$PATH"

# Reload shell configuration
source ~/.zshrc  # or source ~/.bash_profile
```

**Linux:**
```bash
# Usually automatic, but if needed:
export PATH="/usr/local/texlive/2023/bin/x86_64-linux:$PATH"
```

#### "LaTeX compilation failed"
Install additional packages:
```bash
sudo tlmgr install amsmath amssymb amsfonts enumitem geometry
```

### PyQt5 Issues on macOS

If PyQt5 fails to install:
```bash
# Try via Homebrew
brew install pyqt5

# Then create symlink for Python to find it
pip3 install pyqt5
```

## Verification Test

Run this complete test:
```bash
cd math-worksheet-generator

# Test all dependencies
python3 << 'EOF'
import sys
sys.path.insert(0, 'src')

# Test imports
from PyQt5 import QtWidgets
print("✅ PyQt5 imported")

import pdfplumber
print("✅ pdfplumber imported")

from pdf_generator import PDFGenerator
print("✅ PDF Generator imported")

from gui.main_window import MainWindow
print("✅ Main Window imported")

print("\n🎉 All dependencies installed correctly!")
EOF

# Test LaTeX
pdflatex --version > /dev/null 2>&1 && echo "✅ LaTeX installed" || echo "❌ LaTeX not found - install BasicTeX"
```

## Next Steps

Once installation is complete:
1. Read [QUICK_START.md](QUICK_START.md) for usage instructions
2. See [README_NEW.md](README_NEW.md) for full documentation
3. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) if you encounter issues

## System Requirements

- **OS**: macOS 10.14+, Linux (Ubuntu 20.04+), Windows 10+
- **RAM**: 2GB minimum (4GB recommended for large PDFs)
- **Disk**: 500MB for Python packages + 100MB-4GB for LaTeX
- **Display**: 1280x720 minimum resolution
