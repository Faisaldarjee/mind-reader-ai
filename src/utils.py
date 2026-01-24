import os
import json
import re
import time
from collections import deque
from typing import Dict, Any

import google.generativeai as genai
from dotenv import load_dotenv

# =========================================
# ENV + API SETUP
# =========================================
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

genai.configure(api_key=api_key)

# =========================================
# CONSTANTS
# =========================================
AVOIDANCE_WORDS = ["maybe", "honestly", "to be frank", "sort of", "i think", "guess"]
DEFENSIVE_PATTERNS = ["why would i", "i already told", "trust me", "believe me"]

CRISIS_WORDS = [
    "kill myself",
    "end it all",
    "no reason to live",
    "suicide",
    "i want to die",
    "i don't want to live",
]

MAX_CONTEXT = 5
MODEL_FALLBACK = "models/gemini-1.5-flash"

# =========================================
# MEMORY (SHORT-TERM CONTEXT)
# =========================================
conversation_memory = deque(maxlen=MAX_CONTEXT)


def remember(user_text: str, mood: str = "Unknown"):
    conversation_memory.append(
        {
            "time": time.strftime("%H:%M:%S"),
            "text": user_text[:80],
            "mood": mood,
        }
    )


def get_context():
    return list(conversation_memory)


# =========================================
# MODEL CACHE
# =========================================
_MODEL_CACHE = None


def get_model_name():
    """
    Dynamically find best available Gemini model
    """
    try:
        for m in genai.list_models():
            if "generateContent" in m.supported_generation_methods:
                if "flash" in m.name.lower() or "pro" in m.name.lower():
                    return m.name
    except:
        pass
    return MODEL_FALLBACK


def get_model():
    global _MODEL_CACHE
    if _MODEL_CACHE is None:
        model_name = get_model_name()
        _MODEL_CACHE = genai.GenerativeModel(model_name)
    return _MODEL_CACHE


# =========================================
# UTILS
# =========================================
def clamp(v):
    try:
        return max(0, min(100, int(v)))
    except:
        return 0


def safe_json_load(text: str) -> Dict[str, Any]:
    """
    Fix broken Gemini JSON
    """
    try:
        return json.loads(text)
    except:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError("No JSON object found in response")
        return json.loads(match.group())


def rule_based_flags(text: str):
    flags = []
    t = text.lower()

    for w in AVOIDANCE_WORDS:
        if w in t:
            flags.append(f"Avoidance word: {w}")

    for p in DEFENSIVE_PATTERNS:
        if p in t:
            flags.append(f"Defensive phrase: {p}")

    return flags


def is_crisis(text: str) -> bool:
    t = text.lower()
    return any(w in t for w in CRISIS_WORDS)


def explain_score(score: int) -> str:
    if score >= 80:
        return "Very confident & emotionally stable"
    if score >= 60:
        return "Moderate confidence with mild emotional tension"
    if score >= 40:
        return "Emotionally uncertain or guarded"
    return "High emotional stress or defensiveness detected"


def therapist_style_prompt(style: str) -> str:
    styles = {
        "calm": "Speak gently, slowly, and reassuringly.",
        "friendly": "Be warm, casual, and supportive.",
        "professional": "Use structured, therapist-style clinical language.",
        "motivational": "Be energetic, inspiring, and confidence-boosting.",
    }
    return styles.get(style, styles["calm"])


# =========================================
# CORE CALLER
# =========================================
def call_gemini(prompt, parts=None):
    model = get_model()
    if parts:
        response = model.generate_content(parts)
    else:
        response = model.generate_content(prompt)

    cleaned = response.text.replace("```json", "").replace("```", "").strip()
    return safe_json_load(cleaned)


