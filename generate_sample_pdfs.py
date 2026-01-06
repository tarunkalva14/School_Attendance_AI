from fpdf import FPDF
import os

# Ensure PDFs folder exists
os.makedirs("pdfs", exist_ok=True)

def create_pdf(file_name, student_name, note_type="medical", attendance_date=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Convert date to string
    date_str = attendance_date.strftime("%Y-%m-%d") if attendance_date else "Unknown Date"

    if note_type == "medical":
        lines = [
            "To Whom It May Concern,",
            "",
            f"This is to certify that {student_name} was sick and advised to rest on {date_str}.",
            "Please excuse his/her absence from school.",
            "",
            "Doctor: Dr. Smith",
            f"Date: {date_str}"
        ]
    elif note_type == "family":
        lines = [
            "To Whom It May Concern,",
            "",
            f"{student_name} was absent due to a family emergency on {date_str}.",
            "Please excuse his/her absence.",
            "",
            "Regards,",
            "Parent/Guardian"
        ]
    else:
        lines = [f"{student_name} - Unknown note type"]

    for line in lines:
        pdf.cell(200, 10, txt=line, ln=True)

    pdf.output(f"pdfs/{file_name}")
    print(f"{file_name} generated for {student_name} on {date_str}.")
