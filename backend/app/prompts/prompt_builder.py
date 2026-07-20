import json
from typing import Dict, List, Any

def build_resume_review_prompt(resume_text: str, resume_info: dict, job_details: dict = None) -> str:
    """
    Builds the prompt for Feature 1: AI Resume Review.

    When job_details is supplied, the ATS score is judged against that specific
    posting. Without it the review was resume-only, so every job card showed an
    identical ATS number no matter which role it was attached to.
    """
    resume_summary = {
        "name": resume_info.get("name", ""),
        "summary": resume_info.get("summary", ""),
        "skills": resume_info.get("skills", []),
        "experience_count": len(resume_info.get("experience", [])),
        "projects_count": len(resume_info.get("projects", [])),
        "education_count": len(resume_info.get("education", [])),
    }
    
    # Job-targeted section. Only present when the review is attached to a
    # specific posting, which is what makes the ATS score vary per job.
    job_block = ""
    scoring_rule = (
        '  "ats_compatibility_score": 78, // Integer 0-100: general ATS parse-ability'
    )
    if job_details:
        job_block = f"""
TARGET JOB — score the resume AGAINST THIS SPECIFIC POSTING:
Title: {job_details.get('title', '')}
Company: {job_details.get('company', '')}
Description:
\"\"\"
{(job_details.get('description') or '')[:2000]}
\"\"\"

Scoring rules for this job:
- "overall_score" = how strong this candidate is FOR THIS ROLE (0-100).
- "ats_compatibility_score" = how well the resume would pass an ATS keyword
  screen FOR THIS POSTING (0-100). Base it on overlap between the resume and the
  job's required keywords, titles and technologies. A resume missing most of the
  posting's core keywords MUST score low, even if it is well formatted.
- "strengths"/"weaknesses" must reference THIS job's requirements specifically.
- Do NOT give generic advice that would apply to any job.
"""
        scoring_rule = (
            '  "ats_compatibility_score": 78, // Integer 0-100 for THIS posting'
        )

    return f"""
You are an expert ATS (Applicant Tracking System) reviewer and hiring consultant.
Analyze the following resume details and raw text.
Provide an overall review and score.

Resume summary details:
{json.dumps(resume_summary, indent=2)}

Raw Resume Text:
\"\"\"
{(resume_text or "")[:4000]}
\"\"\"
{job_block}
You MUST return a JSON object with the following structure:
{{
  "overall_score": 85, // Integer score from 0 to 100
  "resume_summary": "Short 2-3 sentence professional summary...",
  "strengths": ["Strength 1", "Strength 2", ...],
  "weaknesses": ["Weakness 1", "Weakness 2", ...],
{scoring_rule},
  "formatting_suggestions": ["Suggestion 1", "Suggestion 2", ...],
  "missing_sections": ["Missing section 1", "Missing section 2", ...],
  "resume_improvement_suggestions": ["Suggestion 1", "Suggestion 2", ...],
  "project_suggestions": ["Suggestion 1", "Suggestion 2", ...],
  "technical_skill_suggestions": ["Suggestion 1", "Suggestion 2", ...],
  "soft_skill_suggestions": ["Suggestion 1", "Suggestion 2", ...]
}}

Ensure all suggestions are highly actionable and realistic. Do not return any Markdown wrapping or text outside the JSON object.
"""

def build_job_analysis_prompt(resume_info: dict, job_details: dict) -> str:
    """
    Builds the prompt for Feature 2: AI Match Explanation.
    """
    candidate_profile = {
        "summary": resume_info.get("summary", ""),
        "skills": resume_info.get("skills", []),
        "experience": resume_info.get("experience", []),
        "projects": resume_info.get("projects", [])
    }
    
    return f"""
You are a technical career match analyzer. Evaluate how well the candidate's profile matches the job description.

Candidate Profile:
{json.dumps(candidate_profile, indent=2)}

Job Details:
- Title: {job_details.get("title", "")}
- Company: {job_details.get("company", "")}
- Similarity Score: {job_details.get("similarity_score", 0.0)}
- Description: {(job_details.get("description") or "")[:2000]}

Generate a match explanation. You MUST return a JSON object matching this schema:
{{
  "why_matches": "A concise explanation of why the candidate fits this job...",
  "matched_skills": ["Skill 1", "Skill 2", ...],
  "matched_experience": ["Experience item 1", ...],
  "matched_projects": ["Project 1", ...],
  "match_explanation": "Detailed explanation of the alignment (2-3 paragraphs)...",
  "missing_skills": ["Skill 1", ...],
  "missing_technologies": ["Tech 1", ...],
  "improvement_suggestions": ["Improvement 1", "Improvement 2", ...],
  "career_advice": "Actionable career advice for landing this role..."
}}

Ensure the output is valid JSON and directly consumable. No text, markup, or wrapper code blocks.
"""

