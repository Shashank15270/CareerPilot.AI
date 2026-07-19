import re
from pathlib import Path

# Define common section headings mapping to their normalized key names.
# This ensures flexible parsing of different section headers.
SECTION_MAPPING = {
    "summary": [
        "summary", "professional summary", "summary of qualifications",
        "objective", "career objective", "career goal", "profile",
        "professional profile", "about me", "executive summary"
    ],
    "skills": [
        "skills", "technical skills", "core competencies", "expertise",
        "technologies", "specialties", "key skills", "skills & tools",
        "skills & technology", "skills and technologies", "programming languages"
    ],
    "experience": [
        "experience", "work experience", "employment history",
        "professional experience", "work history", "employment",
        "professional background", "career history", "experience details"
    ],
    "education": [
        "education", "academic background", "academic qualifications",
        "qualifications", "education history", "academic profile", "degrees"
    ],
    "projects": [
        "projects", "academic projects", "personal projects",
        "selected projects", "technical projects", "key projects"
    ],
    "certifications": [
        "certifications", "certificates", "licenses", "courses",
        "certifications & courses", "credentials"
    ],
    "achievements": [
        "achievements", "awards", "honors", "accomplishments",
        "awards & achievements", "key accomplishments"
    ],
    "languages": [
        "languages", "language proficiency", "languages spoken", "linguistic skills"
    ]
}


def extract_email(text: str) -> str:
    """
    Extracts the first email address found in the resume text using a regular expression.

    Args:
        text (str): The raw text of the resume.

    Returns:
        str: The extracted email address, or an empty string if not found.
    """
    email_pattern = r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
    match = re.search(email_pattern, text)
    return match.group(0) if match else ""


def extract_phone(text: str) -> str:
    """
    Extracts the first phone number found in the resume text using a regular expression.
    Supports standard formats including parenthesis, dots, dashes, and international codes.

    Args:
        text (str): The raw text of the resume.

    Returns:
        str: The extracted phone number, or an empty string if not found.
    """
    # Regex matching typical telephone structures:
    # Optional leading '+' and country code, area codes in parenthesis, and numbers
    # separated by dashes, dots, or spaces.
    phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}'
    match = re.search(phone_pattern, text)
    return match.group(0).strip() if match else ""


def extract_name(text: str) -> str:
    """
    Extracts the candidate's name from the resume text.
    Heuristic: The name is typically at the top of the resume, in the first few
    lines, and does not contain email addresses, phone numbers, URLs, or section headings.

    Args:
        text (str): The raw text of the resume.

    Returns:
        str: The candidate's name, or an empty string if not found.
    """
    lines = [line.strip() for line in text.split('\n') if line.strip()]

    # Skip lines that contain contact details, links, or common headers
    ignore_keywords = {
        "resume", "cv", "curriculum", "vitae", "email", "phone", "contact",
        "address", "linkedin", "github", "portfolio", "page", "website"
    }

    # Inspect the first 5 non-empty lines
    for line in lines[:5]:
        # Ignore lines with email symbol or typical phone numbers
        if "@" in line or (any(char.isdigit() for char in line) and len([c for c in line if c.isdigit()]) >= 7):
            continue
        
        # Ignore links or websites
        lower_line = line.lower()
        if any(url_indicator in lower_line for url_indicator in ["http", "www.", ".com", "linkedin.com"]):
            continue
        
        # Ignore lines containing resume/contact labels
        if any(keyword in lower_line for keyword in ignore_keywords):
            continue
            
        # A name is typically 1 to 4 words, containing mostly alphabetic characters
        words = line.split()
        if 1 <= len(words) <= 4 and all(word[0].isalpha() or word[0] in ['"', "'"] for word in words if word):
            return line

    return ""


def _normalize_heading(line: str) -> str:
    """
    Helper function to clean and normalize a heading line.
    Removes leading numbers/bullets and trailing punctuation.

    Args:
        line (str): The raw line text.

    Returns:
        str: Normalized heading.
    """
    # Remove leading numbering or list bullets like "1. ", "A. ", "• "
    cleaned = re.sub(r'^(?:\d+\.|\w\.|[-•*●▪])\s*', '', line)
    # Lowercase and strip whitespace and common trailing punctuation (e.g. colons)
    return cleaned.strip().lower().rstrip(':,.•').strip()


