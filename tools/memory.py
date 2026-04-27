import os
import json
import uuid
import secrets
from pymongo import MongoClient
from datetime import datetime, timedelta
from dotenv import load_dotenv
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DATABASE_NAME = "startupscope"

# Collection Names
COLLECTION_NAME = "ideas"
USERS_COLLECTION = "users"
ADMINS_COLLECTION = "admins"
CHAT_COLLECTION = "chats"
BOOKINGS_COLLECTION = "bookings"
REGISTRATIONS_COLLECTION = "registrations"
MENTORS_COLLECTION = "mentors"
EVENTS_COLLECTION = "events"
RESET_TOKENS_COLLECTION = "password_resets"

# JSON Fallback Files
JSON_FILE = "data/history.json"
USERS_JSON_FILE = "data/users.json"
RESET_JSON_FILE = "data/password_resets.json"
CHAT_JSON_FILE = "data/chats.json"
BOOKINGS_JSON = "data/bookings.json"
REGISTRATIONS_JSON = "data/registrations.json"
MENTORS_JSON = "static/data/mentors.json"
EVENTS_JSON = "static/data/events.json"
ADMINS_JSON = "data/admins.json"

def get_db_client():
    """
    Attempts to connect to MongoDB. Returns None if connection fails.
    """
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
        client.server_info()
        return client
    except Exception as e:
        print(f"MongoDB not available: {e}. Falling back to JSON.")
        return None

def _now_iso():
    return datetime.now().isoformat()

def _ensure_data_dir():
    os.makedirs("data", exist_ok=True)

def _find_json_record(items, key, value):
    for item in items:
        if item.get(key) == value:
            return item
    return None

# --- AUTHENTICATION MEMORY ---

def create_user(name: str, email: str, password_hash: str):
    """
    Creates a new user. Returns user_id if successful, None if email exists.
    """
    user_id = str(uuid.uuid4())
    user_doc = {
        "id": user_id,
        "name": name,
        "email": email,
        "password": password_hash,
        "created_at": _now_iso()
    }
    
    client = get_db_client()
    if client:
        db = client[DATABASE_NAME]
        users_col = db[USERS_COLLECTION]
        if users_col.find_one({"email": email}):
            return None
        users_col.insert_one(user_doc)
        return user_id
    else:
        # Fallback JSON auth logic
        _ensure_data_dir()
        users = []
        if os.path.exists(USERS_JSON_FILE):
            with open(USERS_JSON_FILE, "r") as f:
                try:
                    users = json.load(f)
                except:
                    pass
        if any(u.get("email") == email for u in users):
            return None
        users.append(user_doc)
        with open(USERS_JSON_FILE, "w") as f:
            json.dump(users, f, indent=4)
        return user_id

def get_user_by_id(user_id: str):
    client = get_db_client()
    if client:
        db = client[DATABASE_NAME]
        user = db[USERS_COLLECTION].find_one({"id": user_id}, {"_id": 0})
        return user

    users = _load_json(USERS_JSON_FILE)
    return _find_json_record(users, "id", user_id)

def get_user_by_email(email: str):
    normalized_email = (email or "").strip().lower()
    client = get_db_client()
    if client:
        db = client[DATABASE_NAME]
        user = db[USERS_COLLECTION].find_one({"email": normalized_email}, {"_id": 0})
        return user

    users = _load_json(USERS_JSON_FILE)
    return _find_json_record(users, "email", normalized_email)

def verify_user(email: str, password: str):
    """
    Verifies credentials returning the user object or None.
    """
    client = get_db_client()
    if client:
        db = client[DATABASE_NAME]
        user = db[USERS_COLLECTION].find_one({"email": email})
        if user and check_password_hash(user["password"], password):
            return {"id": user["id"], "name": user.get("name", "User"), "email": user["email"]}
    else:
        # Fallback JSON logic
        if os.path.exists(USERS_JSON_FILE):
            with open(USERS_JSON_FILE, "r") as f:
                try:
                    users = json.load(f)
                    for u in users:
                        if u.get("email") == email and check_password_hash(u["password"], password):
                            return {"id": u["id"], "name": u.get("name", "User"), "email": u["email"]}
                except:
                    pass
    return None

