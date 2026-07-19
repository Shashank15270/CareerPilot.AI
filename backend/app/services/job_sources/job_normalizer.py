import re
import uuid
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def _strip_html(text: str) -> str:
    """Strips HTML tags from description text."""
    if not text:
        return ""
    # Replace common block elements with newlines for readability
    text = (
        text.replace("<p>", "")
        .replace("</p>", "\n")
        .replace("<br>", "\n")
        .replace("<br/>", "\n")
        .replace("<li>", "- ")
        .replace("</li>", "\n")
    )
    # Strip any other tags
    clean = re.compile(r'<.*?>')
    cleaned_text = re.sub(clean, '', text)
    # Decode common HTML entities
    cleaned_text = (
        cleaned_text.replace("&nbsp;", " ")
        .replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", '"')
        .replace("&#39;", "'")
    )
    return cleaned_text.strip()

def _format_date(date_str: str) -> str:
    """Parses date string and returns standard YYYY-MM-DD format."""
    if not date_str:
        return datetime.today().strftime('%Y-%m-%d')
    try:
        # Check standard ISO formats like '2026-07-16T12:00:00Z'
        match = re.match(r'^(\d{4}-\d{2}-\d{2})', date_str)
        if match:
            return match.group(1)
        # Try custom parse if needed
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d')
    except Exception:
        # Return today's date if parsing fails
        return datetime.today().strftime('%Y-%m-%d')

def _guess_workplace_type(title: str, location: str, description: str, default: str = "Onsite") -> str:
    """Guesses workplace type (Remote, Hybrid, Onsite) from text fields."""
    combined = f"{title} {location} {description}".lower()
    if "remote" in combined or "work from home" in combined or "wfh" in combined or "anywhere" in combined:
        return "Remote"
    if "hybrid" in combined or "flexible location" in combined or "partially remote" in combined:
        return "Hybrid"
    return default

def _guess_experience_level(title: str, description: str, default: str = "Mid Level") -> str:
    """Guesses experience level based on title and description content."""
    combined = f"{title} {description}".lower()
    
    if any(keyword in combined for keyword in ["executive", "chief", "director", " vp ", "vice president"]):
        return "Executive"
    if any(keyword in combined for keyword in ["lead", "principal", "architect", "manager"]):
        return "Lead"
    if any(keyword in combined for keyword in ["senior", "sr.", "sr "]) or "5+" in combined or "8+" in combined:
        return "Senior Level"
    if any(keyword in combined for keyword in ["junior", "jr.", "entry", "intern", "associate", "graduate"]) or "0-2" in combined or "1+" in combined:
        return "Entry Level"
    
    return default

def _extract_skills(title: str, description: str) -> list[str]:
    """Helper to extract typical technical skills from title and description if not explicitly provided."""
    common_skills = [
        "Python", "FastAPI", "React", "Docker", "PostgreSQL", "SQL", "Java", "C++",
        "JavaScript", "TypeScript", "HTML", "CSS", "MongoDB", "AWS", "Git", "Kubernetes",
        "Terraform", "CI/CD", "Machine Learning", "PyTorch", "TensorFlow", "NLP",
        "LLM", "Hugging Face", "Pandas", "NumPy", "Power BI", "Tableau", "Excel"
    ]
    combined = f"{title} {description}".lower()
    found_skills = []
    for skill in common_skills:
        # Match word boundaries or boundary with non-word character (like C++)
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if skill.lower() in ["c++", "c#", ".net"]:
            pattern = re.escape(skill.lower())
        if re.search(pattern, combined):
            found_skills.append(skill)
    return found_skills

