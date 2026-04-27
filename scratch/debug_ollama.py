import json
import requests

prompt = "Analyze a startup idea: 'Smart Honeybee tracking using AI'. Return ONLY a JSON object with keys: strengths, weaknesses, market_gaps, improvements, idea_score, confidence."

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "llama3",
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }
)
print("RAW RESPONSE FROM OLLAMA:")
print(response.json().get('response'))