def build_skill_gap_prompt(resume_info: dict, job_details: dict) -> str:
    """
    Builds the prompt for Feature 3: Skill Gap Analysis.
    """
    candidate_skills = resume_info.get("skills", [])
    if isinstance(candidate_skills, dict):
        # Flatten skills
        flat_skills = []
        for cat, items in candidate_skills.items():
            if isinstance(items, list):
                flat_skills.extend(items)
            else:
                flat_skills.append(str(items))
        candidate_skills = flat_skills

    return f"""
You are a senior technical educator. Analyze the skills gap between the candidate and the target job description.

Candidate Skills:
{json.dumps(candidate_skills, indent=2)}

Job Description:
- Title: {job_details.get("title", "")}
- Company: {job_details.get("company", "")}
- Description: {(job_details.get("description") or "")[:2000]}

Compare their skills and generate recommendations to close the gaps.
You MUST return a JSON object with this exact schema:
{{
  "current_skills": ["Skill 1", "Skill 2", ...],
  "missing_skills": ["Skill A", "Skill B", ...],
  "recommended_courses": [
    {{
      "course_name": "Course Title (e.g. Deep Learning Specialization)",
      "platform": "Coursera / Udemy / edX / etc.",
      "priority": "High / Medium / Low",
      "estimated_time": "e.g. 40 hours"
    }}
  ],
  "recommended_certifications": [
    {{
      "certification_name": "Cert Name (e.g. AWS Certified Solutions Architect)",
      "priority": "High / Medium / Low",
      "estimated_time": "e.g. 80 hours"
    }}
  ],
  "estimated_time_to_learn": "Overall estimate to bridge key gaps, e.g. 3-6 months",
  "priority_order": ["Skill A", "Skill B", ...] // ordered from highest priority to lowest
}}

Ensure no markdown tags are present. Only return valid JSON.
"""

def build_interview_prep_prompt(resume_info: dict, job_details: dict) -> str:
    """
    Builds the prompt for Feature 4: Interview Preparation.
    """
    candidate_profile = {
        "summary": resume_info.get("summary", ""),
        "skills": resume_info.get("skills", []),
        "experience": resume_info.get("experience", [])
    }
    
    return f"""
You are a professional technical interviewer. Generate customized interview questions based on the candidate's profile and the job description.

Candidate Profile:
{json.dumps(candidate_profile, indent=2)}

Job Details:
- Title: {job_details.get("title", "")}
- Company: {job_details.get("company", "")}
- Description: {(job_details.get("description") or "")[:2000]}

Generate a set of questions (at least 3 per category) categorized by type.
Include:
- Technical Questions
- Behavioral Questions
- HR Questions
- Coding Questions (if it is a coding/software engineering role)
- Machine Learning Questions (only if it is an AI, ML, or Data Science role)
- Backend Questions (only if it is a backend or system engineering role)
- SQL Questions (only if it is an analyst, database, or data engineer role)
- Cloud Questions (only if it is a cloud, DevOps, or infrastructure role)

For every question, specify difficulty ("Easy", "Medium", "Hard"), expected topics, hints, and ideal answer guidelines.
You MUST return a JSON object structured exactly like this:
{{
  "technical_questions": [
    {{
      "question": "Question text...",
      "difficulty": "Medium",
      "expected_topics": ["Topic A", "Topic B"],
      "hints": ["Hint 1"],
      "ideal_answer_guidelines": "Explain this detail, mention that practice..."
    }}
  ],
  "behavioral_questions": [ ... ],
  "hr_questions": [ ... ],
  "coding_questions": [ ... ], // Optional (empty list if not applicable)
  "machine_learning_questions": [ ... ], // Optional (empty list if not applicable)
  "backend_questions": [ ... ], // Optional (empty list if not applicable)
  "sql_questions": [ ... ], // Optional (empty list if not applicable)
  "cloud_questions": [ ... ] // Optional (empty list if not applicable)
}}

Make sure the questions are highly relevant, challenging, and specific to the candidate's skills and the job's requirements. Only return valid JSON.
"""

def build_mock_interview_questions_prompt(resume_info: dict, job_details: dict, count: int = 5) -> str:
    """
    Builds the prompt to pre-generate mock interview questions.
    """
    candidate_profile = {
        "summary": resume_info.get("summary", ""),
        "skills": resume_info.get("skills", []),
        "experience": resume_info.get("experience", [])
    }
    
    return f"""
You are an interviewer. Generate exactly {count} distinct, customized interview questions for this candidate targeting this job.
The questions should progress in difficulty and cover:
- 1-2 Technical questions specific to their tech stack
- 1 Practical coding/scenario question or ML/SQL question depending on the job
- 1 Behavioral question (STAR method)
- 1 HR/Situational question

Candidate Profile:
{json.dumps(candidate_profile, indent=2)}

Job Details:
- Title: {job_details.get("title", "")}
- Company: {job_details.get("company", "")}
- Description: {(job_details.get("description") or "")[:2000]}

You MUST return a JSON object with this exact schema:
{{
  "questions": [
    "Question 1 content here...",
    "Question 2 content here...",
    "Question 3 content here...",
    "Question 4 content here...",
    "Question 5 content here..."
  ]
}}

Ensure there are exactly {count} questions in the list. Do not include markdown code block wrappers.
"""