def extract_sections(text: str) -> dict:
    """
    Parses the resume text line-by-line and groups lines under their respective
    section headings (e.g., Skills, Experience, Education).

    Args:
        text (str): The raw text of the resume.

    Returns:
        dict: A dictionary of sections mapped to their text content.
    """
    sections = {
        "summary": "",
        "skills": "",
        "experience": "",
        "education": "",
        "projects": "",
        "certifications": "",
        "achievements": "",
        "languages": ""
    }

    current_section = None
    section_lines = {sec: [] for sec in sections}

    # Build a lookup mapping of keyword -> section_name
    keyword_map = {}
    for sec_name, keywords in SECTION_MAPPING.items():
        for kw in keywords:
            keyword_map[kw] = sec_name

    lines = text.split("\n")
    for line in lines:
        cleaned_line = line.strip()
        if not cleaned_line:
            # Maintain paragraph flow inside sections
            if current_section:
                section_lines[current_section].append("")
            continue

        # Check if the line constitutes a section heading
        # Section headings are generally brief (6 words or less)
        words = cleaned_line.split()
        if len(words) <= 6:
            normalized = _normalize_heading(cleaned_line)
            if normalized in keyword_map:
                current_section = keyword_map[normalized]
                continue

        # Append line to currently active section
        if current_section:
            section_lines[current_section].append(line)

    # Reassemble parsed sections into single strings and clean up whitespace
    for sec in sections:
        content = "\n".join(section_lines[sec]).strip()
        sections[sec] = content

    return sections


def parse_education(text: str) -> list:
    """
    Parses education text into a list of structured education objects.
    Uses heuristics like common degree keywords, location comma patterns,
    and year patterns to distinguish lines.

    Args:
        text (str): The raw text of the education section.

    Returns:
        list: A list of dicts, each with keys: institution, degree, duration, location.
    """
    if not text.strip():
        return []

    lines = [line.strip() for line in text.split("\n") if line.strip()]
    entries = []

    degree_keywords = [
        "b.s", "m.s", "b.a", "m.a", "b.tech", "m.tech", "b.e", "m.sc", "bachelor",
        "master", "phd", "ph.d", "doctorate", "degree", "diploma", "graduate",
        "undergraduate", "school", "high school", "associate"
    ]

    inst_keywords = [
        "university", "college", "institute", "school", "academy", "polytechnic", "iit", "nit", "bits"
    ]

    def get_line_type(line: str) -> str:
        line_lower = line.lower()
        if re.search(r'\b(19|20)\d{2}\b', line):
            return "duration"
        if any(dk in line_lower for dk in degree_keywords):
            return "degree"
        if "," in line and len(line) <= 35 and not any(ik in line_lower for ik in inst_keywords):
            return "location"
        return "institution"

    current_entry = {}

    for line in lines:
        ltype = get_line_type(line)

        if ltype == "institution" and current_entry:
            entries.append(current_entry)
            current_entry = {}
        elif ltype in current_entry:
            entries.append(current_entry)
            current_entry = {}

        if ltype == "institution":
            current_entry["institution"] = line
        elif ltype == "location":
            current_entry["location"] = line
        elif ltype == "degree":
            current_entry["degree"] = line
        elif ltype == "duration":
            current_entry["duration"] = line

    if current_entry:
        entries.append(current_entry)

    final_entries = []
    for entry in entries:
        final_entries.append({
            "institution": entry.get("institution", ""),
            "degree": entry.get("degree", ""),
            "duration": entry.get("duration", ""),
            "location": entry.get("location", "")
        })

    return final_entries


