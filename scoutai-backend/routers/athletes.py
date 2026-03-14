"""
ScoutAI — Athlete CRUD endpoints
"""

from flask import Blueprint, request, jsonify
from db.database import SessionLocal, Athlete, AnalysisJob, AnalysisResult, Report, ChatMessage

athletes_bp = Blueprint("athletes", __name__)


# --------------------------------------------------------------------------
# POST /api/athletes/
# --------------------------------------------------------------------------
@athletes_bp.route("/athletes/", methods=["POST"])
def create_athlete():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    name = data.get("name")
    sport = data.get("sport")

    if not name or not sport:
        return jsonify({"error": "name and sport are required"}), 400

    db = SessionLocal()
    try:
        athlete = Athlete(
            name=name,
            sport=sport,
            age=data.get("age"),
            region=data.get("region"),
        )
        db.add(athlete)
        db.commit()
        db.refresh(athlete)

        return jsonify({
            "id": athlete.id,
            "name": athlete.name,
            "sport": athlete.sport,
            "age": athlete.age,
            "region": athlete.region,
            "created_at": athlete.created_at.isoformat(),
        }), 201
    finally:
        db.close()


# --------------------------------------------------------------------------
# GET /api/athletes/
# --------------------------------------------------------------------------
@athletes_bp.route("/athletes/", methods=["GET"])
def list_athletes():
    sport = request.args.get("sport")
    region = request.args.get("region")

    db = SessionLocal()
    try:
        query = db.query(Athlete)
        if sport:
            query = query.filter(Athlete.sport == sport)
        if region:
            query = query.filter(Athlete.region == region)

        athletes = query.order_by(Athlete.created_at.desc()).all()
        return jsonify([
            {
                "id": a.id,
                "name": a.name,
                "sport": a.sport,
                "age": a.age,
                "region": a.region,
                "created_at": a.created_at.isoformat(),
            }
            for a in athletes
        ])
    finally:
        db.close()


# --------------------------------------------------------------------------
# GET /api/athletes/<id>
# --------------------------------------------------------------------------
@athletes_bp.route("/athletes/<int:athlete_id>", methods=["GET"])
def get_athlete(athlete_id):
    db = SessionLocal()
    try:
        athlete = db.query(Athlete).filter(Athlete.id == athlete_id).first()
        if not athlete:
            return jsonify({"error": "Athlete not found"}), 404

        return jsonify({
            "id": athlete.id,
            "name": athlete.name,
            "sport": athlete.sport,
            "age": athlete.age,
            "region": athlete.region,
            "created_at": athlete.created_at.isoformat(),
        })
    finally:
        db.close()


# --------------------------------------------------------------------------
# DELETE /api/athletes/<id>
# --------------------------------------------------------------------------
@athletes_bp.route("/athletes/<int:athlete_id>", methods=["DELETE"])
def delete_athlete(athlete_id):
    db = SessionLocal()
    try:
        athlete = db.query(Athlete).filter(Athlete.id == athlete_id).first()
        if not athlete:
            return jsonify({"error": "Athlete not found"}), 404

        db.delete(athlete)
        db.commit()
        return jsonify({"message": f"Athlete {athlete_id} deleted successfully"}), 200
    finally:
        db.close()


# --------------------------------------------------------------------------
# GET /api/athletes/<id>/history
# --------------------------------------------------------------------------
@athletes_bp.route("/athletes/<int:athlete_id>/history", methods=["GET"])
def get_athlete_history(athlete_id):
    import json

    db = SessionLocal()
    try:
        athlete = db.query(Athlete).filter(Athlete.id == athlete_id).first()
        if not athlete:
            return jsonify({"error": "Athlete not found"}), 404

        jobs = (
            db.query(AnalysisJob)
            .filter(AnalysisJob.athlete_id == athlete_id)
            .order_by(AnalysisJob.created_at.desc())
            .all()
        )

        history = []
        for job in jobs:
            entry = {
                "job_id": job.id,
                "sport": job.sport,
                "status": job.status,
                "progress": job.progress,
                "created_at": job.created_at.isoformat(),
            }
            if job.result:
                r = job.result
                entry["result"] = {
                    "id": r.id,
                    "talent_score": r.talent_score,
                    "grade": r.grade,
                    "metrics": json.loads(r.metrics_json) if r.metrics_json else {},
                    "breakdown": json.loads(r.breakdown_json) if r.breakdown_json else {},
                    "ai_summary": r.ai_summary,
                    "jersey_number": r.jersey_number,
                    "scoreboard_text": r.scoreboard_text,
                }
            history.append(entry)

        return jsonify({
            "athlete": {
                "id": athlete.id,
                "name": athlete.name,
                "sport": athlete.sport,
            },
            "history": history,
        })
    finally:
        db.close()
