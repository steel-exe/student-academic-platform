class Student:
    """Student domain model and validation schema."""

    def __init__(self, student_id, name, email, department="Computer Science", semester=1):
        self.student_id = student_id
        self.name = name
        self.email = email
        self.department = department
        self.semester = int(semester)
        self.enrolled_credits = 0
        self.cumulative_gpa = 0.0
        self.academic_standing = "Good Standing"

    @classmethod
    def validate(cls, student_id, name, email, department=None, semester=1):
        if not student_id or not str(student_id).strip():
            raise ValueError("Student ID is mandatory and cannot be empty.")
        if not name or not str(name).strip():
            raise ValueError("Student name is mandatory and cannot be empty.")
        if not email or "@" not in str(email):
            raise ValueError("A valid university email address is mandatory.")
        try:
            sem = int(semester)
            if sem < 1 or sem > 12:
                raise ValueError("Semester must be between 1 and 12.")
        except (ValueError, TypeError):
            raise ValueError("Semester must be an integer between 1 and 12.")
        return True

    def to_dict(self):
        return {
            "student_id": self.student_id,
            "name": self.name,
            "email": self.email,
            "department": self.department,
            "semester": self.semester,
            "enrolled_credits": self.enrolled_credits,
            "cumulative_gpa": round(self.cumulative_gpa, 2),
            "academic_standing": self.academic_standing
        }
