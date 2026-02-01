import os
import sys
from dotenv import load_dotenv

# Ensure we can import from src
sys.path.append(os.getcwd())

from src.analyzer import MindReader
from src.utils import get_api_key

def test_mind_reader():
    print("Testing MindReader Class...")
    try:
        load_dotenv()
        api_key = get_api_key()
        print("API Key loaded.")
        
        mr = MindReader(api_key)
        print("MindReader initialized.")
        
        text = "I am feeling a bit anxious about the future."
        print(f"Analyzing text: '{text}'")
        
        res = mr.analyze_text(text)
        print("Analysis Result:")
        print(res)
        
        if "error" in res:
            print("ERROR IN ANALYSIS")
        else:
            print("Analysis Successful")
            
    except Exception as e:
        print(f"CRITICAL EXCEPTION: {e}")

if __name__ == "__main__":
    test_mind_reader()
