class Course:
    """Course domain entity and validation schema."""

    def __init__(self, course_id, title, credits, faculty_id, max_capacity=30, semester="Fall 2026"):
        self.course_id = course_id
        self.title = title
        self.credits = int(credits)
        self.faculty_id = faculty_id
        self.max_capacity = int(max_capacity)
        self.enrolled_count = 0
        self.semester = semester

    @classmethod
    def validate(cls, course_id, title, credits, faculty_id, max_capacity=30):
        if not course_id or not str(course_id).strip():
            raise ValueError("Course ID is mandatory.")
        if not title or not str(title).strip():
            raise ValueError("Course title is mandatory.")
        try:
            c = int(credits)
            if c < 1 or c > 6:
                raise ValueError("Course credits must be between 1 and 6.")
        except (ValueError, TypeError):
            raise ValueError("Course credits must be a valid integer between 1 and 6.")
        if not faculty_id:
            raise ValueError("Faculty ID assignment is mandatory.")
        try:
            cap = int(max_capacity)
            if cap < 1:
                raise ValueError("Max capacity must be at least 1.")
        except (ValueError, TypeError):
            raise ValueError("Max capacity must be an integer greater than 0.")
        return True

    def to_dict(self):
        return {
            "course_id": self.course_id,
            "title": self.title,
            "credits": self.credits,
            "faculty_id": self.faculty_id,
            "max_capacity": self.max_capacity,
            "enrolled_count": self.enrolled_count,
            "semester": self.semester
        }
