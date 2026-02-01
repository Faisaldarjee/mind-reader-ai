import os
import json
import re
from typing import Dict, Any
from dotenv import load_dotenv

# =========================================
# ENV SETUP
# =========================================
load_dotenv()

def get_api_key():
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError("GEMINI_API_KEY not found in .env")
    return key.strip()

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
            # Return empty dict or raise error handled by caller
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
