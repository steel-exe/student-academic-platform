from datetime import datetime, timezone


class Grade:
    """Grade and marks evaluation entity."""

    GRADE_SCALE = [
        (90.0, "A", 4.0),
        (80.0, "B", 3.0),
        (70.0, "C", 2.0),
        (60.0, "D", 1.0),
        (0.0,  "F", 0.0),
    ]

    def __init__(self, grade_id, student_id, course_id, semester, marks):
        self.grade_id = grade_id
        self.student_id = student_id
        self.course_id = course_id
        self.semester = semester
        self.marks = float(marks)
        self.letter_grade, self.grade_points = self.calculate_grade(self.marks)
        self.recorded_at = datetime.now(timezone.utc).isoformat()

    @classmethod
    def calculate_grade(cls, marks):
        m = float(marks)
        for threshold, letter, points in cls.GRADE_SCALE:
            if m >= threshold:
                return letter, points
        return "F", 0.0

    @classmethod
    def validate(cls, student_id, course_id, semester, marks):
        if not student_id:
            raise ValueError("Student ID is mandatory.")
        if not course_id:
            raise ValueError("Course ID is mandatory.")
        if not semester:
            raise ValueError("Semester is mandatory.")
        try:
            m = float(marks)
            if m < 0.0 or m > 100.0:
                raise ValueError("Marks must be between 0.0 and 100.0.")
        except (ValueError, TypeError):
            raise ValueError("Marks must be a numerical value between 0.0 and 100.0.")
        return True

    def to_dict(self):
        return {
            "grade_id": self.grade_id,
            "student_id": self.student_id,
            "course_id": self.course_id,
            "semester": self.semester,
            "marks": round(self.marks, 1),
            "letter_grade": self.letter_grade,
            "grade_points": self.grade_points,
            "recorded_at": self.recorded_at
        }
