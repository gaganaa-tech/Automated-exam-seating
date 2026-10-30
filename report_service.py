from backend.database.connection import fetch_all


def get_reports():
    reports = {
        "student_seating": fetch_all("""
            SELECT sa.student_id, s.roll_no, s.name, sa.room_id, r.room_number, sa.seat_number, e.name AS exam_name
            FROM seat_assignments sa
            LEFT JOIN students s ON s.id = sa.student_id
            LEFT JOIN rooms r ON r.id = sa.room_id
            LEFT JOIN seating_arrangements arr ON arr.id = sa.arrangement_id
            LEFT JOIN exams e ON e.id = arr.exam_id
        """),
        "room_seating": fetch_all("""
            SELECT r.room_number, COUNT(sa.id) AS assigned_students, r.capacity
            FROM rooms r
            LEFT JOIN seat_assignments sa ON sa.room_id = r.id
            GROUP BY r.id
        """),
        "exam_summary": fetch_all("""
            SELECT e.name AS exam_name, COUNT(DISTINCT sa.student_id) AS students_assigned
            FROM exams e
            LEFT JOIN seating_arrangements arr ON arr.exam_id = e.id
            LEFT JOIN seat_assignments sa ON sa.arrangement_id = arr.id
            GROUP BY e.id
        """),
        "attendance_summary": fetch_all("""
            SELECT e.name AS exam_name,
                   SUM(CASE WHEN a.present_status = 1 THEN 1 ELSE 0 END) AS present,
                   SUM(CASE WHEN a.present_status = 0 THEN 1 ELSE 0 END) AS absent
            FROM exams e
            LEFT JOIN attendance a ON a.exam_id = e.id
            GROUP BY e.id
        """),
    }
    return reports
