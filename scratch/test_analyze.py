import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_analyze():
    print("=== Testing Analyze Route ===")
    
    # 1. Register/Login user
    session = requests.Session()
    user_payload = {
        "name": "Analyze Tester",
        "email": "tester@example.com",
        "password": "password123"
    }
    session.post(f"{BASE_URL}/register", json=user_payload)
    
    # 2. Analyze idea
    print("\n[2] Analyzing Idea...")
    payload = {
        "idea_name": "AI Garden",
        "target_users": "Home owners",
        "description": "An AI that helps you grow vegetables in your backyard."
    }
    res = session.post(f"{BASE_URL}/analyze", json=payload)
    print(f"Status: {res.status_code}")
    if res.status_code == 200:
        data = res.json()
        print(f"Idea Score: {data.get('analysis', {}).get('idea_score')}")
    else:
        print(f"Error: {res.text}")

    # 3. Check history
    print("\n[3] Checking History...")
    res = session.get(f"{BASE_URL}/history")
    history = res.json()
    print(f"History count: {len(history)}")
    found = any(h.get("idea_name") == "AI Garden" for h in history)
    print(f"Idea found in history: {found}")

if __name__ == "__main__":
    test_analyze()
