import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_lottie import st_lottie  # type: ignore
import requests
import time
import html
import json
from audio_recorder_streamlit import audio_recorder

from src.utils import (
    get_mind_reading,
    analyze_face_image,
    analyze_audio_tone,
    get_mind_suggestions
)

# =========================================
# PAGE CONFIG
# =========================================
st.set_page_config(
    page_title="Mind Reader AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================
# CONSTANTS
# =========================================
MAX_FILE_MB = 5
API_COOLDOWN = 10  # seconds

# =========================================
# SESSION STATE
# =========================================
if "history" not in st.session_state:
    st.session_state["history"] = []

if "text_result" not in st.session_state:
    st.session_state["text_result"] = None

if "mood_result" not in st.session_state:
    st.session_state["mood_result"] = None

if "image_result" not in st.session_state:
    st.session_state["image_result"] = None

if "audio_result" not in st.session_state:
    st.session_state["audio_result"] = None

if "last_call" not in st.session_state:
    st.session_state["last_call"] = 0


# =========================================
# HELPERS
# =========================================
def can_call_api():
    return time.time() - st.session_state["last_call"] > API_COOLDOWN


def mark_api_call():
    st.session_state["last_call"] = time.time()


def load_lottieurl(url):
    try:
        r = requests.get(url, timeout=2)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None


def file_size_ok(uploaded_file):
    if uploaded_file.size > MAX_FILE_MB * 1024 * 1024:
        st.error(f"❌ File too large. Max allowed size is {MAX_FILE_MB} MB.")
        return False
    return True


def safe(text):
    return html.escape(str(text))


# =========================================
# ASSETS
# =========================================
lottie_brain = load_lottieurl(
    "https://lottie.host/6a56c3b8-9366-4f48-a006-218456f338d4/S8y8l9kS4w.json"
)

# =========================================
# CSS WITH ANIMATIONS
# =========================================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

.stApp { 
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); 
    font-family: 'Outfit', sans-serif; 
}

#MainMenu, footer, header {visibility: hidden;}

h1, h2, h3, h4, p, div, span { color: #2D3436 !important; }

/* Glass Card with Hover Animation */
.glass-card {
    background: rgba(255, 255, 255, 0.65);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.6);
    border-radius: 20px;
    padding: 20px;
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
    margin-bottom: 20px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    animation: fadeInUp 0.5s ease-out;
}

.glass-card:hover { 
    transform: translateY(-5px) scale(1.01);
    box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.2);
}

/* Animated Score Numbers */
.score-num { 
    font-size: 2.5rem; 
    font-weight: 800; 
    background: linear-gradient(45deg, #6C5CE7, #a55eea);
    -webkit-background-clip: text; 
    -webkit-text-fill-color: transparent;
    animation: pulse 2s ease-in-out infinite;
    display: inline-block;
}

@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.05); }
}

