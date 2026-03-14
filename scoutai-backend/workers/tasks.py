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

        # Stage 1: Pose estimation
        job.status = "processing"
        job.progress = 10
        db.commit()
        if update_progress:
            update_progress(10, "Extracting pose data...")

        pose_data = extract_pose_sequence(video_path)

        # Stage 2: Player tracking
        job.progress = 40
        db.commit()
        if update_progress:
            update_progress(40, "Tracking players and ball...")

        trajectories = track_players_and_ball(video_path)

        # Stage 3: Metrics computation
        metrics = compute_all_metrics(pose_data, trajectories)

        # Stage 4: OCR Processing
        job.progress = 75
        db.commit()
        if update_progress:
            update_progress(75, "Extracting jersey and scoreboard data...")
        
        cap = cv2.VideoCapture(video_path)
        ret, first_frame = cap.read()
        cap.release()
        
        jersey_num = ""
        if trajectories and ret:
            # Try OCR on the first detection for the first player
            first_tid = next(iter(trajectories))
            if trajectories[first_tid]:
                jersey_num = extract_jersey_number(first_frame, trajectories[first_tid][0]["bbox"])
        
        scoreboard_txt = extract_scoreboard(first_frame) if ret else ""

        # Stage 5: ML scoring
        job.progress = 85
        db.commit()
        if update_progress:
            update_progress(85, "Scoring talent...")

        talent_result = score_talent(metrics)

        # Stage 6: Save results
        athlete = job.athlete
        athlete_name = athlete.name if athlete else "Athlete"

        ai_summary = (
            f"{athlete_name} demonstrates a talent score of "
            f"{talent_result['talent_score']}/100 ({talent_result['grade']}). "
            f"Key strengths: speed ({talent_result['breakdown'].get('speed', 0):.0f}/100), "
            f"technique ({talent_result['breakdown'].get('technique', 0):.0f}/100), "
            f"athleticism ({talent_result['breakdown'].get('athleticism', 0):.0f}/100). "
        )

        if talent_result["grade"] == "Elite":
            ai_summary += "Outstanding performance detected. Recommend advanced competition exposure."
        elif talent_result["grade"] == "Advanced":
            ai_summary += "Strong foundation. Recommend focused drills on weaker areas."
        elif talent_result["grade"] == "Developing":
            ai_summary += "Promising potential. Recommend structured training regimen."
        else:
            ai_summary += "Building fundamentals. Recommend regular practice and coaching."

        result = AnalysisResult(
            job_id=job.id,
            talent_score=talent_result["talent_score"],
            grade=talent_result["grade"],
            metrics_json=json.dumps(metrics),
            breakdown_json=json.dumps(talent_result["breakdown"]),
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
            "talent_score": talent_result["talent_score"],
            "grade": talent_result["grade"],
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
