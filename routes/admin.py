from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for
from tools.memory import (get_all_users, get_all_bookings, get_all_registrations,
                          update_booking_status, update_registration_status, get_db_client,
                          DATABASE_NAME, get_all_mentors, save_mentor, delete_mentor,
                          get_all_events, save_event, delete_event)
from werkzeug.security import generate_password_hash, check_password_hash

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# --- Admin Auth ---

def clean_text(value):
    return (value or "").strip()

def is_admin():
    return session.get('is_admin', False)

@admin_bp.route("/login", methods=['GET'])
def admin_login_page():
    if is_admin():
        return redirect('/admin/dashboard')
    return render_template("admin/login.html")

@admin_bp.route("/login", methods=['POST'])
def admin_login():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    
    # Check against admin collection
    client = get_db_client()
    if client:
        db = client[DATABASE_NAME]
        admin = db["admins"].find_one({"email": email})
        if admin and check_password_hash(admin["password"], password):
            session['user_id'] = admin.get("id", "admin")
            session['name'] = admin.get("name", "Admin")
            session['email'] = email
            session['is_admin'] = True
            return jsonify({"message": "Admin login successful"})
    
    return jsonify({"error": "Invalid admin credentials"}), 401

@admin_bp.route("/logout", methods=['POST'])
def admin_logout():
    session.clear()
    return jsonify({"message": "Logged out"})

@admin_bp.route("/dashboard")
def admin_dashboard():
    if not is_admin():
        return redirect('/admin/login')
    return render_template("admin/dashboard.html")

# --- Admin Data APIs ---

@admin_bp.route("/api/stats")
def admin_stats():
    if not is_admin():
        return jsonify({"error": "Unauthorized"}), 403
    
    users = get_all_users()
    bookings = get_all_bookings()
    registrations = get_all_registrations()
    
    return jsonify({
        "total_users": len(users),
        "total_bookings": len(bookings),
        "pending_bookings": len([b for b in bookings if b.get("status") == "pending"]),
        "total_registrations": len(registrations),
        "pending_registrations": len([r for r in registrations if r.get("status") == "pending"])
    })

@admin_bp.route("/api/users")
def admin_users():
    if not is_admin():
        return jsonify({"error": "Unauthorized"}), 403
    users = get_all_users()
    # Strip passwords
    for u in users:
        u.pop("password", None)
    return jsonify(users)

@admin_bp.route("/api/bookings")
def admin_bookings():
    if not is_admin():
        return jsonify({"error": "Unauthorized"}), 403
    return jsonify(get_all_bookings())

@admin_bp.route("/api/registrations")
def admin_registrations():
    if not is_admin():
        return jsonify({"error": "Unauthorized"}), 403
    return jsonify(get_all_registrations())

@admin_bp.route("/api/booking/<booking_id>/status", methods=['POST'])
def update_booking(booking_id):
    if not is_admin():
        return jsonify({"error": "Unauthorized"}), 403
    data = request.json
    new_status = data.get("status")  # approved, rejected
    update_booking_status(booking_id, new_status)
    return jsonify({"message": f"Booking {new_status}"})

@admin_bp.route("/api/registration/<reg_id>/status", methods=['POST'])
def update_registration(reg_id):
    if not is_admin():
        return jsonify({"error": "Unauthorized"}), 403
    data = request.json
    new_status = data.get("status")  # confirmed, cancelled
    update_registration_status(reg_id, new_status)
    return jsonify({"message": f"Registration {new_status}"})

# --- Mentor APIs ---

@admin_bp.route("/api/mentors", methods=['GET'])
def get_mentors_admin():
    if not is_admin():
        return jsonify({"error": "Unauthorized"}), 403
    return jsonify(get_all_mentors())

@admin_bp.route("/api/mentor", methods=['POST'])
def save_mentor_admin():
    if not is_admin():
        return jsonify({"error": "Unauthorized"}), 403
    data = request.json or {}
    required = ["name", "role", "specialty", "bio"]
    missing = [field.replace("_", " ").title() for field in required if not clean_text(data.get(field))]
    if missing:
        return jsonify({"error": f"Please fill: {', '.join(missing)}."}), 400

    data["name"] = clean_text(data.get("name"))
    data["role"] = clean_text(data.get("role"))
    data["specialty"] = clean_text(data.get("specialty"))
    data["bio"] = clean_text(data.get("bio"))
    data["photo"] = clean_text(data.get("photo")) or "https://i.pravatar.cc/150"
    mentor_id = save_mentor(data)
    return jsonify({"message": "Mentor saved", "id": mentor_id})

@admin_bp.route("/api/mentor/<mentor_id>", methods=['DELETE'])
def delete_mentor_admin(mentor_id):
    if not is_admin():
        return jsonify({"error": "Unauthorized"}), 403
    delete_mentor(mentor_id)
    return jsonify({"message": "Mentor deleted"})

# --- Event APIs ---

@admin_bp.route("/api/events", methods=['GET'])
def get_events_admin():
    if not is_admin():
        return jsonify({"error": "Unauthorized"}), 403
    return jsonify(get_all_events())

@admin_bp.route("/api/event", methods=['POST'])
def save_event_admin():
    if not is_admin():
        return jsonify({"error": "Unauthorized"}), 403
    data = request.json or {}
    required = ["title", "type", "date", "time", "mentor", "spots", "description"]
    missing = [field.replace("_", " ").title() for field in required if not clean_text(data.get(field))]
    if missing:
        return jsonify({"error": f"Please fill: {', '.join(missing)}."}), 400

    try:
        spots = int(data.get("spots"))
    except (TypeError, ValueError):
        return jsonify({"error": "Total spots must be a number."}), 400
    if spots <= 0:
        return jsonify({"error": "Total spots must be greater than zero."}), 400

    data["title"] = clean_text(data.get("title"))
    data["type"] = clean_text(data.get("type"))
    data["date"] = clean_text(data.get("date"))
    data["time"] = clean_text(data.get("time"))
    data["mentor"] = clean_text(data.get("mentor"))
    data["description"] = clean_text(data.get("description"))
    try:
        registered = int(data.get("registered") or 0)
    except (TypeError, ValueError):
        registered = 0
    data["spots"] = spots
    data["registered"] = max(0, registered)
    data["status"] = clean_text(data.get("status")) or "upcoming"
    event_id = save_event(data)
    return jsonify({"message": "Event saved", "id": event_id})

@admin_bp.route("/api/event/<event_id>", methods=['DELETE'])
def delete_event_admin(event_id):
    if not is_admin():
        return jsonify({"error": "Unauthorized"}), 403
    delete_event(event_id)
    return jsonify({"message": "Event deleted"})
