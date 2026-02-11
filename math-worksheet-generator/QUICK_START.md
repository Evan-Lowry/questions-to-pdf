# Quick Start Guide

## Prerequisites

**You must have LaTeX installed for PDF generation!**

```bash
# macOS - Install BasicTeX (recommended)
brew install --cask basictex

# Then add to PATH
eval "$(/usr/libexec/path_helper)"
```

See [INSTALLATION.md](INSTALLATION.md) for detailed LaTeX installation instructions.

## Running the Application

### Option 1: Using the Shell Script
```bash
./run.sh
```

### Option 2: Using Python Directly
```bash
python3 src/main.py
```

## How to Use

1. **Launch the application** using one of the methods above

2. **Click "Select PDF File"** and choose your course notes PDF
   - The PDF must contain **"Section X.Y Problems"** headers (e.g., "Section 2.1 Problems")
   - Questions must be numbered as `X.Y.Z.` (e.g., `2.1.1.`, `2.1.2.`)
   - The app stops scanning at page breaks (full page spacing before next section)

3. **Review the extracted questions** in the preview panel
   - Verify that all questions were detected correctly
   - Check that section headers are preserved
   - If some questions are missing, check the formatting in your PDF

4. **Customize the worksheet title** (optional)
   - Default is "Math Worksheet"
   - Change it to match your needs (e.g., "Differential Equations Practice")

5. **Click "Generate Worksheet PDF"**
   - The app will compile the PDF using LaTeX (this may take a few moments)
   - Choose where to save the file
   - The PDF will be generated with proper mathematical notation and spacing

## Example Input Format

Your PDF **must** have questions formatted like this:

```
Section 2.1 Problems

2.1.1. Determine the order of the following differential equations.
(a) y'' + y = 2
(b) (y')² = e^x - y
(c) y'''y' + y'' + y - x² = 0

2.1.2. Determine all real values of a and b such that y = ax + b is a solution.

2.1.3. (a) For what values of k ∈ R does the function y = cos(kt) satisfy...
(b) For the values of k that you found in part (a), verify that...

[FULL PAGE BREAK - Next section starts on new page]

Section 2.2 Problems

2.2.1. Another question...
```

**Key requirements:**
- Section headers: `Section X.Y Problems` (exact format)
- Question numbers: `X.Y.Z.` (must match section number)
- Page breaks: Full page spacing stops question extraction for that section

## Output Format

The generated worksheet PDF includes:
- Your custom title at the top
- Section headers preserved from the original
- Each question followed by approximately **1/4 page of blank space** (2.75 inches)
- **Proper mathematical notation** rendered by LaTeX (no blank characters!)
- Professional formatting with proper margins

### LaTeX Benefits:
- ✅ Perfect mathematical symbols (∈, ≤, ∫, etc.)
- ✅ Properly formatted equations
- ✅ Greek letters (α, β, γ, etc.)
- ✅ Professional typography
- ✅ No garbled or missing characters

## Troubleshooting

### "pdflatex not found"
- **You need to install LaTeX** - see [INSTALLATION.md](INSTALLATION.md)
- macOS: `brew install --cask basictex`
- Make sure `/Library/TeX/texbin` is in your PATH

### "No questions found"
- **Check section headers**: Must be exactly `Section X.Y Problems`
- **Check question numbering**: Must be `X.Y.Z.` (matching the section number)
- **Verify PDF is searchable**: Scanned images won't work; the PDF must have extractable text
- **Check for page breaks**: Sections should be separated by page breaks

### "LaTeX compilation failed"
- Install missing LaTeX packages: `sudo tlmgr install amsmath amssymb amsfonts`
- Check the console output for specific LaTeX errors
- Ensure your PDF doesn't have unusual characters that break LaTeX

### "Import errors" when running
- Make sure you've installed all dependencies: `pip install -r requirements.txt`
- Use Python 3.8 or higher

### Application won't start on macOS
- If you get a security warning, go to System Preferences > Security & Privacy
- Click "Open Anyway" for the Python application
- Grant Terminal full disk access if needed

### Questions are cut off or incomplete
- This happens when a section ends at a page break (by design)
- Verify your PDF has proper section separators
- Questions should not span across page breaks unnaturally

## Tips for Best Results

1. **PDF Quality**: Use high-quality, text-based PDFs (not scanned images)
2. **Consistent Formatting**: Ensure all questions use "Section X.Y Problems" headers
3. **Question Numbering**: Make sure questions are numbered X.Y.Z. matching the section
4. **Page Breaks**: Sections should be separated by full page breaks
5. **Test First**: Try with a small section first to verify the extraction works
6. **Preview**: Always review the preview before generating the final PDF
7. **LaTeX Installation**: Install LaTeX before first use for best results

## Advanced Usage

### Adjusting Spacing
To change the spacing between questions, edit `pdf_generator.py`, line ~130:
```latex
% Change 2.75in to your desired spacing
\vspace{2.75in}
```

### Custom Section Detection
If your PDFs use different section headers, edit `pdf_generator.py`, line ~43:
```python
# Change the pattern to match your format
section_pattern = r'Section\s+(\d+\.\d+)\s+Problems'
```

### Stopping at Different Markers
To change when extraction stops, edit `pdf_generator.py`, line ~60:
```python
# Adjust the page break pattern
page_break_pattern = r'\[PAGE_BREAK\]\s*\[PAGE_BREAK\]'
```

Enjoy using the Course Notes to Worksheet Generator! 📚✨
