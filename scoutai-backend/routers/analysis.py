"""
ScoutAI — Analysis endpoints (trigger, poll status, get results)
"""

import json
from flask import Blueprint, request, jsonify
from db.database import SessionLocal, AnalysisJob, AnalysisResult

analysis_bp = Blueprint("analysis", __name__)


# --------------------------------------------------------------------------
# POST /api/analysis/trigger
# --------------------------------------------------------------------------
@analysis_bp.route("/analysis/trigger", methods=["POST"])
def trigger_analysis():
    """Trigger the analysis pipeline for a given job_id."""
    data = request.get_json(silent=True)
    if not data or "job_id" not in data:
        return jsonify({"error": "job_id is required"}), 400

    job_id = data["job_id"]

    db = SessionLocal()
    try:
        job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
        if not job:
            return jsonify({"error": "Job not found"}), 404

        if job.status not in ("pending", "failed"):
            return jsonify({"error": f"Job is already {job.status}"}), 400

        # Try Celery first; fall back to synchronous processing
        try:
            from workers.tasks import analyze_video_task
            task = analyze_video_task.delay(
                job.video_path, job.athlete_id, job.sport, job.id
            )
            job.status = "processing"
            job.progress = 5
            db.commit()
            return jsonify({
                "message": "Analysis started (async)",
                "job_id": job.id,
                "celery_task_id": task.id,
            })
        except Exception:
            # Synchronous fallback (no Redis/Celery)
            # We run this in a background thread so the HTTP request can return immediately
            # and the frontend can start polling the status.
            try:
                from workers.tasks import _run_pipeline
                import threading

                # Create a wrapper to run in thread
                def run_in_background():
                    try:
                        _run_pipeline(job.video_path, job.athlete_id, job.sport, job.id)
                    except Exception as e:
                        print(f"Background analysis failed: {e}")

                thread = threading.Thread(target=run_in_background)
                thread.daemon = True
                thread.start()

                job.status = "processing"
                job.progress = 5
                db.commit()

                return jsonify({
                    "message": "Analysis started (sync-thread)",
                    "job_id": job.id,
                })

            except Exception as e:
                return jsonify({"error": f"Failed to start background analysis: {str(e)}"}), 500
    finally:
        db.close()


# --------------------------------------------------------------------------
# GET /api/analysis/<job_id>
# --------------------------------------------------------------------------
@analysis_bp.route("/analysis/<int:job_id>", methods=["GET"])
def poll_job_status(job_id):
    db = SessionLocal()
    try:
        job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
        if not job:
            return jsonify({"error": "Job not found"}), 404

        return jsonify({
            "job_id": job.id,
            "athlete_id": job.athlete_id,
            "sport": job.sport,
            "status": job.status,
            "progress": job.progress,
            "created_at": job.created_at.isoformat(),
        })
    finally:
        db.close()


# --------------------------------------------------------------------------
# GET /api/analysis/<job_id>/results
# --------------------------------------------------------------------------
@analysis_bp.route("/analysis/<int:job_id>/results", methods=["GET"])
def get_job_results(job_id):
    db = SessionLocal()
    try:
        job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
        if not job:
            return jsonify({"error": "Job not found"}), 404

        if job.status != "complete":
            return jsonify({
                "error": f"Job is {job.status}, not complete yet",
                "status": job.status,
                "progress": job.progress,
            }), 400

        r = job.result
        if not r:
            return jsonify({"error": "No results available"}), 404

        return jsonify({
            "job_id": job.id,
            "athlete_id": job.athlete_id,
            "sport": job.sport,
            "talent_score": r.talent_score,
            "grade": r.grade,
            "metrics": json.loads(r.metrics_json) if r.metrics_json else {},
            "breakdown": json.loads(r.breakdown_json) if r.breakdown_json else {},
            "ai_summary": r.ai_summary,
            "jersey_number": r.jersey_number,
            "scoreboard_text": r.scoreboard_text,
            "created_at": r.created_at.isoformat(),
        })
    finally:
        db.close()