def update_user_profile(user_id: str, name: str, email: str):
    name = (name or "").strip()
    email = (email or "").strip().lower()

    if not name or not email:
        return False, "Name and email are required."

    client = get_db_client()
    if client:
        db = client[DATABASE_NAME]
        existing = db[USERS_COLLECTION].find_one({"email": email, "id": {"$ne": user_id}})
        if existing:
            return False, "Email already registered."

        result = db[USERS_COLLECTION].update_one(
            {"id": user_id},
            {"$set": {"name": name, "email": email, "updated_at": _now_iso()}}
        )
        if result.matched_count == 0:
            return False, "User not found."
    else:
        users = _load_json(USERS_JSON_FILE)
        current_user = _find_json_record(users, "id", user_id)
        if not current_user:
            return False, "User not found."
        if any(user.get("email") == email and user.get("id") != user_id for user in users):
            return False, "Email already registered."

        current_user["name"] = name
        current_user["email"] = email
        current_user["updated_at"] = _now_iso()
        _save_json(USERS_JSON_FILE, users)

    return True, {"id": user_id, "name": name, "email": email}

def update_user_password(user_id: str, current_password: str, new_password: str):
    user = get_user_by_id(user_id)
    if not user:
        return False, "User not found."

    if not check_password_hash(user.get("password", ""), current_password or ""):
        return False, "Current password is incorrect."

    new_hash = generate_password_hash(new_password)
    client = get_db_client()
    if client:
        db = client[DATABASE_NAME]
        db[USERS_COLLECTION].update_one(
            {"id": user_id},
            {"$set": {"password": new_hash, "updated_at": _now_iso()}}
        )
    else:
        users = _load_json(USERS_JSON_FILE)
        current_user = _find_json_record(users, "id", user_id)
        if not current_user:
            return False, "User not found."
        current_user["password"] = new_hash
        current_user["updated_at"] = _now_iso()
        _save_json(USERS_JSON_FILE, users)

    return True, "Password updated successfully."

def create_password_reset_token(email: str):
    user = get_user_by_email(email)
    if not user:
        return None

    token = secrets.token_urlsafe(32)
    record = {
        "id": str(uuid.uuid4()),
        "user_id": user["id"],
        "email": user["email"],
        "token": token,
        "used": False,
        "created_at": _now_iso(),
        "expires_at": (datetime.now() + timedelta(hours=1)).isoformat()
    }

    client = get_db_client()
    if client:
        db = client[DATABASE_NAME]
        db[RESET_TOKENS_COLLECTION].insert_one(record)
    else:
        tokens = _load_json(RESET_JSON_FILE)
        tokens.append(record)
        _save_json(RESET_JSON_FILE, tokens)

    return token

def get_password_reset_request(token: str):
    client = get_db_client()
    if client:
        db = client[DATABASE_NAME]
        record = db[RESET_TOKENS_COLLECTION].find_one({"token": token}, {"_id": 0})
    else:
        tokens = _load_json(RESET_JSON_FILE)
        record = _find_json_record(tokens, "token", token)

    if not record or record.get("used"):
        return None

    try:
        if datetime.fromisoformat(record["expires_at"]) < datetime.now():
            return None
    except Exception:
        return None

    return record

def reset_user_password_with_token(token: str, new_password: str):
    record = get_password_reset_request(token)
    if not record:
        return False, "Reset link is invalid or has expired."

    new_hash = generate_password_hash(new_password)
    client = get_db_client()
    if client:
        db = client[DATABASE_NAME]
        db[USERS_COLLECTION].update_one(
            {"id": record["user_id"]},
            {"$set": {"password": new_hash, "updated_at": _now_iso()}}
        )
        db[RESET_TOKENS_COLLECTION].update_one(
            {"token": token},
            {"$set": {"used": True, "used_at": _now_iso()}}
        )
    else:
        users = _load_json(USERS_JSON_FILE)
        current_user = _find_json_record(users, "id", record["user_id"])
        if not current_user:
            return False, "User not found."
        current_user["password"] = new_hash
        current_user["updated_at"] = _now_iso()
        _save_json(USERS_JSON_FILE, users)

        tokens = _load_json(RESET_JSON_FILE)
        reset_record = _find_json_record(tokens, "token", token)
        if reset_record:
            reset_record["used"] = True
            reset_record["used_at"] = _now_iso()
            _save_json(RESET_JSON_FILE, tokens)

    return True, "Password reset successfully."

