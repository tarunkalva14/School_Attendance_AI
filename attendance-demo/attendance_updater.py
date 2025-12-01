from pymongo import MongoClient
from datetime import datetime
import logging
import os

# Ensure log file folder exists (optional)
if not os.path.exists("attendance_changes.log"):
    open("attendance_changes.log", "w").close()

# Setup logging
logging.basicConfig(
    filename='attendance_changes.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

client = MongoClient("mongodb://localhost:27017/")
db = client.school_attendance
students_col = db.students

def update_attendance(student_id, date, status, note):
    # Convert datetime.date to datetime.datetime for MongoDB
    if isinstance(date, datetime) is False:
        date = datetime(date.year, date.month, date.day)

    result = students_col.update_one(
        {"student_id": student_id, "date": date},
        {"$set": {"status": status, "note": note}},
        upsert=True
    )

    # Log the update
    logging.info(f"Updated student_id={student_id}, date={date.date()}, status={status}, note={note}")

    return result
