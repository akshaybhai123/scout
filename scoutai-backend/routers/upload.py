"""
ScoutAI — Upload endpoints (video / image)
"""

import os
import uuid
from flask import Blueprint, request, jsonify
from db.database import SessionLocal, AnalysisJob
from werkzeug.utils import secure_filename
from utils.cloudinary_utils import upload_to_cloudinary, is_cloudinary_configured

upload_bp = Blueprint("upload", __name__)

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")

ALLOWED_VIDEO_EXT = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
ALLOWED_IMAGE_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def _save_file(file, sub_dir):
    """Save an uploaded file with a unique name and return the path."""
    original = secure_filename(file.filename)
    ext = os.path.splitext(original)[1].lower()
    unique_name = f"{uuid.uuid4().hex}_{original}"
    dest_dir = os.path.join(UPLOAD_DIR, sub_dir)
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, unique_name)
    file.save(dest)
    return dest, ext


# --------------------------------------------------------------------------
# POST /api/upload/video
# --------------------------------------------------------------------------
@upload_bp.route("/upload/video", methods=["POST"])
def upload_video():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "Empty filename"}), 400

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_VIDEO_EXT:
        return jsonify({"error": f"Invalid video format. Allowed: {', '.join(ALLOWED_VIDEO_EXT)}"}), 400

    athlete_id = request.form.get("athlete_id")
    sport = request.form.get("sport", "general")

    if not athlete_id:
        return jsonify({"error": "athlete_id is required"}), 400

    path, _ = _save_file(file, "videos")

    # Cloudinary Upload
    final_url = path
    if is_cloudinary_configured():
        print(f"DEBUG: Uploading {path} to Cloudinary...")
        cloud_url = upload_to_cloudinary(path, folder="scoutai/videos")
        if cloud_url:
            final_url = cloud_url
            print(f"DEBUG: Cloudinary upload successful: {final_url}")

    # Create analysis job
    db = SessionLocal()
    try:
        job = AnalysisJob(
            athlete_id=int(athlete_id),
            video_path=final_url,
            sport=sport,
            status="pending",
            progress=0,
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        job_id = job.id
    finally:
        db.close()

    return jsonify({
        "message": "Video uploaded successfully",
        "job_id": job_id,
        "file_path": path,
    }), 201


# --------------------------------------------------------------------------
# POST /api/upload/image
# --------------------------------------------------------------------------
@upload_bp.route("/upload/image", methods=["POST"])
def upload_image():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "Empty filename"}), 400

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_IMAGE_EXT:
        return jsonify({"error": f"Invalid image format. Allowed: {', '.join(ALLOWED_IMAGE_EXT)}"}), 400

    path, _ = _save_file(file, "images")

    # Cloudinary Upload
    final_url = path
    if is_cloudinary_configured():
        cloud_url = upload_to_cloudinary(path, folder="scoutai/images")
        if cloud_url:
            final_url = cloud_url

    return jsonify({
        "message": "Image uploaded successfully",
        "file_path": final_url,
    }), 201
