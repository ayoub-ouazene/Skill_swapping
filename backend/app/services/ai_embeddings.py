from sentence_transformers import SentenceTransformer

# We use all-MiniLM-L6-v2 because it is free, fast, and outputs exactly 384 dimensions 
# (which matches the Vector(384) column in our Neon database!)
model = SentenceTransformer('all-MiniLM-L6-v2')

def generate_embedding(text: str) -> list[float]:
    """
    Takes a string (like a skill name) and returns a list of 384 floats. ( vector representation)
    """
    try:
        # Encode the text into a vector
        embedding = model.encode(text)
        # Convert the numpy array to a standard Python list for SQLAlchemy
        return embedding.tolist()
    except Exception as e:
        print(f"Embedding Error: {e}")
        return []