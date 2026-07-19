import logging
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


def _validate_embedding(emb: list[float], name: str = "Embedding") -> None:
    """
    Validate that an embedding vector is a non-empty list containing only numerical values.

    Args:
        emb (list[float]): The embedding vector to validate.
        name (str): The name of the embedding field for clean error reporting.

    Raises:
        ValueError: If validation fails.
    """
    if not isinstance(emb, list):
        logger.error(f"{name} validation failed: input is not a list (got {type(emb).__name__}).")
        raise ValueError(f"{name} must be a list of floats.")

    if len(emb) == 0:
        logger.error(f"{name} validation failed: embedding is empty.")
        raise ValueError(f"{name} cannot be empty.")

    # Check that all elements are numeric
    for idx, val in enumerate(emb):
        if not isinstance(val, (int, float)) or isinstance(val, bool):
            logger.error(f"{name} validation failed: element at index {idx} is not numeric.")
            raise ValueError(f"All elements in {name} must be numbers (got {type(val).__name__} at index {idx}).")


def calculate_similarity(
    resume_embedding: list[float],
    job_embedding: list[float]
) -> float:
    """
    Calculate the cosine similarity between a resume embedding and a job embedding.

    Args:
        resume_embedding (list[float]): The resume embedding vector.
        job_embedding (list[float]): The job embedding vector.

    Returns:
        float: The cosine similarity score as a Python float.

    Raises:
        ValueError: If either embedding is empty, not a list, contains non-numeric values,
                    or if their dimensions do not match.
    """
    _validate_embedding(resume_embedding, "Resume embedding")
    _validate_embedding(job_embedding, "Job embedding")

    if len(resume_embedding) != len(job_embedding):
        logger.error(f"Embedding dimension mismatch: resume ({len(resume_embedding)}) vs job ({len(job_embedding)}).")
        raise ValueError(f"Embedding dimensions must match. Got {len(resume_embedding)} and {len(job_embedding)}.")

    # Convert lists to 2D numpy arrays as expected by scikit-learn's cosine_similarity
    u = np.array(resume_embedding).reshape(1, -1)
    v = np.array(job_embedding).reshape(1, -1)

    similarity = float(cosine_similarity(u, v)[0][0])
    return similarity


def rank_jobs(
    resume_embedding: list[float],
    jobs: list[dict]
) -> list[dict]:
    """
    Compare a resume embedding against multiple job embeddings using cosine similarity
    and return the jobs sorted in descending order of similarity.

    Args:
        resume_embedding (list[float]): The resume embedding vector.
        jobs (list[dict]): A list of job dictionaries, where each dict contains an "embedding" key.

    Returns:
        list[dict]: A new list of job dictionaries containing a new "similarity_score" key,
                    sorted in descending order by the score.

    Raises:
        ValueError: If validation fails (e.g. empty inputs, invalid dimensions, missing fields, mismatch).
    """
    _validate_embedding(resume_embedding, "Resume embedding")

    if not isinstance(jobs, list):
        logger.error("Input 'jobs' is not a list.")
        raise ValueError("Input 'jobs' must be a list of dictionaries.")

    if not jobs:
        logger.error("Input 'jobs' list is empty.")
        raise ValueError("Jobs list cannot be empty.")

    resume_dim = len(resume_embedding)
    ranked_jobs = []

    for idx, job in enumerate(jobs):
        if not isinstance(job, dict):
            logger.error(f"Job at index {idx} is not a dictionary.")
            raise ValueError(f"Job at index {idx} must be a dictionary.")

        if "embedding" not in job:
            logger.error(f"Job at index {idx} is missing the 'embedding' key.")
            raise ValueError(f"Job at index {idx} must contain the 'embedding' key.")

        job_emb = job["embedding"]
        _validate_embedding(job_emb, f"Job embedding at index {idx}")

        if len(job_emb) != resume_dim:
            logger.error(
                f"Job embedding dimension mismatch at index {idx}. Got {len(job_emb)}, expected {resume_dim}."
            )
            raise ValueError(
                f"Job embedding at index {idx} dimension ({len(job_emb)}) "
                f"does not match resume embedding dimension ({resume_dim})."
            )

        similarity_score = calculate_similarity(resume_embedding, job_emb)

        # Create a copy of the job dictionary to avoid mutating the original input
        ranked_job = dict(job)
        ranked_job["similarity_score"] = similarity_score
        ranked_jobs.append(ranked_job)

    # Sort descending by similarity_score
    ranked_jobs.sort(key=lambda x: x["similarity_score"], reverse=True)

    logger.info(f"Successfully ranked {len(ranked_jobs)} jobs.")
    return ranked_jobs
