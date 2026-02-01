import streamlit as st
import pandas as pd
import requests
from src.utils import analyze_audio_tone
from streamlit_lottie import st_lottie

# --- PAGE CONFIG ---
st.set_page_config(page_title="Voice Scanner", page_icon="🎙️", layout="wide")

# --- ASSETS ---
def load_lottieurl(url):
    try:
        r = requests.get(url)
        return r.json()
    except: return None

# Sound Wave Animation
lottie_audio = load_lottieurl("https://lottie.host/9f6d4822-4418-4a5d-a006-218456f338d4/S8y8l9kS4w.json") # Placeholder link
# Note: Using same brain animation for now or find a waveform Lottie if you prefer

# --- CSS (Wahi Premium Theme) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); font-family: 'Outfit', sans-serif; }
    h1, h2, h3, p, div { color: #2D3436 !important; }
    .glass-card {
        background: rgba(255, 255, 255, 0.65);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.5);
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
        margin-bottom: 20px;
    }
    .score-num { font-size: 3rem; font-weight: 800; color: #6C5CE7; }
    
    /* Audio Player Style */
    .stAudio { width: 100%; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("# 🎙️ Voice Stress & Lie Detector")
st.markdown("<p style='opacity:0.7'>Analyze vocal patterns, pitch, and hesitation to detect deception.</p>", unsafe_allow_html=True)
st.markdown("---")

# --- MAIN LAYOUT ---
col1, col2 = st.columns([1, 1.5])

with col1:
    st.markdown("### 📤 Input Audio")
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    
    # 1. File Uploader
    audio_file = st.file_uploader("Upload Audio (MP3/WAV)", type=['mp3', 'wav'])
    
    # OR 2. Audio Input (New Streamlit Feature)
    # st.audio_input is available in newer streamlit versions
    # mic_input = st.audio_input("Or Record Voice") 
    
    final_audio = audio_file # Add mic_input logic if you update streamlit
    
    if final_audio:
        st.audio(final_audio, format="audio/mp3")
        st.write("")
        if st.button("🎙️ Analyze Voice Tone", use_container_width=True):
            with st.spinner("🎧 Listening to vocal cues..."):
                bytes_data = final_audio.getvalue()
                res = analyze_audio_tone(bytes_data)
                
                if "error" not in res:
                    st.session_state['audio_result'] = res
                else:
                    st.error(res['error'])
    else:
        st.info("Upload an audio recording of the subject talking.")
        
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    if 'audio_result' in st.session_state:
        r = st.session_state['audio_result']
        
        # Color Logic
        status = r['truthfulness_indicator']['status']
        color = "#27ae60" if "Truth" in status or "Calm" in status else "#c0392b"
        
        st.markdown(f"""
        <div class='glass-card' style='border-left: 5px solid {color};'>
            <h2 style='margin:0; color:{color} !important;'>{status}</h2>
            <p>Vocal Integrity Score: <strong>{r['truthfulness_indicator']['score']}/100</strong></p>
            <p><em>"{r['truthfulness_indicator']['reason']}"</em></p>
        </div>
        """, unsafe_allow_html=True)
        
        c_a, c_b = st.columns(2)
        with c_a:
            st.markdown(f"""
            <div class='glass-card'>
                <h4>🗣️ Tone Analysis</h4>
                <p>{r['emotional_tone']}</p>
            </div>
            """, unsafe_allow_html=True)
        with c_b:
            st.markdown(f"""
            <div class='glass-card'>
                <h4>📉 Patterns</h4>
                <p>{r['speech_patterns']}</p>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown(f"""
        <div class='glass-card'>
            <h4>📝 Transcript</h4>
            <p style='background:rgba(0,0,0,0.05); padding:10px; border-radius:10px; font-style:italic;'>
                "{r['transcript']}"
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    else:
        st.info("👈 Upload audio to detect voice stress.")