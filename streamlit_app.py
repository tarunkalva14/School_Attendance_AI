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

# Hide Streamlit footer and menu
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# -------------------------
# Load Premium CSS
# -------------------------
css_file = "premium_ui.css"
if os.path.exists(css_file):
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# -------------------------
# MongoDB Atlas connection
# -------------------------
client = MongoClient("mongodb+srv://kalvatarun7479_db_user:iJwZRXFs6LIRPyZv@cluster0.5ixiefr.mongodb.net/school_attendance")
db = client["school_attendance"]
collection = db["students_attendance_records"]
config_col = db["config"]

# -------------------------
# Ensure pdfs folder
# -------------------------
os.makedirs("pdfs", exist_ok=True)

# Sidebar - Premium Student Info
st.sidebar.markdown('<h3 style="text-align:center;">Student Info</h3>', unsafe_allow_html=True)

# Main Student Icon with Glow
st.sidebar.markdown("""
<div style="text-align:center; margin-bottom:20px;">
    <img src='https://cdn-icons-png.flaticon.com/512/3135/3135715.png' 
         style='width:120px; height:120px; border-radius:50%; transition: all 0.3s;'
         title="Student Icon"
         onmouseover="this.style.transform='scale(1.12)'; this.style.boxShadow='0 0 25px #00a8ff';"
         onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='none';" />
</div>
""", unsafe_allow_html=True)

# Function to add field with icon and tooltip
def sidebar_field(icon_url, label, widget_func, **kwargs):
    col1, col2 = st.sidebar.columns([1, 4])
    with col1:
        st.image(icon_url, width=30, use_column_width=False, output_format="png", clamp=False)
    with col2:
        return widget_func(label, **kwargs)

# Student ID
student_id = sidebar_field(
    "https://cdn-icons-png.flaticon.com/512/1087/1087925.png",
    "Student ID",
    st.number_input,
    min_value=1, step=1, key="id_input", help="Student ID"
)
# -------------------------
# AUTO-FETCH STUDENT INFO FROM MONGODB (Fixed)
# -------------------------
if "last_student_id" not in st.session_state:
    st.session_state["last_student_id"] = None

if st.session_state["last_student_id"] != student_id:
    st.session_state["last_student_id"] = student_id

    latest_record = collection.find_one(
        {"student_id": student_id},
        sort=[("attendance_date", -1)]
    )

    if latest_record:
        st.session_state["name_input"] = latest_record.get("student_name", "")
        st.session_state["age_input"] = latest_record.get("age", 10)

        db_date = latest_record.get("attendance_date")
        if isinstance(db_date, datetime):
            st.session_state["date_input"] = db_date.date()
    else:
        st.session_state["name_input"] = ""
        st.session_state["age_input"] = 10
        st.session_state["date_input"] = dt_date.today()

# Student Name
student_name = sidebar_field(
    "https://cdn-icons-png.flaticon.com/512/747/747376.png",
    "Student Name",
    st.text_input,
    key="name_input", 
    value=st.session_state.get("name_input", ""),
    help="Student Name"
)

# Age
age = sidebar_field(
    "https://cdn-icons-png.flaticon.com/512/2910/2910766.png",
    "Student Age",
    st.number_input,
    min_value=1, max_value=120, step=1,
    key="age_input",
    value=st.session_state.get("age_input", 10),
    help="Student Age"
)

# Attendance Date
attendance_date = sidebar_field(
    "https://cdn-icons-png.flaticon.com/512/2921/2921222.png",
    "Attendance Date",
    st.date_input,
    key="date_input",
    value=st.session_state.get("date_input", dt_date.today()),
    help="Attendance Date"
)

# Reason / Doctor Note
message = st.sidebar.text_area("Reason / Doctor Note (Optional)")

# PDF Uploader
pdf_file = st.sidebar.file_uploader("Upload Doctor Note PDF (optional)", type=["pdf"])

# -------------------------
# Attendance Status Override
# -------------------------
status_override = st.sidebar.selectbox("Override Attendance Status (Optional)", ["Auto Detect", "Present", "Absent", "Late"])

