import logging
import asyncio
from app.services.job_sources.base_source import BaseJobSource

logger = logging.getLogger(__name__)

# Static high-quality simulated startup jobs from Wellfound (focused on India and remote startup hubs)
SIMULATED_STARTUP_JOBS = [
    {
        "id": "wf-101",
        "title": "Backend Engineer (FastAPI/Python)",
        "company": "Kredible AI",
        "location": "Bengaluru, India",
        "country": "India",
        "employment_type": "Full-time",
        "experience_level": "Mid Level",
        "salary": "₹15,00,000 - ₹22,00,000",
        "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "REST API"],
        "description": "Kredible AI is building next-generation credit risk assessment APIs for fintech startups. We are looking for a backend engineer who is passionate about Python, clean code, and database design. You will own the development of our core ledger service.",
        "source": "Wellfound",
        "url": "https://wellfound.com/jobs/kredible-ai-backend-engineer",
        "posted_date": "2026-07-18",
        "workplace_type": "Onsite",
        "company_logo": "https://images.unsplash.com/photo-1549719386-74dfcbf7dbed?w=100&h=100&fit=crop&q=80"
    },
    {
        "id": "wf-102",
        "title": "Machine Learning Engineer",
        "company": "NeuralFlow Systems",
        "location": "Remote (Pune, India)",
        "country": "India",
        "employment_type": "Full-time",
        "experience_level": "Senior Level",
        "salary": "₹24,00,000 - ₹36,00,000",
        "required_skills": ["Python", "PyTorch", "Hugging Face", "Transformers", "NLP"],
        "description": "NeuralFlow is an LLM-orchestration startup creating agents for customer service teams. We are seeking a machine learning engineer to build, fine-tune, and deploy custom NLP models using Hugging Face and PyTorch.",
        "source": "Wellfound",
        "url": "https://wellfound.com/jobs/neuralflow-ml-engineer",
        "posted_date": "2026-07-17",
        "workplace_type": "Remote",
        "company_logo": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=100&h=100&fit=crop&q=80"
    },
    {
        "id": "wf-103",
        "title": "Frontend React Developer",
        "company": "ZetaCart",
        "location": "Mumbai, India",
        "country": "India",
        "employment_type": "Full-time",
        "experience_level": "Entry Level",
        "salary": "₹8,00,000 - ₹12,00,000",
        "required_skills": ["JavaScript", "React", "TailwindCSS", "Redux", "HTML5"],
        "description": "ZetaCart is a hyper-local e-commerce startup. We are looking for an energetic React Developer to help us design, build, and maintain our merchant dashboard interface. Experience with Tailwind and state management is required.",
        "source": "Wellfound",
        "url": "https://wellfound.com/jobs/zetacart-react-developer",
        "posted_date": "2026-07-19",
        "workplace_type": "Onsite",
        "company_logo": "https://images.unsplash.com/photo-1557200134-90327ee9fafa?w=100&h=100&fit=crop&q=80"
    },
    {
        "id": "wf-104",
        "title": "DevOps & Cloud Engineer",
        "company": "CloudSprint Technologies",
        "location": "Noida, India",
        "country": "India",
        "employment_type": "Contract",
        "experience_level": "Senior Level",
        "salary": "₹18,00,000 - ₹28,00,000",
        "required_skills": ["AWS", "Terraform", "Docker", "Kubernetes", "CI/CD"],
        "description": "CloudSprint assists enterprises in transitioning legacy architectures to serverless infrastructures on AWS. We are looking for a DevOps contractor experienced in Infrastructure as Code (Terraform) and Kubernetes orchestration.",
        "source": "Wellfound",
        "url": "https://wellfound.com/jobs/cloudsprint-devops-engineer",
        "posted_date": "2026-07-15",
        "workplace_type": "Hybrid",
        "company_logo": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=100&h=100&fit=crop&q=80"
    },
    {
        "id": "wf-105",
        "title": "Full Stack Engineer (React + Node.js)",
        "company": "Veloce Health",
        "location": "San Francisco, CA",
        "country": "USA",
        "employment_type": "Full-time",
        "experience_level": "Mid Level",
        "salary": "$110,000 - $140,000",
        "required_skills": ["React", "Node.js", "Express", "MongoDB", "TypeScript"],
        "description": "Veloce Health is a digital therapeutics platform. We are seeking a full stack software engineer to build patient engagement tools. Experience with TypeScript and Node.js backend development is highly valued.",
        "source": "Wellfound",
        "url": "https://wellfound.com/jobs/veloce-health-full-stack",
        "posted_date": "2026-07-16",
        "workplace_type": "Remote",
        "company_logo": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=100&h=100&fit=crop&q=80"
    },
    {
        "id": "wf-106",
        "title": "Data Analyst (SQL / Tableau)",
        "company": "QuickData Insights",
        "location": "Bengaluru, India",
        "country": "India",
        "employment_type": "Full-time",
        "experience_level": "Entry Level",
        "salary": "₹6,00,000 - ₹9,00,000",
        "required_skills": ["SQL", "Excel", "Tableau", "Python", "Data Extraction"],
        "description": "QuickData provides real-time SaaS performance logs to startup operators. We need a Data Analyst to build query pipelines, extract KPI dashboards, and write data summary briefings for our leadership teams.",
        "source": "Wellfound",
        "url": "https://wellfound.com/jobs/quickdata-analyst",
        "posted_date": "2026-07-19",
        "workplace_type": "Hybrid",
        "company_logo": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=100&h=100&fit=crop&q=80"
    }
]

class WellfoundSource(BaseJobSource):
    async def fetch_jobs(self, query: str = "", location: str = "", limit: int = 50) -> list[dict]:
        logger.info(f"Simulating Wellfound API search (query: '{query}', location: '{location}')...")
        
        # Simulate small latency to reflect external API call behavior
        await asyncio.sleep(0.3)
        
        filtered_jobs = []
        q_lower = query.lower() if query else ""
        loc_lower = location.lower() if location else ""
        
        for job in SIMULATED_STARTUP_JOBS:
            # Check query matches title, company, description, or skills
            query_match = not q_lower or (
                q_lower in job["title"].lower() or
                q_lower in job["company"].lower() or
                q_lower in job["description"].lower() or
                any(q_lower in skill.lower() for skill in job["required_skills"])
            )
            
            # Check location matches location or country
            loc_match = not loc_lower or (
                loc_lower in job["location"].lower() or
                loc_lower in job["country"].lower() or
                (loc_lower == "remote" and job["workplace_type"] == "Remote")
            )
            
            if query_match and loc_match:
                filtered_jobs.append(job)
                
        logger.info(f"Wellfound simulation returned {len(filtered_jobs)} matching listings.")
        return filtered_jobs[:limit]