/* Fade In Up Animation */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Slide In from Left */
@keyframes slideInLeft {
    from {
        opacity: 0;
        transform: translateX(-50px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

/* Slide In from Right */
@keyframes slideInRight {
    from {
        opacity: 0;
        transform: translateX(50px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

/* Glow Effect */
@keyframes glow {
    0%, 100% { box-shadow: 0 0 5px rgba(108, 92, 231, 0.5); }
    50% { box-shadow: 0 0 20px rgba(108, 92, 231, 0.8); }
}

.glow-effect {
    animation: glow 2s ease-in-out infinite;
}

/* Tabs Animation */
.stTabs [data-baseweb="tab-list"] { gap: 10px; }
.stTabs [data-baseweb="tab"] { 
    background-color: rgba(255,255,255,0.7); 
    border-radius: 10px; 
    padding: 10px 20px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    transition: all 0.3s ease;
}

.stTabs [data-baseweb="tab"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(0,0,0,0.1);
}

.stTabs [aria-selected="true"] { 
    background-color: #6C5CE7 !important; 
    color: white !important;
    animation: slideInRight 0.3s ease-out;
}

/* File Uploader */
[data-testid='stFileUploader'] section {
    background-color: rgba(255, 255, 255, 0.5);
    border: 2px dashed #6C5CE7;
    border-radius: 15px;
    transition: all 0.3s ease;
}

[data-testid='stFileUploader'] section:hover {
    border-color: #a55eea;
    background-color: rgba(255, 255, 255, 0.7);
}

/* Button Animations */
.stButton > button {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 16px rgba(108, 92, 231, 0.3);
}

.stButton > button:active {
    transform: translateY(0);
}

/* Loading Spinner Enhancement */
.stSpinner > div {
    border-color: #6C5CE7 !important;
}

/* Animated Hidden Meaning Card */
.hidden-meaning-card {
    animation: slideInLeft 0.6s ease-out;
}

/* Audio Recorder Styling */
.audio-recorder-container {
    background: rgba(255, 255, 255, 0.8);
    border-radius: 15px;
    padding: 15px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    animation: fadeInUp 0.4s ease-out;
}
</style>
""",
    unsafe_allow_html=True
)

# =========================================
# HEADER
# =========================================
c1, c2 = st.columns([1, 8])
with c1:
    if lottie_brain:
        st_lottie(lottie_brain, height=80, key="head_anim")
    else:
        st.markdown("<h1>🧠</h1>", unsafe_allow_html=True)

with c2:
    st.markdown(
        "<h1 style='margin-bottom:0;'>Mind Reader <span style='color:#6C5CE7'>AI</span></h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='margin-top:-10px; opacity:0.7;'>Advanced Psychological & Micro-Expression Decoder</p>",
        unsafe_allow_html=True,
    )

# =========================================
# TABS
# =========================================
tab1, tab2, tab3 = st.tabs(
    ["📝 Text Analysis", "📸 Visual Scanner", "🎙️ Voice Stress"]
)

# =========================================
# TAB 1: TEXT
# =========================================
with tab1:
    col_in, col_out = st.columns([1, 1.5])

    with col_in:
        st.markdown("### Input Text")
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

        txt_input = st.text_area(
            "Text",
            height=300,
            label_visibility="collapsed",
            placeholder="Paste chat, email, or write how you feel...",
        )

        st.write("")
        if st.button("🚀 Analyze & Fix Mood", use_container_width=True):
            if not txt_input.strip():
                st.warning("Please enter some text first.")
            elif not can_call_api():
                st.warning("⏳ Please wait a few seconds before trying again.")
            else:
                mark_api_call()
                with st.spinner("🧠 Reading Mind & Generating Solutions..."):
                    res_text = get_mind_reading(txt_input)
                    res_mood = get_mind_suggestions(txt_input)

                    if "error" not in res_text and "error" not in res_mood:
                        st.session_state["text_result"] = res_text
                        st.session_state["mood_result"] = res_mood

                        # History tracking
                        st.session_state["history"].append(
                            {
                                "snippet": txt_input[:50],
                                "truth": res_text["lie_detection"][
                                    "truthfulness_score"
                                ],
                                "mood": res_mood["mood_analysis"],
                            }
                        )
                        st.rerun()
                    else:
                        st.error("AI Brain Freeze! Try again.")

        st.markdown("</div>", unsafe_allow_html=True)

    with col_out:
        if st.session_state["text_result"]:
            r = st.session_state["text_result"]

            hidden_meaning = safe(r.get("hidden_meaning", ""))

            st.markdown(
                f"""
            <div class='glass-card hidden-meaning-card' style='background:#fff3cd; border-left:5px solid #ffc107;'>
                <strong>🕵️ Hidden Meaning:</strong> {hidden_meaning}
            </div>
            """,
                unsafe_allow_html=True,
            )

            c_a, c_b = st.columns(2)
            with c_a:
                st.markdown(
                    f"""
                <div class='glass-card glow-effect' style='text-align:center;'>
                    Truth Score<br>
                    <span class='score-num'>{r['lie_detection']['truthfulness_score']}%</span>
                </div>
                """,
                    unsafe_allow_html=True,
                )

            with c_b:
                st.markdown(
                    f"""
                <div class='glass-card glow-effect' style='text-align:center;'>
                    Confidence<br>
                    <span class='score-num'>{r['lie_detection']['confidence_score']}%</span>
                </div>
                """,
                    unsafe_allow_html=True,
                )

            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

            emotions = r["emotional_spectrum"]
            categories = [*list(emotions.keys()), list(emotions.keys())[0]]
            values = [*list(emotions.values()), list(emotions.values())[0]]

            fig = go.Figure(
                go.Scatterpolar(
                    r=values,
                    theta=categories,
                    fill="toself",
                    fillcolor="rgba(108, 92, 231, 0.3)",
                    line=dict(color="#6C5CE7", width=3),
                )
            )
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, showticklabels=False),
                    bgcolor="rgba(0,0,0,0)",
                ),
                paper_bgcolor="rgba(0,0,0,0)",
                height=250,
                margin=dict(t=10, b=10),
            )
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("</div>", unsafe_allow_html=True)

        if st.session_state["mood_result"]:
            m = st.session_state["mood_result"]

            st.markdown("---")
            st.markdown(f"### 💊 AI Prescription (Detected: {safe(m['mood_analysis'])})")

            c1, c2 = st.columns(2)
            with c1:
                st.markdown(
                    f"""
                <div class='glass-card' style='border-left: 4px solid #6C5CE7'>
                    <strong>🎵 Recommended Music</strong><br>
                    {safe(m['music'])}
                </div>
                """,
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"""
                <div class='glass-card' style='border-left: 4px solid #e17055'>
                    <strong>🍕 Comfort Food</strong><br>
                    {safe(m['food'])}
                </div>
                """,
                    unsafe_allow_html=True,
                )

            with c2:
                st.markdown(
                    f"""
                <div class='glass-card' style='border-left: 4px solid #00b894'>
                    <strong>⚡ Activity (Do Now)</strong><br>
                    {safe(m['activity'])}
                </div>
                """,
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"""
                <div class='glass-card' style='background:#6C5CE7; color:white !important;'>
                    <strong>💬 Quote</strong><br>
                    "{safe(m['quote'])}"
                </div>
                """,
                    unsafe_allow_html=True,
                )

# =========================================
# TAB 2: IMAGE
# =========================================
with tab2:
    st.markdown("### 📸 Face & Micro-Expression Scanner")

    c_img, c_res = st.columns([1, 1.5])

    with c_img:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Upload Subject Image", type=["jpg", "jpeg", "png"]
        )

        if uploaded_file and file_size_ok(uploaded_file):
            st.image(uploaded_file, use_column_width=True)
            st.write("")

            if st.button("📸 Scan Face Now", use_container_width=True):
                if not can_call_api():
                    st.warning("⏳ Please wait before scanning again.")
                else:
                    mark_api_call()
                    with st.spinner("🧠 Analyzing facial muscles & cues..."):
                        res = analyze_face_image(uploaded_file.getvalue())
                        if "error" not in res:
                            st.session_state["image_result"] = res
                            st.rerun()
                        else:
                            st.error(res["error"])

        st.markdown("</div>", unsafe_allow_html=True)

    with c_res:
        if st.session_state["image_result"]:
            ir = st.session_state["image_result"]

            status = ir["truthfulness_indicator"]["status"]
            color = "#27ae60" if "Truth" in status else "#c0392b"

            st.markdown(
                f"""
            <div class='glass-card glow-effect' style='border-left: 5px solid {color};'>
                <h3 style='margin:0; color:{color} !important;'>{safe(status)}</h3>
                <p>Credibility Score: <strong>{ir['truthfulness_indicator']['score']}/100</strong></p>
                <p style='background:rgba(0,0,0,0.05); padding:10px; border-radius:8px; font-style:italic;'>
                    "{safe(ir['truthfulness_indicator']['reason'])}"
                </p>
            </div>

            <div class='glass-card'>
                <h4>👁️ Micro-Expression Analysis</h4>
                <p><strong>Dominant:</strong> {safe(ir['primary_emotion'])}</p>
                <hr style='opacity:0.2'>
                <p><strong>Cues Detected:</strong><br>{safe(ir['micro_expressions'])}</p>
                <hr style='opacity:0.2'>
                <p><strong>Psychological Summary:</strong><br>{safe(ir['mental_state_summary'])}</p>
            </div>
            """,
                unsafe_allow_html=True,
            )
        else:
            st.info("👈 Upload an image to start the visual scan.")

# =========================================
# TAB 3: AUDIO WITH VOICE RECORDING
# =========================================
with tab3:
    c_aud, c_aud_res = st.columns([1, 1.5])

    with c_aud:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        
        # Toggle between Upload and Record
        audio_mode = st.radio(
            "Choose Input Method:",
            ["🎙️ Record Voice", "📤 Upload Audio"],
            horizontal=True
        )
        
        st.markdown("---")
        
        audio_data = None
        
        if audio_mode == "🎙️ Record Voice":
            st.markdown("<div class='audio-recorder-container'>", unsafe_allow_html=True)
            st.markdown("**Press to record, release to stop:**")
            audio_bytes = audio_recorder(
                text="",
                recording_color="#6C5CE7",
                neutral_color="#d1d5db",
                icon_name="microphone",
                icon_size="2x",
            )
            st.markdown("</div>", unsafe_allow_html=True)
            
            if audio_bytes:
                st.audio(audio_bytes, format="audio/wav")
                audio_data = audio_bytes
                
                if st.button("🎙️ Analyze Recorded Voice", use_container_width=True):
                    if not can_call_api():
                        st.warning("⏳ Please wait before analyzing again.")
                    else:
                        mark_api_call()
                        with st.spinner("🎧 Listening to vocal patterns..."):
                            res = analyze_audio_tone(audio_bytes)
                            if "error" not in res:
                                st.session_state["audio_result"] = res
                                st.rerun()
                            else:
                                st.error(res["error"])
        
        else:  # Upload Mode
            audio_file = st.file_uploader("Upload Audio (MP3/WAV)", type=["mp3", "wav"])

            if audio_file and file_size_ok(audio_file):
                st.audio(audio_file)
                audio_data = audio_file.getvalue()

                if st.button("🎙️ Analyze Uploaded Audio", use_container_width=True):
                    if not can_call_api():
                        st.warning("⏳ Please wait before analyzing again.")
                    else:
                        mark_api_call()
                        with st.spinner("🎧 Listening to vocal patterns..."):
                            res = analyze_audio_tone(audio_data)
                            if "error" not in res:
                                st.session_state["audio_result"] = res
                                st.rerun()
                            else:
                                st.error(res["error"])

        st.markdown("</div>", unsafe_allow_html=True)

    with c_aud_res:
        if st.session_state["audio_result"]:
            ar = st.session_state["audio_result"]

            status = ar["truthfulness_indicator"]["status"]
            color = "#27ae60" if "Truth" in status else "#c0392b"

            st.markdown(
                f"""
            <div class='glass-card glow-effect' style='border-left: 5px solid {color};'>
                <h3 style='margin:0; color:{color} !important;'>{safe(status)}</h3>
                <p>Voice Integrity: <strong>{ar['truthfulness_indicator']['score']}/100</strong></p>
                <p><em>"{safe(ar['truthfulness_indicator']['reason'])}"</em></p>
            </div>

            <div class='glass-card'>
                <h4>🗣️ Tone Analysis</h4>
                <p><strong>Tone:</strong> {safe(ar['emotional_tone'])}</p>
                <p><strong>Patterns:</strong> {safe(ar['speech_patterns'])}</p>
                <hr>
                <p><strong>Transcript:</strong> <em>"{safe(ar['transcript'])}"</em></p>
            </div>
            """,
                unsafe_allow_html=True,
            )
        else:
            st.info("👈 Record or upload audio to start voice analysis.")
