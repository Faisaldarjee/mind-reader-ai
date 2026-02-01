import google.generativeai as genai
import time
from collections import deque
from typing import Dict, Any, List
from .utils import safe_json_load, clamp, rule_based_flags, is_crisis, explain_score, therapist_style_prompt

class MindReader:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API Key is required")
        genai.configure(api_key=api_key)
        self.model = self._get_model()
        self.memory = deque(maxlen=5)

    def _get_model_name(self):
        try:
            for m in genai.list_models():
                if "generateContent" in m.supported_generation_methods:
                    if "flash" in m.name.lower() or "pro" in m.name.lower():
                        return m.name
        except:
            pass
        return "models/gemini-1.5-flash"

    def _get_model(self):
        return genai.GenerativeModel(self._get_model_name())

    def remember(self, user_text: str, mood: str = "Unknown"):
        self.memory.append({
            "time": time.strftime("%H:%M:%S"),
            "text": user_text[:80],
            "mood": mood
        })

    def get_context(self) -> List[Dict]:
        return list(self.memory)

    def _call_gemini(self, prompt, parts=None):
        try:
            if parts:
                response = self.model.generate_content(parts)
            else:
                response = self.model.generate_content(prompt)
            
            cleaned = response.text.replace("```json", "").replace("```", "").strip()
            return safe_json_load(cleaned)
        except Exception as e:
            return {"error": str(e)}

    def analyze_text(self, text: str, style="calm"):
        try:
            flags = rule_based_flags(text)
            context = self.get_context()

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
            data = self._call_gemini(prompt)

            if "error" in data:
                return data

            # Post-processing
            for k in data["emotional_spectrum"]:
                data["emotional_spectrum"][k] = clamp(data["emotional_spectrum"][k])

            data["lie_detection"]["truthfulness_score"] = clamp(
                data["lie_detection"]["truthfulness_score"] - len(flags) * 5
            )
            data["lie_detection"]["confidence_score"] = clamp(
                data["lie_detection"]["confidence_score"]
            )
            data["lie_detection"]["flags"] = flags
            data["lie_detection"]["confidence_label"] = explain_score(
                data["lie_detection"]["confidence_score"]
            )

            self.remember(text, mood=data["personality_profile"]["type"])
            return data

        except Exception as e:
            return {"error": str(e)}

    def analyze_image(self, image_bytes: bytes):
        try:
            image_part = {"mime_type": "image/jpeg", "data": image_bytes}
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
            return self._call_gemini(prompt, [prompt, image_part])
        except Exception as e:
            return {"error": f"Visual Scan Failed: {str(e)}"}

    def analyze_audio(self, audio_bytes: bytes):
        try:
            audio_part = {"mime_type": "audio/wav", "data": audio_bytes}
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
            return self._call_gemini(prompt, [prompt, audio_part])
        except Exception as e:
            return {"error": f"Audio Analysis Failed: {str(e)}"}

    def get_suggestions(self, text: str, style="calm"):
        if is_crisis(text):
            return {
                "mood_analysis": "Crisis",
                "music": "—",
                "activity": "Please reach out to someone you trust right now.",
                "food": "—",
                "quote": "You matter more than you know.",
                "support": "If you're in India: AASRA 24/7 Helpline: +91-9820466726",
            }

        context = self.get_context()
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
"{text}"

Return JSON:
{{
    "mood_analysis": "One-word mood",
    "music": "Song Name - Artist (matches mood)",
    "activity": "A 2-minute action they can do now",
    "food": "Comfort food recommendation",
    "quote": "Short powerful motivation"
}}
"""
        data = self._call_gemini(prompt)
        # Avoid double remembering if called after analyze_text, but safe to update mood
        # self.remember(text, mood=data.get("mood_analysis", "Unknown"))
        return data
