from pathlib import Path

from app.services.resume_parser import parse_resume
from app.services.resume_information_extractor import (
    extract_resume_information,
)

# Path to your uploaded resume
BASE_DIR = Path(__file__).resolve().parent

resume_path = (
    BASE_DIR
    / "uploads"
    / "1f0986e69c1b47628ddbd226b4291dbb.pdf"
)

# Step 1: Extract text from PDF
resume_text = parse_resume(str(resume_path))

# Step 2: Extract structured information
resume_information = extract_resume_information(resume_text)

# Step 3: Pretty print the result
print("\n===== STRUCTURED RESUME =====\n")

for key, value in resume_information.items():

    print(f"{key.upper()}")

    print("-" * 40)

    if isinstance(value, str):

        if value.strip():
            print(value)      # Only print first 500 chars
        else:
            print("(Not Found)")

    else:
        print(value)

    print("\n")