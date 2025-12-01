# Smart School Attendance Management System with AI Q&A

![Streamlit](https://img.shields.io/badge/Streamlit-App-blue)
![MongoDB](https://img.shields.io/badge/MongoDB-Database-green)
![Python](https://img.shields.io/badge/Python-3.11-orange)

---

## **Project Overview**

This project is an **end-to-end Smart Attendance Management System** designed for schools, integrating:

- **Attendance entry** with optional doctor/family notes (PDFs)  
- **AI-driven Q&A** for natural language queries about student attendance  
- **PDF processing** for scanned or digital notes using OCR  
- **Analytics** for attendance trends and visualization  

The system demonstrates **full-stack development**, **AI integration**, and **data-driven insights**, making it a complete solution for automated attendance tracking.

---

## **Key Features**

### **1. Attendance Entry**
- Input **Student ID, Name, Age, and Date**  
- Upload **Doctor or Family Notes (PDF)** (optional)  
- System can **automatically infer attendance status** (Present, Absent, Late)  
- Teachers can **override** the status manually  

### **2. AI Q&A**
- Ask natural language questions about a student’s attendance  
- Automatically retrieves **MongoDB data** and **PDF content**  
- Suggested Questions tab provides **20+ ready-to-click queries**  
- Example queries:
  - “Why was the student absent on 2025-11-30?”  
  - “Show the doctor note for the latest absence.”  

### **3. PDF Integration**
- Extract text from PDFs using **Tesseract OCR**  
- Supports **multi-page and scanned PDFs**  
- Stored PDFs are automatically searched and used for AI answers  

### **4. Analytics**
- Attendance table: **student name, age, date, status, notes**  
- Bar chart: **Present / Absent / Late counts**  
- Line chart: **Attendance trends over time**  

---

## **Technical Stack**

| Layer | Technology |
|-------|------------|
| Frontend | Streamlit (interactive UI) |
| Backend | Python |
| Database | MongoDB |
| PDF Processing | pdf2image + Tesseract OCR |
| AI | OpenAI API (or local fallback) |

---

## **Explanation of Workflow**

- **Input:** Teacher enters **student info** or uploads **PDFs**.  
- **Processing:** **Chatbot module** combines messages + **PDF content**, infers **attendance status**.  
- **Storage:** **MongoDB** stores structured **attendance data** including **age** and **notes**.  
- **AI Q&A:** Retrieves relevant **database records** + **PDFs** to answer **natural language questions**.  
- **Analytics:** Displays **trends**, **distribution**, and **patterns** in interactive charts.  

---

## **Suggested Questions / AI Demo Examples**

- “**List all dates the student was absent.**”  
- “**Show the latest doctor note.**”  
- “**How many days was the student late this month?**”  
- “**Summarize all absence reasons.**”  

> These can be tested using the **Suggested Questions** tab in the app. **AI** will fetch answers automatically from **MongoDB** and **PDFs**.

---

## **Project Highlights**

- True **end-to-end solution** from **input → processing → storage → AI → analytics**  
- **AI integration** for **natural language reasoning**  
- **OCR PDF processing** for **scanned or handwritten notes**  
- Real-time **analytics and visualization**  
- **Modular, scalable, and reusable design**

---

## **Future Enhancements**

- **Multi-school support** with `school_id` field  
- **Role-based access** for **teachers** and **admins**  
- **Automatic notifications** for **absent students** (**email/SMS**)  
- **Cloud deployment** for scalability and **multi-user access**

  ----
  ## **Conclusion**

This **Smart School Attendance Management System with AI Q&A** demonstrates a complete **end-to-end solution** for modern educational institutions. 

Key takeaways:

- **Automation & Accuracy:** Automates attendance entry and analysis while reducing human errors.  
- **AI-Powered Insights:** Provides natural language answers from both structured **MongoDB records** and **PDF notes**, enhancing decision-making.  
- **OCR Integration:** Supports scanned or handwritten doctor/family notes through **Tesseract OCR**.  
- **Interactive Analytics:** Real-time **charts and tables** provide actionable insights for teachers and administrators.  
- **Scalable & Modular:** Designed for future enhancements such as **multi-school support**, **role-based access**, and **cloud deployment**.  

This project highlights the integration of **full-stack development**, **AI capabilities**, and **data-driven analytics** in a practical, real-world application.