def build_mock_interview_evaluation_prompt(job_details: dict, question: str, answer: str) -> str:
    """
    Builds the prompt to evaluate a single mock interview question.
    """
    return f"""
You are a senior technical recruiter. Evaluate the candidate's response to the interview question below.

Job Role: {job_details.get("title", "")} ({job_details.get("company", "")})
Question Asked: {question}
Candidate's Response: {answer}

Evaluate the candidate's answer based on:
1. Technical Accuracy (Does it show correctness and depth?)
2. Communication (Is it clear, structured, and easy to follow?)
3. Confidence (Does it sound professional, structured, and assertive?)
4. Completeness (Did they answer all parts of the question?)
5. Problem Solving (Did they show logical thinking or proper trade-off considerations?)

For each dimension, assign a score out of 100 and brief feedback. Also provide overall strengths, weaknesses, suggestions, and an overall score.
You MUST return a JSON object with this structure:
{{
  "technical_accuracy": {{ "score": 80, "feedback": "Feedback..." }},
  "communication": {{ "score": 85, "feedback": "Feedback..." }},
  "confidence": {{ "score": 75, "feedback": "Feedback..." }},
  "completeness": {{ "score": 70, "feedback": "Feedback..." }},
  "problem_solving": {{ "score": 80, "feedback": "Feedback..." }},
  "overall_score": 78, // Integer 0 to 100
  "strengths": ["Strength 1", "Strength 2"],
  "weaknesses": ["Weakness 1", "Weakness 2"],
  "suggestions": ["Suggestion 1", "Suggestion 2"]
}}

Do not include markdown code block wrappers. Output strict JSON.
"""

def build_mock_interview_final_report_prompt(job_details: dict, history: List[Dict[str, Any]]) -> str:
    """
    Builds the prompt to compile the final evaluation report.
    """
    return f"""
You are a principal hiring manager. Compile a final comprehensive candidate evaluation report based on their entire mock interview history.

Job Role: {job_details.get("title", "")} ({job_details.get("company", "")})
Interview History:
{json.dumps(history, indent=2)}

Provide a summary report evaluating whether you would hire this candidate.
You MUST return a JSON object with this structure:
{{
  "overall_recommendation": "Strong Hire / Hire / No Hire",
  "average_score": 82, // Integer 0 to 100
  "overall_summary": "A 3-4 sentence comprehensive evaluation summary...",
  "strengths": ["Strengths 1", "Strengths 2", ...],
  "weaknesses": ["Weakness 1", "Weakness 2", ...],
  "coaching_roadmap": ["Step 1", "Step 2", ...],
  "performance_by_question": [
    {{
      "question": "Question text",
      "user_answer": "Candidate's response",
      "score": 80,
      "feedback": "Individual question feedback summary"
    }}
  ]
}}

Ensure no markdown tags are present. Only return valid JSON.
"""

def build_career_coach_prompt(resume_info: dict) -> str:
    """
    Builds the prompt for Feature 6: Career Coach.
    """
    candidate_profile = {
        "name": resume_info.get("name", ""),
        "summary": resume_info.get("summary", ""),
        "skills": resume_info.get("skills", []),
        "experience": resume_info.get("experience", []),
        "projects": resume_info.get("projects", []),
        "certifications": resume_info.get("certifications", [])
    }
    
    return f"""
You are an executive career advisor. Analyze this candidate's profile and outline a career roadmap.

Candidate Profile:
{json.dumps(candidate_profile, indent=2)}

Provide structured, high-value career path advice. You MUST return a JSON object with this structure:
{{
  "career_path": ["Next role in 1-2 years", "Mid-term role in 3-5 years", "Long-term role in 5-10 years"],
  "next_roles": ["Role Title A", "Role Title B", "Role Title C"],
  "expected_salary_growth": "A brief analysis of salary benchmarks and growth percentage projections...",
  "recommended_technologies": ["Technology A", "Technology B", ...],
  "recommended_projects": [
    {{
      "title": "Project Title",
      "description": "Comprehensive description of a high-value portfolio project...",
      "technologies": ["Tech A", "Tech B"]
    }}
  ],
  "recommended_certifications": ["Certification 1", "Certification 2", ...],
  "learning_roadmap": [
    {{
      "phase": "Phase 1: Foundation (Months 1-3)",
      "milestone": "What to build/accomplish",
      "action_items": ["Action 1", "Action 2"]
    }}
  ],
  "ninety_day_improvement_plan": [
    {{
      "timeframe": "Days 1-30: Core Skill-up",
      "actions": ["Action A", "Action B"]
    }},
    {{
      "timeframe": "Days 31-60: Project Build",
      "actions": ["Action A", "Action B"]
    }},
    {{
      "timeframe": "Days 61-90: Interview prep & Applications",
      "actions": ["Action A", "Action B"]
    }}
  ]
}}

Ensure no markdown tags are present. Only return valid JSON.
"""
