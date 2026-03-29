from functools import lru_cache


@lru_cache(maxsize=1)
def _get_model():
    # Import and load only when a route actually needs embeddings (faster app startup).
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer("all-MiniLM-L6-v2")


def generate_embedding(text: str) -> list[float]:
    """
    Takes a string (like a skill name) and returns a list of 384 floats (vector representation).
    """
    try:
        embedding = _get_model().encode(text)
        return embedding.tolist()
    except Exception as e:
        print(f"Embedding Error: {e}")
        return []
