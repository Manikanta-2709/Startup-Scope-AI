import requests
import json
import uuid

BASE_URL = "http://127.0.0.1:8000"

def test_api():
    print("=== Testing API Routes ===")
    
    # 1. Login as admin
    print("\n[1] Admin Login...")
    login_payload = {
        "email": "admin@startupscope.ai",
        "password": "admin123"
    }
    session = requests.Session()
    res = session.post(f"{BASE_URL}/admin/login", json=login_payload)
    if res.status_code != 200:
        print(f"Admin login failed: {res.text}")
        return
    print("Admin login successful.")

    # 2. Add a mentor
    print("\n[2] Adding Mentor...")
    mentor_payload = {
        "name": "API Test Mentor",
        "role": "Consultant",
        "specialty": "Strategy",
        "bio": "Testing via API",
        "photo": "https://via.placeholder.com/150"
    }
    res = session.post(f"{BASE_URL}/admin/api/mentor", json=mentor_payload)
    print(f"Add Mentor Status: {res.status_code}")
    print(f"Response: {res.text}")
    mentor_id = res.json().get("id")

    # 3. Add an event
    print("\n[3] Adding Event...")
    event_payload = {
        "title": "API Test Event",
        "type": "Workshop",
        "date": "2026-07-01",
        "time": "2:00 PM",
        "mentor": "API Test Mentor",
        "spots": 20,
        "description": "Testing via API",
        "status": "upcoming"
    }
    res = session.post(f"{BASE_URL}/admin/api/event", json=event_payload)
    print(f"Add Event Status: {res.status_code}")
    print(f"Response: {res.text}")
    event_id = res.json().get("id")

    # 4. Verify in Stats
    print("\n[4] Checking Stats...")
    res = session.get(f"{BASE_URL}/admin/api/stats")
    print(f"Stats: {res.text}")

    # 5. User Registration
    print("\n[5] User Registration...")
    user_email = f"user_{uuid.uuid4().hex[:6]}@test.com"
    user_payload = {
        "name": "API Test User",
        "email": user_email,
        "password": "password123"
    }
    user_session = requests.Session()
    res = user_session.post(f"{BASE_URL}/register", json=user_payload)
    print(f"User Register Status: {res.status_code}")
    
    # 6. Book session
    print("\n[6] Booking Session...")
    booking_payload = {
        "mentor_id": mentor_id,
        "topic": "API Testing",
        "preferred_date": "2026-07-05",
        "preferred_time": "10:00 AM"
    }
    res = user_session.post(f"{BASE_URL}/book-session", json=booking_payload)
    print(f"Booking Status: {res.status_code}")
    print(f"Response: {res.text}")

    # 7. Register for event
    print("\n[7] Registering for Event...")
    reg_payload = {
        "event_id": event_id
    }
    res = user_session.post(f"{BASE_URL}/register-event", json=reg_payload)
    print(f"Event Reg Status: {res.status_code}")
    print(f"Response: {res.text}")

    # 8. Verify bookings in admin
    print("\n[8] Verifying in Admin Dashboard...")
    res = session.get(f"{BASE_URL}/admin/api/bookings")
    bookings = res.json()
    found_b = any(b.get("user_email") == user_email for b in bookings)
    print(f"Booking found in admin: {found_b}")

    res = session.get(f"{BASE_URL}/admin/api/registrations")
    regs = res.json()
    found_r = any(r.get("user_email") == user_email for r in regs)
    print(f"Registration found in admin: {found_r}")

if __name__ == "__main__":
    test_api()
