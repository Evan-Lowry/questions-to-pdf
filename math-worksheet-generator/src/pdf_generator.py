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
    # Spacing constants
    ANSWER_SPACE_PT = 198   # ~2.75 inches of blank answer space after each question region
    SECTION_GAP_PT  = 28    # extra gap between sections
    PAGE_MARGIN_PT  = 36    # top/bottom margin when slicing into pages

    def generate_worksheet_pdf(self, output_path, title="Math Worksheet"):
        """
        Build a worksheet PDF with a two-phase approach:

        Phase 1 – Assemble one tall "scroll" page that contains every
                  question region (cropped from the source PDF) separated
                  by blank answer space.

        Phase 2 – Slice that scroll into standard letter-sized pages and
                  write the final multi-page PDF.
        """
        if not self.pdf_path or not self.sections:
            raise Exception("No questions to generate. Please extract questions first.")

        try:
            reader = PdfReader(self.pdf_path)

            # Derive page dimensions from the first source page
            ref_page   = reader.pages[self.sections[0]['start_page']]
            PAGE_W     = float(ref_page.mediabox.width)   # e.g. 612 pt (letter)
            PAGE_H     = float(ref_page.mediabox.height)  # e.g. 792 pt (letter)

            # ----------------------------------------------------------
            # Phase 1: collect (cropped_page_obj, strip_height) pairs
            #          and compute the total scroll height.
            # ----------------------------------------------------------
            strips = []   # list of (PyPDF2 page object, strip_height_pt)

            for sec_idx, sec in enumerate(self.sections):
                for pg_idx in range(sec['start_page'], sec['end_page'] + 1):
                    original    = reader.pages[pg_idx]
                    page_height = float(original.mediabox.height)

                    # --- crop bounds in pdfplumber (top-down) coords ---
                    if pg_idx == sec['start_page']:
                        crop_top = max(sec['start_y'] - 10, 0)
                    else:
                        crop_top = 50   # skip running header

                    if pg_idx == sec['end_page']:
                        crop_bot = min(sec['end_y'], page_height)
                    else:
                        crop_bot = page_height - 40   # skip running footer

                    strip_h = crop_bot - crop_top
                    if strip_h <= 0:
                        continue

                    # Convert to PDF (bottom-up) coordinates
                    pdf_lower = page_height - crop_bot
                    pdf_upper = page_height - crop_top

                    cropped = copy.copy(original)
                    cropped.mediabox = RectangleObject([0, pdf_lower, PAGE_W, pdf_upper])
                    strips.append((cropped, strip_h))

                # After every section add an answer-space marker (None = blank gap)
                strips.append((None, self.ANSWER_SPACE_PT))

                # Extra visual gap between sections (except after the last one)
                if sec_idx < len(self.sections) - 1:
                    strips.append((None, self.SECTION_GAP_PT))

            # ----------------------------------------------------------
            # Phase 2: slice the scroll into letter pages.
            #
            # Strategy: walk through strips top-to-bottom.  Each strip is
            # either a real cropped page or a blank gap.  Accumulate content
            # onto the current output page; when a strip would overflow, emit
            # the current page and start a new one.
            # ----------------------------------------------------------
            writer = PdfWriter()

            usable_h   = PAGE_H - 2 * self.PAGE_MARGIN_PT
            cursor_y   = usable_h   # remaining space on current output page
            cur_page_h = 0          # how much of usable_h has been consumed

            def flush_page(pending_strips, total_h):
                """Create one output page from the accumulated pending strips."""
                out_page = writer.add_blank_page(width=PAGE_W, height=PAGE_H)
                for (strip, sh, dest_y_bot) in pending_strips:
                    if strip is None:
                        continue  # blank gap – nothing to draw
                    # Merge the cropped strip onto out_page at the right y-offset.
                    # PyPDF2's merge_page uses a transformation matrix.
                    # We need to translate the strip so its bottom lands at dest_y_bot.
                    # The strip's own coordinate system starts at pdf_lower (already 0
                    # after cropping sets mediabox lower = pdf_lower, but the content
                    # stream still uses original coords).
                    # Use mergeTransformedPage with a vertical translation.
                    strip_mb_bottom = float(strip.mediabox.lower_left[1])
                    tx = self.PAGE_MARGIN_PT   # left margin indent (same as source)
                    ty = dest_y_bot - strip_mb_bottom
                    out_page.mergeTransformedPage(strip, [1, 0, 0, 1, tx, ty])

            y_bottom = PAGE_H - self.PAGE_MARGIN_PT  # current top-of-page in PDF coords (from bottom)
            page_strips = []

            for (strip, sh) in strips:
                if sh > usable_h:
                    # Strip is taller than a full page – scale it down by splitting
                    # at page boundaries (rare edge case: just let it overflow for now)
                    sh = usable_h

                if sh > cursor_y:
                    # Flush current page
                    flush_page(page_strips, cur_page_h)
                    # Start new page
                    cursor_y   = usable_h
                    y_bottom   = PAGE_H - self.PAGE_MARGIN_PT
                    page_strips = []
                    cur_page_h  = 0

                dest_y_bot = y_bottom - sh
                page_strips.append((strip, sh, dest_y_bot))
                y_bottom   -= sh
                cursor_y   -= sh
                cur_page_h += sh

            # Flush the last (possibly partial) page
            if page_strips:
                flush_page(page_strips, cur_page_h)

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
