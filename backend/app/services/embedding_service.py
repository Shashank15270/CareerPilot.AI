import logging

logger = logging.getLogger(__name__)

# Private variable to store the single instance of the SentenceTransformer model
_model = None


def _get_model():
    """
    Retrieves the initialized SentenceTransformer model.
    Loads it lazily on the first request to ensure it is loaded only once (singleton).

    Returns:
        SentenceTransformer: The loaded model instance.
    """
    global _model
    if _model is None:
        logger.info("Initializing and loading SentenceTransformer model: sentence-transformers/all-MiniLM-L6-v2")
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        logger.info("SentenceTransformer model successfully loaded.")
    return _model


def generate_embedding(text: str) -> list[float]:
    """
    Generates a semantic vector embedding for a single text string.

    Args:
        text (str): The input text to embed.

    Returns:
        list[float]: The generated semantic vector embedding as a Python list.

    Raises:
        ValueError: If the input text is empty or not a string.
    """
    if not isinstance(text, str):
        logger.error("Input 'text' is not a string.")
        raise ValueError("Input 'text' must be a string.")

    if not text:
        logger.error("Input 'text' is empty.")
        raise ValueError("Input 'text' cannot be empty.")

    model = _get_model()
    embedding = model.encode(text)
    return embedding.tolist()


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Generates semantic vector embeddings for a list of text strings.

    Args:
        texts (list[str]): The list of input texts to embed.

    Returns:
        list[list[float]]: The list of generated semantic vector embeddings as Python lists.

    Raises:
        ValueError: If the input list is empty, not a list, or contains empty strings.
    """
    if not isinstance(texts, list):
        logger.error("Input 'texts' is not a list.")
        raise ValueError("Input 'texts' must be a list of strings.")

    if not texts:
        logger.error("Input 'texts' list is empty.")
        raise ValueError("Input list 'texts' cannot be empty.")

    for i, t in enumerate(texts):
        if not isinstance(t, str):
            logger.error(f"Element at index {i} in 'texts' is not a string.")
            raise ValueError(f"All elements in 'texts' must be strings (index {i} is not a string).")
        if not t:
            logger.error(f"Element at index {i} in 'texts' is empty.")
            raise ValueError(f"Elements in 'texts' cannot be empty strings (index {i} is empty).")

    model = _get_model()
    embeddings = model.encode(texts)
    return embeddings.tolist()
