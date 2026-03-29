# Import sentence_transformers only inside generate_embedding so importing this module
# does not load PyTorch (seconds–minutes). Required for PaaS port checks (e.g. Render).
model = None


def generate_embedding(text: str) -> list[float]:
    """
    Takes a string (like a skill name) and returns a list of 384 floats (vector representation).
    """
    global model

    try:
        if model is None:
            from sentence_transformers import SentenceTransformer

            print("Loading HuggingFace model into memory... (this may take 5-10 seconds)")
            model = SentenceTransformer("all-MiniLM-L6-v2")
            print("Model loaded successfully!")
            
        embedding = model.encode(text)
        return embedding.tolist()
        
    except Exception as e:
        print(f"Embedding Error: {e}")
        return []