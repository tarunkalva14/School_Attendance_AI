import random
from datetime import datetime, timedelta
from db_setup import students_col

NUM_RECORDS = 100000  # 100k for sample
BATCH_SIZE = 10000
statuses = ["present", "absent", "medical"]

def generate_record(student_id):
    date = datetime(2023, 1, 1) + timedelta(days=random.randint(0, 364))
    status = random.choices(statuses, weights=[0.85, 0.10, 0.05])[0]
    return {"student_id": student_id, "date": date, "status": status, "notes": ""}

def main():
    batch = []
    for i in range(1, NUM_RECORDS + 1):
        batch.append(generate_record(i))
        if len(batch) >= BATCH_SIZE:
            students_col.insert_many(batch)
            batch = []
            print(f"{i} records inserted...")
    if batch:
        students_col.insert_many(batch)
        print(f"{NUM_RECORDS} records inserted successfully!")

if __name__ == "__main__":
    main()
