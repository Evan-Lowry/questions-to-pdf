import re


def clean_question_text(text):
    """Clean and format question text for better display."""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    text = text.strip()
    return text


def format_question_number(question_text):
    """Extract and format question number."""
    match = re.match(r'(\d+\.\d+\.\d+\.)', question_text)
    if match:
        return match.group(1)
    return None


def is_section_header(text):
    """Check if text is a section header."""
    return bool(re.match(r'Section\s+[\d.]+\s+\w+', text))


def extract_sub_questions(question_text):
    """Extract sub-questions (a), (b), (c), etc. from a question."""
    # Pattern to match sub-questions like (a), (b), (c)
    sub_question_pattern = r'\(([a-z])\)'
    sub_questions = re.split(sub_question_pattern, question_text)
    
    result = []
    main_question = sub_questions[0].strip() if sub_questions else question_text
    
    # Pair up the sub-question labels with their content
    for i in range(1, len(sub_questions), 2):
        if i + 1 < len(sub_questions):
            label = sub_questions[i]
            content = sub_questions[i + 1].strip()
            result.append((label, content))
    
    return main_question, result


def format_for_display(questions):
    """Format questions for preview display in the GUI."""
    formatted = []
    for i, question in enumerate(questions, 1):
        if is_section_header(question):
            formatted.append(f"\n{'='*50}\n{question}\n{'='*50}")
        else:
            formatted.append(f"{question}")
    return "\n\n".join(formatted)


def calculate_spacing_height(page_fraction=0.25):
    """Calculate spacing height based on page fraction.
    
    Args:
        page_fraction: Fraction of page to use for spacing (0.25 = quarter page)
    
    Returns:
        Height in inches
    """
    # Letter size page height is 11 inches
    page_height = 11
    return page_height * page_fraction