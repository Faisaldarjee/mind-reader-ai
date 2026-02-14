# 🧠 Mind Reader AI

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**Advanced Psychological & Micro-Expression Decoder**

Mind Reader AI is a sophisticated forensic psychology and deception analysis tool that combines AI-powered analysis with behavioral science to decode emotions, detect deception, and provide mental health insights through text, image, and voice analysis.

---

## ✨ Features

### 📝 **Text Analysis**
- **Emotional Spectrum Detection**: Analyzes text for 6 core emotions (joy, sadness, anger, fear, surprise, love)
- **Lie Detection**: Truthfulness scoring with confidence metrics and deception flag detection
- **Personality Profiling**: Identifies personality types (Introvert/Extrovert/Ambivert) with behavioral insights
- **Hidden Meaning Extraction**: Reveals what the person ACTUALLY means beyond surface-level text
- **Smart Reply Suggestions**: Generates diplomatic, direct, and professional response options
- **Text Enhancement**: Provides improved professional rewrites
- **AI Mood Prescription**: Personalized recommendations including:
  - 🎵 Music suggestions based on detected mood
  - 🍕 Comfort food recommendations
  - ⚡ Immediate actionable activities
  - 💬 Motivational quotes

### 📸 **Visual Scanner (Micro-Expression Analysis)**
- **Facial Expression Recognition**: Detects primary emotions from uploaded images
- **Micro-Expression Detection**: Analyzes subtle cues in eyes, lips, and posture
- **Truthfulness Indicators**: Provides credibility scores with detailed reasoning
- **Mental State Analysis**: Comprehensive psychological summary based on visual cues

### 🎙️ **Voice Stress Analysis**
- **Dual Input Methods**: 
  - Live voice recording via microphone
  - Audio file upload (MP3/WAV)
- **Emotional Tone Detection**: Identifies tone (nervous, aggressive, calm, deceptive)
- **Speech Pattern Analysis**: Detects pauses, stuttering, speed variations
- **Voice Integrity Scoring**: Truthfulness assessment with stress detection
- **Audio Transcription**: Accurate conversion of speech to text

### 🧠 **Advanced Features**
- **Conversational Memory**: Tracks last 5 interactions for context-aware analysis
- **Crisis Detection**: Identifies urgent mental health concerns with helpline information
- **Rule-Based Flag System**: Detects common deception patterns and avoidance tactics
- **Multi-Style Responses**: Choose between calm, direct, or professional communication styles

---

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- Google Gemini API Key ([Get it here](https://makersuite.google.com/app/apikey))

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/MindReaderAI.git
   cd MindReaderAI
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API Key**
   
   Create a `.env` file in the project root:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

6. **Open in browser**
   
   The app will automatically open at `http://localhost:8501`

---

## 📖 Usage Guide

### Text Analysis
1. Navigate to the **"📝 Text Analysis"** tab
2. Enter text (chat messages, emails, self-reflection, etc.)
3. Click **"🚀 Analyze & Fix Mood"**
4. View results including:
   - Truth Score & Confidence metrics
   - Emotional spectrum radar chart
   - Hidden meaning interpretation
   - Mood-based AI prescription (music, food, activities, quotes)

### Visual Scanner
1. Go to the **"📸 Visual Scanner"** tab
2. Upload an image (JPG, JPEG, PNG) - max 5MB
3. Click **"📸 Scan Face Now"**
4. Review the analysis:
   - Credibility score
   - Dominant emotion
   - Micro-expression details
   - Psychological summary

### Voice Stress Analysis
1. Open the **"🎙️ Voice Stress"** tab
2. Choose your input method:
   - **Record Voice**: Click to start/stop recording
   - **Upload Audio**: Select an MP3/WAV file
3. Click **"🎙️ Analyze"**
4. Examine results:
   - Voice integrity score
   - Emotional tone
   - Speech patterns
   - Full transcript

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| **Streamlit** | Interactive web interface |
| **Google Gemini AI** | Core AI analysis engine |
| **Plotly** | Data visualization (emotion radar charts) |
| **Transformers** | NLP processing |
| **PyTorch** | Deep learning backend |
| **TextBlob** | Sentiment analysis support |
| **Deep Translator** | Multi-language support |
| **Streamlit Mic Recorder** | Live audio recording |
| **Python-dotenv** | Environment configuration |

---

## 📂 Project Structure

```
MindReaderAI/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── .env                    # API key configuration (create this)
├── .gitignore             # Git ignore rules
├── src/
│   ├── analyzer.py        # Core MindReader analysis engine
│   └── utils.py           # Utility functions
├── pages/
│   └── Voice_Scanner.py   # Additional voice analysis page
├── debug_test.py          # Testing utilities
└── verify_key.py          # API key validation script
```

---

## 🔑 API Key Setup

### Getting Your Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy the generated key
5. Add it to your `.env` file:
   ```env
   GEMINI_API_KEY=your_actual_key_here
   ```

### Verify Your API Key

Run the verification script:
```bash
python verify_key.py
```

---

## 🎨 UI Features

- **Modern Dark Theme**: Futuristic gradient background with glassmorphism effects
- **Neon Cyber Aesthetics**: Glowing elements and smooth animations
- **Responsive Design**: Optimized for desktop and tablet viewing
- **Interactive Visualizations**: Dynamic emotion radar charts with Plotly
- **Real-time Animations**: Smooth transitions and hover effects
- **Lottie Animations**: Animated brain icon in header

---

## ⚠️ Important Notes

### Rate Limiting
- API calls are rate-limited to prevent quota exhaustion (10-second cooldown between requests)

### File Size Limits
- Maximum file upload size: **5 MB** (images and audio)

### Crisis Support
If the system detects crisis-related language, it provides:
- **India AASRA Helpline**: +91-9820466726 (24/7)

### Privacy & Ethics
- No data is stored permanently
- Analysis is performed in real-time
- Session memory limited to last 5 interactions
- All data is cleared when the session ends

---

## 🐛 Troubleshooting

### "API Key Expired" Error
1. Check your `.env` file exists and contains the key
2. Verify the key is valid at [Google AI Studio](https://makersuite.google.com/app/apikey)
3. Ensure no extra spaces or quotes around the key

### Microphone Not Working
1. Grant microphone permissions in your browser
2. Ensure a microphone is connected
3. Try using the "Upload Audio" option instead

### Import Errors
```bash
pip install --upgrade -r requirements.txt
```

### "Model Not Found" Error
The app automatically selects the best available Gemini model. If issues persist:
- Check your internet connection
- Verify API key permissions

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👨‍💻 Author

**Faisal Darjee**

---

## 🙏 Acknowledgments

- Google Gemini AI for the powerful language model
- Streamlit for the amazing web framework
- All open-source contributors whose libraries made this possible

---

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact: [Faisaldarjee9@gmail.com]

---

<div align="center">

**Made with ❤️ and 🧠 by Farooq Darjee**

⭐ Star this repo if you find it useful!

</div>
