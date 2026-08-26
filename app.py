import os
import sqlite3
import logging
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.getenv("SECRET_KEY", "senior-buddy-secret-key-2026-production-safe")
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), 'senior_buddy.db')

# --- Database Initialization ---
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Users Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Profiles Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                degree TEXT,
                year TEXT,
                target_role TEXT,
                skills TEXT,
                interests TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')

        # Chat Messages Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                sender TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        conn.commit()
        logger.info("Database initialized successfully.")

# Run DB initialization on startup
init_db()


# --- System Prompt Generator ---
def build_system_prompt(profile: dict = None, action_type: str = None) -> str:
    prompt = (
        "You are 'Senior Buddy' — an experienced, smart, encouraging, and highly approachable "
        "college senior & career mentor. Your goal is to guide college students through career options, "
        "internship/job searches, resume improvements, interview preparation, and general academic life.\n\n"
        "GUIDELINES FOR YOUR RESPONSES:\n"
        "1. Tone: Friendly, empathetic, realistic, structured, and practical (like a helpful senior student).\n"
        "2. Formatting: Use Markdown headers, bold highlights, bullet points, and clean numbered lists.\n"
        "3. Actionable Advice: Give concrete next steps, specific tools, resource suggestions, and practical tips.\n"
        "4. Speak directly and genuinely to a college student.\n"
    )

    if profile and isinstance(profile, dict):
        name = profile.get('name', '').strip()
        degree = profile.get('degree', '').strip()
        year = profile.get('year', '').strip()
        skills = profile.get('skills', '').strip()
        interests = profile.get('interests', '').strip()
        target_role = profile.get('target_role', '').strip()

        context_lines = []
        if name:
            context_lines.append(f"- Student Name: {name}")
        if degree:
            context_lines.append(f"- Degree/Major: {degree}")
        if year:
            context_lines.append(f"- Year of Study: {year}")
        if target_role:
            context_lines.append(f"- Target Role / Goal: {target_role}")
        if skills:
            context_lines.append(f"- Skills: {skills}")
        if interests:
            context_lines.append(f"- Interests: {interests}")

        if context_lines:
            prompt += "\nSTUDENT PROFILE CONTEXT:\n" + "\n".join(context_lines) + "\n"
            prompt += "Tailor your guidance specifically using the student's background, target role, and skill set above.\n"

    if action_type:
        action_instructions = {
            "career_guidance": (
                "\nSPECIAL FOCUS: Provide comprehensive Career Guidance. Outline potential career roadmaps, "
                "industry trends, key milestones for college years, and high-impact skill-building projects."
            ),
            "resume_help": (
                "\nSPECIAL FOCUS: Provide Resume & Portfolio Advice. Share bulletproof resume bullet-point formulas "
                "(Action Verb + Task + Quantifiable Result), structure advice, and common resume mistakes to avoid."
            ),
            "interview_prep": (
                "\nSPECIAL FOCUS: Provide Technical & Behavioral Interview Preparation tips. Include sample questions, "
                "STAR method framework for answering behavioral questions, and live interview strategies."
            ),
            "internship_advice": (
                "\nSPECIAL FOCUS: Provide Internship & Job Application Strategies. Share cold emailing templates, "
                "networking strategies on LinkedIn, application timelines, and portfolio project ideas."
            )
        }
        prompt += action_instructions.get(action_type, "")

    return prompt


