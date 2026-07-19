from pathlib import Path
import fitz  # PyMuPDF
import docx  # python-docx


def extract_text_from_pdf(file_path: str) -> str:

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF file not found at: {file_path}")

    # Open the PDF using fitz (PyMuPDF)
    with fitz.open(path) as doc:
        # Append text from each page
        # pyrefly: ignore [no-matching-overload]
        text = "\n".join(page.get_text("text") for page in doc)

    return text


def extract_text_from_docx(file_path: str) -> str:

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"DOCX file not found at: {file_path}")

    # Load the document using python-docx
    doc = docx.Document(str(path))
    
    # Extract text from paragraphs and join them with newlines
    paragraphs_text = [paragraph.text for paragraph in doc.paragraphs]
    return "\n".join(paragraphs_text)


def parse_resume(file_path: str) -> str:
    
    path = Path(file_path)
    extension = path.suffix.lower()

    if extension == ".pdf":
        return extract_text_from_pdf(str(path))
    elif extension == ".docx":
        return extract_text_from_docx(str(path))
    else:
        raise ValueError(
            f"Unsupported file extension '{extension}'. Only PDF and DOCX are supported."
        )

