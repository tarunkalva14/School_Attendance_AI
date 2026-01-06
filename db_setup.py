from pymongo import MongoClient

# -------------------------
# Connect to MongoDB Atlas
# -------------------------
MONGO_URI = "mongodb+srv://kalvatarun7479_db_user:iJwZRXFs6LIRPyZv@cluster0.5ixiefr.mongodb.net/school_attendance"
client = MongoClient(MONGO_URI)
db = client["school_attendance"]
students_col = db["students"]

# Create indexes for performance
students_col.create_index("student_id", unique=True)
students_col.create_index("date")
students_col.create_index("status")