# --- Smart Demo Fallback Generator ---
def generate_demo_fallback_response(user_message: str, profile: dict = None, action_type: str = None) -> str:
    name = (profile.get('name') if profile else '') or 'there'
    degree = (profile.get('degree') if profile else '') or 'your degree'
    year = (profile.get('year') if profile else '') or 'your current year'
    target_role = (profile.get('target_role') if profile else '') or 'your dream role'
    skills = (profile.get('skills') if profile else '') or 'core technical & soft skills'

    msg_lower = user_message.lower()

    footer_note = (
        "\n\n---\n"
        "💡 *Note: Senior Buddy is operating in **Demo Mentor Mode**. "
        "To enable live dynamic Gemini AI responses, configure `GEMINI_API_KEY` in your environment variables.*"
    )

    if action_type == "resume_help" or any(k in msg_lower for k in ["resume", "cv", "portfolio", "bullet", "project"]):
        return (
            f"### 📄 Senior Buddy's Resume & Portfolio Blueprint for {name}\n\n"
            f"Hey {name}! Tailoring your resume for **{target_role}** while pursuing **{degree}** ({year}) requires "
            f"making every bullet point count. Here is my proven senior framework:\n\n"
            f"#### 1. The Bulletproof Resume Formula\n"
            f"Always write your project and internship bullet points using this formula:\n"
            f"> **[Strong Action Verb]** + **[Task/Feature Developed]** + **[Tech Stack Used]** + **[Quantifiable Result/Metric]**\n\n"
            f"**Example:**\n"
            f"- *Before:* Worked on a full-stack project using React and Python.\n"
            f"- *After:* **Architected and deployed** a responsive student portal using `{skills.split(',')[0] if ',' in skills else skills}`, "
            f"reducing API response latency by **35%** and serving 500+ active users.\n\n"
            f"#### 2. Key Sections to Include for {target_role}\n"
            f"1. **Header**: Name, LinkedIn, GitHub, Portfolio URL, and Contact Info.\n"
            f"2. **Education**: {degree} | Expected Grad Year.\n"
            f"3. **Technical Skills**: Grouped into *Languages*, *Frameworks*, *Tools & Databases*.\n"
            f"4. **Featured Projects**: 2–3 end-to-end projects demonstrating `{skills}`.\n"
            f"5. **Experience / Extra-Curriculars**: Hackathons, club leadership, or campus involvement.\n\n"
            f"#### 3. Pro Senior Advice\n"
            f"- Keep your resume strictly to **1 page**.\n"
            f"- Use single-column ATS-friendly templates (avoid fancy multi-column graphics).\n"
            f"- Host live working demos and clear GitHub `README.md` files for every project!"
            + footer_note
        )
    elif action_type == "interview_prep" or any(k in msg_lower for k in ["interview", "star", "behavioral", "coding", "technical"]):
        return (
            f"### 💼 Technical & Behavioral Interview Master Guide for {name}\n\n"
            f"Getting ready for interviews for **{target_role}**? Don't worry, {name} — here is the exact strategy "
            f"that helps students stand out in campus placements and company interviews:\n\n"
            f"#### 1. Behavioral Questions: The STAR Method\n"
            f"For questions like *'Tell me about a technical challenge you faced'*, structure your answer in 2 minutes:\n"
            f"- **Situation (15%)**: Set the context of your project or coursework in {degree}.\n"
            f"- **Task (15%)**: State the specific problem or requirement you had to solve.\n"
            f"- **Action (50%)**: Explain the exact steps YOU took using `{skills}`.\n"
            f"- **Result (20%)**: Highlight the positive outcome, key learning, or metric.\n\n"
            f"#### 2. Technical Interview Roadmap for {target_role}\n"
            f"1. **Data Structures & Algorithms**: Master Arrays, Strings, HashMaps, Two Pointers, Trees, and Dynamic Programming.\n"
            f"2. **System Basics**: Understand REST APIs, Database Indexing, SQL vs NoSQL, and basic HTTP lifecycle.\n"
            f"3. **Dry Run Out Loud**: Always communicate your thought process before writing code.\n\n"
            f"#### 3. Top 3 Questions to Ask the Interviewer\n"
            f"- *'What does a typical day look like for an intern/junior developer on your team?'*\n"
            f"- *'What engineering challenges is the team currently working to solve?'*\n"
            f"- *'What onboarding or mentorship structure is provided to help new hires succeed?'*"
            + footer_note
        )
    elif action_type == "internship_advice" or any(k in msg_lower for k in ["internship", "intern", "cold email", "linkedin", "apply", "job"]):
        return (
            f"### 🚀 Internship Acquisition & Cold Outreach Strategy for {name}\n\n"
            f"Securing an internship as a {year} student in **{degree}** requires a dual strategy: "
            f"on-campus placements + smart off-campus outreach.\n\n"
            f"#### 1. Direct Cold Email Template for Recruiters / Founders\n"
            f"```text\n"
            f"Subject: {degree} Student Interested in {target_role} Roles at [Company Name]\n\n"
            f"Hi [Name / Hiring Manager],\n\n"
            f"I hope you're having a great week! My name is {name}, a {year} student pursuing {degree}. "
            f"I've been following [Company Name]'s recent work in [Domain] and loved your recent project on [Topic].\n\n"
            f"I specialize in {skills} and recently built [Project Name], which solved [Problem]. "
            f"I'd love the opportunity to contribute as a {target_role} intern at [Company Name].\n\n"
            f"I've attached my resume for your reference: [Portfolio/GitHub Link]\n"
            f"Would you be open to a brief 5-minute chat next week?\n\n"
            f"Best regards,\n"
            f"{name}\n"
            f"```\n\n"
            f"#### 2. Action Plan for Next 30 Days\n"
            f"1. **Optimize LinkedIn Profile**: Headline should be: *'{degree} Student | Aspiring {target_role} | {skills}'*.\n"
            f"2. **Send 5 Outreach Messages Daily**: Target Engineering Managers and Tech Recruiters.\n"
            f"3. **Build 1 High-Quality Full-Stack Project**: Deploy it live so recruiters can test it immediately."
            + footer_note
        )
    else:
        return (
            f"### 🎯 Personal Career Roadmap for {name}\n\n"
            f"Hello {name}! As a {year} student in **{degree}**, aiming for **{target_role}** is a fantastic target. "
            f"Here is your step-by-step career navigation roadmap:\n\n"
            f"#### 📍 Milestone 1: Core Fundamentals ({year})\n"
            f"- Deepen your understanding of your primary tools: **{skills}**.\n"
            f"- Practice consistent coding / problem solving (e.g. 1-2 problems daily on LeetCode/HackerRank).\n"
            f"- Ensure foundational CS subjects (Data Structures, DBMS, Computer Networks, OS) are solid.\n\n"
            f"#### 🚀 Milestone 2: Portfolio Building\n"
            f"- Build 2 signature projects tailored to **{target_role}**.\n"
            f"- Ensure your projects feature real authentication, API endpoints, database persistence, and a polished UI.\n"
            f"- Write detailed `README.md` files with screenshots and setup guides.\n\n"
            f"#### 💼 Milestone 3: Campus & Off-Campus Preparation\n"
            f"- Prepare a 1-page ATS-optimized resume.\n"
            f"- Practice mock interviews with peers to build confidence.\n"
            f"- Build your LinkedIn network actively by connecting with alumni working in your target companies.\n\n"
            f"Feel free to ask me any specific question about resumes, interview questions, or project ideas!"
            + footer_note
        )


