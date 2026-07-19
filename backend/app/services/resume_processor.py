from pathlib import Path
from app.services.resume_parser import parse_resume
from app.services.resume_information_extractor import extract_resume_information


class ResumeProcessingError(Exception):
    """Base exception class for any failures in the resume processing pipeline."""
    pass


class ResumeParsingError(ResumeProcessingError):
    """Exception raised when text extraction from the resume file fails."""
    pass


class ResumeExtractionError(ResumeProcessingError):
    """Exception raised when parsing raw text into structured objects fails."""
    pass


def process_resume(file_path: str) -> dict:
    """
    Executes the full resume processing pipeline.
    It reads raw text from a PDF or DOCX file, extracts contact info,
    skills, experience, education, projects, and certifications, and returning
    a unified dictionary containing all metadata and content.

    This service is independent of web frameworks (e.g. FastAPI) and raises standard,
    meaningful Python exceptions.

    Args:
        file_path (str): Path to the resume file (PDF or DOCX).

    Returns:
        dict: A dictionary structured as:
            {
                "file_path": "...",
                "resume_text": "...",
                "resume_information": {...}
            }

    Raises:
        FileNotFoundError: If the specified file does not exist on disk.
        ResumeParsingError: If text extraction from the document fails.
        ResumeExtractionError: If structuring raw text into sections fails.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Resume file not found at path: {file_path}")

    resolved_path = str(path.resolve())

    # Step 1: Extract raw text from the resume file
    try:
        raw_text = parse_resume(resolved_path)
    except FileNotFoundError as fnf_err:
        raise FileNotFoundError(str(fnf_err)) from fnf_err
    except Exception as exc:
        raise ResumeParsingError(f"Failed to extract text from {file_path}: {str(exc)}") from exc

    # Step 2: Convert raw text into structured resume information
    try:
        structured_info = extract_resume_information(raw_text)
    except Exception as exc:
        raise ResumeExtractionError(f"Failed to structure extracted resume details: {str(exc)}") from exc

    # Step 3: Return unified structure
    result = {
        "file_path": resolved_path,
        "resume_text": raw_text,
        "resume_information": structured_info
    }

    # Save to latest_resume.json for downstream AI career coach endpoints
    try:
        import json
        uploads_dir = Path(__file__).resolve().parent.parent.parent / "uploads"
        uploads_dir.mkdir(parents=True, exist_ok=True)
        latest_path = uploads_dir / "latest_resume.json"
        with open(latest_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Failed to cache parsed resume: {e}")

    return result