# --- HISTORY MEMORY ---

def save_to_memory(data: dict, user_id: str = None):
    """
    Stores analysis ensuring isolation by user_id.
    """
    if isinstance(data.get("created_at"), datetime):
        data["created_at"] = data["created_at"].isoformat()
    elif "created_at" not in data:
        data["created_at"] = datetime.now().isoformat()
        
    data["user_id"] = user_id

    client = get_db_client()
    if client:
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        doc = data.copy()
        try:
            doc["created_at"] = datetime.fromisoformat(doc["created_at"])
        except:
            pass
        result = collection.insert_one(doc)
        print(f"Saved to MongoDB: {result.inserted_id}")
        return str(result.inserted_id)
    else:
        _ensure_data_dir()
        history = []
        if os.path.exists(JSON_FILE):
            with open(JSON_FILE, "r") as f:
                try:
                    history = json.load(f)
                except:
                    history = []
        
        history.append(data)
        with open(JSON_FILE, "w") as f:
            json.dump(history, f, indent=4)
        print("Saved to history.json (Fallback)")
        return "json_save"

def get_history(user_id: str = None):
    """
    Retrieves isolated history for the specific user.
    """
    client = get_db_client()
    if client:
        db = client[DATABASE_NAME]
        query = {"user_id": user_id}
        cursor = db[COLLECTION_NAME].find(query, {"_id": 0})
        history = list(cursor)
        for h in history:
            if isinstance(h.get("created_at"), datetime):
                h["created_at"] = h["created_at"].isoformat()
        return history
    else:
        if os.path.exists(JSON_FILE):
            with open(JSON_FILE, "r") as f:
                try:
                    history = json.load(f)
                    return [h for h in history if h.get("user_id") == user_id]
                except:
                    return []
        return []

# --- BOOKMARK MEMORY ---

def toggle_bookmark(user_id: str, idea_name: str):
    """Toggle bookmark status on an idea by name."""
    client = get_db_client()
    if client:
        db = client[DATABASE_NAME]
        col = db[COLLECTION_NAME]
        doc = col.find_one({"user_id": user_id, "idea_name": idea_name})
        if doc:
            new_state = not doc.get("bookmarked", False)
            col.update_one({"_id": doc["_id"]}, {"$set": {"bookmarked": new_state}})
            return {"bookmarked": new_state, "idea_name": idea_name}
    else:
        if os.path.exists(JSON_FILE):
            with open(JSON_FILE, "r") as f:
                history = json.load(f)
            for h in history:
                if h.get("user_id") == user_id and h.get("idea_name") == idea_name:
                    h["bookmarked"] = not h.get("bookmarked", False)
                    with open(JSON_FILE, "w") as f:
                        json.dump(history, f, indent=4)
                    return {"bookmarked": h["bookmarked"], "idea_name": idea_name}
    return {"bookmarked": False, "idea_name": idea_name}

def get_bookmarks(user_id: str):
    """Get all bookmarked ideas for a user."""
    client = get_db_client()
    if client:
        db = client[DATABASE_NAME]
        cursor = db[COLLECTION_NAME].find({"user_id": user_id, "bookmarked": True}, {"_id": 0})
        results = list(cursor)
        for r in results:
            if isinstance(r.get("created_at"), datetime):
                r["created_at"] = r["created_at"].isoformat()
        return results
    else:
        if os.path.exists(JSON_FILE):
            with open(JSON_FILE, "r") as f:
                history = json.load(f)
            return [h for h in history if h.get("user_id") == user_id and h.get("bookmarked")]
        return []

# --- CHAT MEMORY ---

CHAT_COLLECTION = "chats"
CHAT_JSON_FILE = "data/chats.json"

