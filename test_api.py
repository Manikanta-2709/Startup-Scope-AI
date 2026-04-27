import requests
import json

cases = [
    {
        "idea_name": "AI app for regional SSC prep",
        "target_users": "Tier-2/3 students",
        "description": "AI app for SSC exam preparation in regional languages with daily mock tests and voice explanations"
    },
    {
        "idea_name": "Healthcare Provider Assistant",
        "target_users": "Doctors and Medical Clinics",
        "description": "AI assistant for doctors to summarize patient history and automate appointment scheduling"
    },
    {
        "idea_name": "Crop Disease Detector",
        "target_users": "Farmers",
        "description": "Mobile app for farmers to detect crop diseases using image recognition"
    }
]

for idx, case in enumerate(cases):
    print(f"\n==================== TEST CASE {idx+1} ====================")
    try:
        r = requests.post('http://localhost:8000/analyze', json=case)
        if r.status_code == 200:
            print(json.dumps(r.json(), indent=2))
        else:
            print(f"Error {r.status_code}: {r.text}")
    except Exception as e:
        print(f"Request failed: {e}")
