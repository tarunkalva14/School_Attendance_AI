from attendance_updater import update_attendance
from datetime import date

# Example updates
update_attendance(student_id=101, date=date(2025,11,26), status="medical", note="Sick with fever")
update_attendance(student_id=102, date=date(2025,11,26), status="family", note="Family emergency")
