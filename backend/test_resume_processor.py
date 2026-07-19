from pathlib import Path

from app.services.resume_processor import process_resume

resume = process_resume(
    str(Path("uploads") / "718e33f4f0ae44e382cbf3222d17a949.pdf")
)

print(resume.keys())

print()

print(resume["resume_information"]["name"])

print()

print(resume["resume_information"]["education"])

