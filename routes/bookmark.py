from flask import Blueprint, request, jsonify, session
from tools.memory import toggle_bookmark, get_bookmarks

bookmark_bp = Blueprint('bookmark', __name__)

@bookmark_bp.route("/bookmark", methods=['POST'])
def bookmark():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Login required"}), 401
    
    data = request.json
    idea_name = data.get("idea_name")
    if not idea_name:
        return jsonify({"error": "idea_name required"}), 400
    
    result = toggle_bookmark(user_id, idea_name)
    return jsonify(result)

@bookmark_bp.route("/bookmarks", methods=['GET'])
def bookmarks():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Login required"}), 401
    
    items = get_bookmarks(user_id)
    return jsonify(items)
