from flask import Blueprint, request, jsonify, session
from tools.analyzer import analyze_startup
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

chat_bp = Blueprint('chat', __name__)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

@chat_bp.route("/chat", methods=['POST'])
def chat():
    """AI Consultant Chat — follows up on the user's startup analysis."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Login required"}), 401

    data = request.json
    message = data.get("message", "")
    idea_context = data.get("idea_context", {})
    chat_history = data.get("history", [])

    if not message:
        return jsonify({"error": "Message is required"}), 400

    # Build the system context from the analysis
    system_prompt = f"""You are a startup consultant for StartupScope AI. 
The user already validated their startup idea and you are now having a follow-up conversation.

Here is their idea context:
- Name: {idea_context.get('idea_name', 'Unknown')}
- Target: {idea_context.get('target_users', 'Unknown')}
- Description: {idea_context.get('description', 'No description')}
- Score: {idea_context.get('idea_score', 'N/A')}/10

RULES:
- Be direct and practical. No fluff.
- Give specific, actionable advice.
- Keep responses under 150 words unless the user asks for detail.
- Reference their specific idea, not generic startup advice.
"""

    # Build conversation for the API
    messages = [system_prompt]
    for msg in chat_history[-10:]:  # Keep last 10 messages for context
        role = "User" if msg.get("role") == "user" else "Consultant"
        messages.append(f"{role}: {msg.get('content', '')}")
    messages.append(f"User: {message}")

    full_prompt = "\n".join(messages) + "\nConsultant:"

    try:
        # 1. Try Gemini
        if GOOGLE_API_KEY:
            genai.configure(api_key=GOOGLE_API_KEY)
            for model_name in ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-flash-latest']:
                try:
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(full_prompt)
                    reply = response.text.strip()
                    
                    from tools.memory import save_chat_message
                    save_chat_message(user_id, idea_context.get('idea_name', ''), message, reply)
                    return jsonify({"reply": reply})
                except Exception as e:
                    print(f"Gemini {model_name} failed: {e}")
                    continue

        # 2. Try OpenAI Fallback
        if OPENAI_API_KEY:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=OPENAI_API_KEY)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": message}],
                    max_tokens=300
                )
                reply = response.choices[0].message.content.strip()
                from tools.memory import save_chat_message
                save_chat_message(user_id, idea_context.get('idea_name', ''), message, reply)
                return jsonify({"reply": reply})
            except Exception as e:
                print(f"OpenAI fallback failed: {e}")

        # 3. Final Fallback Message
        if not GOOGLE_API_KEY and not OPENAI_API_KEY:
            return jsonify({"reply": "AI Consultant is not configured. Please add GOOGLE_API_KEY or OPENAI_API_KEY to your .env file."})
        
        return jsonify({"reply": "I'm having trouble connecting to the AI models right now. Please check your API keys or try again later."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
