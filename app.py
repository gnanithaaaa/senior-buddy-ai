import os
import logging
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- System Prompt Builder ---
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


# --- Smart Senior Buddy Demo Fallback Generator ---
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

    # 1. Resume / Portfolio Help
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

    # 2. Interview Preparation
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

    # 3. Internship Strategy & Cold Emails
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

    # 4. Career Guidance / General Roadmap
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


# --- Gemini API Call Handler ---
def generate_gemini_response(user_message: str, profile: dict = None, history: list = None, action_type: str = None) -> str:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    
    # If key is missing or is template placeholder, use Smart Fallback Demo Engine
    if not api_key or api_key == "your_gemini_api_key_here":
        logger.info("GEMINI_API_KEY is not configured. Utilizing Smart Senior Buddy Fallback Engine.")
        return generate_demo_fallback_response(user_message, profile, action_type)

    system_prompt = build_system_prompt(profile, action_type)
    full_prompt = f"{system_prompt}\n\nUser Question: {user_message}"

    # Attempt 1: google.genai SDK
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

    # Attempt 2: google.generativeai SDK fallback
    try:
        import google.generativeai as genai_legacy
        genai_legacy.configure(api_key=api_key)
        model = genai_legacy.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(full_prompt)
        if response and response.text:
            return response.text
    except Exception as e2:
        logger.warning(f"google.generativeai legacy SDK fallback error: {e2}")

    # Final Graceful Fallback if API call fails or quota exhausted
    logger.info("API call failed or quota exceeded. Serving Smart Fallback response.")
    return generate_demo_fallback_response(user_message, profile, action_type)


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
        "message": "Senior Buddy server is running smoothly in Live Gemini AI mode." if has_key else "Senior Buddy server is running smoothly in Demo Mentor Mode."
    })


@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json() or {}
        user_message = data.get('message', '').strip()
        profile = data.get('profile', {})
        history = data.get('history', [])
        action_type = data.get('action_type', None)

        if not user_message and not action_type:
            return jsonify({
                "success": False,
                "error": "Please provide a question or select a quick action."
            }), 400

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

        return jsonify({
            "success": True,
            "response": ai_response,
            "user_message": user_message
        })

    except Exception as e:
        logger.error(f"Error handling chat request: {e}", exc_info=True)
        # Always return graceful response rather than crashing UI
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
