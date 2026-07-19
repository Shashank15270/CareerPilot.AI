import uuid
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException, status

router = APIRouter()


UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"


UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
   
    # Define allowed file extensions and MIME types
    allowed_extensions = {".pdf", ".docx"}
    allowed_content_types = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    }

    # Extract filename and extension using pathlib
    filename = file.filename or "unnamed_file"
    file_path_obj = Path(filename)
    extension = file_path_obj.suffix.lower()

    # Validate file type by extension and content type header
    is_valid = (
        extension in allowed_extensions or 
        file.content_type in allowed_content_types
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only PDF and DOCX files are accepted."
        )

    # Generate a unique name for the file to prevent filename collisions
    # using a cryptographically secure UUID4 hex string.
    unique_filename = f"{uuid.uuid4().hex}{extension}"
    
    # Construct the full destination path using Path division operator
    destination_path = UPLOAD_DIR / unique_filename

    try:
        # Open the destination file in binary write mode ('wb')
        # using pathlib's path.open() method.
        with destination_path.open("wb") as buffer:
            # Read the file in 1MB chunks asynchronously to avoid 
            # blocking the event loop for large uploads.
            while chunk := await file.read(1024 * 1024):
                buffer.write(chunk)
    except Exception as e:
        # In case of any disk I/O error, raise a 500 Internal Server Error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save the uploaded file: {str(e)}"
        )
    finally:
        # Always close the upload file to release system resources
        await file.close()

    return {
        "original_filename": filename,
        "saved_filename": unique_filename,
        "file_path": str(destination_path.resolve()),
        "content_type": file.content_type,
        "message": "Resume received and saved successfully."
    }
