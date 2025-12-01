# ai_qa.py
import os
import glob
from pymongo import MongoClient
from chatbot import extract_text_from_pdf

# Default PDF naming pattern
PDF_NAMING_PATTERN = "{student_name}_*.pdf"  # e.g., John_Doe_note.pdf

def get_attendance_answer(student_id, question, pdf_path=None, student_name=None, pdf_pattern=None):
    """
    Fetch attendance info from MongoDB + PDFs, then answer question using AI.

    Parameters:
        student_id: int
        question: str
        pdf_path: str, optional, if provided will use this PDF
        student_name: str, required if pdf_path is None
        pdf_pattern: str, optional, overrides default PDF_NAMING_PATTERN
    Returns:
        str: AI answer
    """
    context_text = ""

    # Use custom pattern if provided
    pattern = pdf_pattern or PDF_NAMING_PATTERN

    # 1️⃣ Extract text from uploaded PDF (if any)
    if pdf_path and os.path.exists(pdf_path):
        context_text += extract_text_from_pdf(pdf_path) + "\n"

    # 2️⃣ Search PDFs folder by naming convention if pdf_path not provided
    elif student_name:
        search_pattern = pattern.format(student_name=student_name.replace(" ", "_"))
        pdf_files = glob.glob(os.path.join("pdfs", search_pattern))
        for pdf_file in pdf_files:
            context_text += extract_text_from_pdf(pdf_file) + "\n"

    # 3️⃣ Fetch attendance info from MongoDB
    client = MongoClient("mongodb://localhost:27017/")
    db = client["school_attendance"]
    collection = db["students_attendance_records"]

    records = list(collection.find({"student_id": student_id}))

    if records:
        for rec in records:
            context_text += (
                f"Date: {rec.get('attendance_date')}, "
                f"Status: {rec.get('status')}, "
                f"Note: {rec.get('note', '')}, "
                f"Age: {rec.get('age', '')}\n"
            )
    else:
        context_text += "No attendance records found for this student.\n"

    # 4️⃣ Call OpenAI / AI model
    try:
        from openai import OpenAI
        client_ai = OpenAI()  # assumes API key in environment
        prompt = f"Context:\n{context_text}\n\nQuestion: {question}\nAnswer:"
        response = client_ai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        answer = response.choices[0].message.content
    except Exception:
        # fallback to local summary if OpenAI fails
        answer = "Could not access AI. Attendance info summarized:\n" + context_text[:1000]

    return answer
