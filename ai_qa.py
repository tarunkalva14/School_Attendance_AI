# ai_qa.py
import os
import glob
import requests
from pymongo import MongoClient
from chatbot import extract_text_from_pdf

PDF_NAMING_PATTERN = "{student_name}_*.pdf"

# -------------------------
# MongoDB Atlas connection
# -------------------------
MONGO_URI = "mongodb+srv://kalvatarun7479_db_user:iJwZRXFs6LIRPyZv@cluster0.5ixiefr.mongodb.net/school_attendance"
client = MongoClient(MONGO_URI)
db = client["school_attendance"]
collection = db["students_attendance_records"]

# -------------------------
# Function to get attendance answer
# -------------------------
def get_attendance_answer(student_id, question, pdf_path=None, student_name=None, pdf_pattern=None):
    context_text = ""

    # 1️⃣ PDF takes priority
    pattern = pdf_pattern or PDF_NAMING_PATTERN
    if pdf_path and os.path.exists(pdf_path):
        context_text += extract_text_from_pdf(pdf_path) + "\n"
    elif student_name:
        search_pattern = pattern.format(student_name=student_name.replace(" ", "_"))
        pdf_files = glob.glob(os.path.join("pdfs", search_pattern))
        for pdf_file in pdf_files:
            context_text += extract_text_from_pdf(pdf_file) + "\n"

    # 2️⃣ MongoDB fallback only if no PDF text
    if not context_text:
        records = list(collection.find({"student_id": student_id}))
        if records:
            for rec in records:
                date_str = rec.get('attendance_date')
                if hasattr(date_str, 'strftime'):
                    date_str = date_str.strftime("%Y-%m-%d")
                context_text += (
                    f"Date: {date_str}, "
                    f"Status: {rec.get('status')}, "
                    f"Note: {rec.get('note', '')}, "
                    f"Age: {rec.get('age', '')}\n"
                )
        else:
            context_text += "No attendance records found for this student.\n"

    # 3️⃣ Hugging Face Router API call
    hf_token = os.environ.get("HF_API_TOKEN")
    if hf_token:
        try:
            hf_api_url = "https://router.huggingface.co/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {hf_token}",
                "Content-Type": "application/json"
            }

            # ✅ Updated model to free HF-compatible model
            payload = {
                "model": "meta-llama/Meta-Llama-3-8B-Instruct",
                "messages": [
                    {"role": "system", "content": "You are a helpful attendance assistant."},
                    {"role": "user", "content": f"Context:\n{context_text}\n\nQuestion: {question}"}
                ],
                "temperature": 0.2,
                "max_tokens": 300
            }

            response = requests.post(hf_api_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()

            if "choices" in result and len(result["choices"]) > 0:
                answer = result["choices"][0]["message"]["content"]
            else:
                answer = "AI could not generate a response. Here’s a summary:\n" + context_text[:1000]

        except Exception as e:
            answer = f"Could not access AI (error: {e}). Attendance info summarized:\n" + context_text[:1000]
    else:
        answer = "No Hugging Face API token set. Attendance info summarized:\n" + context_text[:1000]

    return answer