note_type_option = None
if status_override == "Absent" or status_override == "Auto Detect":
    note_type_option = st.sidebar.selectbox("Generate Doctor Note PDF Type", ["None", "Medical", "Family"])
    if st.sidebar.button("Generate Doctor Note PDF"):
        if student_name.strip() == "":
            st.sidebar.error("Please enter student name!")
        elif note_type_option != "None":
            file_name = f"{student_name.replace(' ', '_')}_note.pdf"
            create_pdf(
                file_name,
                student_name=student_name,
                note_type=note_type_option.lower(),
                attendance_date=attendance_date
            )
            st.sidebar.success(f"Doctor note PDF generated: {file_name}")

# Optional: set Hugging Face API key
st.sidebar.markdown("---")
st.sidebar.subheader("Hugging Face API Key (optional)")
hf_token_input = st.sidebar.text_input("Paste HF API Key (session)", type="password")
if hf_token_input:
    os.environ["HF_API_TOKEN"] = hf_token_input
    st.sidebar.success("Hugging Face API key set for this session")
    if st.sidebar.checkbox("Save HF API key to DB (optional)", value=False):
        config_col.update_one({"key_name": "HF_API_TOKEN"},
                              {"$set": {"key_value": hf_token_input}}, upsert=True)
        st.sidebar.success("HF API key saved to DB (config collection)")

st.sidebar.markdown("App version: professional-demo")

# -------------------------
# Helper Functions for Premium UI
# -------------------------
def display_ai_card(answer_text):
    st.markdown(f"""
    <div class="ai-card">
        <h4>AI Response</h4>
        <p>{answer_text}</p>
    </div>
    """, unsafe_allow_html=True)

def display_suggested_card(question_text, key, student_id):
    if st.button(question_text, key=key):
        try:
            resp = get_attendance_answer(student_id, question_text, student_name=student_name)
            st.markdown(f'<div class="suggested-card">{resp}</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"AI processing failed: {str(e)}")

def display_analytics_panel(title, content_callable):
    st.markdown(f"""
    <div class="analytics-panel">
        <h4>{title}</h4>
    </div>
    """, unsafe_allow_html=True)
    content_callable()

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

    if st.button("Submit Attendance"):
        if age < 5 or age > 16:
            st.error("This person is not considered a student. Age must be between 5 and 16 to submit attendance.")
        else:
            pdf_path = None
            if pdf_file is not None:
                pdf_path = os.path.join("pdfs", pdf_file.name)
                with open(pdf_path, "wb") as f:
                    f.write(pdf_file.getbuffer())
            elif status_override == "Absent" and note_type_option != "None" and os.path.exists(f"pdfs/{student_name.replace(' ', '_')}_note.pdf"):
                pdf_path = f"pdfs/{student_name.replace(' ', '_')}_note.pdf"

            if student_name.strip() == "":
                st.error("Please enter student name!")
            else:
                if isinstance(attendance_date, datetime):
                    mongo_date = attendance_date
                else:
                    mongo_date = datetime.combine(attendance_date, datetime.min.time())

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
                    st.markdown(f'<div class="pdf-preview">{extract_text_from_pdf(pdf_path)}</div>', unsafe_allow_html=True)

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
            pdf_path2 = None
            if pdf_path_qa is not None:
                pdf_path2 = os.path.join("pdfs", pdf_path_qa.name)
                with open(pdf_path2, "wb") as f:
                    f.write(pdf_path_qa.getbuffer())

            try:
                with st.spinner("AI is processing your question..."):
                    answer = get_attendance_answer(student_id, question, pdf_path=pdf_path2, student_name=student_name)
                display_ai_card(answer)
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
                display_suggested_card(q, btn_key, student_id)

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
        if 'student_name' not in df.columns:
            df['student_name'] = student_name if student_name else ""
        if 'age' not in df.columns:
            df['age'] = age if age else None

        def show_records():
            show_cols = [c for c in ["attendance_date", "status", "note", "student_name", "age"] if c in df.columns]
            st.dataframe(df[show_cols])

        display_analytics_panel("Attendance Records", show_records)

        def show_status_chart():
            if "status" in df.columns:
                status_counts = df["status"].value_counts()
                st.bar_chart(status_counts)
            else:
                st.info("No status data to chart.")

        display_analytics_panel("Attendance Status Distribution", show_status_chart)

        def show_over_time():
            try:
                if 'attendance_date' in df.columns:
                    df['attendance_date'] = pd.to_datetime(df['attendance_date'])
                    df_over_time = df.groupby('attendance_date').size()
                    st.line_chart(df_over_time)
                else:
                    st.info("No attendance_date column available.")
            except Exception:
                st.warning("Some attendance_date values could not be parsed. Check stored records.")
