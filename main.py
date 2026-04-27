import os
import json
from flask import Flask, jsonify, render_template, session, redirect, url_for, request, abort
from flask_cors import CORS
from routes.analyze import analyze_bp
from routes.auth import auth_bp
from routes.chat import chat_bp
from routes.bookmark import bookmark_bp
from routes.booking import booking_bp
from routes.admin import admin_bp
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, template_folder="templates", static_folder="static")

# Security and Session config
app.secret_key = os.getenv("SECRET_KEY", "super_secret_dev_key_123")
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=False  # Set to True in production with HTTPS
)

# Enable CORS
CORS(app, supports_credentials=True)

# Register Blueprints
app.register_blueprint(analyze_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(bookmark_bp)
app.register_blueprint(booking_bp)
app.register_blueprint(admin_bp)

from tools.memory import get_all_mentors, get_all_events, get_history, get_password_reset_request

# --- HTML Page Routes ---

@app.route("/admin")
def admin_root():
    return redirect("/admin/dashboard")

@app.route("/")
def root():
    mentors = get_all_mentors()
    events = [e for e in get_all_events() if e.get('status') == 'upcoming']
    
    # We still load testimonials statically if we haven't built DB logic for them yet.
    # Let's add a quick fallback for testimonials to avoid error.
    path = os.path.join(app.static_folder, 'data', 'testimonials.json')
    try:
        with open(path, 'r') as f:
            testimonials = json.load(f)
    except:
        testimonials = []
        
    return render_template("landing.html", mentors=mentors, events=events, testimonials=testimonials)

@app.route("/login-page")
def login_page():
    if session.get('user_id'):
        if session.get('is_admin'):
            return redirect('/admin/dashboard')
        return redirect(url_for('dashboard'))
    return render_template("login.html")

@app.route("/register-page")
def register_page():
    if session.get('user_id'):
        if session.get('is_admin'):
            return redirect('/admin/dashboard')
        return redirect(url_for('dashboard'))
    return render_template("register.html")

@app.route("/forgot-password-page")
def forgot_password_page():
    return render_template("forgot_password.html")

@app.route("/reset-password/<token>")
def reset_password_page(token):
    if not get_password_reset_request(token):
        return render_template("reset_password.html", token=token, valid=False)
    return render_template("reset_password.html", token=token, valid=True)

@app.route("/dashboard")
def dashboard():
    if not session.get('user_id'):
        return redirect(url_for('login_page'))
    if session.get('is_admin'):
        return redirect('/admin/dashboard')
    return render_template("dashboard.html", name=session.get('name'), email=session.get('email'))

@app.route("/chat-page")
def chat_page_route():
    if not session.get('user_id'):
        return redirect(url_for('login_page'))
    return render_template("chat_page.html")

@app.route("/account")
def account_page():
    if not session.get('user_id') or session.get('is_admin'):
        return redirect(url_for('login_page'))
    return render_template("account.html", name=session.get('name'), email=session.get('email'))

@app.route("/mentors")
def mentors_page():
    mentors = get_all_mentors()
    return render_template("mentors.html", mentors=mentors)

@app.route("/events")
def events_page():
    events = get_all_events()
    return render_template("events.html", events=events)

@app.route("/privacy")
def privacy_page():
    return render_template("privacy.html")

@app.route("/terms")
def terms_page():
    return render_template("terms.html")

@app.route("/contact")
def contact_page():
    return render_template("contact.html")

@app.route("/report")
def report_page():
    user_id = session.get('user_id')
    if not user_id or session.get('is_admin'):
        return redirect(url_for('login_page'))

    idea_name = (request.args.get("idea_name") or "").strip()
    if not idea_name:
        abort(400)

    history = get_history(user_id=user_id)
    matching = [item for item in history if item.get("idea_name") == idea_name]
    if not matching:
        abort(404)

    record = sorted(matching, key=lambda item: item.get("created_at", ""))[-1]
    return render_template("report.html", record=record, autoprint=request.args.get("autoprint") == "1")

if __name__ == "__main__":
    # Seed admin on first run
    from tools.memory import seed_admin
    seed_admin()
    app.run(host="0.0.0.0", port=8000, debug=False)
