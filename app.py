import streamlit as st
import pandas as pd
import plotly.graph_objects as go  # Graph 
from streamlit_lottie import st_lottie # type: ignore
import requests
from src.utils import get_mind_reading, analyze_face_image, analyze_audio_tone

# --- 1. PAGE SETUP ---
st.set_page_config(
    page_title="Mind Reader AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. ASSETS ---
def load_lottieurl(url):
    try:
        r = requests.get(url, timeout=2)
        if r.status_code != 200: return None
        return r.json()
    except: return None

lottie_brain = load_lottieurl("https://lottie.host/6a56c3b8-9366-4f48-a006-218456f338d4/S8y8l9kS4w.json")

# --- 3. CSS: PREMIUM LIGHT GLASS THEME ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    
    /* Main Background */
    .stApp { 
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); 
        font-family: 'Outfit', sans-serif; 
    }
    
    /* Hide Streamlit Header */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Text Colors */
    h1, h2, h3, h4, p, div, span { color: #2D3436 !important; }
    
    /* GLASS CARDS */
    .glass-card {
        background: rgba(255, 255, 255, 0.65);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.6);
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
        margin-bottom: 20px;
        transition: transform 0.2s;
    }
    .glass-card:hover { transform: translateY(-3px); }

    /* DECODER BOX (The Real Meaning) */
    .decoder-box {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 15px;
        border-radius: 10px;
        font-weight: 600;
        color: #856404 !important;
        margin-top: 10px;
    }

    /* SCORE NUMBERS */
    .score-num { 
        font-size: 2.5rem; 
        font-weight: 800; 
        background: linear-gradient(45deg, #6C5CE7, #a55eea);
        -webkit-background-clip: text; 
        -webkit-text-fill-color: transparent; 
    }

    /* TABS STYLING */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: rgba(255,255,255,0.7); 
        border-radius: 10px; 
        padding: 10px 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .stTabs [aria-selected="true"] { 
        background-color: #6C5CE7 !important; 
        color: white !important; 
    }
    
    /* UPLOADER */
    [data-testid='stFileUploader'] section {
        background-color: rgba(255, 255, 255, 0.5);
        border: 2px dashed #6C5CE7;
        border-radius: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. SESSION STATE ---
if 'history' not in st.session_state: st.session_state['history'] = []
if 'text_result' not in st.session_state: st.session_state['text_result'] = None
if 'image_result' not in st.session_state: st.session_state['image_result'] = None
if 'audio_result' not in st.session_state: st.session_state['audio_result'] = None
# --- 5. HEADER ---
c1, c2 = st.columns([1, 8])
with c1:
    if lottie_brain: st_lottie(lottie_brain, height=80, key="head_anim")
    else: st.markdown("<h1>🧠</h1>", unsafe_allow_html=True)
with c2:
    st.markdown("<h1 style='margin-bottom:0;'>Mind Reader <span style='color:#6C5CE7'>AI</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='margin-top:-10px; opacity:0.7;'>Advanced Psychological & Micro-Expression Decoder</p>", unsafe_allow_html=True)

# --- 6. MAIN TABS ---
tab1, tab2, tab3 = st.tabs(["📝 Text Analysis", "📸 Visual Scanner", "🎙️ Voice Stress"])

# =========================================
# TAB 1: TEXT ANALYSIS
# =========================================
with tab1:
    col_in, col_out = st.columns([1, 1.5])
    
    # Input Column
    with col_in:
        st.markdown("### Input Stream")
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        txt_input = st.text_area("Analysis Text", height=300, placeholder="Paste email, chat, or statement...", label_visibility="collapsed")
        
        st.write("")
        if st.button("🚀 Analyze Subtext", use_container_width=True):
            if txt_input:
                with st.spinner("🧠 Decoding hidden meaning..."):
                    res = get_mind_reading(txt_input)
                    if "error" not in res:
                        st.session_state['text_result'] = res
                        # History Log
                        if not st.session_state['history'] or st.session_state['history'][-1] != txt_input:
                            st.session_state['history'].append(txt_input)
                    else:
                        st.error(res['error'])
            else:
                st.warning("⚠️ Input cannot be empty.")
        st.markdown("</div>", unsafe_allow_html=True)

    # Output Column
    with col_out:
        if st.session_state['text_result']:
            r = st.session_state['text_result']
            
            # 1. Decoder Box (Hidden Meaning)
            st.markdown(f"""
            <div class='glass-card'>
                <h4 style='margin:0; color:#d35400 !important;'>🕵️ The Decoder</h4>
                <div class='decoder-box'>
                    "{r.get('hidden_meaning', 'No subtext detected.')}"
                </div>
                <div style='font-size:12px; margin-top:5px; color:#636e72;'>AI analysis of subconscious intent.</div>
            </div>
            """, unsafe_allow_html=True)
            
            # 2. Score Cards
            c_a, c_b = st.columns(2)
            with c_a:
                st.markdown(f"<div class='glass-card' style='text-align:center;'><div style='font-size:12px; letter-spacing:1px;'>TRUTH SCORE</div><div class='score-num'>{r['lie_detection']['truthfulness_score']}%</div></div>", unsafe_allow_html=True)
            with c_b:
                st.markdown(f"<div class='glass-card' style='text-align:center;'><div style='font-size:12px; letter-spacing:1px;'>CONFIDENCE</div><div class='score-num'>{r['lie_detection']['confidence_score']}%</div></div>", unsafe_allow_html=True)
            
            # 3. Graph & Profile
            c_graph, c_prof = st.columns([1.2, 1])
            
            with c_graph:
                st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                st.caption("🌊 EMOTIONAL RADAR")
                
                # --- NEW PROFESSIONAL GRAPH CODE ---
                emotions = r['emotional_spectrum']
                categories = list(emotions.keys())
                values = list(emotions.values())
                
                # Close the loop
                categories = [*categories, categories[0]]
                values = [*values, values[0]]

                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=values,
                    theta=categories,
                    fill='toself',
                    fillcolor='rgba(108, 92, 231, 0.3)', # Nice Purple Fill
                    line=dict(color='#6C5CE7', width=2),
                    marker=dict(size=6, color='#6C5CE7'),
                    name='Emotion'
                ))
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0, 100], showticklabels=False, linecolor='rgba(0,0,0,0.1)'),
                        angularaxis=dict(tickfont=dict(size=10, color='#2D3436'), gridcolor='rgba(0,0,0,0.1)'),
                        bgcolor='rgba(0,0,0,0)'
                    ),
                    paper_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=30, r=30, t=10, b=10),
                    height=220,
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with c_prof:
                st.markdown(f"""
                <div class='glass-card' style='height: 300px;'>
                    <h4>👤 Profile</h4>
                    <span style='background:#f1f2f6; color:#6C5CE7; padding:4px 10px; border-radius:10px; font-weight:bold; font-size:12px;'>{r['personality_profile']['type']}</span>
                    <hr>
                    <p style='font-style:italic; font-size:14px; opacity:0.8;'>"{r['personality_profile']['summary']}"</p>
                    <div style='margin-top:15px; background:#f8f9fa; padding:10px; border-radius:8px; border-left:3px solid #6C5CE7; font-size:12px;'>
                        <strong>Tip:</strong> {r.get('suggested_replies', ['Be honest'])[0]}
                    </div>
                </div>
                """, unsafe_allow_html=True)