def parse_projects(text: str) -> list:
    """
    Parses projects text into structured project objects.
    Uses line characteristics (bullets, dates, pipe separators) to group
    project titles, durations, technologies, and descriptions, resolving
    line-wrapping issues.

    Args:
        text (str): The raw text of the projects section.

    Returns:
        list: A list of dicts, each with keys: title, duration, technologies, description.
    """
    if not text.strip():
        return []

    lines = [line.strip() for line in text.split("\n") if line.strip()]
    entries = []

    current_project = None

    def is_date_range(line: str) -> bool:
        months = r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*"
        year = r"\b(19|20)\d{2}\b"
        present = r"present|current|ongoing"
        has_year = re.search(r'\b(19|20)\d{2}\b', line.lower())
        has_months = re.search(months, line.lower())
        has_present = re.search(present, line.lower())
        return bool(has_year and (has_months or has_present or "–" in line or "-" in line))

    def is_tech_line(line: str) -> bool:
        cleaned = line.strip()
        # Bullet lines are descriptions, not tech lines
        if cleaned.startswith(("•", "-", "*", "●", "▪", "–")) or re.match(r'^\d+\.\s', cleaned):
            return False

        tech_words = {
            "python", "fastapi", "react", "docker", "postgres", "sql", "java", "c++",
            "javascript", "html", "css", "mongodb", "aws", "git", "langchain", "langgraph", "chromadb", "openai"
        }
        has_separator = "|" in cleaned or "," in cleaned
        techs_found = sum(1 for word in cleaned.lower().split() if word.strip(",()|") in tech_words)
        
        if "|" in cleaned:
            return len(cleaned.split("|")) >= 2
            
        return has_separator and techs_found >= 2 and len(cleaned.split()) <= 12

    for idx, line in enumerate(lines):
        is_bullet = line.startswith(("•", "-", "*", "●", "▪", "–")) or re.match(r'^\d+\.\s', line)

        # Check if this line is a continuation of the description
        is_continuation = False
        if current_project and current_project["description"] and not is_bullet:
            desc_lines = current_project["description"].split("\n")
            last_line = desc_lines[-1].strip() if desc_lines else ""
            
            # Check lookahead: if the next line or the line after next is a metadata line,
            # then this line is a title, not a continuation.
            has_upcoming_metadata = False
            if idx + 1 < len(lines) and (is_date_range(lines[idx + 1]) or is_tech_line(lines[idx + 1])):
                has_upcoming_metadata = True
            elif idx + 2 < len(lines) and is_date_range(lines[idx + 2]) and is_tech_line(lines[idx + 1]):
                has_upcoming_metadata = True

            if not has_upcoming_metadata:
                if (line and line[0].islower()) or last_line.endswith("-") or (not is_date_range(line) and not is_tech_line(line) and len(line.split()) > 4 and not line.isupper()):
                    is_continuation = True

        if is_continuation:
            if current_project["description"].endswith("-"):
                current_project["description"] = current_project["description"][:-1] + line
            else:
                current_project["description"] += " " + line
            continue

        if not is_bullet:
            if current_project:
                if is_date_range(line):
                    current_project["duration"] = line
                    continue
                elif is_tech_line(line):
                    current_project["technologies"] = line
                    continue
                elif "|" in line and not current_project.get("technologies"):
                    current_project["technologies"] = line
                    continue

            if current_project:
                entries.append(current_project)
            current_project = {
                "title": line,
                "duration": "",
                "technologies": "",
                "description": ""
            }

        else:
            if current_project:
                cleaned_desc = re.sub(r'^(?:[•\-*●▪–]|\d+\.)\s*', '', line).strip()
                if current_project["description"]:
                    current_project["description"] += "\n" + cleaned_desc
                else:
                    current_project["description"] = cleaned_desc

    if current_project:
        entries.append(current_project)

    final_entries = []
    for entry in entries:
        final_entries.append({
            "title": entry.get("title", ""),
            "duration": entry.get("duration", ""),
            "technologies": entry.get("technologies", ""),
            "description": entry.get("description", "")
        })
    return final_entries


