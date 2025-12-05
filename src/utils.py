import PyPDF2
from typing import List

def extract_text_from_pdf(file_path):
    reader = PyPDF2.PdfReader(file_path)
    pages_text: List[str] = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages_text.append(text)

    return "\n\n".join(pages_text)