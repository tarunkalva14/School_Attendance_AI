def parse_doctor_note(text):
    text = text.lower()
    medical_keywords = ["doctor", "fever", "sick", "hospital", "illness"]
    valid_keywords = ["family emergency", "personal reason","other emergencies"]

    if any(k in text for k in medical_keywords):
        return "medical"
    elif any(k in text for k in valid_keywords):
        return "valid_reason"
    else:
        return None