def parse_experience(text: str) -> list:
    """
    Parses experience text into structured experience objects.
    Uses heuristics to split text into distinct job entries and identify
    company, role, duration, and bulleted description points, resolving
    line-wrapping issues.

    Args:
        text (str): The raw text of the experience section.

    Returns:
        list: A list of dicts, each with keys: company, role, duration, description.
    """
    if not text.strip():
        return []

    lines = [line.strip() for line in text.split("\n") if line.strip()]
    entries = []

    current_exp = None

    def is_date_range(line: str) -> bool:
        months = r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*"
        year = r"\b(19|20)\d{2}\b"
        present = r"present|current|ongoing"
        has_year = re.search(r'\b(19|20)\d{2}\b', line.lower())
        has_months = re.search(months, line.lower())
        has_present = re.search(present, line.lower())
        return bool(has_year and (has_months or has_present or "–" in line or "-" in line))

    for idx, line in enumerate(lines):
        is_bullet = line.startswith(("•", "-", "*", "●", "▪", "–")) or re.match(r'^\d+\.\s', line)

        # Check if this line is a continuation of the description
        is_continuation = False
        if current_exp and current_exp["description"] and not is_bullet:
            desc_lines = current_exp["description"].split("\n")
            last_line = desc_lines[-1].strip() if desc_lines else ""
            
            # Check lookahead: if the next line or the line after next is a date range
            has_upcoming_metadata = False
            if idx + 1 < len(lines) and is_date_range(lines[idx + 1]):
                has_upcoming_metadata = True

            if not has_upcoming_metadata:
                if (line and line[0].islower()) or last_line.endswith("-") or (not is_date_range(line) and len(line.split()) > 4 and not line.isupper()):
                    is_continuation = True

        if is_continuation:
            if current_exp["description"].endswith("-"):
                current_exp["description"] = current_exp["description"][:-1] + line
            else:
                current_exp["description"] += " " + line
            continue

        if not is_bullet:
            if current_exp and not current_exp.get("duration") and is_date_range(line):
                current_exp["duration"] = line
                continue

            company = ""
            role = ""
            if "|" in line:
                parts = [p.strip() for p in line.split("|")]
                company, role = parts[0], parts[1]
            elif " – " in line:
                parts = [p.strip() for p in line.split(" – ")]
                company, role = parts[0], parts[1]
            elif " - " in line:
                parts = [p.strip() for p in line.split(" - ")]
                company, role = parts[0], parts[1]
            else:
                company = line
                role = ""

            if current_exp:
                entries.append(current_exp)

            if company and role:
                current_exp = {
                    "company": company,
                    "role": role,
                    "duration": "",
                    "description": ""
                }
            else:
                current_exp = {
                    "company": company,
                    "role": "",
                    "duration": "",
                    "description": ""
                }

        else:
            if current_exp:
                cleaned_desc = re.sub(r'^(?:[•\-*●▪–]|\d+\.)\s*', '', line).strip()
                if current_exp["description"]:
                    current_exp["description"] += "\n" + cleaned_desc
                else:
                    current_exp["description"] = cleaned_desc

    if current_exp:
        entries.append(current_exp)

    final_entries = []
    for entry in entries:
        final_entries.append({
            "company": entry.get("company", ""),
            "role": entry.get("role", ""),
            "duration": entry.get("duration", ""),
            "description": entry.get("description", "")
        })
    return final_entries


def parse_certifications(text: str) -> list:
    """
    Parses certifications text into a list of clean certification strings.
    Removes leading bullet points or numbers.

    Args:
        text (str): The raw text of the certifications section.

    Returns:
        list: A list of clean certification strings.
    """
    if not text.strip():
        return []

    lines = [line.strip() for line in text.split("\n") if line.strip()]
    certs = []
    for line in lines:
        cleaned = re.sub(r'^(?:[•\-*●▪–]|\d+\.)\s*', '', line).strip()
        if cleaned:
            certs.append(cleaned)
    return certs


def split_skills_line(text: str) -> list:
    """
    Splits a skill text line by common delimiters (comma, pipe, bullets)
    while keeping text inside parentheses intact to avoid splitting details.

    Args:
        text (str): The raw skill line text.

    Returns:
        list: A list of cleaned skill items.
    """
    parts = []
    current = []
    paren_depth = 0
    for char in text:
        if char == '(':
            paren_depth += 1
            current.append(char)
        elif char == ')':
            paren_depth -= 1
            current.append(char)
        elif char in [',', '|', '•', '●', '▪'] and paren_depth == 0:
            parts.append("".join(current).strip())
            current = []
        else:
            current.append(char)
    if current:
        parts.append("".join(current).strip())
    return [p for p in parts if p]


