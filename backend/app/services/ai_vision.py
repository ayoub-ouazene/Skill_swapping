import os
import json
from google import genai
from dotenv import load_dotenv

# Load the API key from your .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Initialize the new standard Gemini Client
client = genai.Client(api_key=api_key)

def analyze_external_certificate(image_file_path: str) -> dict:
    """
    Takes a path to an uploaded image file, sends it to Gemini, 
    and returns a structured dictionary with the extracted data.
    """
    
    prompt = """
    You are an expert document analyzer for a Skill-Swapping platform.
    Analyze this certificate or diploma. 
    Extract the following information and return it strictly as a JSON object.
    Do not use markdown formatting like ```json. Just return the raw JSON.
    
    Required JSON structure:
    {
        "status": "VALID" (if it looks like a real educational certificate) or "INVALID" (if it's blurry, fake, or not a certificate),
        "student_name": "The full name of the person receiving the certificate",
        "skill_name": "The main topic or skill taught in this certificate (e.g., Python, Graphic Design, NLP)"
    }
    """

    try:
        # 1. Upload the file to Gemini's temporary storage securely (New Syntax)
        sample_file = client.files.upload(file=image_file_path)
        
        # 2. Generate the response (New Syntax)
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=[sample_file, prompt]
        )
        
        # 3. Clean up the response and convert it from a string to a Python dictionary
        raw_json_string = response.text.strip()
        
        # Remove markdown if the AI accidentally adds it
        if raw_json_string.startswith("```json"):
            raw_json_string = raw_json_string[7:-3]
        elif raw_json_string.startswith("```"):
            raw_json_string = raw_json_string[3:-3]
            
        extracted_data = json.loads(raw_json_string)
        
        # 4. Delete the file from Google's servers after we are done
        client.files.delete(name=sample_file.name)
        
        return extracted_data
        
    except Exception as e:
        print(f"AI Vision Error: {e}")
        # Fail gracefully
        return {"status": "INVALID", "student_name": None, "skill_name": None}