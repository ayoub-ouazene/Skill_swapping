import os
import json
import base64
from groq import Groq
from dotenv import load_dotenv

# Load the API key from your .env file
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

# Initialize the Groq Client
client = Groq(api_key=api_key)

# Function to encode the image to base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_external_certificate(image_file_path: str) -> dict:
    """
    Takes a path to an uploaded image file, sends it to Groq Vision, 
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
        # 1. Convert the image to a base64 string
        base64_image = encode_image(image_file_path)
        
        # 2. Generate the response using Llama 3.2 Vision Preview
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                # Note: Assuming jpeg/png. Base64 handles the raw bytes nicely.
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            temperature=0, # Set to 0 to make the JSON output as consistent as possible
        )
        
        # 3. Clean up the response and convert it from a string to a Python dictionary
        raw_json_string = response.choices[0].message.content.strip()
        
        # Remove markdown if the AI accidentally adds it
        if raw_json_string.startswith("```json"):
            raw_json_string = raw_json_string[7:-3]
        elif raw_json_string.startswith("```"):
            raw_json_string = raw_json_string[3:-3]
            
        extracted_data = json.loads(raw_json_string)
        
        return extracted_data
        
    except Exception as e:
        print(f"AI Vision Error (Groq): {e}")
        # Fail gracefully
        return {"status": "INVALID", "student_name": None, "skill_name": None}