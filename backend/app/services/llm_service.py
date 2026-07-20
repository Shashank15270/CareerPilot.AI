import os
import json
import uuid
import logging
import asyncio
from typing import Dict, List, Any, Optional

import httpx
from fastapi import HTTPException, status

from app.prompts.prompt_builder import (
    build_resume_review_prompt,
    build_job_analysis_prompt,
    build_skill_gap_prompt,
    build_interview_prep_prompt,
    build_mock_interview_questions_prompt,
    build_mock_interview_evaluation_prompt,
    build_mock_interview_final_report_prompt,
    build_career_coach_prompt
)

logger = logging.getLogger(__name__)

# Stateful Mock Interview Sessions
MOCK_INTERVIEW_SESSIONS: Dict[str, Dict[str, Any]] = {}

async def call_groq(prompt: str, retries: int = 3, timeout_sec: float = 30.0) -> dict:
    """
    Calls the Groq API with retry logic, timeout handling, invalid API key handling,
    rate limit handling, and JSON parsing error fallback.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        logger.error("GROQ_API_KEY not found in environment variables.")
        raise ValueError("Groq API key is not configured. Please set GROQ_API_KEY in the backend .env file.")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Use llama-3.3-70b-versatile for high quality and generous limits
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a professional career coach and hiring assistant. You must respond ONLY with a valid, clean JSON object. Do not include markdown code block wrappers (like ```json ... ```) or any other text before/after the JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.2
    }

    for attempt in range(1, retries + 1):
        try:
            timeouts = httpx.Timeout(timeout_sec, connect=8.0)
            async with httpx.AsyncClient(timeout=timeouts) as client:
                logger.info(f"Groq API request attempt {attempt}/{retries} using model {model}")
                response = await client.post(url, headers=headers, json=payload)

                # Handle Rate Limits (HTTP 429).
                if response.status_code == 429:
                    retry_after = response.headers.get("retry-after")
                    try:
                        wait_s = float(retry_after) if retry_after else 6.0
                    except ValueError:
                        wait_s = 6.0

                    remaining = response.headers.get("x-ratelimit-remaining-tokens", "?")
                    logger.warning(
                        f"Groq rate limit on attempt {attempt}/{retries} "
                        f"(tokens remaining: {remaining}, retry-after: {wait_s}s)"
                    )

                    if attempt == retries or wait_s > 20:
                        raise HTTPException(
                            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                            detail=(
                                f"AI rate limit reached (Groq free tier allows ~12k tokens/min). "
                                f"Please wait about {int(wait_s) + 1}s and try again."
                            )
                        )
                    await asyncio.sleep(wait_s)
                    continue

                response.raise_for_status()

                response_data = response.json()
                content = response_data["choices"][0]["message"]["content"].strip()

                # Clean up output in case the model ignored system prompts and wrapped in markdown
                if content.startswith("```"):
                    lines = content.split("\n")
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines and lines[-1].strip() == "```":
                        lines = lines[:-1]
                    content = "\n".join(lines).strip()

                try:
                    data = json.loads(content)
                    return data
                except json.JSONDecodeError as je:
                    logger.error(f"JSONDecodeError on attempt {attempt}: {str(je)}. Response text was:\n{content}")
                    if attempt == retries:
                        raise ValueError(f"Groq API response was not valid JSON: {str(je)}") from je

        except httpx.HTTPStatusError as hse:
            logger.error(f"Groq API returned HTTP error status {hse.response.status_code}: {hse.response.text}")
            if attempt == retries:
                raise ValueError(f"Groq API returned an error: {hse.response.text}") from hse
            await asyncio.sleep(1.0)

        except asyncio.TimeoutError as te:
            logger.warning(f"Groq API request timed out on attempt {attempt}")
            if attempt == retries:
                raise TimeoutError("Groq API request timed out. Please try again.") from te
            await asyncio.sleep(1.0)

        except HTTPException:
            # Already a well-formed API error (e.g. the 429 raised above).
            raise

        except (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout) as ce:
            # Network-level failure reaching Groq. Retry quickly with a short backoff.
            logger.warning(
                f"Network error reaching Groq on attempt {attempt}/{retries}: "
                f"{type(ce).__name__}"
            )
            if attempt == retries:
                raise ConnectionError(
                    "Could not reach the Groq API. Check your internet connection "
                    "and try again."
                ) from ce
            await asyncio.sleep(1.5 * attempt)

        except Exception as e:
            logger.exception(f"Unexpected error in Groq API call on attempt {attempt}: {str(e)}")
            if attempt == retries:
                raise ValueError(f"An error occurred while communicating with Groq API: {str(e)}") from e
            await asyncio.sleep(1.0)

    raise ValueError("Failed to obtain a response from Groq API after retries.")


# -------------------------------------------------------------
# Career Coach Services
# -------------------------------------------------------------

async def review_resume(resume_text: str, resume_info: dict, job_details: dict = None) -> dict:
    """
    Feature 1: Review resume. When job_details is given, the scores are
    tailored to that specific posting rather than being generic.
    """
    prompt = build_resume_review_prompt(resume_text, resume_info, job_details)
    return await call_groq(prompt)


async def analyze_job_match(resume_info: dict, job_details: dict) -> dict:
    """
    Feature 2: Generate AI Match Explanation for a target job.
    """
    prompt = build_job_analysis_prompt(resume_info, job_details)
    return await call_groq(prompt)


async def analyze_skill_gap(resume_info: dict, job_details: dict) -> dict:
    """
    Feature 3: Generate Skill Gap Analysis for a target job.
    """
    prompt = build_skill_gap_prompt(resume_info, job_details)
    return await call_groq(prompt)


async def prepare_interview(resume_info: dict, job_details: dict) -> dict:
    """
    Feature 4: Generate customized interview prep questions.
    """
    prompt = build_interview_prep_prompt(resume_info, job_details)
    return await call_groq(prompt)


async def start_mock_interview_session(resume_info: dict, job_details: dict) -> dict:
    """
    Feature 5 (Part A): Starts a mock interview session.
    Generates 5 questions, saves state, and returns the first question.
    """
    prompt = build_mock_interview_questions_prompt(resume_info, job_details, count=5)
    result = await call_groq(prompt)
    
    questions = result.get("questions", [])
    if not questions or len(questions) < 5:
        logger.warning(f"Groq returned an invalid question list: {questions}. Using fallback questions.")
        questions = [
            "Tell me about a challenging technical project you worked on recently. What was your role?",
            "How do you keep up with learning new technologies or frameworks, and apply them in your job?",
            "Describe a time when you had a technical disagreement with a team member. How was it resolved?",
            "What is your strategy for optimizing application performance and code quality?",
            "Why are you interested in this role, and how do your skills align with our goals?"
        ]
    
    session_id = str(uuid.uuid4())
    MOCK_INTERVIEW_SESSIONS[session_id] = {
        "session_id": session_id,
        "resume_info": resume_info,
        "job_details": job_details,
        "questions": questions,
        "current_index": 0,
        "history": []
    }
    
    return {
        "session_id": session_id,
        "question": questions[0],
        "current_index": 0,
        "total_questions": len(questions),
        "completed": False
    }


async def submit_mock_interview_answer(session_id: str, answer: str) -> dict:
    """
    Feature 5 (Part B): Evaluates user's answer, advances to next question,
    and returns evaluation + next question (or final report if interview is complete).
    """
    session = MOCK_INTERVIEW_SESSIONS.get(session_id)
    if not session:
        raise ValueError(f"Mock interview session {session_id} not found or expired.")
        
    questions = session["questions"]
    idx = session["current_index"]
    
    if idx >= len(questions):
        raise ValueError("Mock interview has already been completed.")
        
    question_asked = questions[idx]
    job_details = session["job_details"]
    
    # 1. Evaluate current answer
    prompt = build_mock_interview_evaluation_prompt(job_details, question_asked, answer)
    evaluation = await call_groq(prompt)
    
    # 2. Append history
    session["history"].append({
        "question": question_asked,
        "user_answer": answer,
        "score": evaluation.get("overall_score", 0),
        "evaluation": evaluation
    })
    
    # 3. Advance index
    session["current_index"] += 1
    next_idx = session["current_index"]
    
    completed = next_idx >= len(questions)
    next_question = None if completed else questions[next_idx]
    final_report = None
    
    # 4. Generate final report if complete
    if completed:
        final_prompt = build_mock_interview_final_report_prompt(job_details, session["history"])
        final_report = await call_groq(final_prompt)
        # Cleanup session
        MOCK_INTERVIEW_SESSIONS.pop(session_id, None)
        
    return {
        "session_id": session_id,
        "evaluation": evaluation,
        "next_question": next_question,
        "current_index": next_idx,
        "total_questions": len(questions),
        "completed": completed,
        "final_report": final_report
    }


async def provide_career_advice(resume_info: dict) -> dict:
    """
    Feature 6: Generate general Career Coach recommendations.
    """
    prompt = build_career_coach_prompt(resume_info)
    return await call_groq(prompt)
