import pdfplumber
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import RectangleObject
import re
import copy
import os


class PDFGenerator:
    def __init__(self):
        self.pdf_path = None
        self.sections = []  # List of {title, start_page, start_y, end_page, end_y, questions}

    def extract_questions_from_pdf(self, pdf_path):
        """Scan PDF to find all question sections and their page ranges."""
        self.pdf_path = pdf_path
        self.sections = []

        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                section_pattern = re.compile(r'Section\s+(\d+\.\d+)\s+Problems')

                # --- Pass 1: find every "Section X.Y Problems" location -----------
                section_starts = []  # (page_idx, y_top_of_header, section_id)

                for page_idx, page in enumerate(pdf.pages):
                    page_height = page.height
                    words = page.extract_words(keep_blank_chars=False, 
                                                x_tolerance=3, y_tolerance=3)
                    # Rebuild lines from words
                    lines = self._words_to_lines(words)

                    for line in lines:
                        if section_pattern.search(line['text']):
                            section_starts.append({
                                'page': page_idx,
                                'y_top': line['top'],
                                'title': line['text'].strip(),
                                'section_id': section_pattern.search(line['text']).group(1),
                            })

                if not section_starts:
                    return ["No pages with 'Section X.Y Problems' found."]

                # --- Pass 2: figure out where each section's questions END ---------
                for i, sec in enumerate(section_starts):
                    sec_id = sec['section_id']
                    question_pattern = re.compile(
                        rf'{re.escape(sec_id)}\.\d+'
                    )

                    # Start scanning from the section header page
                    last_question_page = sec['page']
                    last_question_bottom = sec['y_top']

                    # The boundary is either the next section start or end of document
                    if i + 1 < len(section_starts):
                        boundary_page = section_starts[i + 1]['page']
                        boundary_y = section_starts[i + 1]['y_top']
                    else:
                        boundary_page = total_pages - 1
                        boundary_y = None  # scan to bottom

                    # Count questions found
                    question_count = 0

                    for pg in range(sec['page'], boundary_page + 1):
                        page = pdf.pages[pg]
                        page_height = page.height
                        words = page.extract_words(keep_blank_chars=False,
                                                    x_tolerance=3, y_tolerance=3)
                        lines = self._words_to_lines(words)

                        for line in lines:
                            # Stop if we've reached the next section on this page
                            if pg == boundary_page and boundary_y is not None:
                                if line['top'] >= boundary_y:
                                    break

                            # Skip header/footer regions (top 50pt, bottom 50pt)
                            if line['top'] < 50 or line['bottom'] > page_height - 40:
                                continue

                            # Check if this line is part of the questions
                            if question_pattern.search(line['text']):
                                question_count += 1
                                last_question_page = pg
                                last_question_bottom = line['bottom']
                            elif last_question_page == pg and question_count > 0:
                                # Continuation of question text (sub-questions, etc.)
                                last_question_bottom = line['bottom']

                    # Add some padding below the last question
                    last_question_bottom += 20

                    self.sections.append({
                        'title': sec['title'],
                        'section_id': sec_id,
                        'start_page': sec['page'],
                        'start_y': sec['y_top'],
                        'end_page': last_question_page,
                        'end_y': last_question_bottom,
                        'question_count': question_count,
                    })

            # Build summary for GUI
            summaries = []
            for sec in self.sections:
                page_range = f"p.{sec['start_page']+1}"
                if sec['end_page'] != sec['start_page']:
                    page_range += f"-{sec['end_page']+1}"
                summaries.append(
                    f"{sec['title']}  ({sec['question_count']} questions, {page_range})"
                )
            return summaries

        except Exception as e:
            raise Exception(f"Error extracting questions: {str(e)}")

    # ------------------------------------------------------------------
    def generate_worksheet_pdf(self, output_path, title="Math Worksheet"):
        """
        Build a worksheet by cropping question regions from the original PDF
        and inserting blank space after each question.
        """
        if not self.pdf_path or not self.sections:
            raise Exception("No questions to generate. Please extract questions first.")

        try:
            reader = PdfReader(self.pdf_path)
            writer = PdfWriter()

            for sec in self.sections:
                for pg_idx in range(sec['start_page'], sec['end_page'] + 1):
                    original = reader.pages[pg_idx]
                    page_height = float(original.mediabox.height)
                    page_width = float(original.mediabox.width)

                    # Determine crop boundaries (in PDF coords: 0 = bottom)
                    # pdfplumber y is from top; PDF mediabox y is from bottom
                    if pg_idx == sec['start_page']:
                        crop_top_plumber = max(sec['start_y'] - 10, 0)  # a little above header
                    else:
                        crop_top_plumber = 50  # skip header

                    if pg_idx == sec['end_page']:
                        crop_bottom_plumber = min(sec['end_y'], page_height)
                    else:
                        crop_bottom_plumber = page_height - 40  # skip footer

                    # Convert pdfplumber coords (top-down) to PDF coords (bottom-up)
                    pdf_lower_y = page_height - crop_bottom_plumber
                    pdf_upper_y = page_height - crop_top_plumber

                    # Create a cropped copy of the page
                    cropped = copy.copy(original)
                    cropped.mediabox = RectangleObject([
                        0,                # left
                        pdf_lower_y,      # bottom
                        page_width,       # right
                        pdf_upper_y,      # top
                    ])

                    writer.add_page(cropped)

                # Add a blank page after each section for answer space
                ref_page = reader.pages[sec['start_page']]
                writer.add_blank_page(
                    width=float(ref_page.mediabox.width),
                    height=float(ref_page.mediabox.height),
                )

            with open(output_path, 'wb') as f:
                writer.write(f)

            return True

        except Exception as e:
            raise Exception(f"Error generating PDF: {str(e)}")

    # ------------------------------------------------------------------
    @staticmethod
    def _words_to_lines(words, y_tolerance=3):
        """Group words into lines based on y-position."""
        if not words:
            return []

        # Sort by vertical position, then horizontal
        sorted_words = sorted(words, key=lambda w: (round(w['top'] / y_tolerance), w['x0']))

        lines = []
        current_line = {
            'text': sorted_words[0]['text'],
            'top': sorted_words[0]['top'],
            'bottom': sorted_words[0]['bottom'],
        }

        for word in sorted_words[1:]:
            if abs(word['top'] - current_line['top']) <= y_tolerance:
                current_line['text'] += ' ' + word['text']
                current_line['bottom'] = max(current_line['bottom'], word['bottom'])
            else:
                lines.append(current_line)
                current_line = {
                    'text': word['text'],
                    'top': word['top'],
                    'bottom': word['bottom'],
                }

        lines.append(current_line)
        return lines