# =========================================
# TAB 2: VISUAL SCANNER
# =========================================
with tab2:
    st.markdown("### 📸 Face & Micro-Expression Scanner")
    c_img, c_res = st.columns([1, 1.5])
    
    with c_img:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload Subject Image", type=['jpg', 'jpeg', 'png'])
        if uploaded_file:
            st.image(uploaded_file, use_column_width=True, caption="Target Subject")
            st.write("")
            if st.button("📸 Scan Face Now", use_container_width=True):
                with st.spinner("🧠 Analyzing facial muscles & cues..."):
                    bytes_data = uploaded_file.getvalue()
                    res = analyze_face_image(bytes_data)
                    if "error" not in res:
                        st.session_state['image_result'] = res
                    else:
                        st.error(res['error'])
        st.markdown("</div>", unsafe_allow_html=True)
        
    with c_res:
        if st.session_state['image_result']:
            ir = st.session_state['image_result']
            
            # Dynamic Color for Status
            status = ir['truthfulness_indicator']['status']
            color = "#27ae60" if "Truth" in status else "#c0392b"
            
            st.markdown(f"""
            <div class='glass-card' style='border-left: 5px solid {color};'>
                <h3 style='margin:0; color:{color} !important;'>{status}</h3>
                <p>Credibility Score: <strong>{ir['truthfulness_indicator']['score']}/100</strong></p>
                <p style='background:rgba(0,0,0,0.05); padding:10px; border-radius:8px; font-style:italic;'>
                    "{ir['truthfulness_indicator']['reason']}"
                </p>
            </div>
            
            <div class='glass-card'>
                <h4>👁️ Micro-Expression Analysis</h4>
                <div style='display:flex; justify-content:space-between;'>
                    <div><strong>Dominant:</strong> {ir['primary_emotion']}</div>
                </div>
                <hr style='opacity:0.2'>
                <p><strong>Cues Detected:</strong><br>{ir['micro_expressions']}</p>
                <hr style='opacity:0.2'>
                <p><strong>Psychological Summary:</strong><br>{ir['mental_state_summary']}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            if not uploaded_file:
                st.info("👈 Upload an image to start the visual scan.")

# ================= TAB 3: VOICE (NEW) =================
with tab3:
    c_aud, c_aud_res = st.columns([1, 1.5])
    with c_aud:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### 📤 Upload Voice")
        audio_file = st.file_uploader("Upload Audio (MP3/WAV)", type=['mp3', 'wav'])
        
        if audio_file:
            st.audio(audio_file)
            st.write("")
            if st.button("🎙️ Analyze Voice Stress"):
                with st.spinner("🎧 Listening to vocal patterns..."):
                    res = analyze_audio_tone(audio_file.getvalue())
                    if "error" not in res: st.session_state['audio_result'] = res
                    else: st.error(res['error'])
        st.markdown("</div>", unsafe_allow_html=True)
        
    with c_aud_res:
        if st.session_state['audio_result']:
            ar = st.session_state['audio_result']
            color = "#27ae60" if "Truth" in ar['truthfulness_indicator']['status'] else "#c0392b"
            
            st.markdown(f"""
            <div class='glass-card' style='border-left: 5px solid {color};'>
                <h3 style='margin:0; color:{color} !important;'>{ar['truthfulness_indicator']['status']}</h3>
                <p>Voice Integrity: <strong>{ar['truthfulness_indicator']['score']}/100</strong></p>
                <p><em>"{ar['truthfulness_indicator']['reason']}"</em></p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class='glass-card'>
                <h4>🗣️ Tone Analysis</h4>
                <p><strong>Tone:</strong> {ar['emotional_tone']}</p>
                <p><strong>Patterns:</strong> {ar['speech_patterns']}</p>
                <hr>
                <p><strong>Transcript:</strong> <em>"{ar['transcript']}"</em></p>
            </div>
            """, unsafe_allow_html=True)                
