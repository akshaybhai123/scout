"""
ScoutAI — Chatbot API routes
"""

from flask import Blueprint, request, jsonify
from db.database import SessionLocal, ChatMessage
from chatbot.chatbot_engine import ChatbotEngine

chatbot_bp = Blueprint("chatbot", __name__)
engine = ChatbotEngine()


# --------------------------------------------------------------------------
# POST /api/chatbot/message
# --------------------------------------------------------------------------
@chatbot_bp.route("/chatbot/message", methods=["POST"])
def send_message():
    data = request.get_json(silent=True)
    if not data or "message" not in data:
        return jsonify({"error": "message is required"}), 400

    user_message = data["message"].strip()
    sport = data.get("sport")
    athlete_id = data.get("athlete_id")

    if not user_message:
        return jsonify({"error": "message cannot be empty"}), 400

    # Get chatbot response
    result = engine.get_response(user_message, sport=sport, athlete_id=athlete_id)

    # Save to DB
    db = SessionLocal()
    try:
        # Save user message
        user_msg = ChatMessage(
            athlete_id=athlete_id,
            role="user",
            message=user_message,
            category=result.get("category"),
            sport=sport,
        )
        db.add(user_msg)

        # Save bot response
        bot_msg = ChatMessage(
            athlete_id=athlete_id,
            role="bot",
            message=result["reply"],
            category=result.get("category"),
            sport=sport,
        )
        db.add(bot_msg)
        db.commit()
    finally:
        db.close()

    return jsonify({
        "reply": result["reply"],
        "category": result.get("category"),
        "suggestions": result.get("suggestions", []),
    })


# --------------------------------------------------------------------------
# GET /api/chatbot/history/<athlete_id>
# --------------------------------------------------------------------------
@chatbot_bp.route("/chatbot/history/<int:athlete_id>", methods=["GET"])
def get_chat_history(athlete_id):
    limit = request.args.get("limit", 50, type=int)

    db = SessionLocal()
    try:
        messages = (
            db.query(ChatMessage)
            .filter(ChatMessage.athlete_id == athlete_id)
            .order_by(ChatMessage.created_at.asc())
            .limit(limit)
            .all()
        )

        return jsonify([
            {
                "id": m.id,
                "role": m.role,
                "message": m.message,
                "category": m.category,
                "sport": m.sport,
                "created_at": m.created_at.isoformat(),
            }
            for m in messages
        ])
    finally:
        db.close()


# --------------------------------------------------------------------------
# GET /api/chatbot/sports
# --------------------------------------------------------------------------
@chatbot_bp.route("/chatbot/sports", methods=["GET"])
def get_supported_sports():
    sports = engine.get_supported_sports()
    return jsonify(sports)
