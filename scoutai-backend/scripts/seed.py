"""
ScoutAI — Database Seeder
Populates the DB with sample athletes and training history for demonstration.
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import SessionLocal, Athlete, AnalysisJob, AnalysisResult, ChatMessage, init_db

def seed():
    init_db()
    db = SessionLocal()
    
    # Check if already seeded
    if db.query(Athlete).count() > 1:
        print("[INFO] DB already seeded.")
        db.close()
        return

    print("[INFO] Seeding database...")
    
    # Sample Athletes
    athletes_data = [
        {"name": "Aryan Sharma", "sport": "cricket", "age": 19, "region": "Mumbai, India"},
        {"name": "Sarah Chen", "sport": "badminton", "age": 22, "region": "Singapore"},
        {"name": "Marcus Jordan", "sport": "basketball", "age": 20, "region": "Chicago, USA"},
        {"name": "Elena Rossi", "sport": "volleyball", "age": 21, "region": "Milan, Italy"},
        {"name": "Yuki Tanaka", "sport": "tennis", "age": 18, "region": "Tokyo, Japan"}
    ]
    
    for a_data in athletes_data:
        athlete = Athlete(**a_data)
        db.add(athlete)
        db.flush() # Get ID
        
        # Add a sample completed job and result for each
        job = AnalysisJob(
            athlete_id=athlete.id,
            sport=athlete.sport,
            video_path=f"uploads/videos/sample_{athlete.id}.mp4",
            status="complete",
            progress=100
        )
        db.add(job)
        db.flush()
        
        # Random metrics
        import random
        metrics = {
            "avg_speed": round(random.uniform(15, 28), 2),
            "max_speed": round(random.uniform(25, 35), 2),
            "jump_height": round(random.uniform(20, 65), 2),
            "form_score": round(random.uniform(60, 95), 2),
            "agility": round(random.uniform(50, 90), 2),
            "consistency": round(random.uniform(70, 98), 2)
        }
        
        scores = [88.5, 76.2, 91.0, 68.4, 82.1]
        grades = ["Elite", "Advanced", "Elite", "Developing", "Advanced"]
        idx = athletes_data.index(a_data)
        
        result = AnalysisResult(
            job_id=job.id,
            talent_score=scores[idx],
            grade=grades[idx],
            metrics_json=json.dumps(metrics),
            breakdown_json=json.dumps({
                "speed": metrics["avg_speed"] * 3,
                "athleticism": metrics["jump_height"] * 1.2,
                "technique": metrics["form_score"],
                "agility": metrics["agility"],
                "consistency": metrics["consistency"]
            }),
            ai_summary=f"Analysis of {athlete.name} shows strong {athlete.sport} fundamentals with high {random.choice(['agility', 'speed', 'technique'])}."
        )
        db.add(result)

    # Add some chat history
    chat = ChatMessage(
        athlete_id=1,
        role="user",
        message="What is the best pre-training meal for a cricketer?",
        category="diet_query",
        sport="cricket"
    )
    db.add(chat)
    
    bot_chat = ChatMessage(
        athlete_id=1,
        role="bot",
        message="For cricket, focus on complex carbohydrates 2-3 hours before. Oats with banana or brown rice with chicken are great options.",
        category="diet_query",
        sport="cricket"
    )
    db.add(bot_chat)

    db.commit()
    print("[SUCCESS] Database seeded with sample athletes.")
    db.close()

if __name__ == "__main__":
    seed()
