from datetime import datetime, timezone


class Enrollment:
    """Enrollment entity representing student registration in a course."""

    def __init__(self, enrollment_id, student_id, course_id, semester="Fall 2026", status="ENROLLED"):
        self.enrollment_id = enrollment_id
        self.student_id = student_id
        self.course_id = course_id
        self.semester = semester
        self.status = status
        self.enrolled_at = datetime.now(timezone.utc).isoformat()

    @classmethod
    def validate(cls, student_id, course_id, semester="Fall 2026"):
        if not student_id:
            raise ValueError("Student ID is required for enrollment.")
        if not course_id:
            raise ValueError("Course ID is required for enrollment.")
        if not semester:
            raise ValueError("Semester is required for enrollment.")
        return True

    def to_dict(self):
        return {
            "enrollment_id": self.enrollment_id,
            "student_id": self.student_id,
            "course_id": self.course_id,
            "semester": self.semester,
            "status": self.status,
            "enrolled_at": self.enrolled_at
        }