def generate_gemini_response(user_message: str, profile: dict = None, history: list = None, action_type: str = None) -> str:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "your_gemini_api_key_here":
        return generate_demo_fallback_response(user_message, profile, action_type)

    system_prompt = build_system_prompt(profile, action_type)
    full_prompt = f"{system_prompt}\n\nUser Question: {user_message}"

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        contents = []

        if history and isinstance(history, list):
            for item in history:
                role = item.get("role", "user")
                text = item.get("content") or item.get("parts", "")
                if isinstance(text, list):
                    text = " ".join(text)
                if text:
                    contents.append(types.Content(
                        role="user" if role == "user" else "model",
                        parts=[types.Part.from_text(text=text)]
                    ))

        contents.append(types.Content(
            role="user",
            parts=[types.Part.from_text(text=full_prompt)]
        ))

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                temperature=0.7,
                top_p=0.9,
                max_output_tokens=2048,
            )
        )
        if response and response.text:
            return response.text
    except Exception as e1:
        logger.warning(f"google.genai SDK call error/fallback: {e1}")

    try:
        import google.generativeai as genai_legacy
        genai_legacy.configure(api_key=api_key)
        model = genai_legacy.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(full_prompt)
        if response and response.text:
            return response.text
    except Exception as e2:
        logger.warning(f"google.generativeai legacy SDK fallback error: {e2}")

    return generate_demo_fallback_response(user_message, profile, action_type)


