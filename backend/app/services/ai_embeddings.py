from sentence_transformers import SentenceTransformer

# 1. Start with the model as None so your FastAPI server boots instantly!
model = None 

def generate_embedding(text: str) -> list[float]:
    """
    Takes a string (like a skill name) and returns a list of 384 floats (vector representation).
    """
    global model  # Tell Python we want to use the global 'model' variable
    
    try:
        # 2. Lazy Load: Only load the model the VERY first time this function is called.
        if model is None:
            print("Loading HuggingFace model into memory... (this may take 5-10 seconds)")
            model = SentenceTransformer("all-MiniLM-L6-v2")
            print("Model loaded successfully!")
            
        embedding = model.encode(text)
        return embedding.tolist()
        
    except Exception as e:
        print(f"Embedding Error: {e}")
        return []