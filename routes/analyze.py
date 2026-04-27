from flask import Blueprint, request, jsonify, session
from tools.search import search_competitors
from tools.analyzer import analyze_startup
from tools.memory import save_to_memory, get_history
from datetime import datetime

analyze_bp = Blueprint('analyze', __name__)

@analyze_bp.route("/analyze", methods=['POST'])
def analyze_idea():
    try:
        user_id = session.get('user_id')
        data = request.json
        idea_name = data.get("idea_name")
        description = data.get("description")
        target_users = data.get("target_users")

        if not all([idea_name, description, target_users]):
            return jsonify({"error": "Missing required fields"}), 400

        # 1. Search for competitors
        competitors = search_competitors(idea_name, description)
        
        # 2. Analyze using LLM (V2 logic)
        analysis = analyze_startup(data, competitors)
        
        # 3. Save to MongoDB/Memory
        record = {
            "idea_name": idea_name,
            "description": description,
            "target_users": target_users,
            "analysis": analysis,
            "created_at": datetime.now()
        }
        
        save_to_memory(record, user_id=user_id)
        
        return jsonify(record)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analyze_bp.route("/history", methods=['GET'])
def history():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"error": "Authentication required to view history", "needs_auth": True}), 401
            
        h = get_history(user_id=user_id)
        return jsonify(h)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analyze_bp.route("/compare/<idea_name>", methods=['GET'])
def compare_idea(idea_name):
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"error": "Authentication required"}), 401
            
        h = get_history(user_id=user_id)
        # Filter all versions of this idea, sorted chronologically (oldest to newest)
        versions = [v for v in h if v.get("idea_name") == idea_name]
        versions.sort(key=lambda x: x.get("created_at", ""))
        
        return jsonify(versions)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
