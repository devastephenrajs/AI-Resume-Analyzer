"""
Text extraction service supporting PDF, DOCX, and TXT files.
"""
import os
import fitz  # PyMuPDF


def extract_text_from_pdf(file_path: str) -> str:
    """Extracts all text from a given PDF file."""
    text = ""
    try:
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
    return text


def extract_text_from_docx(file_path: str) -> str:
    """Extracts all text from a given DOCX file."""
    text = ""
    try:
        from docx import Document
        doc = Document(file_path)
        paragraphs = [para.text for para in doc.paragraphs]
        text = "\n".join(paragraphs)
    except Exception as e:
        print(f"Error reading DOCX {file_path}: {e}")
    return text


def extract_text_from_txt(file_path: str) -> str:
    """Reads all text from a plain text file."""
    text = ""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
    except Exception as e:
        print(f"Error reading TXT {file_path}: {e}")
    return text


def extract_text(file_path: str) -> str:
    """
    Dispatcher: extract text from any supported file format.
    Routes to the appropriate extractor based on file extension.
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    elif ext == ".txt":
        return extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")