def normalize_adzuna_job(raw_job: dict) -> dict:
    """Normalizes an Adzuna raw job dictionary."""
    job_id = str(raw_job.get("id") or uuid.uuid4().hex)
    title = raw_job.get("title") or ""
    # Strip any markup from title
    title = re.sub('<[^<]+?>', '', title).strip()
    
    company = raw_job.get("company", {}).get("display_name") or ""
    
    location_parts = []
    location_data = raw_job.get("location", {})
    if location_data.get("display_name"):
        location_parts.append(location_data["display_name"])
    if location_data.get("area"):
        # area is list from most general to specific, e.g. ["UK", "London"]
        areas = [a for a in location_data["area"] if isinstance(a, str)]
        location_parts.extend(reversed(areas))
        
    location = ", ".join(dict.fromkeys(location_parts)) or "India"
    
    country = "India"
    if "united states" in location.lower() or "usa" in location.lower():
        country = "USA"
    elif "united kingdom" in location.lower() or "uk" in location.lower():
        country = "UK"
    elif "canada" in location.lower():
        country = "Canada"
    elif "australia" in location.lower():
        country = "Australia"
    elif location_data.get("area") and len(location_data["area"]) > 0:
        # usually country is first item in area, e.g. "India"
        country = location_data["area"][0]

    # Map contract types
    contract_type = raw_job.get("contract_type") or ""
    contract_time = raw_job.get("contract_time") or ""
    emp_type = "Full-time"
    if "part" in contract_time.lower() or "part" in contract_type.lower():
        emp_type = "Part-time"
    elif "contract" in contract_type.lower() or "contract" in contract_time.lower():
        emp_type = "Contract"
    elif "freelance" in contract_type.lower() or "freelance" in contract_time.lower():
        emp_type = "Freelance"

    description = _strip_html(raw_job.get("description") or "")
    
    salary_min = raw_job.get("salary_min")
    salary_max = raw_job.get("salary_max")
    salary = ""
    if salary_min is not None and salary_max is not None:
        salary = f"₹{salary_min:,.0f} - ₹{salary_max:,.0f}" if country == "India" else f"${salary_min:,.0f} - ${salary_max:,.0f}"
    elif salary_min is not None:
        salary = f"₹{salary_min:,.0f}+" if country == "India" else f"${salary_min:,.0f}+"

    posted_date = _format_date(raw_job.get("created"))
    workplace_type = _guess_workplace_type(title, location, description, default="Onsite")
    experience_level = _guess_experience_level(title, description)
    required_skills = _extract_skills(title, description)

    return {
        "id": f"adzuna-{job_id}",
        "title": title,
        "company": company,
        "location": location,
        "country": country,
        "employment_type": emp_type,
        "experience_level": experience_level,
        "salary": salary,
        "required_skills": required_skills,
        "description": description,
        "source": "Adzuna",
        "url": raw_job.get("redirect_url") or "",
        "posted_date": posted_date,
        "workplace_type": workplace_type,
        "company_logo": ""
    }

def normalize_jsearch_job(raw_job: dict) -> dict:
    """Normalizes a JSearch raw job dictionary."""
    job_id = str(raw_job.get("job_id") or uuid.uuid4().hex)
    title = raw_job.get("job_title") or ""
    company = raw_job.get("employer_name") or ""
    
    city = raw_job.get("job_city")
    state = raw_job.get("job_state")
    country_code = raw_job.get("job_country") or "IN"
    
    location_parts = [p for p in [city, state, country_code] if p]
    location = ", ".join(location_parts) or "India"
    
    country = "India"
    if country_code == "US":
        country = "USA"
    elif country_code == "GB":
        country = "UK"
    elif country_code == "CA":
        country = "Canada"
    elif country_code == "AU":
        country = "Australia"
    elif country_code != "IN":
        country = country_code

    emp_type_raw = str(raw_job.get("job_employment_type") or "").upper()
    emp_type = "Full-time"
    if "PART" in emp_type_raw:
        emp_type = "Part-time"
    elif "CONTRACT" in emp_type_raw:
        emp_type = "Contract"
    elif "INTERN" in emp_type_raw:
        emp_type = "Internship"
    elif "FREE" in emp_type_raw or "GIG" in emp_type_raw:
        emp_type = "Freelance"

    description = _strip_html(raw_job.get("job_description") or "")
    
    # Format salary
    min_sal = raw_job.get("job_min_salary")
    max_sal = raw_job.get("job_max_salary")
    currency = raw_job.get("job_salary_currency") or "$"
    salary = ""
    if min_sal is not None and max_sal is not None:
        salary = f"{currency}{min_sal:,.0f} - {currency}{max_sal:,.0f}"
    elif min_sal is not None:
        salary = f"{currency}{min_sal:,.0f}+"

    # Workplace type
    workplace_type = "Onsite"
    if raw_job.get("job_is_remote"):
        workplace_type = "Remote"
    else:
        workplace_type = _guess_workplace_type(title, location, description, default="Onsite")

    posted_date = _format_date(raw_job.get("job_posted_at_datetime_utc"))
    experience_level = _guess_experience_level(title, description)
    
    # Skills from description or parameters
    required_skills = raw_job.get("job_required_skills")
    if not required_skills:
        required_skills = _extract_skills(title, description)

    return {
        "id": f"jsearch-{job_id}",
        "title": title,
        "company": company,
        "location": location,
        "country": country,
        "employment_type": emp_type,
        "experience_level": experience_level,
        "salary": salary,
        "required_skills": required_skills,
        "description": description,
        "source": "JSearch",
        "url": raw_job.get("job_apply_link") or raw_job.get("job_google_link") or "",
        "posted_date": posted_date,
        "workplace_type": workplace_type,
        "company_logo": raw_job.get("employer_logo") or ""
    }

