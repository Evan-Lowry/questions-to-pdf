# Course Notes to Worksheet Generator

A desktop application that extracts questions from course notes PDFs and generates a separate worksheet PDF with spacing for answers.

## Features

- 📁 **PDF Upload**: Upload your course notes in PDF format
- 🔍 **Automatic Question Extraction**: Automatically detects and extracts questions based on numbering patterns (e.g., 2.1.1., 2.1.2., etc.)
- 📄 **Worksheet Generation**: Creates a clean worksheet PDF with quarter-page spacing under each question for student answers
- 👁️ **Preview**: Preview extracted questions before generating the worksheet
- 🎨 **Modern GUI**: User-friendly interface built with PyQt5

## Installation

1. **Clone or download this repository**

2. **Install Python 3.8 or higher** (if not already installed)

3. **Install required packages**:
   ```bash
   cd math-worksheet-generator
   pip install -r requirements.txt
   ```

## Usage

1. **Run the application**:
   ```bash
   python src/main.py
   ```

2. **Upload your course notes PDF**:
   - Click "Select PDF File" button
   - Choose your course notes PDF file
   - The application will automatically extract all questions

3. **Preview the questions**:
   - Review the extracted questions in the preview panel
   - Verify that all questions were detected correctly

4. **Generate the worksheet**:
   - Optionally customize the worksheet title
   - Click "Generate Worksheet PDF"
   - Choose where to save the output PDF
   - Your worksheet is ready!

## Question Format Requirements

The application is designed to work with course notes that have questions formatted with numbered sections. For example:

```
Section 2.1 Problems

2.1.1. First question text here...

2.1.2. Second question text here...
(a) Sub-question a
(b) Sub-question b

2.1.3. Third question text here...
```

The application looks for:
- Section headers: `Section X.Y Problems`
- Question numbers: `X.Y.Z.` format
- Sub-questions: `(a)`, `(b)`, `(c)`, etc.

## Output Format

The generated worksheet PDF includes:
- Title at the top
- Section headers preserved from the original
- Each question with approximately 1/4 page (2.75 inches) of blank space below for answers
- Professional formatting with proper margins

## Troubleshooting

**No questions found:**
- Verify your PDF uses the numbering format (e.g., 2.1.1., 2.1.2.)
- Ensure the PDF is searchable (not a scanned image)

**Installation issues on macOS:**
- If you encounter issues installing PyQt5, you may need to install it via Homebrew:
  ```bash
  brew install pyqt5
  ```

**Python package issues:**
- Try upgrading pip first: `pip install --upgrade pip`
- Install packages one by one if batch installation fails

## Requirements

- Python 3.8+
- PyQt5 (GUI framework)
- pdfplumber (PDF text extraction)
- reportlab (PDF generation)

## Project Structure
```
math-worksheet-generator/
├── src/
│   ├── main.py               # Application entry point
│   ├── pdf_generator.py      # PDF extraction and generation logic
│   ├── gui/
│   │   ├── main_window.py    # Main GUI window
│   │   └── components.py     # Reusable GUI components
│   └── utils/
│       └── formatting.py     # Text formatting utilities
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## License

MIT License - Feel free to use and modify for your needs!

## Support

For issues or questions, please open an issue on the GitHub repository.