# --- Authentication & User API Endpoints ---

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    has_key = bool(api_key and api_key != "your_gemini_api_key_here")
    return jsonify({
        "status": "online",
        "app": "Senior Buddy AI",
        "has_api_key": has_key,
        "mode": "live_gemini" if has_key else "demo_fallback",
        "user_logged_in": 'user_id' in session
    })


@app.route('/api/auth/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json() or {}
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()
        degree = data.get('degree', 'Computer Science').strip()
        year = data.get('year', '3rd Year').strip()
        target_role = data.get('target_role', 'Software Engineer').strip()
        skills = data.get('skills', 'Python, Problem Solving').strip()
        interests = data.get('interests', 'Software Development').strip()

        if not name or not email or not password:
            return jsonify({"success": False, "error": "Name, email, and password are required."}), 400

        if len(password) < 6:
            return jsonify({"success": False, "error": "Password must be at least 6 characters long."}), 400

        hashed_password = generate_password_hash(password)

        with get_db() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                    (name, email, hashed_password)
                )
                user_id = cursor.lastrowid

                cursor.execute(
                    "INSERT INTO profiles (user_id, degree, year, target_role, skills, interests) VALUES (?, ?, ?, ?, ?, ?)",
                    (user_id, degree, year, target_role, skills, interests)
                )
                conn.commit()
            except sqlite3.IntegrityError:
                return jsonify({"success": False, "error": "An account with this email already exists."}), 400

        session['user_id'] = user_id
        session.permanent = True

        return jsonify({
            "success": True,
            "user": {
                "id": user_id,
                "name": name,
                "email": email,
                "profile": {
                    "degree": degree,
                    "year": year,
                    "target_role": target_role,
                    "skills": skills,
                    "interests": interests
                }
            }
        })
    except Exception as e:
        logger.error(f"Signup error: {e}", exc_info=True)
        return jsonify({"success": False, "error": "Sign up failed. Please try again."}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json() or {}
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()

        if not email or not password:
            return jsonify({"success": False, "error": "Email and password are required."}), 400

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()

            if not user or not check_password_hash(user['password_hash'], password):
                return jsonify({"success": False, "error": "Invalid email or password."}), 401

            user_id = user['id']
            cursor.execute("SELECT * FROM profiles WHERE user_id = ?", (user_id,))
            profile = cursor.fetchone()

        session['user_id'] = user_id
        session.permanent = True

        profile_data = {
            "degree": profile['degree'] if profile else "Computer Science",
            "year": profile['year'] if profile else "3rd Year",
            "target_role": profile['target_role'] if profile else "Software Engineer",
            "skills": profile['skills'] if profile else "",
            "interests": profile['interests'] if profile else ""
        } if profile else {}

        return jsonify({
            "success": True,
            "user": {
                "id": user['id'],
                "name": user['name'],
                "email": user['email'],
                "profile": profile_data
            }
        })
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        return jsonify({"success": False, "error": "Login failed. Please try again."}), 500


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success": True, "message": "Logged out successfully."})


@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"authenticated": False})

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()

        if not user:
            session.clear()
            return jsonify({"authenticated": False})

        cursor.execute("SELECT degree, year, target_role, skills, interests FROM profiles WHERE user_id = ?", (user_id,))
        profile = cursor.fetchone()

        cursor.execute("SELECT COUNT(*) as msg_count FROM chat_messages WHERE user_id = ?", (user_id,))
        stats = cursor.fetchone()

    profile_data = dict(profile) if profile else {}

    return jsonify({
        "authenticated": True,
        "user": {
            "id": user['id'],
            "name": user['name'],
            "email": user['email'],
            "profile": profile_data,
            "total_chats": stats['msg_count'] if stats else 0
        }
    })


