import os
import json
import sys
import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash

# Add current directory to sys.path to import tools.memory
sys.path.insert(0, os.getcwd())

from tools.memory import (
    get_db_client, create_user, get_user_by_email, verify_user,
    save_to_memory, get_history,
    save_mentor, get_all_mentors, delete_mentor,
    save_event, get_all_events, delete_event,
    save_booking, get_all_bookings,
    save_event_registration, get_all_registrations
)

def test_all_db():
    print("=== Testing All DB Operations ===")
    
    client = get_db_client()
    if client:
        print("MongoDB is available.")
    else:
        print("MongoDB is NOT available. Using JSON fallback.")

    # 1. User Operations
    print("\n[1] Testing User Operations...")
    test_email = f"test_{uuid.uuid4().hex[:6]}@example.com"
    pw_hash = generate_password_hash("password123")
    user_id = create_user("Test User", test_email, pw_hash)
    print(f"Created user: {test_email}, ID: {user_id}")
    
    user = get_user_by_email(test_email)
    print(f"Fetch by email: {'Success' if user else 'Failed'}")
    
    verified = verify_user(test_email, "password123")
    print(f"Verify password: {'Success' if verified else 'Failed'}")

    # 2. Idea (Analysis) Operations
    print("\n[2] Testing Idea (Analysis) Operations...")
    idea_data = {
        "idea_name": "Test Startup",
        "description": "A test startup idea.",
        "target_users": "Testers",
        "analysis": {"score": 90, "summary": "Great idea!"}
    }
    save_to_memory(idea_data, user_id=user_id)
    history = get_history(user_id=user_id)
    print(f"History count for user: {len(history)}")
    found_idea = any(h.get("idea_name") == "Test Startup" for h in history)
    print(f"Idea found in history: {found_idea}")

    # 3. Mentor Operations
    print("\n[3] Testing Mentor Operations...")
    mentor_data = {
        "name": "Test Mentor " + uuid.uuid4().hex[:4],
        "role": "Test Guru",
        "specialty": "Testing",
        "bio": "I test things.",
        "photo": "https://via.placeholder.com/150"
    }
    m_id = save_mentor(mentor_data)
    print(f"Saved mentor: {m_id}")
    mentors = get_all_mentors()
    print(f"Total mentors: {len(mentors)}")
    found_mentor = any(m.get("id") == m_id for m in mentors)
    print(f"Mentor found: {found_mentor}")

    # 4. Event Operations
    print("\n[4] Testing Event Operations...")
    event_data = {
        "title": "Test Event " + uuid.uuid4().hex[:4],
        "date": "2026-06-01",
        "time": "11:00 AM",
        "type": "Webinar",
        "status": "upcoming",
        "spots": 50,
        "registered": 0
    }
    e_id = save_event(event_data)
    print(f"Saved event: {e_id}")
    events = get_all_events()
    print(f"Total events: {len(events)}")
    found_event = any(e.get("id") == e_id for e in events)
    print(f"Event found: {found_event}")

    # 5. Booking Operations
    print("\n[5] Testing Booking Operations...")
    booking_data = {
        "user_id": user_id,
        "user_name": "Test User",
        "user_email": test_email,
        "mentor_id": m_id,
        "mentor_name": mentor_data["name"],
        "topic": "Testing",
        "status": "pending"
    }
    b_id = save_booking(booking_data)
    print(f"Saved booking: {b_id}")
    bookings = get_all_bookings()
    print(f"Total bookings: {len(bookings)}")
    found_booking = any(b.get("id") == b_id for b in bookings)
    print(f"Booking found: {found_booking}")

    # 6. Registration Operations
    print("\n[6] Testing Registration Operations...")
    reg_data = {
        "user_id": user_id,
        "user_name": "Test User",
        "user_email": test_email,
        "event_id": e_id,
        "event_title": event_data["title"],
        "status": "confirmed"
    }
    r_id = save_event_registration(reg_data)
    print(f"Saved registration: {r_id}")
    regs = get_all_registrations()
    print(f"Total registrations: {len(regs)}")
    found_reg = any(r.get("id") == r_id for r in regs)
    print(f"Registration found: {found_reg}")

    # Cleanup (Optional)
    # delete_mentor(m_id)
    # delete_event(e_id)

if __name__ == "__main__":
    test_all_db()
