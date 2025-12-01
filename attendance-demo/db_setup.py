from pymongo import MongoClient

# Connect to local MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["school_attendance"]
students_col = db["students"]

# Create indexes for performance
students_col.create_index("student_id", unique=True)
students_col.create_index("date")
students_col.create_index("status")
