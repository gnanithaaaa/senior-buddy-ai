# 🎓 Senior Buddy — AI-Powered College Career & Academic Assistant

**Senior Buddy** is a sleek, context-aware AI web application built for college students. Acting as an experienced, supportive upperclassman and career mentor, Senior Buddy provides tailored career roadmaps, internship application strategies, resume optimization advice, technical & behavioral interview prep, and academic guidance.

---

## ✨ Key Features

- 💬 **Context-Aware AI Guidance**: Powered by the **Gemini API** (`gemini-2.5-flash`), delivering practical, encouraging, and structured mentorship formatted in rich Markdown.
- 🎓 **Personalized Student Profile**: Save your degree, major, year of study, target career roles, skills, and interests. Senior Buddy automatically injects your profile into every AI interaction for hyper-relevant responses.
- ⚡ **Quick-Action Mentorship Modules**:
  - 🎯 **Career Guidance**: Strategic roadmaps, skill building, and industry trends.
  - 📄 **Resume & Portfolio Advice**: Action-oriented bullet point formulas (Action Verb + Task + Result) and layout reviews.
  - 💼 **Interview Preparation**: Technical questions, coding strategies, and behavioral STAR framework answers.
  - 🚀 **Internship Strategy**: LinkedIn networking tips, cold email templates, and application timelines.
- 🎤 **Voice Input & Text-to-Speech**: Speech-to-text dictation for asking questions and speech synthesis for reading AI responses aloud.
- 💾 **Session History Persistence**: Save and resume chat history across browser reloads.
- 🎨 **Modern Glassmorphic Dark UI**: High-end aesthetic with vibrant HSL gradient accents, micro-animations, mobile-responsive layout, and Google Fonts (`Plus Jakarta Sans`, `Inter`, `Fira Code`).
- 🛡️ **Secure API Key Management**: Loads `GEMINI_API_KEY` securely from `.env` with fallback error detection and health indicator status.

---

## 🛠️ Tech Stack

- **Frontend**: HTML5, Vanilla CSS3 (Custom Glassmorphism Design System), JavaScript (ES6+, Web Speech API, Marked.js)
- **Backend**: Python 3.10+ with Flask, Flask-CORS, and Gunicorn WSGI Server
- **AI Integration**: Google GenAI SDK (`google-genai` / `google-generativeai`)
- **Environment Management**: `python-dotenv`

---

## 📁 Project Structure

```text
AI-SeniorBuddy/
├── app.py                  # Flask backend server & Gemini API orchestrator
├── Procfile                # Gunicorn process file for production deployment
├── requirements.txt        # Python package dependencies
├── .env.example            # Environment configuration template
├── .env                    # Local environment variables (git-ignored)
├── .gitignore              # Standard git ignore rules
├── README.md               # Documentation & deployment guide
├── static/
│   ├── css/
│   │   └── style.css       # Complete design system & glassmorphism CSS
│   └── js/
│       └── app.js          # Frontend controller, state & API integration
└── templates/
    └── index.html          # Main application UI template
```

---

## 🚀 Local Development Setup

### 1. Prerequisites
- **Python 3.8+** installed on your system.
- A **Gemini API Key** from [Google AI Studio](https://aistudio.google.com/).

### 2. Clone / Navigate to Directory
```bash
git clone https://github.com/YOUR_USERNAME/AI-SeniorBuddy.git
cd AI-SeniorBuddy
```

### 3. Create a Virtual Environment

#### On Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\activate
```

#### On macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables
Copy `.env.example` to `.env` and insert your Gemini API Key:

```bash
# On Windows PowerShell
Copy-Item .env.example .env

# On Linux/macOS
cp .env.example .env
```

Open `.env` and set your key:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
PORT=5000
FLASK_ENV=development
```

### 6. Run the Application
```bash
python app.py
```

Access the UI at `http://127.0.0.1:5000` in your web browser.

---

## 🐙 Pushing to GitHub

Follow these steps to publish your project on GitHub:

```bash
# 1. Initialize git repository (if not already initialized)
git init

# 2. Add all files to staging
git add .

# 3. Commit changes
git commit -m "Initial commit: Senior Buddy AI application"

# 4. Create a new repository on GitHub and link remote
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/AI-SeniorBuddy.git

# 5. Push code to GitHub
git push -u origin main
```

> **Note**: `.env` is included in `.gitignore` to keep your API key secure.

---

## 🌐 Deploying to Production (Render / Railway / Heroku)

### Deploying on Render (Free Tier Supported)
1. Push your code to GitHub.
2. Go to [Render Dashboard](https://dashboard.render.com/) and click **New +** -> **Web Service**.
3. Connect your GitHub repository.
4. Set the build settings:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. In **Environment Variables**, add:
   - Key: `GEMINI_API_KEY`, Value: *`your_gemini_api_key_here`*
6. Click **Create Web Service**.

---

## 📄 License
Created for college students to navigate their academic and career journey. Open source and customizable!
