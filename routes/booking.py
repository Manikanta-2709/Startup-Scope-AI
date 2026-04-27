from flask import Blueprint, request, jsonify, session
from tools.memory import (save_booking, get_bookings_for_user, get_all_bookings,
                          save_event_registration, get_event_registrations, get_all_registrations,
                          get_registrations_for_user, get_mentor_by_id, get_event_by_id,
                          cancel_booking_for_user, reschedule_booking_for_user,
                          cancel_registration_for_user)
from datetime import datetime

booking_bp = Blueprint('booking', __name__)

def _clean_text(value):
    return (value or "").strip()

@booking_bp.route("/book-session", methods=['POST'])
def book_session():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Login required"}), 401
    
    data = request.json or {}
    mentor_id = _clean_text(data.get("mentor_id"))
    required_fields = {
        "topic": "Topic",
        "preferred_date": "Preferred date",
        "preferred_time": "Preferred time",
        "session_format": "Session format",
        "message": "Message",
    }
    missing = [
        label for key, label in required_fields.items()
        if not _clean_text(data.get(key))
    ]
    if not mentor_id:
        missing.insert(0, "Mentor")
    if missing:
        return jsonify({"error": f"Please fill: {', '.join(missing)}."}), 400

    mentor = get_mentor_by_id(mentor_id)
    if not mentor:
        return jsonify({"error": "Selected mentor was not found."}), 404

    booking = {
        "user_id": user_id,
        "user_name": session.get('name', ''),
        "user_email": session.get('email', ''),
        "mentor_id": mentor_id,
        "mentor_name": mentor.get("name", data.get("mentor_name")),
        "topic": _clean_text(data.get("topic")),
        "message": _clean_text(data.get("message")),
        "preferred_date": _clean_text(data.get("preferred_date")),
        "preferred_time": _clean_text(data.get("preferred_time")),
        "session_format": _clean_text(data.get("session_format")),
        "status": "pending",  # pending, approved, rejected
        "created_at": datetime.now().isoformat()
    }
    
    result = save_booking(booking)
    return jsonify({"message": "Booking request submitted!", "booking_id": result})

@booking_bp.route("/register-event", methods=['POST'])
def register_event():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Login required"}), 401
    
    data = request.json or {}
    event_id = data.get("event_id")
    event = get_event_by_id(event_id)
    if not event:
        return jsonify({"error": "Selected event was not found."}), 404
    if event.get("status") != "upcoming":
        return jsonify({"error": "This event is no longer open for registration."}), 409
    if int(event.get("registered", 0)) >= int(event.get("spots", 0)):
        return jsonify({"error": "This event is already full."}), 409

    existing = [
        item for item in get_registrations_for_user(user_id)
        if item.get("event_id") == event_id and item.get("status") != "cancelled"
    ]
    if existing:
        return jsonify({"error": "You are already registered for this event."}), 409

    registration = {
        "user_id": user_id,
        "user_name": session.get('name', ''),
        "user_email": session.get('email', ''),
        "event_id": event_id,
        "event_title": event.get("title", data.get("event_title")),
        "status": "confirmed",
        "created_at": datetime.now().isoformat()
    }
    
    result = save_event_registration(registration)
    return jsonify({"message": "Registration submitted!", "reg_id": result})

@booking_bp.route("/my-bookings", methods=['GET'])
@booking_bp.route("/api/my-bookings", methods=['GET'])
def my_bookings():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Login required"}), 401
    return jsonify(get_bookings_for_user(user_id))

@booking_bp.route("/my-registrations", methods=['GET'])
@booking_bp.route("/api/my-registrations", methods=['GET'])
def my_registrations():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Login required"}), 401
    return jsonify(get_registrations_for_user(user_id))


@booking_bp.route("/booking/<booking_id>/cancel", methods=['POST'])
def cancel_booking(booking_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Login required"}), 401

    if not cancel_booking_for_user(user_id, booking_id):
        return jsonify({"error": "Booking not found."}), 404
    return jsonify({"message": "Booking cancelled."})


@booking_bp.route("/booking/<booking_id>/reschedule", methods=['POST'])
def reschedule_booking(booking_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Login required"}), 401

    data = request.json or {}
    updated = reschedule_booking_for_user(user_id, booking_id, data)
    if not updated:
        return jsonify({"error": "Booking not found or no updates were provided."}), 400
    return jsonify({"message": "Reschedule request sent."})


@booking_bp.route("/registration/<reg_id>/cancel", methods=['POST'])
def cancel_registration(reg_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Login required"}), 401

    if not cancel_registration_for_user(user_id, reg_id):
        return jsonify({"error": "Registration not found."}), 404
    return jsonify({"message": "Registration cancelled."})