# =========================================
# FUNCTION 1: TEXT ANALYSIS
# =========================================
def get_mind_reading(text: str, style="calm"):
    try:
        flags = rule_based_flags(text)
        context = get_context()

        prompt = f"""
You are a forensic psychologist & deception analyst.

Conversation context:
{context}

Style:
{therapist_style_prompt(style)}

Rules:
- Penalize avoidance & defensiveness
- All scores must be integers 0–100
- Return valid JSON only. No markdown. No extra text.

Analyze this text:
"{text}"

Return JSON:
{{
    "emotional_spectrum": {{
        "joy": 0,
        "sadness": 0,
        "anger": 0,
        "fear": 0,
        "surprise": 0,
        "love": 0
    }},
    "lie_detection": {{
        "truthfulness_score": 0,
        "confidence_score": 0
    }},
    "personality_profile": {{
        "type": "Introvert/Extrovert/Ambivert",
        "summary": "One sentence insight"
    }},
    "hidden_meaning": "What do they ACTUALLY mean? (Be direct, not rude)",
    "suggested_replies": ["Diplomatic", "Direct", "Professional"],
    "better_version": "Improved professional rewrite"
}}
"""

        data = call_gemini(prompt)

        # Clamp emotions
        for k in data["emotional_spectrum"]:
            data["emotional_spectrum"][k] = clamp(
                data["emotional_spectrum"][k]
            )

        # Penalize for flags
        data["lie_detection"]["truthfulness_score"] = clamp(
            data["lie_detection"]["truthfulness_score"]
            - len(flags) * 5
        )

        data["lie_detection"]["confidence_score"] = clamp(
            data["lie_detection"]["confidence_score"]
        )

        data["lie_detection"]["flags"] = flags
        data["lie_detection"]["confidence_label"] = explain_score(
            data["lie_detection"]["confidence_score"]
        )

        remember(text, mood=data["personality_profile"]["type"])

        return data

    except Exception as e:
        return {"error": str(e)}


# =========================================
# FUNCTION 2: FACE ANALYSIS
# =========================================
def analyze_face_image(image_bytes: bytes):
    try:
        image_part = {
            "mime_type": "image/jpeg",
            "data": image_bytes,
        }

        prompt = """
You are an expert behavioral psychologist and facial expression analyst.

Rules:
- Return valid JSON only
- No markdown, no explanations

Analyze the micro-expressions in this image.

Return JSON:
{
    "primary_emotion": "Dominant emotion",
    "micro_expressions": "Describe eyes, lips, posture cues",
    "truthfulness_indicator": {
        "status": "Likely Truthful / Deceptive / Anxious",
        "score": 0,
        "reason": "Why?"
    },
    "mental_state_summary": "Psychological summary"
}
"""

        return call_gemini(prompt, [prompt, image_part])

    except Exception as e:
        return {"error": f"Visual Scan Failed: {str(e)}"}


# =========================================
# FUNCTION 3: AUDIO ANALYSIS
# =========================================
def analyze_audio_tone(audio_bytes: bytes):
    try:
        # Detect format (WAV for recorded, MP3 for uploaded)
        mime_type = "audio/wav"  # Default for recorder
        
        audio_part = {
            "mime_type": mime_type,
            "data": audio_bytes,
        }
        # ... rest same

        prompt = """
You are a voice stress analyst and behavioral psychologist.

Rules:
- Return valid JSON only
- No markdown, no extra text

Analyze tone, pitch, speed, and pauses.

Return JSON:
{
    "emotional_tone": "e.g., Nervous, Aggressive, Calm, Deceptive",
    "speech_patterns": "Describe pauses, stuttering, speed",
    "truthfulness_indicator": {
        "status": "Likely Truthful / High Stress Detected / Deceptive",
        "score": 0,
        "reason": "Why?"
    },
    "transcript": "Accurate transcription"
}
"""

        return call_gemini(prompt, [prompt, audio_part])

    except Exception as e:
        return {"error": f"Audio Analysis Failed: {str(e)}"}


# =========================================
# FUNCTION 4: MIND ALCHEMIST (THERAPY MODE)
# =========================================
def get_mind_suggestions(text_input: str, style="calm"):
    try:
        # CRISIS OVERRIDE
        if is_crisis(text_input):
            return {
                "mood_analysis": "Crisis",
                "music": "—",
                "activity": "Please reach out to someone you trust right now.",
                "food": "—",
                "quote": "You matter more than you know.",
                "support": "If you're in India: AASRA 24/7 Helpline: +91-9820466726",
            }

        context = get_context()

        prompt = f"""
You are a psychological therapist & AI companion.

Conversation context:
{context}

Style:
{therapist_style_prompt(style)}

Rules:
- Return valid JSON only
- No markdown, no explanations

User said:
"{text_input}"

Return JSON:
{{
    "mood_analysis": "One-word mood",
    "music": "Song Name - Artist (matches mood)",
    "activity": "A 2-minute action they can do now",
    "food": "Comfort food recommendation",
    "quote": "Short powerful motivation"
}}
"""

        data = call_gemini(prompt)
        remember(text_input, mood=data.get("mood_analysis", "Unknown"))

        return data

    except Exception as e:
        return {"error": str(e)}

