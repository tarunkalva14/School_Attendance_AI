from pymongo import MongoClient
from datetime import datetime
import logging
import os

# Ensure log file exists (optional)
if not os.path.exists("attendance_changes.log"):
    open("attendance_changes.log", "w").close()

# Setup logging
logging.basicConfig(
    filename='attendance_changes.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

# -------------------------
# Connect to MongoDB Atlas
# -------------------------
MONGO_URI = "mongodb+srv://kalvatarun7479_db_user:iJwZRXFs6LIRPyZv@cluster0.5ixiefr.mongodb.net/school_attendance"
client = MongoClient(MONGO_URI)
db = client.school_attendance
students_col = db.students

# -------------------------
# Function to update attendance
# -------------------------
def update_attendance(student_id, date, status, note):
    # Convert datetime.date to datetime.datetime for MongoDB
    if not isinstance(date, datetime):
        date = datetime(date.year, date.month, date.day)

    result = students_col.update_one(
        {"student_id": student_id, "date": date},
        {"$set": {"status": status, "note": note}},
        upsert=True
    )

    # Log the update
    logging.info(f"Updated student_id={student_id}, date={date.date()}, status={status}, note={note}")

    return result
