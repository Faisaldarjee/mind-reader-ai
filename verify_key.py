import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

# Force reload of .env
load_dotenv(override=True)

def verify_key():
    print("Verifying New API Key...")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GENIMI_API_KEY still not found in environment.")
        return

    print(f"Key found: {api_key[:4]}...{api_key[-4:]}")
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        response = model.generate_content("Say hello")
        print("API Call Successful!")
        print(f"Response: {response.text.strip()}")
    except Exception as e:
        print(f"API Verification Failed: {e}")

if __name__ == "__main__":
    verify_key()
