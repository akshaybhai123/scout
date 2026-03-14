"""
ScoutAI — Reports endpoints (PDF generation, leaderboard)
"""

import os
import json
from flask import Blueprint, request, jsonify, send_file
from db.database import SessionLocal, AnalysisResult, AnalysisJob, Athlete, Report
from utils.cloudinary_utils import upload_to_cloudinary, is_cloudinary_configured

reports_bp = Blueprint("reports", __name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(BASE_DIR, "uploads", "reports")


# --------------------------------------------------------------------------
# GET /api/reports/<id>/pdf
# --------------------------------------------------------------------------
@reports_bp.route("/reports/<int:result_id>/pdf", methods=["GET"])
def download_pdf(result_id):
    os.makedirs(REPORTS_DIR, exist_ok=True)

    db = SessionLocal()
    try:
        result = db.query(AnalysisResult).filter(AnalysisResult.id == result_id).first()
        if not result:
            return jsonify({"error": "Result not found"}), 404

        # Check if PDF already generated
        report = db.query(Report).filter(Report.result_id == result_id).first()
        if report and report.pdf_path and os.path.exists(report.pdf_path):
            return send_file(report.pdf_path, as_attachment=True, download_name=f"scoutai_report_{result_id}.pdf")

        # Generate PDF
        try:
            from fpdf import FPDF
        except ImportError:
            return jsonify({"error": "fpdf2 not installed"}), 500

        job = db.query(AnalysisJob).filter(AnalysisJob.id == result.job_id).first()
        athlete = db.query(Athlete).filter(Athlete.id == job.athlete_id).first() if job else None

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 24)
        pdf.cell(0, 15, "ScoutAI Talent Report", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(5)

        pdf.set_font("Helvetica", "", 12)
        if athlete:
            pdf.cell(0, 8, f"Athlete: {athlete.name}", new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 8, f"Sport: {athlete.sport}", new_x="LMARGIN", new_y="NEXT")
            if athlete.age:
                pdf.cell(0, 8, f"Age: {athlete.age}", new_x="LMARGIN", new_y="NEXT")
            if athlete.region:
                pdf.cell(0, 8, f"Region: {athlete.region}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)

        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, f"Talent Score: {result.talent_score}/100  ({result.grade})", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)

        # Metrics
        metrics = json.loads(result.metrics_json) if result.metrics_json else {}
        if metrics:
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(0, 10, "Performance Metrics", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 11)
            for key, val in metrics.items():
                pdf.cell(0, 7, f"  {key}: {val}", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(3)

        # Breakdown
        breakdown = json.loads(result.breakdown_json) if result.breakdown_json else {}
        if breakdown:
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(0, 10, "Score Breakdown", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 11)
            for key, val in breakdown.items():
                pdf.cell(0, 7, f"  {key}: {val}/100", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(3)

        # AI Summary
        if result.ai_summary:
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(0, 10, "AI Assessment", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 11)
            pdf.multi_cell(0, 7, result.ai_summary)

        pdf_path = os.path.join(REPORTS_DIR, f"report_{result_id}.pdf")
        pdf.output(pdf_path)

        # Cloudinary Upload
        final_url = pdf_path
        if is_cloudinary_configured():
            cloud_url = upload_to_cloudinary(pdf_path, folder="scoutai/reports")
            if cloud_url:
                final_url = cloud_url

        # Save report record
        if not report:
            report = Report(result_id=result_id, pdf_path=final_url)
            db.add(report)
        else:
            report.pdf_path = final_url
        db.commit()

        # If it's a cloud URL, we should redirect or tell the client.
        # But for now, since we still have the local file, we send it.
        # In a real deployed environment, we would likely return the URL.
        return send_file(pdf_path, as_attachment=True, download_name=f"scoutai_report_{result_id}.pdf")
    finally:
        db.close()


# --------------------------------------------------------------------------
# GET /api/leaderboard
# --------------------------------------------------------------------------
@reports_bp.route("/leaderboard", methods=["GET"])
def get_leaderboard():
    sport = request.args.get("sport")
    age_min = request.args.get("age_min", type=int)
    age_max = request.args.get("age_max", type=int)
    region = request.args.get("region")
    limit = request.args.get("limit", 50, type=int)

    db = SessionLocal()
    try:
        from sqlalchemy import func
        
        # Subquery to find the maximum talent_score for each athlete_id
        subquery = (
            db.query(
                AnalysisJob.athlete_id,
                func.max(AnalysisResult.talent_score).label("max_score")
            )
            .join(AnalysisResult, AnalysisJob.id == AnalysisResult.job_id)
            .group_by(AnalysisJob.athlete_id)
            .subquery()
        )

        # Main query to get the full records for those max scores
        query = (
            db.query(AnalysisResult, AnalysisJob, Athlete)
            .join(AnalysisJob, AnalysisResult.job_id == AnalysisJob.id)
            .join(Athlete, AnalysisJob.athlete_id == Athlete.id)
            .join(
                subquery,
                (Athlete.id == subquery.c.athlete_id) & 
                (AnalysisResult.talent_score == subquery.c.max_score)
            )
        )

        if sport:
            query = query.filter(Athlete.sport == sport)
        if region:
            query = query.filter(Athlete.region == region)
        if age_min:
            query = query.filter(Athlete.age >= age_min)
        if age_max:
            query = query.filter(Athlete.age <= age_max)

        query = query.order_by(AnalysisResult.talent_score.desc()).limit(limit)
        rows = query.all()

        leaderboard = []
        for i, (result, job, athlete) in enumerate(rows, 1):
            leaderboard.append({
                "rank": i,
                "athlete_id": athlete.id,
                "name": athlete.name,
                "sport": athlete.sport,
                "age": athlete.age,
                "region": athlete.region,
                "talent_score": result.talent_score,
                "grade": result.grade,
                "result_id": result.id,
            })

        return jsonify(leaderboard)
    finally:
        db.close()
