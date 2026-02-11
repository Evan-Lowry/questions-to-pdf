# Course Notes to Worksheet Generator

A desktop application that extracts questions from PDF course notes and generates professional worksheets with proper mathematical notation using LaTeX.

## ✨ Features

- 📁 **Smart PDF Processing**: Detects "Section X.Y Problems" and extracts questions
- 🔍 **Page Break Detection**: Stops scanning at full page spacing between sections
- 📄 **LaTeX Output**: Generates PDFs with perfect mathematical notation (no blank characters!)
- 👁️ **Preview**: Review extracted questions before generating
- 🎨 **Modern GUI**: User-friendly PyQt5 interface
- ✅ **Professional Quality**: Publication-ready worksheets with proper formatting

## 🎯 Perfect For

- Math and science course instructors
- Problem set creation from textbooks
- Practice worksheet generation
- Homework assignment preparation
- Study guide creation

## 📋 Requirements

### Software
- **Python 3.8+**
- **LaTeX distribution** (BasicTeX/MacTeX/MiKTeX/TeX Live)
- Python packages: PyQt5, pdfplumber, PyPDF2

### PDF Format
Your course notes must have:
- Section headers: `Section X.Y Problems` (e.g., "Section 2.1 Problems")
- Question numbering: `X.Y.Z.` format (e.g., 2.1.1., 2.1.2.)
- Page breaks between sections

## 🚀 Quick Start

### 1. Install LaTeX

**macOS:**
```bash
brew install --cask basictex
eval "$(/usr/libexec/path_helper)"
```

**Linux:**
```bash
sudo apt-get install texlive-latex-base texlive-latex-extra
```

See [INSTALLATION.md](INSTALLATION.md) for detailed instructions.

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
./run.sh
# or
python3 src/main.py
```

### 4. Use the App
1. Click "Select PDF File" and choose your course notes
2. Review extracted questions in preview
3. Customize worksheet title (optional)
4. Click "Generate Worksheet PDF"
5. Save and distribute!

## 📖 Documentation

- **[INSTALLATION.md](INSTALLATION.md)** - Complete installation guide with LaTeX setup
- **[QUICK_START.md](QUICK_START.md)** - Step-by-step usage instructions
- **[UPDATE_SUMMARY.md](UPDATE_SUMMARY.md)** - Details on LaTeX implementation and changes
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues and solutions

## 💡 Example

**Input PDF:**
```
Section 2.1 Problems

2.1.1. Determine the order of the following differential equations.
(a) y'' + y = 2
(b) (y')² = e^x - y

2.1.2. Determine all real values of a and b such that y = ax + b
is a solution to (y')² = x - y.

[FULL PAGE BREAK]

Section 2.2 Problems
...
```

**Output PDF:**
- Professional LaTeX-formatted worksheet
- Perfect rendering of: y'', e^x, mathematical symbols
- 1/4 page spacing under each question for student answers
- Section headers preserved
- Clean, publication-quality formatting

## 🔧 Features in Detail

### Section-Based Extraction
- Finds "Section X.Y Problems" headers
- Extracts only questions from that section
- Stops at page breaks (natural section boundaries)
- Prevents cross-section contamination

### LaTeX Math Support
- **Greek letters**: α, β, γ, δ, θ, λ, π, σ, etc.
- **Operators**: ∫, ∑, ∏, ∂, ∇
- **Relations**: ≤, ≥, ≠, ≈, ∈, ⊆
- **Arrows**: →, ←, ⇒, ⇔
- **Special**: ±, ×, ÷, √, ∞, ∅
- Plus all standard math equations and formulas!

### Customizable Output
- Worksheet title
- Spacing amount (default: 2.75 inches = 1/4 page)
- Section and question formatting
- Margins and page layout

## 🏗️ Project Structure

```
math-worksheet-generator/
├── src/
│   ├── main.py              # Application entry point
│   ├── pdf_generator.py     # Question extraction & LaTeX generation
│   ├── gui/
│   │   ├── main_window.py   # GUI implementation
│   │   ├── components.py    # Reusable components
│   │   └── __init__.py
│   └── utils/
│       ├── formatting.py    # Text utilities
│       └── __init__.py
├── requirements.txt         # Python dependencies
├── run.sh                  # Launch script
├── INSTALLATION.md         # Setup guide
├── QUICK_START.md         # Usage guide
├── UPDATE_SUMMARY.md      # Recent changes
└── README.md              # This file
```

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Support for alternative section formats
- Batch processing multiple PDFs
- More LaTeX customization options
- OCR support for scanned PDFs
- Additional output formats

## 📝 License

MIT License - Feel free to use and modify!

## 🆘 Support

**Installation issues?** → See [INSTALLATION.md](INSTALLATION.md)
**Usage questions?** → See [QUICK_START.md](QUICK_START.md)
**Something broken?** → See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
**Still stuck?** → Open a GitHub issue with:
- Your Python version (`python3 --version`)
- LaTeX version (`pdflatex --version`)
- Error messages
- Sample of your PDF format

## 🙏 Acknowledgments

Built with:
- PyQt5 - Cross-platform GUI framework
- pdfplumber - PDF text extraction
- LaTeX - Professional document typesetting
- Python - Everything else!

---

**Made with ❤️ for educators and students**

Transform your course notes into professional worksheets in seconds!