@app.route('/api/profile/update', methods=['POST'])
def update_profile():
    user_id = session.get('user_id')
    data = request.get_json() or {}

    name = data.get('name', '').strip()
    degree = data.get('degree', '').strip()
    year = data.get('year', '').strip()
    target_role = data.get('target_role', '').strip()
    skills = data.get('skills', '').strip()
    interests = data.get('interests', '').strip()

    with get_db() as conn:
        cursor = conn.cursor()

        if user_id:
            if name:
                cursor.execute("UPDATE users SET name = ? WHERE id = ?", (name, user_id))

            cursor.execute('''
                INSERT INTO profiles (user_id, degree, year, target_role, skills, interests)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    degree=excluded.degree,
                    year=excluded.year,
                    target_role=excluded.target_role,
                    skills=excluded.skills,
                    interests=excluded.interests,
                    updated_at=CURRENT_TIMESTAMP
            ''', (user_id, degree, year, target_role, skills, interests))
            conn.commit()

    return jsonify({"success": True, "message": "Profile updated successfully."})


@app.route('/api/history', methods=['GET', 'DELETE'])
def manage_history():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"success": True, "messages": []})

    with get_db() as conn:
        cursor = conn.cursor()

        if request.method == 'DELETE':
            cursor.execute("DELETE FROM chat_messages WHERE user_id = ?", (user_id,))
            conn.commit()
            return jsonify({"success": True, "message": "History cleared."})

        cursor.execute(
            "SELECT sender, content, created_at FROM chat_messages WHERE user_id = ? ORDER BY id ASC",
            (user_id,)
        )
        rows = cursor.fetchall()
        messages = [{"sender": row['sender'], "content": row['content'], "created_at": row['created_at']} for row in rows]
        return jsonify({"success": True, "messages": messages})


@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json() or {}
        user_message = data.get('message', '').strip()
        profile = data.get('profile', {})
        history = data.get('history', [])
        action_type = data.get('action_type', None)

        if not user_message and not action_type:
            return jsonify({"success": False, "error": "Please provide a question or select a quick action."}), 400

        if not user_message and action_type:
            action_prompts = {
                "career_guidance": "Can you provide me with a clear career roadmap and guidance for my degree and field?",
                "resume_help": "How can I build an impactful resume and portfolio to stand out for jobs?",
                "interview_prep": "What are the best tips, techniques, and common questions to prepare for tech and behavioral interviews?",
                "internship_advice": "What is the step-by-step strategy for finding and securing top internships?"
            }
            user_message = action_prompts.get(action_type, "Can you provide general career and placement advice?")

        ai_response = generate_gemini_response(
            user_message=user_message,
            profile=profile,
            history=history,
            action_type=action_type
        )

        # Store in DB if user is logged in
        user_id = session.get('user_id')
        if user_id:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO chat_messages (user_id, sender, content) VALUES (?, 'user', ?)",
                    (user_id, user_message)
                )
                cursor.execute(
                    "INSERT INTO chat_messages (user_id, sender, content) VALUES (?, 'ai', ?)",
                    (user_id, ai_response)
                )
                conn.commit()

        return jsonify({
            "success": True,
            "response": ai_response,
            "user_message": user_message
        })

    except Exception as e:
        logger.error(f"Error handling chat request: {e}", exc_info=True)
        fallback_msg = generate_demo_fallback_response(
            user_message=user_message if 'user_message' in locals() else "career advice",
            profile=profile if 'profile' in locals() else {},
            action_type=action_type if 'action_type' in locals() else None
        )
        return jsonify({
            "success": True,
            "response": fallback_msg,
            "user_message": user_message if 'user_message' in locals() else "Question"
        })


if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    debug_mode = os.getenv("FLASK_ENV") == "development"
    print(f"\n[Senior Buddy] Server running on http://127.0.0.1:{port}\n")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
