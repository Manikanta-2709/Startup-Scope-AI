from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash
from tools.memory import (
    create_user,
    verify_user,
    update_user_profile,
    update_user_password,
    create_password_reset_token,
    reset_user_password_with_token,
)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/register", methods=['POST'])
def register():
    data = request.json or {}
    name = data.get("name")
    email = (data.get("email") or "").strip().lower()
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({"error": "Name, email, and password required"}), 400

    hashed_password = generate_password_hash(password)
    user_id = create_user(name, email, hashed_password)

    if not user_id:
        return jsonify({"error": "Email already registered"}), 409

    # Automatically log in after registration
    session['user_id'] = user_id
    session['name'] = name
    session['email'] = email
    session['is_admin'] = False
    
    return jsonify({"message": "Registration successful", "user": {"id": user_id, "name": name, "email": email}})


@auth_bp.route("/login", methods=['POST'])
def login():
    data = request.json or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    user = verify_user(email, password)
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    session['user_id'] = user['id']
    session['name'] = user['name']
    session['email'] = user['email']
    session['is_admin'] = False
    
    return jsonify({"message": "Login successful", "user": {"id": user['id'], "name": user['name'], "email": user['email']}})


@auth_bp.route("/logout", methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"})


@auth_bp.route("/me", methods=['GET'])
def me():
    user_id = session.get('user_id')
    name = session.get('name')
    email = session.get('email')
    
    if user_id:
        return jsonify({"authenticated": True, "user": {"id": user_id, "name": name, "email": email}})
    else:
        return jsonify({"authenticated": False}), 401


@auth_bp.route("/account/profile", methods=['POST'])
def account_profile():
    user_id = session.get('user_id')
    if not user_id or session.get('is_admin'):
        return jsonify({"error": "Login required"}), 401

    data = request.json or {}
    ok, result = update_user_profile(user_id, data.get("name"), data.get("email"))
    if not ok:
        return jsonify({"error": result}), 400

    session['name'] = result["name"]
    session['email'] = result["email"]
    return jsonify({"message": "Profile updated successfully.", "user": result})


@auth_bp.route("/account/password", methods=['POST'])
def account_password():
    user_id = session.get('user_id')
    if not user_id or session.get('is_admin'):
        return jsonify({"error": "Login required"}), 401

    data = request.json or {}
    current_password = data.get("current_password")
    new_password = data.get("new_password")

    if not current_password or not new_password:
        return jsonify({"error": "Current and new password are required."}), 400
    if len(new_password) < 8:
        return jsonify({"error": "New password must be at least 8 characters."}), 400

    ok, message = update_user_password(user_id, current_password, new_password)
    if not ok:
        return jsonify({"error": message}), 400
    return jsonify({"message": message})


@auth_bp.route("/forgot-password", methods=['POST'])
def forgot_password():
    data = request.json or {}
    email = (data.get("email") or "").strip().lower()
    new_password = data.get("new_password")

    if not email:
        return jsonify({"error": "Email is required."}), 400
    if not new_password or len(new_password) < 8:
        return jsonify({"error": "New password must be at least 8 characters."}), 400

    token = create_password_reset_token(email)
    if not token:
        return jsonify({"error": "No account was found for that email."}), 404

    ok, message = reset_user_password_with_token(token, new_password)
    if not ok:
        return jsonify({"error": message}), 400
    return jsonify({"message": "Password changed successfully. You can log in with the new password now."})


@auth_bp.route("/reset-password/<token>", methods=['POST'])
def reset_password(token):
    data = request.json or {}
    new_password = data.get("new_password")

    if not new_password or len(new_password) < 8:
        return jsonify({"error": "New password must be at least 8 characters."}), 400

    ok, message = reset_user_password_with_token(token, new_password)
    if not ok:
        return jsonify({"error": message}), 400
    return jsonify({"message": message})
