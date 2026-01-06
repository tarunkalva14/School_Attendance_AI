from pymongo import MongoClient

client = MongoClient("mongodb+srv://kalvatarun7479_db_user:iJwZRXFs6LIRPyZv@cluster0.5ixiefr.mongodb.net")
db = client["school_attendance"]
collection = db["students_attendance_records"]

print(collection.find_one())
