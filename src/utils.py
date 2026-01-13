import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# 1. SETUP
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

genai.configure(api_key=api_key)

# 2. HELPER FUNCTIONS (Tumhare logic wale)
AVOIDANCE_WORDS = ["maybe", "honestly", "to be frank", "sort of", "i think", "guess"]
DEFENSIVE_PATTERNS = ["why would i", "i already told", "trust me", "believe me"]

def clamp(v):
    try:
        return max(0, min(100, int(v)))
    except:
        return 0

def rule_based_flags(text):
    flags = []
    t = text.lower()
    for w in AVOIDANCE_WORDS:
        if w in t: flags.append(f"Avoidance word: {w}")
    for p in DEFENSIVE_PATTERNS:
        if p in t: flags.append(f"Defensive phrase: {p}")
    return flags

# 3. DYNAMIC MODEL FINDER (The Hero Function)
def get_model():
    """
    Ye function available models list karega aur best wala uthayega.
    Hardcoding nahi karenge taaki 404 error na aaye.
    """
    try:
        for m in genai.list_models():
            if "generateContent" in m.supported_generation_methods:
                # Flash ya Pro model sabse best hain text+image ke liye
                if "flash" in m.name or "pro" in m.name:
                    return m.name
        return "models/gemini-1.5-flash" # Fallback default
    except:
        return "models/gemini-1.5-flash"

# --- FUNCTION 1: TEXT ANALYSIS (Tumhara Original Logic) ---
def get_mind_reading(text):
    try:
        model_name = get_model()
        if not model_name:
            return {"error": "No Gemini model available"}

        model = genai.GenerativeModel(model_name)
        flags = rule_based_flags(text)

        prompt = f"""
        You are a forensic psychologist & deception analyst.
        Analyze this text: "{text}"

        Rules:
        - Penalize avoidance & defensiveness
        - All scores must be integers 0–100

        Return STRICT JSON only (No Markdown):
        {{
            "emotional_spectrum": {{ "joy": 0, "sadness": 0, "anger": 0, "fear": 0, "surprise": 0, "love": 0 }},
            "lie_detection": {{ "truthfulness_score": 0, "confidence_score": 0 }},
            "personality_profile": {{ "type": "Introvert/Extrovert/Ambivert", "summary": "One sentence insight" }},
            "hidden_meaning": "What do they ACTUALLY mean? (Be blunt)",
            "suggested_replies": ["Diplomatic", "Direct", "Professional"],
            "better_version": "Improved professional rewrite"
        }}
        """

        response = model.generate_content(prompt)
        # Clean JSON
        cleaned = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(cleaned)

        # Post Processing (Tumhara logic)
        for k in data["emotional_spectrum"]:
            data["emotional_spectrum"][k] = clamp(data["emotional_spectrum"][k])

        data["lie_detection"]["truthfulness_score"] = clamp(
            data["lie_detection"]["truthfulness_score"] - len(flags) * 5
        )
        data["lie_detection"]["confidence_score"] = clamp(data["lie_detection"]["confidence_score"])
        data["lie_detection"]["flags"] = flags

        return data

    except Exception as e:
        return {"error": str(e)}

# --- FUNCTION 2: IMAGE ANALYSIS (Updated to use Dynamic Model) ---
def analyze_face_image(image_bytes):
    try:
        # Hum wahi same model use karenge jo text ke liye chala (Kyunki Flash/Pro images bhi padh lete hain)
        model_name = get_model()
        model = genai.GenerativeModel(model_name)

        image_part = {
            "mime_type": "image/jpeg",
            "data": image_bytes
        }

        prompt = """
        You are an expert face reader and behavioral psychologist.
        Analyze the micro-expressions in this image.

        Return STRICT JSON only (No Markdown):
        {
            "primary_emotion": "Dominant emotion",
            "micro_expressions": "Describe eyes, lips, posture cues",
            "truthfulness_indicator": {
                "status": "Likely Truthful / Deceptive / Anxious",
                "score": 0-100,
                "reason": "Why?"
            },
            "mental_state_summary": "Psychological summary"
        }
        """

        response = model.generate_content([prompt, image_part])
        cleaned = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned)

    except Exception as e:
        return {"error": f"Visual Scan Failed: {str(e)}"}
# --- FUNCTION 3: AUDIO ANALYSIS (Voice Stress) ---
def analyze_audio_tone(audio_bytes):
    try:
        # Audio ke liye bhi Flash model best hai
        model_name = get_model()
        model = genai.GenerativeModel(model_name)

        prompt = """
        You are a Voice Stress Analyst and Behavioral Psychologist.
        Listen to this audio clip carefully. Analyze the tone, pitch, speed, and pauses.

        Return STRICT JSON only (No Markdown):
        {
            "emotional_tone": "e.g., Nervous, Aggressive, Calm, Deceptive",
            "speech_patterns": "Describe pauses, stuttering, speed (e.g., 'Rapid speech with frequent hesitation')",
            "truthfulness_indicator": {
                "status": "Likely Truthful / High Stress Detected / Deceptive",
                "score": 0-100,
                "reason": "Why? (Based on vocal cues)"
            },
            "transcript": "Transcribe what was said accurately"
        }
        """
        
        # Audio Data Format
        audio_part = {
            "mime_type": "audio/mp3", # Works for wav/mp3 usually
            "data": audio_bytes
        }

        # Call Model
        response = model.generate_content([prompt, audio_part])
        cleaned = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned)

    except Exception as e:
        return {"error": f"Audio Analysis Failed: {str(e)}"}        