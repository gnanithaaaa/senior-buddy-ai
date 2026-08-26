import os
import logging
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# System Prompt Generator for Senior Buddy
def build_system_prompt(profile: dict = None, action_type: str = None) -> str:
    prompt = (
        "You are 'Senior Buddy' — an experienced, smart, encouraging, and highly approachable "
        "college senior & career mentor. Your goal is to guide college students through career options, "
        "internship/job searches, resume improvements, interview preparation, and general academic life.\n\n"
        "GUIDELINES FOR YOUR RESPONSES:\n"
        "1. Tone: Friendly, empathetic, realistic, structured, and practical (like a helpful senior student).\n"
        "2. Formatting: Use Markdown headers, bold highlights, bullet points, and clean numbered lists.\n"
        "3. Actionable Advice: Give concrete next steps, specific tools, resource suggestions, and practical tips.\n"
        "4. Tone down corporate jargon: Speak directly and genuinely to a college student.\n"
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


def generate_gemini_response(user_message: str, profile: dict = None, history: list = None, action_type: str = None) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key.strip() == "" or api_key == "your_gemini_api_key_here":
        raise ValueError("MISSING_API_KEY")

    system_prompt = build_system_prompt(profile, action_type)
    full_prompt = f"{system_prompt}\n\nUser Question: {user_message}"

    # First attempt: google.genai SDK
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        
        # Build contents from history if available
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
        
        # Add current user prompt
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
        logger.info(f"google.genai SDK attempt info: {e1}. Trying fallback SDK google.generativeai...")
        
    # Second attempt: google.generativeai SDK fallback
    try:
        import google.generativeai as genai_legacy
        genai_legacy.configure(api_key=api_key)
        
        # Try gemini-1.5-flash or gemini-pro
        model = genai_legacy.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(full_prompt)
        if response and response.text:
            return response.text
    except Exception as e2:
        logger.error(f"Fallback SDK error: {e2}")
        raise e2

    raise Exception("Unable to get response from Gemini API.")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    api_key = os.getenv("GEMINI_API_KEY", "")
    has_key = bool(api_key and api_key.strip() and api_key != "your_gemini_api_key_here")
    return jsonify({
        "status": "online",
        "app": "Senior Buddy AI",
        "has_api_key": has_key,
        "message": "Senior Buddy server is running smoothly." if has_key else "Server running, but GEMINI_API_KEY is not set in .env file."
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

        # If user selected a quick action without typing text, create default prompt
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

    except ValueError as ve:
        if str(ve) == "MISSING_API_KEY":
            return jsonify({
                "success": False,
                "error": "GEMINI_API_KEY is missing or invalid. Please configure your GEMINI_API_KEY in the .env file.",
                "is_config_error": True
            }), 401
        return jsonify({"success": False, "error": str(ve)}), 400

    except Exception as e:
        logger.error(f"Error handling chat request: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": f"An error occurred while connecting to Senior Buddy AI: {str(e)}"
        }), 500


if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    debug_mode = os.getenv("FLASK_ENV") == "development"
    print(f"\n[Senior Buddy] Server running on http://127.0.0.1:{port}\n")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)