def save_chat_message(user_id: str, idea_name: str, user_msg: str, ai_reply: str):
    """Save a chat exchange to the database."""
    doc = {
        "user_id": user_id,
        "idea_name": idea_name,
        "user_message": user_msg,
        "ai_reply": ai_reply,
        "created_at": _now_iso()
    }
    client = get_db_client()
    if client:
        db = client[DATABASE_NAME]
        db[CHAT_COLLECTION].insert_one(doc)
    else:
        _ensure_data_dir()
        chats = []
        if os.path.exists(CHAT_JSON_FILE):
            with open(CHAT_JSON_FILE, "r") as f:
                try: chats = json.load(f)
                except: pass
        chats.append(doc)
        with open(CHAT_JSON_FILE, "w") as f:
            json.dump(chats, f, indent=4)

# --- BOOKING MEMORY ---

BOOKINGS_COLLECTION = "bookings"
BOOKINGS_JSON = "data/bookings.json"
REGISTRATIONS_COLLECTION = "registrations"
REGISTRATIONS_JSON = "data/registrations.json"

def _load_json(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            try: return json.load(f)
            except: return []
    return []

def _save_json(path, data):
    # Ensure the directory for the file exists
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

def get_mentor_by_id(mentor_id: str):
    mentors = get_all_mentors()
    return next((mentor for mentor in mentors if mentor.get("id") == mentor_id), None)

def get_event_by_id(event_id: str):
    events = get_all_events()
    return next((event for event in events if event.get("id") == event_id), None)

def save_booking(booking: dict):
    booking_id = str(uuid.uuid4())
    booking["id"] = booking_id
    client = get_db_client()
    if client:
        db = client[DATABASE_NAME]
        db[BOOKINGS_COLLECTION].insert_one(booking.copy())
    else:
        items = _load_json(BOOKINGS_JSON)
        items.append(booking)
        _save_json(BOOKINGS_JSON, items)
    return booking_id

def get_bookings_for_user(user_id: str):
    client = get_db_client()
    if client:
        db = client[DATABASE_NAME]
        return list(db[BOOKINGS_COLLECTION].find({"user_id": user_id}, {"_id": 0}))
    return [b for b in _load_json(BOOKINGS_JSON) if b.get("user_id") == user_id]

def get_all_bookings():
    client = get_db_client()
    if client:
        db = client[DATABASE_NAME]
        return list(db[BOOKINGS_COLLECTION].find({}, {"_id": 0}))
    return _load_json(BOOKINGS_JSON)

def update_booking_status(booking_id: str, status: str):
    client = get_db_client()
    if client:
        db = client[DATABASE_NAME]
        db[BOOKINGS_COLLECTION].update_one({"id": booking_id}, {"$set": {"status": status}})
    else:
        items = _load_json(BOOKINGS_JSON)
        for item in items:
            if item.get("id") == booking_id:
                item["status"] = status
                item["updated_at"] = _now_iso()
        _save_json(BOOKINGS_JSON, items)

def cancel_booking_for_user(user_id: str, booking_id: str):
    client = get_db_client()
    if client:
        db = client[DATABASE_NAME]
        result = db[BOOKINGS_COLLECTION].update_one(
            {"id": booking_id, "user_id": user_id},
            {"$set": {"status": "cancelled", "updated_at": _now_iso()}}
        )
        return result.matched_count > 0

    items = _load_json(BOOKINGS_JSON)
    booking = next((item for item in items if item.get("id") == booking_id and item.get("user_id") == user_id), None)
    if not booking:
        return False
    booking["status"] = "cancelled"
    booking["updated_at"] = _now_iso()
    _save_json(BOOKINGS_JSON, items)
    return True

def reschedule_booking_for_user(user_id: str, booking_id: str, updates: dict):
    allowed_fields = {"topic", "message", "preferred_date", "preferred_time", "session_format"}
    clean_updates = {
        key: value for key, value in updates.items()
        if key in allowed_fields and value not in (None, "")
    }
    if not clean_updates:
        return False

    clean_updates["status"] = "reschedule_requested"
    clean_updates["updated_at"] = _now_iso()

    client = get_db_client()
    if client:
        db = client[DATABASE_NAME]
        result = db[BOOKINGS_COLLECTION].update_one(
            {"id": booking_id, "user_id": user_id},
            {"$set": clean_updates}
        )
        return result.matched_count > 0

    items = _load_json(BOOKINGS_JSON)
    booking = next((item for item in items if item.get("id") == booking_id and item.get("user_id") == user_id), None)
    if not booking:
        return False
    booking.update(clean_updates)
    _save_json(BOOKINGS_JSON, items)
    return True

def save_event_registration(reg: dict):
    reg_id = str(uuid.uuid4())
    reg["id"] = reg_id
    client = get_db_client()
    if client:
        db = client[DATABASE_NAME]
        db[REGISTRATIONS_COLLECTION].insert_one(reg.copy())
        # Update event registered count
        db[EVENTS_COLLECTION].update_one({"id": reg["event_id"]}, {"$inc": {"registered": 1}})
    else:
        items = _load_json(REGISTRATIONS_JSON)
        items.append(reg)
        _save_json(REGISTRATIONS_JSON, items)
        
        # Update event registered count for static json fallback
        events = _load_json(EVENTS_JSON)
        for ev in events:
            if ev.get("id") == reg["event_id"]:
                ev["registered"] = ev.get("registered", 0) + 1
        _save_json(EVENTS_JSON, events)
        
    return reg_id

def get_event_registrations(event_id: str = None):
    client = get_db_client()
    if client:
        db = client[DATABASE_NAME]
        query = {"event_id": event_id} if event_id else {}
        return list(db[REGISTRATIONS_COLLECTION].find(query, {"_id": 0}))
    items = _load_json(REGISTRATIONS_JSON)
    if event_id:
        return [r for r in items if r.get("event_id") == event_id]
    return items

def get_registrations_for_user(user_id: str):
    client = get_db_client()
    if client:
        db = client[DATABASE_NAME]
        return list(db[REGISTRATIONS_COLLECTION].find({"user_id": user_id}, {"_id": 0}))
    return [r for r in _load_json(REGISTRATIONS_JSON) if r.get("user_id") == user_id]

def get_all_registrations():
    client = get_db_client()
    if client:
        db = client[DATABASE_NAME]
        return list(db[REGISTRATIONS_COLLECTION].find({}, {"_id": 0}))
    return _load_json(REGISTRATIONS_JSON)

def update_registration_status(reg_id: str, status: str):
    client = get_db_client()
    if client:
        db = client[DATABASE_NAME]
        db[REGISTRATIONS_COLLECTION].update_one({"id": reg_id}, {"$set": {"status": status}})
    else:
        items = _load_json(REGISTRATIONS_JSON)
        for item in items:
            if item.get("id") == reg_id:
                item["status"] = status
                item["updated_at"] = _now_iso()
        _save_json(REGISTRATIONS_JSON, items)

def cancel_registration_for_user(user_id: str, reg_id: str):
    client = get_db_client()
    if client:
        db = client[DATABASE_NAME]
        registration = db[REGISTRATIONS_COLLECTION].find_one({"id": reg_id, "user_id": user_id})
        if not registration or registration.get("status") == "cancelled":
            return False
        db[REGISTRATIONS_COLLECTION].update_one(
            {"id": reg_id, "user_id": user_id},
            {"$set": {"status": "cancelled", "updated_at": _now_iso()}}
        )
        db[EVENTS_COLLECTION].update_one({"id": registration.get("event_id")}, {"$inc": {"registered": -1}})
        return True

    items = _load_json(REGISTRATIONS_JSON)
    registration = next((item for item in items if item.get("id") == reg_id and item.get("user_id") == user_id), None)
    if not registration or registration.get("status") == "cancelled":
        return False

    registration["status"] = "cancelled"
    registration["updated_at"] = _now_iso()
    _save_json(REGISTRATIONS_JSON, items)

    events = _load_json(EVENTS_JSON)
    event = _find_json_record(events, "id", registration.get("event_id"))
    if event:
        event["registered"] = max(0, int(event.get("registered", 0)) - 1)
        _save_json(EVENTS_JSON, events)
    return True

# --- ADMIN MEMORY ---

def get_all_users():
    client = get_db_client()
    if client:
        db = client[DATABASE_NAME]
        return list(db[USERS_COLLECTION].find({}, {"_id": 0}))
    return _load_json(USERS_JSON_FILE)

def seed_admin(name="Admin", email="admin@startupscope.ai", password="admin123"):
    """Seed an admin user if one doesn't exist."""
    client = get_db_client()
    if client:
        db = client[DATABASE_NAME]
        if not db[ADMINS_COLLECTION].find_one({"email": email}):
            db[ADMINS_COLLECTION].insert_one({
                "id": str(uuid.uuid4()),
                "name": name,
                "email": email,
                "password": generate_password_hash(password),
                "created_at": _now_iso()
            })
            print(f"Admin seeded to MongoDB: {email}")
    else:
        admins = _load_json(ADMINS_JSON)
        if not any(a.get("email") == email for a in admins):
            admins.append({
                "id": str(uuid.uuid4()),
                "name": name,
                "email": email,
                "password": generate_password_hash(password),
                "created_at": _now_iso()
            })
            _save_json(ADMINS_JSON, admins)
            print(f"Admin seeded to JSON: {email}")

# --- MENTORS MEMORY ---

def get_all_mentors():
    client = get_db_client()
    if client:
        db = client[DATABASE_NAME]
        if db[MENTORS_COLLECTION].count_documents({}) == 0:
            static_mentors = _load_json(MENTORS_JSON)
            if static_mentors:
                db[MENTORS_COLLECTION].insert_many(static_mentors)
        return list(db[MENTORS_COLLECTION].find({}, {"_id": 0}))
    return _load_json(MENTORS_JSON)

def save_mentor(mentor: dict):
    if "id" not in mentor:
        mentor["id"] = str(uuid.uuid4())
    client = get_db_client()
    if client:
        db = client[DATABASE_NAME]
        db[MENTORS_COLLECTION].update_one({"id": mentor["id"]}, {"$set": mentor}, upsert=True)
    else:
        mentors = _load_json(MENTORS_JSON)
        existing = _find_json_record(mentors, "id", mentor["id"])
        if existing:
            existing.update(mentor)
        else:
            mentors.append(mentor)
        _save_json(MENTORS_JSON, mentors)
    return mentor["id"]

def delete_mentor(mentor_id: str):
    client = get_db_client()
    if client:
        db = client[DATABASE_NAME]
        db[MENTORS_COLLECTION].delete_one({"id": mentor_id})
    else:
        mentors = [mentor for mentor in _load_json(MENTORS_JSON) if mentor.get("id") != mentor_id]
        _save_json(MENTORS_JSON, mentors)

# --- EVENTS MEMORY ---

def get_all_events():
    client = get_db_client()
    if client:
        db = client[DATABASE_NAME]
        if db[EVENTS_COLLECTION].count_documents({}) == 0:
            static_events = _load_json(EVENTS_JSON)
            if static_events:
                db[EVENTS_COLLECTION].insert_many(static_events)
        return list(db[EVENTS_COLLECTION].find({}, {"_id": 0}))
    return _load_json(EVENTS_JSON)

def save_event(event: dict):
    if "id" not in event:
        event["id"] = str(uuid.uuid4())
    client = get_db_client()
    if client:
        db = client[DATABASE_NAME]
        db[EVENTS_COLLECTION].update_one({"id": event["id"]}, {"$set": event}, upsert=True)
    else:
        events = _load_json(EVENTS_JSON)
        existing = _find_json_record(events, "id", event["id"])
        if existing:
            existing.update(event)
        else:
            events.append(event)
        _save_json(EVENTS_JSON, events)
    return event["id"]

def delete_event(event_id: str):
    client = get_db_client()
    if client:
        db = client[DATABASE_NAME]
        db[EVENTS_COLLECTION].delete_one({"id": event_id})
    else:
        events = [event for event in _load_json(EVENTS_JSON) if event.get("id") != event_id]
        _save_json(EVENTS_JSON, events)
