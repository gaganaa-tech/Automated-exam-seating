from backend.algorithms.constraint_checker import validate_arrangement
from backend.algorithms.quality_score import quality_score_from_assignments
from backend.database.connection import execute, fetch_all, fetch_one


def generate_exam_arrangement(exam_id, room_ids=None):
    exam = fetch_one("SELECT * FROM exams WHERE id = %s", (exam_id,))
    if not exam:
        raise ValueError("Exam not found.")

    students = fetch_all(
        """
        SELECT s.*, d.name AS department_name, sec.name AS section_name
        FROM students s
        LEFT JOIN departments d ON d.id = s.department_id
        LEFT JOIN sections sec ON sec.id = s.section_id
        WHERE s.status = 'active'
        """)

    room_query = "SELECT * FROM rooms WHERE status = 'active'"
    if room_ids:
        placeholders = ", ".join(["%s"] * len(room_ids))
        room_query += f" AND id IN ({placeholders})"
        rooms = fetch_all(room_query, tuple(room_ids))
    else:
        rooms = fetch_all(room_query)

    if not rooms:
        raise ValueError("No active rooms available for this exam.")

    total_students = len(students)
    max_capacity = sum(room.get("capacity", 0) for room in rooms)
    if total_students > max_capacity:
        raise ValueError("Room capacity is insufficient for this exam.")

    assignments = []
    seat_index = 0
    for room in rooms:
        rows = int(room.get("rows") or 0)
        cols = int(room.get("columns") or 0)
        capacity = int(room.get("capacity") or 0)
        seats = []
        for row in range(1, rows + 1):
            for col in range(1, cols + 1):
                seat_label = f"{chr(64 + row)}{col:02d}"
                seats.append({"row": row, "column": col, "seat_number": seat_label})
        blocked = fetch_all("SELECT seat_number FROM room_seats WHERE room_id = %s AND status = 'blocked'", (room.get("id"),))
        blocked_numbers = {item["seat_number"] for item in blocked}
        for seat in seats:
            if seat["seat_number"] in blocked_numbers:
                continue
            if len(assignments) >= total_students:
                break
            if seat_index >= len(students):
                break
            student = students[seat_index]
            assignments.append({
                "student_id": student["id"],
                "room_id": room["id"],
                "row": seat["row"],
                "column": seat["column"],
                "seat_number": seat["seat_number"],
                "student_name": student["name"],
                "roll_no": student["roll_no"],
            })
            seat_index += 1
        if len(assignments) >= total_students:
            break

    if len(assignments) < total_students:
        raise ValueError("Unable to generate arrangement with the given constraints.")

    result = validate_arrangement(assignments, exam_id=exam_id)
    if not result["valid"]:
        raise ValueError(result["message"])

    score = quality_score_from_assignments(assignments)
    arrangement_id = execute(
        """
        INSERT INTO seating_arrangements (exam_id, status, quality_score, created_at, updated_at)
        VALUES (%s, 'GENERATED', %s, NOW(), NOW())
        """,
        (exam_id, score),
    )
    for assignment in assignments:
        execute(
            """
            INSERT INTO seat_assignments 
            (arrangement_id, student_id, room_id, row_no, column_no, seat_number, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """,
            (arrangement_id, assignment["student_id"], assignment["room_id"], assignment["row"], assignment["column"], assignment["seat_number"]),
        )

    return {"arrangement_id": arrangement_id, "assignments": assignments, "quality_score": score}


def list_arrangements_for_exam(exam_id):
    return fetch_all("SELECT * FROM seating_arrangements WHERE exam_id = %s ORDER BY created_at DESC", (exam_id,))


def publish_arrangement(arrangement_id):
    arrangement = fetch_one("SELECT * FROM seating_arrangements WHERE id = %s", (arrangement_id,))
    if not arrangement:
        raise ValueError("Arrangement not found.")
    validation = validate_arrangement_for_db(arrangement_id)
    if not validation["valid"]:
        raise ValueError(validation["message"])
    execute("UPDATE seating_arrangements SET status = 'PUBLISHED', updated_at = NOW() WHERE id = %s", (arrangement_id,))
    return {"success": True, "message": "Seating arrangement published."}


def validate_arrangement_for_db(arrangement_id):
    assignments = fetch_all(
        """
        SELECT sa.*, s.name AS student_name, s.roll_no
        FROM seat_assignments sa
        LEFT JOIN students s ON s.id = sa.student_id
        WHERE sa.arrangement_id = %s
        """,
        (arrangement_id,),
    )
    return validate_arrangement(assignments, arrangement_id=arrangement_id)
