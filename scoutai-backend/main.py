"""
ScoutAI — Flask application entry point
"""

import os
from dotenv import load_dotenv
from flask import Flask, send_from_directory

load_dotenv()
from flask_cors import CORS
from db.database import init_db

# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

def create_app():
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024  # 500 MB max upload

    # CORS — allow all origins in dev
    CORS(app)

    # Ensure upload dirs exist
    base = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(os.path.join(base, "uploads", "videos"), exist_ok=True)
    os.makedirs(os.path.join(base, "uploads", "images"), exist_ok=True)
    os.makedirs(os.path.join(base, "ml_models"), exist_ok=True)

    # Create DB tables
    init_db()

    # ------------------------------------------------------------------
    # Register Blueprints
    # ------------------------------------------------------------------
    from routers.upload import upload_bp
    from routers.athletes import athletes_bp
    from routers.analysis import analysis_bp
    from routers.reports import reports_bp
    from routers.chatbot import chatbot_bp

    app.register_blueprint(upload_bp, url_prefix="/api")
    app.register_blueprint(athletes_bp, url_prefix="/api")
    app.register_blueprint(analysis_bp, url_prefix="/api")
    app.register_blueprint(reports_bp, url_prefix="/api")
    app.register_blueprint(chatbot_bp, url_prefix="/api")

    # ------------------------------------------------------------------
    # Serve uploaded files
    # ------------------------------------------------------------------
    @app.route("/uploads/<path:filename>")
    def serve_upload(filename):
        uploads_dir = os.path.join(base, "uploads")
        return send_from_directory(uploads_dir, filename)

    # ------------------------------------------------------------------
    # Health check
    # ------------------------------------------------------------------
    @app.route("/api/health")
    def health():
        return {"status": "ok", "app": "ScoutAI"}

    return app


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app = create_app()
    # Enable use_reloader so that edits to python files trigger a server restart
    app.run(host="0.0.0.0", port=8000, debug=True, use_reloader=True)
