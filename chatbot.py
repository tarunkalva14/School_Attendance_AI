# chatbot.py
import os
import platform
from datetime import datetime
from pymongo import MongoClient
import pytesseract
from io import BytesIO
from pdfplumber import open as pdf_open  # lightweight PDF text extraction
import requests

# ---------------------------
# MongoDB Connection
# ---------------------------
MONGO_URI = "mongodb+srv://kalvatarun7479_db_user:iJwZRXFs6LIRPyZv@cluster0.5ixiefr.mongodb.net/school_attendance"
client = MongoClient(MONGO_URI)
db = client["school_attendance"]
collection = db["students_attendance_records"]

# ---------------------------
# Tesseract OCR Path (Windows)
# ---------------------------
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ---------------------------
# Function to extract text from PDF
# Uses pdfplumber first, then falls back to pytesseract OCR if needed
# ---------------------------
def extract_text_from_pdf(pdf_path):
    if not pdf_path or not os.path.exists(pdf_path):
        return ""

    text_data = ""
    try:
        # Try simple PDF text extraction
        with pdf_open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_data += page_text + "\n"
    except Exception:
        pass  # fallback to OCR

    # If pdfplumber couldn't extract, fallback to OCR
    if not text_data.strip():
        try:
            from pdf2image import convert_from_path
            POPPLER_PATH = None  # cloud doesn't need a path
            images = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
            for img in images:
                text_data += pytesseract.image_to_string(img) + "\n"
        except Exception:
            pass  # just return empty if OCR fails

    return text_data.strip()

# ---------------------------
# Function to process and store attendance
# ---------------------------
def chatbot_process(student_id, attendance_date, message=None, pdf_path=None, student_name="", age=None, status_override=None):
    """
    Process attendance for a student, extract PDF notes, determine status, and save to MongoDB.

    Parameters:
        student_id (int)
        attendance_date (datetime.date or datetime.datetime)
        message (str)
        pdf_path (str)
        student_name (str)
        age (int)
        status_override (str): "Present", "Absent", "Late"
    """
    # Convert date to datetime.datetime for MongoDB
    if isinstance(attendance_date, datetime):
        mongo_date = attendance_date
    else:
        mongo_date = datetime.combine(attendance_date, datetime.min.time())

    # Extract text from PDF
    pdf_note = extract_text_from_pdf(pdf_path) if pdf_path else ""

    # Combine message and PDF text
    final_note = ""
    if message:
        final_note += message.strip()
    if pdf_note:
        final_note += "\n---\n" + pdf_note.strip() if final_note else pdf_note.strip()

    # Determine attendance status
    if status_override in ["Present", "Absent", "Late"]:
        status = status_override
    else:
        lower_text = final_note.lower()
        if "absent" in lower_text or "sick" in lower_text:
            status = "Absent"
        elif "late" in lower_text:
            status = "Late"
        else:
            status = "Present"

    # Prepare MongoDB record
    record = {
        "student_id": student_id,
        "student_name": student_name,
        "age": age,
        "attendance_date": mongo_date,
        "status": status,
        "note": final_note
    }

    # Upsert record to avoid duplicates
    collection.update_one(
        {"student_id": student_id, "attendance_date": mongo_date},
        {"$set": record},
        upsert=True
    )

    return f"Attendance submitted for {student_name}: {status}"