def parse_skills(text: str):
    """
    Parses a skills text block into a categorized dictionary.
    Heuristics are used to detect sections like 'programming_languages',
    'frameworks', 'databases', etc., based on key headings and colons.
    If no categories are matched, returns the original text as a string.

    Args:
        text (str): The raw text of the skills section.

    Returns:
        Union[dict, str]: Categorized dictionary or the original text if no categories found.
    """
    if not text.strip():
        return {}

    # Define target structure
    structured_skills = {
        "programming_languages": [],
        "frameworks": [],
        "databases": [],
        "cloud": [],
        "devops": [],
        "machine_learning": [],
        "other": []
    }

    # Map header keywords to target categories
    category_keywords = {
        "programming_languages": ["programming", "languages", "programming languages", "language"],
        "frameworks": ["frameworks", "libraries", "web frameworks", "backend", "frontend", "framework"],
        "databases": ["databases", "database", "sql", "nosql", "datastore"],
        "cloud": ["cloud", "aws", "azure", "gcp", "platforms"],
        "devops": ["devops", "ci/cd", "tools", "infrastructure", "deployment"],
        "machine_learning": ["machine learning", "ml", "ai", "artificial intelligence", "deep learning", "data science", "nlp", "computer vision"]
    }

    # Find categories by splitting on "Header:" patterns.
    header_pattern = r'(?:\b|\n)([A-Za-z0-9\s&/]{3,35}):'
    matches = list(re.finditer(header_pattern, text))

    if not matches:
        # If no colon-based categories are found, try bullet points or comma list
        # If it's just a comma-separated list, we can put everything in "other"
        skills_list = split_skills_line(text.replace("\n", ","))
        if skills_list:
            structured_skills["other"] = skills_list
            return structured_skills
        return text

    # Extract sections between header matches
    sections = []
    for i in range(len(matches)):
        start = matches[i].end()
        end = matches[i+1].start() if i + 1 < len(matches) else len(text)
        header = matches[i].group(1).strip()
        content = text[start:end].strip()
        sections.append((header, content))

    def get_category_key(header: str) -> str:
        header_lower = header.lower()
        for cat_key, keywords in category_keywords.items():
            for kw in keywords:
                if kw in header_lower:
                    return cat_key
        return "other"

    category_detected = False
    for header, content in sections:
        cat_key = get_category_key(header)
        if cat_key != "other":
            category_detected = True

        content_clean = content.replace("\n", ",")
        parts = split_skills_line(content_clean)

        items = []
        for part in parts:
            item = part.strip()
            if item:
                items.append(item)

        if items:
            structured_skills[cat_key].extend(items)

    # Clean up duplicate entries or empty lists
    for key in list(structured_skills.keys()):
        seen = set()
        deduped = [x for x in structured_skills[key] if not (x in seen or seen.add(x))]
        structured_skills[key] = deduped

    # If no standard categories were actually populated (all fell to 'other'),
    # or if we couldn't detect meaningful categories, return the original text.
    if not category_detected:
        return text

    return structured_skills


def extract_resume_information(resume_text: str) -> dict:
    """
    Extracts structured data from raw resume text, mapping contact details
    and parsed sections to a standard schema.

    Args:
        resume_text (str): The raw text of the resume.

    Returns:
        dict: A dictionary containing extracted name, email, phone, and
              section-by-section text content along with the original raw text.
    """
    # Extract contact information and candidate name
    name = extract_name(resume_text)
    email = extract_email(resume_text)
    phone = extract_phone(resume_text)

    # Segment the resume into main functional sections
    sections = extract_sections(resume_text)

    # Parse and structure complex sections
    education = parse_education(sections["education"])
    projects = parse_projects(sections["projects"])
    experience = parse_experience(sections["experience"])
    certifications = parse_certifications(sections["certifications"])
    skills = parse_skills(sections["skills"])

    # Construct the final unified schema
    structured_resume = {
        "name": name,
        "email": email,
        "phone": phone,
        "summary": sections["summary"],
        "skills": skills,
        "experience": experience,
        "education": education,
        "projects": projects,
        "certifications": certifications,
        "achievements": sections["achievements"],
        "languages": sections["languages"],
        "raw_text": resume_text
    }

    return structured_resume
