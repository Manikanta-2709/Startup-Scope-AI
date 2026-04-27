import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv

# Add current directory to sys.path to import tools.memory
sys.path.insert(0, os.getcwd())

from tools.memory import get_db_client, DATABASE_NAME

def check_db_health():
    print("=== Database Health Check ===")
    
    client = get_db_client()
    if not client:
        print("CRITICAL: MongoDB is not accessible.")
        # Check if JSON fallback files exist
        print("\nChecking JSON Fallback Files:")
        files = [
            "data/users.json",
            "data/history.json",
            "data/bookings.json",
            "data/registrations.json",
            "static/data/mentors.json",
            "static/data/events.json"
        ]
        for f in files:
            exists = os.path.exists(f)
            size = os.path.getsize(f) if exists else 0
            print(f"- {f}: {'Exists' if exists else 'Missing'} ({size} bytes)")
        return

    print("MongoDB is CONNECTED.")
    db = client[DATABASE_NAME]
    
    collections = [
        "users", "ideas", "mentors", "events", "bookings", "registrations", "admins"
    ]
    
    print("\nCollection Statistics:")
    for col_name in collections:
        count = db[col_name].count_documents({})
        print(f"- {col_name}: {count} records")
        
        if count > 0:
            sample = db[col_name].find_one()
            # Print keys except _id
            keys = [k for k in sample.keys() if k != "_id"]
            print(f"  Sample schema: {keys}")

if __name__ == "__main__":
    check_db_health()
