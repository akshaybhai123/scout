
from db.database import SessionLocal, Athlete, AnalysisJob, AnalysisResult, Report, ChatMessage

def test_delete(athlete_id):
    db = SessionLocal()
    try:
        athlete = db.query(Athlete).filter(Athlete.id == athlete_id).first()
        if not athlete:
            print(f"Athlete {athlete_id} not found")
            return
        
        print(f"Deleting athlete {athlete.name} (ID: {athlete.id})")
        db.delete(athlete)
        db.commit()
        print("Successfully deleted")
    except Exception as e:
        db.rollback()
        print(f"Error during deletion: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        test_delete(int(sys.argv[1]))
    else:
        # Try to find the first athlete to test delete
        db = SessionLocal()
        a = db.query(Athlete).first()
        db.close()
        if a:
            test_delete(a.id)
        else:
            print("No athletes to delete")
