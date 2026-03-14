"""
ScoutAI — Celery async video analysis worker
"""

import json
import os
import sys

# Ensure the root directory is in sys.path so we can import 'db', 'pipeline', etc.
# This fixes both runtime and linter issues when running from subdirectories.
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

try:
    from celery import Celery
    app = Celery("scoutai", broker="redis://localhost:6379/0", backend="redis://localhost:6379/1")
    app.conf.update(
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        timezone="UTC",
        enable_utc=True,
    )
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    app = None


# Celery setup (optional)
try:
    import cv2
    from pipeline.pose_estimator import extract_pose_sequence
    from pipeline.player_tracker import track_players_and_ball
    from pipeline.metrics_engine import compute_all_metrics
    from pipeline.ml_scorer import score_talent
    from db.database import SessionLocal, AnalysisJob, AnalysisResult
    from pipeline.ocr_processor import extract_jersey_number, extract_scoreboard
    CORE_IMPORTS_AVAILABLE = True
except ImportError:
    CORE_IMPORTS_AVAILABLE = False


def _run_pipeline(video_path, athlete_id, sport, job_id, update_progress=None):
    """
    Run the full CV analysis pipeline (used by both Celery and sync fallback).
    """
    # These imports are duplicated here for standalone execution or if CORE_IMPORTS_AVAILABLE is False
    # In a production Celery worker, they would ideally be loaded once globally.
    # However, for robustness and local testing without Celery, they are included here.
    import cv2
    from pipeline.pose_estimator import extract_pose_sequence
    from pipeline.player_tracker import track_players_and_ball
    from pipeline.metrics_engine import compute_all_metrics
    from pipeline.ml_scorer import score_talent
    from db.database import SessionLocal, AnalysisJob, AnalysisResult
    from pipeline.ocr_processor import extract_jersey_number, extract_scoreboard

    print(f"DEBUG: Starting pipeline for job {job_id}, video: {video_path}")
    if not os.path.exists(video_path):
        print(f"ERROR: Video file not found at {video_path}")
        # Try relative path check
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # video_path is likely absolute, but if it was recorded relative to something else...
        print(f"DEBUG: Base dir is {base_dir}")

    db = SessionLocal()
    try:
        job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
        if not job:
            raise ValueError(f"Job {job_id} not found")

        # Stage 1: Offload to Hugging Face
        job.status = "processing"
        job.progress = 20
        db.commit()
        if update_progress:
            update_progress(20, "Offloading to Hugging Face AI Space...")

        # Cloudinary URL is stored in job.video_path
        hf_url = os.environ.get("HF_AI_URL", "https://ak47dev-scoutai-ai.hf.space/analyze")
        
        try:
            import requests
            response = requests.post(
                hf_url, 
                json={"video_url": job.video_path, "sport": sport},
                timeout=300 # Wait up to 5 mins for heavy processing
            )
            response.raise_for_status()
            ai_data = response.json()
            
            # Extract results from HF
            metrics = ai_data["metrics"]
            talent_score = ai_data["talent_score"]
            grade = ai_data["grade"]
            breakdown = ai_data["breakdown"]
            jersey_num = ai_data.get("jersey_number", "")
            scoreboard_txt = ai_data.get("scoreboard_text", "")

        except Exception as hf_err:
            print(f"Hugging Face Error: {str(hf_err)}")
            # Fallback or fail
            raise hf_err

        # Stage 2: Save results to PostgreSQL
        job.progress = 90
        db.commit()
        if update_progress:
            update_progress(90, "Finalizing report...")

        athlete = job.athlete
        athlete_name = athlete.name if athlete else "Athlete"

        ai_summary = (
            f"{athlete_name} demonstrates a talent score of "
            f"{talent_score}/100 ({grade}). "
            f"Key strengths: speed ({breakdown.get('speed', 0):.0f}/100), "
            f"technique ({breakdown.get('technique', 0):.0f}/100), "
            f"athleticism ({breakdown.get('athleticism', 0):.0f}/100). "
        )

        result = AnalysisResult(
            job_id=job.id,
            talent_score=talent_score,
            grade=grade,
            metrics_json=json.dumps(metrics),
            breakdown_json=json.dumps(breakdown),
            ai_summary=ai_summary,
            jersey_number=jersey_num,
            scoreboard_text=scoreboard_txt,
        )
        db.add(result)
        job.status = "complete"
        job.progress = 100
        db.commit()

        return {
            "status": "complete",
            "talent_score": talent_score,
            "grade": grade,
        }

    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        print(f"CRITICAL ERROR in _run_pipeline: {error_msg}")
        with open("analysis_debug.log", "a") as f:
            f.write(f"\n--- Job {job_id} Failed ---\n")
            f.write(error_msg)
            f.write("\n---------------------------\n")

        job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
        if job:
            job.status = "failed"
            job.progress = 0
            db.commit()
        # We don't re-raise here if called from a fire-and-forget thread, 
        # but the thread wrapper in analysis.py will see it if we did.
    finally:
        db.close()


if CELERY_AVAILABLE and app is not None:
    @app.task(bind=True, name="scoutai.analyze_video")
    def analyze_video_task(self, video_path, athlete_id, sport, job_id):
        """Celery task wrapper for the analysis pipeline."""
        def update_progress(progress, message):
            self.update_state(
                state="PROCESSING",
                meta={"progress": progress, "message": message},
            )

        try:
            return _run_pipeline(video_path, athlete_id, sport, job_id, update_progress)
        except Exception as e:
            self.update_state(state="FAILED", meta={"error": str(e)})
            raise
