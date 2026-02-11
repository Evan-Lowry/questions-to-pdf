# Troubleshooting Guide

## Common Issues and Solutions

### 1. "Cannot set gray non-stroke color" / "'pgfpat4' is an invalid float value"

**Symptoms:**
- Error appears in terminal: `Cannot set gray non-stroke color because /'pgfpat4' is an invalid float value`
- Popup says: "LaTeX compilation failed: pdflatex did not generate a PDF file"

**Cause:**
This error is caused by special quote characters (smart quotes, apostrophes) in your PDF that LaTeX can't handle.

**Solution:**
✅ **Already Fixed!** The latest version automatically converts these characters.

If you still see this error:
1. Make sure you have the latest version of `src/pdf_generator.py`
2. Check that the debug `.tex` file is created (should show where it's saved)
3. Look for unusual characters like: ', ', ", ", ' in your PDF

### 2. Application Won't Start

#### Issue: `command not found: python3`
**Solution:**
```bash
# Try using python instead
python src/main.py

# Or install Python 3
brew install python3  # macOS with Homebrew
```

#### Issue: `ModuleNotFoundError: No module named 'PyQt5'`
**Solution:**
```bash
# Reinstall dependencies
pip3 install -r requirements.txt

# Or install specific package
pip3 install PyQt5
```

#### Issue: GUI window doesn't appear
**Solution:**
- On macOS, make sure you allow the application in System Preferences > Security & Privacy
- Try running from terminal to see error messages
- Check if Qt is properly installed: `python3 -c "from PyQt5 import QtWidgets; print('OK')"`

---

### 2. PDF Upload Issues

#### Issue: "No questions found in the PDF"
**Possible Causes & Solutions:**

1. **PDF is a scanned image**
   - Test: Try copying text from the PDF. If you can't, it's an image.
   - Solution: Use OCR software to convert it to searchable text first.

2. **Questions use different numbering**
   - Example: Your PDF uses "Q1.", "Q2." instead of "2.1.1."
   - Solution: Modify the regex pattern in `src/pdf_generator.py`, line 32:
   ```python
   # Change this:
   question_pattern = r'(\d+\.\d+\.\d+\..*?)(?=\d+\.\d+\.\d+\.|$)'
   
   # To something like (for Q1, Q2, Q3 format):
   question_pattern = r'(Q\d+\..*?)(?=Q\d+\.|$)'
   ```

3. **PDF has unusual encoding**
   - Try re-saving the PDF using Preview (macOS) or Adobe Reader
   - Export to a new PDF with standard encoding

#### Issue: "Only some questions are extracted"
**Diagnosis:**
```bash
# Run this to see what text is extracted:
python3 -c "
import pdfplumber
with pdfplumber.open('your_file.pdf') as pdf:
    for page in pdf.pages:
        print(page.extract_text())
" > extracted_text.txt
```
Check `extracted_text.txt` to see if all questions are in the extracted text.

---

### 3. PDF Generation Issues

#### Issue: "Error generating PDF"
**Solutions:**
1. Check you have write permissions to the destination folder
2. Make sure the output filename doesn't have special characters
3. Try saving to a different location (Desktop, Documents, etc.)

#### Issue: "Questions are cut off"
**Solution:**
Increase the spacing or adjust margins in `src/pdf_generator.py`:
```python
# Line 98: Adjust margins (in points, 72 pts = 1 inch)
doc = SimpleDocTemplate(
    output_path,
    pagesize=letter,
    rightMargin=50,  # Reduce to give more space
    leftMargin=50,   # Reduce to give more space
    topMargin=72,
    bottomMargin=18,
)
```

#### Issue: "Math symbols look wrong"
**Solution:**
reportlab has limited Unicode support. For complex math:
1. Use simpler notation where possible
2. Or consider exporting to LaTeX instead (requires custom code)

---

### 4. Installation Issues

#### Issue: `pip install fails with permission error`
**Solution:**
```bash
# Install for current user only
pip3 install --user -r requirements.txt

# Or use virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

#### Issue: `PyQt5 installation fails on macOS`
**Solution:**
```bash
# Try installing via Homebrew first
brew install pyqt5

# Then link to Python
pip3 install PyQt5
```

#### Issue: `reportlab installation fails`
**Solution:**
```bash
# Install dependencies first
pip3 install pillow freetype-py

# Then install reportlab
pip3 install reportlab
```

---

### 5. Performance Issues

#### Issue: "Large PDFs take too long to process"
**Solutions:**
1. Split the PDF into smaller sections first
2. Process one section at a time
3. Use faster regex patterns (current implementation is already optimized)

#### Issue: "Application freezes during PDF generation"
**Explanation:**
- This is normal for large documents (100+ questions)
- The application is single-threaded for simplicity
- Wait for it to complete (check terminal for progress)

---

### 6. Format Detection Issues

#### Issue: "Section headers not showing"
**Solution:**
Check the section header format in your PDF. It should match:
```
Section X.Y Problems
```

If yours is different (e.g., "Section X.Y Exercises"), modify line 27 in `pdf_generator.py`:
```python
# Change:
sections = re.split(r'(Section\s+[\d.]+\s+\w+)', text)

# To match your format:
sections = re.split(r'(Section\s+[\d.]+\s+Exercises)', text)
```

#### Issue: "Sub-questions not preserved"
**Current Implementation:**
Sub-questions (a), (b), (c) are included as part of the main question text.

**To format them specially:**
Modify the `_parse_questions()` method to handle them separately.

---

### 7. macOS Specific Issues

#### Issue: "Application is damaged and can't be opened"
**Solution:**
```bash
# Remove quarantine attribute
xattr -cr /path/to/math-worksheet-generator
```

#### Issue: "Operation not permitted"
**Solution:**
Grant Terminal or Python full disk access:
1. System Preferences > Security & Privacy > Privacy
2. Select "Full Disk Access"
3. Add Terminal or Python to the list

---

### 8. Output Quality Issues

#### Issue: "Spacing is too much/too little"
**Solution:**
Edit line 135 in `src/pdf_generator.py`:
```python
# Current: 2.75 inches (quarter page)
elements.append(Spacer(1, 2.75 * inch))

# For half page:
elements.append(Spacer(1, 5.5 * inch))

# For smaller spacing:
elements.append(Spacer(1, 1.5 * inch))
```

#### Issue: "Text is too small/large"
**Solution:**
Edit font sizes in `src/pdf_generator.py`:
```python
# Title (line 104)
fontSize=18,  # Increase/decrease as needed

# Section headers (line 112)
fontSize=14,  # Adjust

# Questions (line 123)
fontSize=11,  # Adjust
```

---

## Testing Your Setup

Run this comprehensive test:

```bash
cd math-worksheet-generator

# Test 1: Check Python version
python3 --version  # Should be 3.8 or higher

# Test 2: Check dependencies
python3 -c "
import PyQt5
import pdfplumber
import reportlab
print('✅ All dependencies installed')
"

# Test 3: Test imports
python3 -c "
import sys
sys.path.insert(0, 'src')
from pdf_generator import PDFGenerator
from gui.main_window import MainWindow
print('✅ All modules import successfully')
"

# Test 4: Launch GUI (will open window)
python3 src/main.py
```

---

## Getting Help

If none of these solutions work:

1. **Check error messages carefully** - They often contain the solution
2. **Look at terminal output** - More details than GUI popups
3. **Test with a simple PDF** - Isolate the problem
4. **Check Python version** - Must be 3.8+
5. **Try in a virtual environment** - Eliminates dependency conflicts

### Create an Issue
If you still need help, provide:
- Python version: `python3 --version`
- OS version: `sw_vers` (macOS) or `uname -a` (Linux)
- Error message: Full stack trace from terminal
- Sample PDF format: First few lines of extracted text
- What you've tried: List of solutions attempted

---

## Debug Mode

For detailed logging, add this to `src/main.py`:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Then run and check the output for detailed debugging information.

---

## Contact

For issues not covered here:
1. Check the README_NEW.md for general information
2. Review QUICK_START.md for usage instructions
3. Check IMPLEMENTATION_SUMMARY.md for technical details
4. Open an issue on GitHub with details

**Remember:** Most issues are due to PDF formatting or dependencies. The test commands above will help identify the problem!
