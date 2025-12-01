# streamlit_app.py
import os
from datetime import datetime, date as dt_date
import streamlit as st
import pandas as pd
from pymongo import MongoClient

from generate_sample_pdfs import create_pdf
from chatbot import chatbot_process, extract_text_from_pdf
from ai_qa import get_attendance_answer

# -------------------------
# Page configuration
# -------------------------
st.set_page_config(
    page_title="School Attendance Dashboard",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------
# MongoDB
# -------------------------
client = MongoClient("mongodb://localhost:27017/")
db = client["school_attendance"]
collection = db["students_attendance_records"]
config_col = db["config"]

# -------------------------
# Ensure pdfs folder
# -------------------------
os.makedirs("pdfs", exist_ok=True)

# -------------------------
# Sidebar - Student & Settings
# -------------------------
st.sidebar.header("Student Information")
student_id = st.sidebar.number_input("Student ID", min_value=1, step=1)
student_name = st.sidebar.text_input("Student Name")
age = st.sidebar.number_input("Student Age", min_value=1, max_value=120, step=1, value=10)
attendance_date = st.sidebar.date_input("Attendance Date", value=dt_date.today())
st.sidebar.markdown("---")
message = st.sidebar.text_area("Reason / Doctor Note (Optional)")
pdf_file = st.sidebar.file_uploader("Upload Doctor Note PDF (optional)", type=["pdf"])

note_type_option = st.sidebar.selectbox("Generate Doctor Note PDF Type", ["medical", "family"])
if st.sidebar.button("Generate Doctor Note PDF"):
    if student_name.strip() == "":
        st.sidebar.error("Please enter student name!")
    else:
        file_name = f"{student_name.replace(' ', '_')}_note.pdf"
        create_pdf(file_name, student_name=student_name, note_type=note_type_option, attendance_date=attendance_date)
        st.sidebar.success(f"Doctor note PDF generated: {file_name}")

# Optional: set OpenAI API key for this session
st.sidebar.markdown("---")
st.sidebar.subheader("OpenAI (optional)")
api_input = st.sidebar.text_input("OpenAI API Key (session)", type="password")
if api_input:
    os.environ["OPENAI_API_KEY"] = api_input
    st.sidebar.success("API key set for this session")
    if st.sidebar.checkbox("Save API key to DB (optional)", value=False):
        config_col.update_one({"key_name": "OPENAI_API_KEY"},
                              {"$set": {"key_value": api_input}}, upsert=True)
        st.sidebar.success("API key saved to DB (config collection)")

st.sidebar.markdown("App version: professional-demo")

# -------------------------
# Main layout: tabs
# -------------------------
tabs = st.tabs(["Attendance Entry", "AI Q&A", "Suggested Questions", "Analytics"])

# -------------------------
# Tab 1: Attendance Entry
# -------------------------
with tabs[0]:
    st.header("Submit Attendance")
    st.write("Enter student details, upload a doctor note (optional), and submit attendance.")
    status_override = st.selectbox("Override Attendance Status (Optional)", ["Auto Detect", "Present", "Absent", "Late"])

    if st.button("Submit Attendance"):
        if age < 5 or age > 16:
            st.error("This person is not considered a student. Age must be between 5 and 16 to submit attendance.")
        else:
            # Save uploaded PDF locally if present
            pdf_path = None
            if pdf_file is not None:
                pdf_path = os.path.join("pdfs", pdf_file.name)
                with open(pdf_path, "wb") as f:
                    f.write(pdf_file.getbuffer())
            elif os.path.exists(f"pdfs/{student_name.replace(' ', '_')}_note.pdf"):
                pdf_path = f"pdfs/{student_name.replace(' ', '_')}_note.pdf"

            if student_name.strip() == "":
                st.error("Please enter student name!")
            else:
                # Convert attendance_date to datetime.datetime
                if isinstance(attendance_date, datetime):
                    mongo_date = attendance_date
                else:
                    mongo_date = datetime.combine(attendance_date, datetime.min.time())

                # Call chatbot_process - now with age and status override
                response = chatbot_process(
                    student_id,
                    mongo_date,
                    message,
                    pdf_path,
                    student_name=student_name,
                    age=age,
                    status_override=(None if status_override == "Auto Detect" else status_override)
                )
                st.success(response)

                if pdf_path:
                    st.subheader("PDF Content Preview")
                    st.text_area("PDF Text", extract_text_from_pdf(pdf_path), height=200)

# -------------------------
# Tab 2: AI Q&A
# -------------------------
with tabs[1]:
    st.header("Ask AI about Attendance")
    st.write("Ask natural language questions about the student's attendance. If OpenAI key is not set or quota exceeded, the app falls back to local answers.")
    question = st.text_input("Enter your question (free text)")
    pdf_path_qa = st.file_uploader("Optional PDF for AI context (upload optional)", type=["pdf"], key="qa_pdf_main")

    if st.button("Get AI Answer"):
        if not question.strip():
            st.error("Please enter a question.")
        else:
            # Save pdf for QA if uploaded
            pdf_path2 = None
            if pdf_path_qa is not None:
                pdf_path2 = os.path.join("pdfs", pdf_path_qa.name)
                with open(pdf_path2, "wb") as f:
                    f.write(pdf_path_qa.getbuffer())

            try:
                answer = get_attendance_answer(student_id, question, pdf_path2)
                st.info(answer)
            except Exception as e:
                st.error(f"AI processing failed: {str(e)}")

# -------------------------
# Tab 3: Suggested Questions
# -------------------------
with tabs[2]:
    st.header("Top 20 Suggested Questions")
    st.write("Quick click suggested queries (Absent / Present / Late). The system fetches data using Student ID only.")

    suggested_groups = {
        "Absent": [
            "Why was the student absent on a specific date?",
            "List all dates when the student was marked absent.",
            "Does the student have consecutive absence days?",
            "Show the doctor note for the latest absence.",
            "Summarize all absence reasons from notes/PDFs.",
            "Identify absence dates with no notes or PDFs attached.",
            "What is the student’s total absence count this month?"
        ],
        "Present": [
            "List all dates when the student was marked present.",
            "What is the student’s most recent present date?",
            "How many days has the student attended this semester?",
            "Show the student’s present vs absent percentage.",
            "Did the student attend all days last week?",
            "Identify the student’s longest present streak.",
            "Has the student’s attendance improved recently?"
        ],
        "Late": [
            "List all dates when the student arrived late.",
            "Why was the student late on a specific date?",
            "How many late arrivals occurred this month?",
            "Was the student late more than 3 times this month?",
            "Identify late entries without notes or PDFs.",
            "Show a timeline of all late arrivals for this student."
        ]
    }

    for group, questions in suggested_groups.items():
        with st.expander(group):
            for idx, q in enumerate(questions):
                btn_key = f"suggest_{group}_{idx}"
                if st.button(q, key=btn_key):
                    try:
                        resp = get_attendance_answer(student_id, q, None)
                        st.info(resp)
                    except Exception as e:
                        st.error(f"AI processing failed: {str(e)}")

# -------------------------
# Tab 4: Analytics
# -------------------------
with tabs[3]:
    st.header("Attendance Analytics")
    records = list(collection.find({"student_id": student_id}))
    if not records:
        st.info("No attendance records found for this student.")
    else:
        df = pd.DataFrame(records)
        # Ensure columns exist
        if 'student_name' not in df.columns:
            df['student_name'] = student_name if student_name else ""
        if 'age' not in df.columns:
            df['age'] = age if age else None

        st.subheader("Attendance Records")
        show_cols = [c for c in ["attendance_date", "status", "note", "student_name", "age"] if c in df.columns]
        st.dataframe(df[show_cols])

        st.subheader("Attendance Status Distribution")
        if "status" in df.columns:
            status_counts = df["status"].value_counts()
            st.bar_chart(status_counts)
        else:
            st.info("No status data to chart.")

        st.subheader("Attendance Over Time")
        try:
            if 'attendance_date' in df.columns:
                df['attendance_date'] = pd.to_datetime(df['attendance_date'])
                df_over_time = df.groupby('attendance_date').size()
                st.line_chart(df_over_time)
            else:
                st.info("No attendance_date column available.")
        except Exception:
            st.warning("Some attendance_date values could not be parsed. Check stored records.")
