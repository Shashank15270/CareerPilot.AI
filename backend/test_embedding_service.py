from app.services.resume_processor import process_resume
from app.services.embedding_service import generate_embedding

resume = process_resume("uploads/718e33f4f0ae44e382cbf3222d17a949.pdf")

# Build the text you want to embed.
# For example, combine summary, skills, projects, and experience.
resume_text = (
    resume["resume_information"]["summary"]
    + "\n"
    + str(resume["resume_information"]["skills"])
    + "\n"
    + "\n".join(project["description"] for project in resume["resume_information"]["projects"])
)

embedding = generate_embedding(resume_text)

print(f"Embedding dimension: {len(embedding)}")