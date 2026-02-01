import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_lottie import st_lottie  # type: ignore
import requests
import time
import html
import json
from streamlit_mic_recorder import mic_recorder

from src.analyzer import MindReader
from src.utils import get_api_key

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

if "mind_reader" not in st.session_state:
    try:
        api_key = get_api_key()
        st.session_state["mind_reader"] = MindReader(api_key)
    except Exception as e:
        st.error(f"Failed to initialize Mind Reader: {e}")
        st.stop()


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
    background: radial-gradient(circle at 50% 10%, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    color: #e0e0e0;
    font-family: 'Outfit', sans-serif; 
}

#MainMenu, footer, header {visibility: hidden;}

h1, h2, h3, h4, p, div, span { color: #e0e0e0; }

/* Cyber Glass Card */
.glass-card {
    background: rgba(22, 33, 62, 0.7);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(0, 255, 209, 0.1);
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
    margin-bottom: 20px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    animation: fadeInUp 0.5s ease-out;
}

.glass-card:hover { 
    transform: translateY(-5px);
    box-shadow: 0 0 20px rgba(0, 255, 209, 0.2), inset 0 0 10px rgba(0, 255, 209, 0.05);
    border-color: rgba(0, 255, 209, 0.3);
}

/* Neon Text Gradient */
.score-num { 
    font-size: 2.5rem; 
    font-weight: 800; 
    background: linear-gradient(90deg, #00fff0, #bc00dd);
    -webkit-background-clip: text; 
    -webkit-text-fill-color: transparent;
    animation: pulse 2s ease-in-out infinite;
    display: inline-block;
    filter: drop-shadow(0 0 5px rgba(188, 0, 221, 0.5));
}

@keyframes pulse {
    0%, 100% { transform: scale(1); filter: drop-shadow(0 0 5px rgba(188, 0, 221, 0.5)); }
    50% { transform: scale(1.05); filter: drop-shadow(0 0 15px rgba(0, 255, 240, 0.6)); }
}

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(30px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes slideInLeft {
    from { opacity: 0; transform: translateX(-50px); }
    to { opacity: 1; transform: translateX(0); }
}

@keyframes slideInRight {
    from { opacity: 0; transform: translateX(50px); }
    to { opacity: 1; transform: translateX(0); }
}

/* Glow Effect */
@keyframes glow {
    0%, 100% { box-shadow: 0 0 10px rgba(188, 0, 221, 0.3); }
    50% { box-shadow: 0 0 25px rgba(0, 255, 240, 0.5); }
}

.glow-effect {
    animation: glow 3s ease-in-out infinite;
    border: 1px solid rgba(0, 255, 240, 0.2);
}

/* Tabs Animation */
.stTabs [data-baseweb="tab-list"] { gap: 10px; }
.stTabs [data-baseweb="tab"] { 
    background-color: rgba(15, 52, 96, 0.6); 
    border-radius: 10px; 
    color: #a0a0a0;
    padding: 10px 20px;
    border: 1px solid rgba(255,255,255,0.05);
    transition: all 0.3s ease;
}

.stTabs [data-baseweb="tab"]:hover {
    color: #e0e0e0;
    background-color: rgba(26, 26, 46, 0.8);
    border-color: #00fff0;
}

.stTabs [aria-selected="true"] { 
    background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
    border: 1px solid #bc00dd !important;
    color: #00fff0 !important;
    text-shadow: 0 0 10px rgba(0, 255, 240, 0.5);
    animation: slideInRight 0.3s ease-out;
}

/* File Uploader */
[data-testid='stFileUploader'] section {
    background-color: rgba(15, 52, 96, 0.4);
    border: 2px dashed #00fff0;
    border-radius: 15px;
    opacity: 0.8;
    transition: all 0.3s ease;
}

[data-testid='stFileUploader'] section:hover {
    border-color: #bc00dd;
    background-color: rgba(15, 52, 96, 0.6);
    box-shadow: 0 0 15px rgba(188, 0, 221, 0.2);
}

/* Button Animations */
.stButton > button {
    background: linear-gradient(90deg, #1a1a2e, #16213e);
    border: 1px solid #00fff0;
    color: #00fff0;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 20px rgba(0, 255, 240, 0.4);
    border-color: #bc00dd;
    color: #bc00dd;
}

/* Loading Spinner */
.stSpinner > div {
    border-color: #bc00dd !important;
    border-right-color: #00fff0 !important;
}

/* Hidden Meaning Card */
.hidden-meaning-card {
    background: rgba(255, 243, 205, 0.05) !important;
    border-left: 5px solid #ffc107;
    color: #ffeeba;
    animation: slideInLeft 0.6s ease-out;
}

/* Audio Recorder Styling */
.audio-recorder-container {
    background: rgba(22, 33, 62, 0.8);
    border: 1px solid #bc00dd;
    border-radius: 15px;
    padding: 15px;
    box-shadow: 0 0 15px rgba(188, 0, 221, 0.2);
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
        "<h1 style='margin-bottom:0; text-shadow: 0 0 10px rgba(0, 255, 240, 0.5);'>Mind Reader <span style='color:#bc00dd; text-shadow: 0 0 10px rgba(188, 0, 221, 0.8);'>AI</span></h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='margin-top:-10px; opacity:0.8; color: #00fff0; letter-spacing: 1px;'>Advanced Psychological & Micro-Expression Decoder</p>",
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
                    mr = st.session_state["mind_reader"]
                    res_text = mr.analyze_text(txt_input)
                    res_mood = mr.get_suggestions(txt_input)

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
                        err_msg = res_text.get("error") or res_mood.get("error") or "Unknown Error"
                        st.error(f"❌ Analysis Failed: {err_msg}")
                        st.error("Check your API Key in .env and internet connection.")

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
                    fillcolor="rgba(188, 0, 221, 0.2)",
                    line=dict(color="#00fff0", width=3),
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
                <div class='glass-card' style='border-left: 4px solid #bc00dd'>
                    <strong style='color:#bc00dd'>🎵 Recommended Music</strong><br>
                    {safe(m['music'])}
                </div>
                """,
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"""
                <div class='glass-card' style='border-left: 4px solid #00fff0'>
                    <strong style='color:#00fff0'>🍕 Comfort Food</strong><br>
                    {safe(m['food'])}
                </div>
                """,
                    unsafe_allow_html=True,
                )

            with c2:
                st.markdown(
                    f"""
                <div class='glass-card' style='border-left: 4px solid #ff0055'>
                    <strong style='color:#ff0055'>⚡ Activity (Do Now)</strong><br>
                    {safe(m['activity'])}
                </div>
                """,
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"""
                <div class='glass-card' style='background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); border: 1px solid #bc00dd;'>
                    <strong style='color:#bc00dd'>💬 Quote</strong><br>
                    <em style='color:#00fff0'>"{safe(m['quote'])}"</em>
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
                        mr = st.session_state["mind_reader"]
                        res = mr.analyze_image(uploaded_file.getvalue())
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

            st.markdown("**Click Start/Stop to record:**")
            
            try:
                # Using standard keys for bytes
                audio_info = mic_recorder(
                    start_prompt="🔴 Start Recording",
                    stop_prompt="⏹️ Stop Recording",
                    just_once=True,
                    use_container_width=True,
                    key="recorder"
                )
                
                if audio_info:
                    audio_bytes = audio_info['bytes']
                else:
                    audio_bytes = None
            except Exception as e:
                st.error(f"Microphone Error: {e}")
                st.warning("Ensure you have a microphone connected and allowed permission.")
                audio_bytes = None

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
                            mr = st.session_state["mind_reader"]
                            res = mr.analyze_audio(audio_bytes)
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
                            mr = st.session_state["mind_reader"]
                            res = mr.analyze_audio(audio_data)
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