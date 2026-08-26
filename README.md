# 🎓 Senior Buddy — AI-Powered College Career & Academic Assistant

**Senior Buddy** is a sleek, context-aware AI web application built for college students. Acting as an experienced, supportive upperclassman and career mentor, Senior Buddy provides tailored career roadmaps, internship application strategies, resume optimization advice, technical & behavioral interview prep, and academic guidance.

---

## ✨ Features

- 🔑 **Complete User Authentication**: Sign Up, Log In, and Log Out with encrypted password hashing (`PBKDF2/SHA256`) and persistent session management.
- 📊 **Student Career Dashboard**: Personalized dashboard tracking student metadata, total mentorship messages, career goals, primary skills, and profile shortcuts.
- 💾 **Persistent Chat History & Profiles**: Stored in a lightweight, zero-config SQLite database (`senior_buddy.db`). User profiles and past chat history automatically persist across reloads and devices.
- 💬 **Context-Aware AI Guidance**: Powered by the **Gemini API** (`gemini-2.5-flash`) with automatic **Smart Demo Mentor Fallback** when no key is configured.
- ⚡ **Quick-Action Mentorship Modules**:
  - 🎯 **Career Guidance**: Strategic roadmaps, skill building, and industry trends.
  - 📄 **Resume & Portfolio Advice**: Action-oriented bullet point formulas (Action Verb + Task + Result) and layout reviews.
  - 💼 **Interview Preparation**: Technical questions, coding strategies, and behavioral STAR framework answers.
  - 🚀 **Internship Strategy**: LinkedIn networking tips, cold email templates, and application timelines.
- 🎤 **Voice Input & Text-to-Speech**: Speech-to-text dictation for asking questions and speech synthesis for reading AI responses aloud.
- 🎨 **Modern Glassmorphic Dark UI**: High-end aesthetic with HSL gradient accents, micro-animations, mobile-responsive layout, and Google Fonts (`Plus Jakarta Sans`, `Inter`, `Fira Code`).
- ☁️ **Deployment Ready**: Fully configured with `gunicorn` and `Procfile` for Render, Heroku, or Railway.

---

## 🛠️ Tech Stack

- **Frontend**: HTML5, Vanilla CSS3 (Custom Glassmorphism Design System), JavaScript (ES6+, Web Speech API, Marked.js)
- **Backend**: Python 3.10+, Flask, Flask-CORS, Gunicorn WSGI Server, Werkzeug Security
- **Database**: SQLite3 (`senior_buddy.db`)
- **AI Integration**: Google GenAI SDK (`google-genai` / `google-generativeai`)
- **Environment Management**: `python-dotenv`

---

## 📁 Project Structure

```text
AI-SeniorBuddy/
├── app.py                  # Flask backend, Auth routes, SQLite DB & Gemini orchestrator
├── Procfile                # Gunicorn process file for production deployment
├── requirements.txt        # Python package dependencies
├── senior_buddy.db         # SQLite database file (created on startup)
├── .env.example            # Environment configuration template
├── .env                    # Local environment variables (git-ignored)
├── .gitignore              # Standard git ignore rules
├── README.md               # Documentation & deployment guide
├── static/
│   ├── css/
│   │   └── style.css       # Complete design system, auth & dashboard styling
│   └── js/
│       └── app.js          # Frontend controller, auth state & API integration
└── templates/
    └── index.html          # Main application UI template
```

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.8+** installed on your system.
- *(Optional)* A **Gemini API Key** from [Google AI Studio](https://aistudio.google.com/).

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
# On Windows PowerShell
Copy-Item .env.example .env

# On Linux/macOS
cp .env.example .env
```

Set your secret key and optional Gemini API Key in `.env`:
```env
SECRET_KEY=your_secure_secret_key_here
GEMINI_API_KEY=your_optional_gemini_api_key
PORT=5000
FLASK_ENV=development
```

### 4. Run the Application
```bash
python app.py
```

Access the UI at `http://127.0.0.1:5000` in your web browser.

---

## 🐙 Pushing to GitHub & Render Deployment

### Push to GitHub
```bash
git add .
git commit -m "Add complete authentication system, user dashboard, and persistent SQLite database"
git push -u origin main
```

### Render Deployment
1. Connect repository on [Render Dashboard](https://dashboard.render.com/).
2. **Build Command**: `pip install -r requirements.txt`
3. **Start Command**: `gunicorn app:app`
4. Set Environment Variables:
   - `SECRET_KEY`: `your_random_secret_key`
   - `GEMINI_API_KEY`: *(Optional)* `your_gemini_api_key`