def normalize_remotive_job(raw_job: dict) -> dict:
    """Normalizes a Remotive raw job dictionary."""
    job_id = str(raw_job.get("id") or uuid.uuid4().hex)
    title = raw_job.get("title") or ""
    company = raw_job.get("company_name") or ""
    
    req_location = raw_job.get("candidate_required_location") or "Remote"
    location = req_location
    
    # Guess country from required location
    country = "Worldwide"
    loc_lower = req_location.lower()
    if "india" in loc_lower:
        country = "India"
    elif "us" in loc_lower or "america" in loc_lower:
        country = "USA"
    elif "uk" in loc_lower or "united kingdom" in loc_lower:
        country = "UK"
    elif "canada" in loc_lower:
        country = "Canada"

    emp_type_raw = str(raw_job.get("job_type") or "").lower()
    emp_type = "Full-time"
    if "part" in emp_type_raw:
        emp_type = "Part-time"
    elif "contract" in emp_type_raw:
        emp_type = "Contract"
    elif "freelance" in emp_type_raw:
        emp_type = "Freelance"
    elif "intern" in emp_type_raw:
        emp_type = "Internship"

    description = _strip_html(raw_job.get("description") or "")
    salary = raw_job.get("salary") or ""
    posted_date = _format_date(raw_job.get("publication_date"))
    
    required_skills = raw_job.get("tags") or []
    if not required_skills:
        required_skills = _extract_skills(title, description)

    experience_level = _guess_experience_level(title, description)

    return {
        "id": f"remotive-{job_id}",
        "title": title,
        "company": company,
        "location": location,
        "country": country,
        "employment_type": emp_type,
        "experience_level": experience_level,
        "salary": salary,
        "required_skills": required_skills,
        "description": description,
        "source": "Remotive",
        "url": raw_job.get("url") or "",
        "posted_date": posted_date,
        "workplace_type": "Remote", # Remotive is always remote
        "company_logo": raw_job.get("company_logo") or ""
    }

def normalize_themuse_job(raw_job: dict) -> dict:
    """Normalizes a The Muse raw job dictionary."""
    job_id = str(raw_job.get("id") or uuid.uuid4().hex)
    title = raw_job.get("name") or ""
    company = raw_job.get("company", {}).get("name") or ""
    
    locations = raw_job.get("locations", [])
    location = locations[0].get("name") if locations else "Flexible / Remote"
    
    # Guess country
    country = "Worldwide"
    loc_lower = location.lower()
    if "india" in loc_lower:
        country = "India"
    elif "united states" in loc_lower or "us" in loc_lower or "ny" in loc_lower or "ca" in loc_lower:
        country = "USA"
    elif "united kingdom" in loc_lower or "uk" in loc_lower:
        country = "UK"

    # Map levels to experience_level
    levels = raw_job.get("levels", [])
    experience_level = "Mid Level"
    if levels:
        level_name = levels[0].get("name", "").lower()
        if "senior" in level_name:
            experience_level = "Senior Level"
        elif "entry" in level_name or "junior" in level_name:
            experience_level = "Entry Level"
        elif "lead" in level_name or "manager" in level_name:
            experience_level = "Lead"

    description = _strip_html(raw_job.get("contents") or "")
    posted_date = _format_date(raw_job.get("publication_date"))
    workplace_type = _guess_workplace_type(title, location, description, default="Onsite")
    
    # The Muse does not have direct tags list
    required_skills = _extract_skills(title, description)

    return {
        "id": f"themuse-{job_id}",
        "title": title,
        "company": company,
        "location": location,
        "country": country,
        "employment_type": "Full-time", # Default for Muse
        "experience_level": experience_level,
        "salary": "", # Muse rarely publishes direct API salary ranges
        "required_skills": required_skills,
        "description": description,
        "source": "The Muse",
        "url": raw_job.get("refs", {}).get("landing_page") or "",
        "posted_date": posted_date,
        "workplace_type": workplace_type,
        "company_logo": ""
    }

def normalize_job(source: str, raw_job: dict) -> dict:
    """Router function to normalize a job based on its source."""
    if source == "Adzuna":
        return normalize_adzuna_job(raw_job)
    elif source == "JSearch":
        return normalize_jsearch_job(raw_job)
    elif source == "Remotive":
        return normalize_remotive_job(raw_job)
    elif source == "The Muse":
        return normalize_themuse_job(raw_job)
    elif source == "Wellfound":
        # Wellfound simulated provider already yields normalized dict format
        return raw_job
    else:
        logger.warning(f"Unknown job source: {source}. Returning raw_job as-is.")
        return raw_job
