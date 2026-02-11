import pdfplumber
import re
import subprocess
import tempfile
import os


class PDFGenerator:
    def __init__(self):
        self.questions = []
        self.sections = []  # Store section-question pairs
        
    def extract_questions_from_pdf(self, pdf_path):
        """Extract questions from the uploaded PDF."""
        self.questions = []
        self.sections = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                full_text = ""
                for page in pdf.pages:
                    # Try different extraction methods for better character preservation
                    text = page.extract_text(layout=True, x_tolerance=2, y_tolerance=2)
                    if text:
                        # Clean up excessive whitespace but preserve structure
                        text = '\n'.join(line.rstrip() for line in text.split('\n'))
                        full_text += text + "\n\n[PAGE_BREAK]\n\n"
                
                # Parse questions based on section headers
                self.sections = self._parse_questions_by_section(full_text)
                
                # Flatten into questions list for preview
                for section_title, section_questions in self.sections:
                    if section_title:
                        self.questions.append(f"\n{section_title}\n")
                    self.questions.extend(section_questions)
                
            return self.questions
        except Exception as e:
            raise Exception(f"Error extracting questions: {str(e)}")
    
    def _parse_questions_by_section(self, text):
        """Parse questions by detecting 'Section X.Y Problems' and stopping at page breaks."""
        sections = []
        
        # Find all "Section X.Y Problems" headers
        section_pattern = r'Section\s+(\d+\.\d+)\s+Problems'
        section_matches = list(re.finditer(section_pattern, text))
        
        for i, match in enumerate(section_matches):
            section_title = match.group(0)
            section_start = match.end()
            
            # Find the end of this section (next section or end of text)
            if i + 1 < len(section_matches):
                section_end = section_matches[i + 1].start()
            else:
                section_end = len(text)
            
            section_text = text[section_start:section_end]
            
            # Stop at the first page break (full page spacing)
            # Look for multiple consecutive page breaks or large whitespace
            page_break_pattern = r'\[PAGE_BREAK\]\s*\[PAGE_BREAK\]|\[PAGE_BREAK\]\s*\n\s*\n\s*\[PAGE_BREAK\]'
            page_break_match = re.search(page_break_pattern, section_text)
            
            if page_break_match:
                section_text = section_text[:page_break_match.start()]
            
            # Extract questions from this section (X.Y.Z. format)
            section_num = match.group(1)
            question_pattern = rf'({re.escape(section_num)}\.\d+\..*?)(?={re.escape(section_num)}\.\d+\.|$)'
            found_questions = re.findall(question_pattern, section_text, re.DOTALL)
            
            # Clean up questions
            cleaned_questions = []
            for question in found_questions:
                question = question.strip()
                # Remove page break markers
                question = re.sub(r'\[PAGE_BREAK\]', '', question)
                question = question.strip()
                if question:
                    cleaned_questions.append(question)
            
            if cleaned_questions:
                sections.append((section_title, cleaned_questions))
        
        return sections
    
    def generate_worksheet_pdf(self, output_path, title="Math Worksheet"):
        """Generate a PDF with extracted questions and spacing using LaTeX."""
        if not self.sections:
            raise Exception("No questions to generate. Please extract questions first.")
        
        try:
            # Generate LaTeX content
            latex_content = self._generate_latex(title)
            
            # Compile LaTeX to PDF
            self._compile_latex_to_pdf(latex_content, output_path)
            
            return True
            
        except Exception as e:
            raise Exception(f"Error generating PDF: {str(e)}")
    
    def _generate_latex(self, title):
        """Generate LaTeX document with questions."""
        latex = r'''\documentclass[12pt,letterpaper]{article}
\usepackage[utf8]{inputenc}
\usepackage[margin=1in]{geometry}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{amsfonts}

\title{''' + title + r'''}
\date{}

\begin{document}

\maketitle

'''
        
        # Add each section and its questions
        for section_title, questions in self.sections:
            # Add section header
            latex += f"\n\\section*{{{section_title}}}\n\n"
            
            # Add questions
            for question in questions:
                # Escape LaTeX special characters, but preserve math mode
                question_latex = self._convert_to_latex(question)
                latex += f"{question_latex}\n\n"
                
                # Add spacing (quarter page ~ 2.75 inches)
                latex += r"\vspace{2.75in}" + "\n\n"
        
        latex += r'''\end{document}'''
        
        return latex
    
    def _convert_to_latex(self, text):
        """Convert text to LaTeX format, preserving mathematical notation."""
        # First, ensure text is properly decoded - handle Windows-1252 bytes that might be in the string
        # These are common in PDFs extracted from Windows systems
        if isinstance(text, bytes):
            # Try UTF-8 first, fall back to Windows-1252
            try:
                text = text.decode('utf-8')
            except UnicodeDecodeError:
                text = text.decode('windows-1252', errors='replace')
        
        # Handle Windows-1252 characters that might have been improperly decoded
        # Map Windows-1252 smart quotes to ASCII
        windows_chars = {
            '\x91': "'",   # Left single quote
            '\x92': "'",   # Right single quote / apostrophe
            '\x93': '"',   # Left double quote
            '\x94': '"',   # Right double quote
            '\x85': '...',  # Ellipsis
            '\x96': '-',   # En dash
            '\x97': '--',  # Em dash
        }
        for win_char, replacement in windows_chars.items():
            text = text.replace(win_char, replacement)
        
        # Handle Unicode smart quotes and apostrophes (these cause the pgfpat4 error)
        # Replace smart quotes with regular ASCII quotes/apostrophes
        text = text.replace('\u2019', "'")  # Right single quote (') -> apostrophe
        text = text.replace('\u2018', "`")  # Left single quote (') -> backtick
        text = text.replace('\u201d', "''")  # Right double quote (") -> two single quotes
        text = text.replace('\u201c', "``")  # Left double quote (") -> two backticks
        text = text.replace('\u2032', "'")   # Prime symbol (′) -> apostrophe
        text = text.replace('\u2033', "''")  # Double prime (″) -> two apostrophes
        text = text.replace('\u2013', '--')  # En dash
        text = text.replace('\u2014', '---') # Em dash
        text = text.replace('\u2026', '...') # Ellipsis
        
        # Clean up artifact question marks from failed character extraction
        # These appear when pdfplumber can't extract certain characters
        # Pattern: " ? " or "? ?" with spaces around them (not part of actual text)
        import re
        # Remove isolated question marks with surrounding spaces
        text = re.sub(r'\s+\?\s+\?+\s+', ' ', text)  # Multiple ? with spaces
        text = re.sub(r'\s+\?\s+(?=[A-Za-z0-9()])', ' ', text)  # ? before letter/number/paren
        text = re.sub(r'(?<=[)\d])\s+\?\s+', ' ', text)  # ? after paren/number with spaces
        # Clean up patterns like "cos ?→" or "lim 1+ ?→"
        text = re.sub(r'\?\s*→', r'\\to ', text)  # ?→ means arrow
        text = re.sub(r'\?\s*=', '=', text)  # ?= means equals (remove ?)

        
        # Replace common Unicode math symbols with LaTeX equivalents
        conversions = {
            '∈': r'$\in$ ',
            '∉': r'$\notin$ ',
            '⊆': r'$\subseteq$ ',
            '⊂': r'$\subset$ ',
            '∪': r'$\cup$ ',
            '∩': r'$\cap$ ',
            '∅': r'$\emptyset$ ',
            '∞': r'$\infty$ ',
            '≤': r'$\leq$ ',
            '≥': r'$\geq$ ',
            '≠': r'$\neq$ ',
            '≈': r'$\approx$ ',
            '∀': r'$\forall$ ',
            '∃': r'$\exists$ ',
            '→': r'$\\to$ ',
            '←': r'$\leftarrow$ ',
            '↔': r'$\leftrightarrow$ ',
            '⇒': r'$\Rightarrow$ ',
            '⇔': r'$\Leftrightarrow$ ',
            '±': r'$\pm$ ',
            '×': r'$\times$ ',
            '÷': r'$\div$ ',
            '·': r'$\cdot$ ',
            '√': r'$\sqrt{}$',
            '∑': r'$\sum$ ',
            '∏': r'$\prod$ ',
            '∫': r'$\int$ ',
            '∂': r'$\partial$ ',
            '∇': r'$\nabla$ ',
            # Greek letters (lowercase)
            'α': r'$\alpha$ ',
            'β': r'$\beta$ ',
            'γ': r'$\gamma$ ',
            'δ': r'$\delta$ ',
            'ε': r'$\epsilon$ ',
            'θ': r'$\theta$ ',
            'λ': r'$\lambda$ ',
            'μ': r'$\mu$ ',
            'π': r'$\pi$ ',
            'σ': r'$\sigma$ ',
            'τ': r'$\tau$ ',
            'φ': r'$\phi$ ',
            'ω': r'$\omega$ ',
            # Greek letters (uppercase)
            'Δ': r'$\Delta$ ',
            'Σ': r'$\Sigma$ ',
            'Π': r'$\Pi$ ',
            'Ω': r'$\Omega$ ',
            # Superscript numbers (often used in PDFs)
            '⁰': r'$^0$',
            '¹': r'$^1$',
            '²': r'$^2$',
            '³': r'$^3$',
            '⁴': r'$^4$',
            '⁵': r'$^5$',
            '⁶': r'$^6$',
            '⁷': r'$^7$',
            '⁸': r'$^8$',
            '⁹': r'$^9$',
            # Subscript numbers
            '₀': r'$_0$',
            '₁': r'$_1$',
            '₂': r'$_2$',
            '₃': r'$_3$',
            '₄': r'$_4$',
            '₅': r'$_5$',
            '₆': r'$_6$',
            '₇': r'$_7$',
            '₈': r'$_8$',
            '₉': r'$_9$',
        }
        
        for unicode_char, latex_cmd in conversions.items():
            text = text.replace(unicode_char, latex_cmd)
        
        # Escape LaTeX special characters
        # Do this AFTER math symbol conversion to avoid double-escaping
        # We need to be careful not to escape $ signs that are part of our math mode commands
        special_chars = [
            ('#', r'\#'),
            ('%', r'\%'),
            ('&', r'\&'),
            ('_', r'\_'),
            ('{', r'\{'),
            ('}', r'\}'),
            ('~', r'\textasciitilde '),
            ('^', r'\textasciicircum '),
        ]
        
        for char, escaped in special_chars:
            text = text.replace(char, escaped)
        
        return text
    
    def _compile_latex_to_pdf(self, latex_content, output_path):
        """Compile LaTeX to PDF using pdflatex."""
        # Create temporary directory for LaTeX compilation
        with tempfile.TemporaryDirectory() as temp_dir:
            # Write LaTeX file with robust encoding handling
            tex_file = os.path.join(temp_dir, 'worksheet.tex')
            try:
                # First, clean any remaining problematic characters
                # Remove or replace any characters that aren't valid ASCII or common LaTeX-safe Unicode
                cleaned_content = latex_content.encode('ascii', errors='replace').decode('ascii')
                
                with open(tex_file, 'w', encoding='utf-8') as f:
                    f.write(cleaned_content)
            except UnicodeEncodeError as e:
                # If we still have encoding issues, save debug file and raise detailed error
                debug_file = output_path.replace('.pdf', '_debug.tex')
                with open(debug_file, 'w', encoding='utf-8', errors='replace') as f:
                    f.write(latex_content)
                raise Exception(
                    f"Encoding error when writing LaTeX file.\n"
                    f"Problem at position {e.start}: {repr(latex_content[max(0,e.start-20):e.start+20])}\n"
                    f"Debug: LaTeX source saved to {debug_file}"
                )
            
            # Try to compile with pdflatex
            try:
                latex_output = ""
                # Run pdflatex twice for proper formatting
                for i in range(2):
                    result = subprocess.run(
                        ['pdflatex', '-interaction=nonstopmode', '-output-directory', temp_dir, tex_file],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    if i == 0:  # Save first run output for error reporting
                        latex_output = result.stdout + result.stderr
                
                # Check if PDF was created
                pdf_file = os.path.join(temp_dir, 'worksheet.pdf')
                if os.path.exists(pdf_file):
                    # Copy to output location
                    import shutil
                    shutil.copy(pdf_file, output_path)
                else:
                    # Extract relevant error from LaTeX output
                    error_lines = []
                    for line in latex_output.split('\n'):
                        if 'Error' in line or '!' in line or 'Undefined' in line:
                            error_lines.append(line.strip())
                    
                    error_msg = '\n'.join(error_lines[:5]) if error_lines else "Unknown LaTeX error"
                    
                    # Save LaTeX file for debugging
                    debug_file = output_path.replace('.pdf', '_debug.tex')
                    with open(debug_file, 'w', encoding='utf-8') as f:
                        f.write(latex_content)
                    
                    raise Exception(
                        f"pdflatex did not generate a PDF file.\n\n"
                        f"LaTeX errors:\n{error_msg}\n\n"
                        f"Debug: LaTeX source saved to {debug_file}"
                    )
                    
            except FileNotFoundError:
                raise Exception(
                    "pdflatex not found. Please install LaTeX:\n"
                    "macOS: brew install --cask basictex\n"
                    "After installing, restart Terminal and run:\n"
                    "eval \"$(/usr/libexec/path_helper)\""
                )
            except subprocess.TimeoutExpired:
                raise Exception("LaTeX compilation timed out. The PDF may be too large or complex.")
            except Exception as e:
                if "pdflatex not found" in str(e) or "pdflatex did not generate" in str(e):
                    raise  # Re-raise our custom exceptions
                # Check if it's a missing package error
                if "not found" in latex_output or "sty' not found" in latex_output:
                    raise Exception(
                        f"LaTeX compilation failed due to missing packages.\n\n"
                        f"To install missing packages on macOS:\n"
                        f"sudo tlmgr update --self\n"
                        f"sudo tlmgr install <package-name>\n\n"
                        f"Error details:\n{str(e)}"
                    )
                raise Exception(f"LaTeX compilation failed: {str(e)}")