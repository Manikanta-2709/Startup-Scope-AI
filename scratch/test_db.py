import os
import json
import sys

# Add current directory to sys.path to import tools.memory
sys.path.insert(0, os.getcwd())

from tools.memory import get_db_client, save_mentor, get_all_mentors, save_event, get_all_events

def test_db():
    print("Testing DB Connection...")
    client = get_db_client()
    if client:
        print("MongoDB is available.")
        db = client["startupscope"]
        print(f"Collections: {db.list_collection_names()}")
    else:
        print("MongoDB is NOT available. Using JSON fallback.")

    print("\n--- Testing Mentor Operations ---")
    initial_mentors = get_all_mentors()
    print(f"Initial mentor count: {len(initial_mentors)}")

    test_mentor = {
        "name": "Test Mentor",
        "role": "Testing Expert",
        "expertise": ["Debugging", "Testing"],
        "bio": "I am a test mentor.",
        "image": "https://via.placeholder.com/150",
        "rating": 5.0,
        "reviews": 0,
        "availability": "Anytime"
    }
    
    mentor_id = save_mentor(test_mentor)
    print(f"Saved mentor with ID: {mentor_id}")

    updated_mentors = get_all_mentors()
    print(f"Updated mentor count: {len(updated_mentors)}")
    
    found = any(m.get("id") == mentor_id for m in updated_mentors)
    print(f"Mentor found in list: {found}")

    print("\n--- Testing Event Operations ---")
    initial_events = get_all_events()
    print(f"Initial event count: {len(initial_events)}")

    test_event = {
        "title": "Test Event",
        "date": "2026-05-01",
        "time": "10:00 AM",
        "type": "Webinar",
        "status": "upcoming",
        "description": "A test event.",
        "image": "https://via.placeholder.com/150",
        "registered": 0,
        "capacity": 100
    }

    event_id = save_event(test_event)
    print(f"Saved event with ID: {event_id}")

    updated_events = get_all_events()
    print(f"Updated event count: {len(updated_events)}")

    found_event = any(e.get("id") == event_id for e in updated_events)
    print(f"Event found in list: {found_event}")

if __name__ == "__main__":
    # Add current directory to sys.path to import tools.memory
    sys.path.append(os.getcwd())
    test_db()
