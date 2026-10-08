import threading


class Database:
    """Thread-safe in-memory database store for Enterprise Student Record & Academic Platform."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(Database, cls).__new__(cls)
                cls._instance._init_db()
            return cls._instance

    def _init_db(self):
        self.students = {}
        self.courses = {}
        self.faculty = {}
        self.enrollments = []
        self.grades = []
        self._seed_initial_data()

    def _seed_initial_data(self):
        # Seed faculty members
        self.faculty["F201"] = {
            "faculty_id": "F201",
            "name": "Dr. Alan Turing",
            "department": "Computer Science",
            "email": "alan.turing@university.edu"
        }
        self.faculty["F202"] = {
            "faculty_id": "F202",
            "name": "Dr. Grace Hopper",
            "department": "Software Engineering",
            "email": "grace.hopper@university.edu"
        }
        self.faculty["F203"] = {
            "faculty_id": "F203",
            "name": "Dr. John von Neumann",
            "department": "Data Science",
            "email": "john.neumann@university.edu"
        }

        # Seed default student records
        self.students["S101"] = {
            "student_id": "S101",
            "name": "Jane Doe",
            "email": "jane.doe@university.edu",
            "department": "Computer Science",
            "semester": 4,
            "enrolled_credits": 7,
            "cumulative_gpa": 3.85,
            "academic_standing": "Dean's List"
        }
        self.students["S102"] = {
            "student_id": "S102",
            "name": "John Smith",
            "email": "john.smith@university.edu",
            "department": "Software Engineering",
            "semester": 3,
            "enrolled_credits": 4,
            "cumulative_gpa": 3.20,
            "academic_standing": "Good Standing"
        }
        self.students["S103"] = {
            "student_id": "S103",
            "name": "Emily Davis",
            "email": "emily.davis@university.edu",
            "department": "Data Science",
            "semester": 2,
            "enrolled_credits": 4,
            "cumulative_gpa": 3.90,
            "academic_standing": "Dean's List"
        }
        self.students["S104"] = {
            "student_id": "S104",
            "name": "Michael Brown",
            "email": "michael.brown@university.edu",
            "department": "Computer Science",
            "semester": 1,
            "enrolled_credits": 0,
            "cumulative_gpa": 0.0,
            "academic_standing": "Good Standing"
        }

        # Seed default academic course catalog
        self.courses["CS101"] = {
            "course_id": "CS101",
            "title": "Cloud Native DevOps Architecture",
            "credits": 4,
            "faculty_id": "F201",
            "max_capacity": 30,
            "enrolled_count": 2,
            "semester": "Fall 2026"
        }
        self.courses["CS102"] = {
            "course_id": "CS102",
            "title": "Continuous Delivery & Automation",
            "credits": 3,
            "faculty_id": "F202",
            "max_capacity": 25,
            "enrolled_count": 1,
            "semester": "Fall 2026"
        }
        self.courses["CS103"] = {
            "course_id": "CS103",
            "title": "Distributed Microservices & Cloud",
            "credits": 4,
            "faculty_id": "F201",
            "max_capacity": 30,
            "enrolled_count": 1,
            "semester": "Fall 2026"
        }
        self.courses["CS104"] = {
            "course_id": "CS104",
            "title": "Database Systems & Data Modeling",
            "credits": 3,
            "faculty_id": "F203",
            "max_capacity": 35,
            "enrolled_count": 0,
            "semester": "Fall 2026"
        }
        self.courses["CS105"] = {
            "course_id": "CS105",
            "title": "Software Quality & Test Engineering",
            "credits": 4,
            "faculty_id": "F202",
            "max_capacity": 25,
            "enrolled_count": 0,
            "semester": "Fall 2026"
        }
        self.courses["CS106"] = {
            "course_id": "CS106",
            "title": "Enterprise Capstone Practicum",
            "credits": 4,
            "faculty_id": "F201",
            "max_capacity": 20,
            "enrolled_count": 0,
            "semester": "Fall 2026"
        }

        # Seed sample active enrollments
        self.enrollments.append({
            "enrollment_id": "ENR-0001",
            "student_id": "S101",
            "course_id": "CS101",
            "semester": "Fall 2026",
            "status": "ENROLLED",
            "enrolled_at": "2026-09-01T09:00:00"
        })
        self.enrollments.append({
            "enrollment_id": "ENR-0002",
            "student_id": "S101",
            "course_id": "CS102",
            "semester": "Fall 2026",
            "status": "ENROLLED",
            "enrolled_at": "2026-09-01T09:05:00"
        })
        self.enrollments.append({
            "enrollment_id": "ENR-0003",
            "student_id": "S102",
            "course_id": "CS101",
            "semester": "Fall 2026",
            "status": "ENROLLED",
            "enrolled_at": "2026-09-02T10:15:00"
        })
        self.enrollments.append({
            "enrollment_id": "ENR-0004",
            "student_id": "S103",
            "course_id": "CS103",
            "semester": "Fall 2026",
            "status": "ENROLLED",
            "enrolled_at": "2026-09-03T11:30:00"
        })

        # Seed initial graded entries
        self.grades.append({
            "grade_id": "GRD-0001",
            "student_id": "S101",
            "course_id": "CS101",
            "semester": "Fall 2026",
            "marks": 94.0,
            "letter_grade": "A",
            "grade_points": 4.0,
            "recorded_at": "2026-09-25T14:00:00"
        })
        self.grades.append({
            "grade_id": "GRD-0002",
            "student_id": "S101",
            "course_id": "CS102",
            "semester": "Fall 2026",
            "marks": 86.0,
            "letter_grade": "B",
            "grade_points": 3.0,
            "recorded_at": "2026-09-26T14:30:00"
        })
        self.grades.append({
            "grade_id": "GRD-0003",
            "student_id": "S102",
            "course_id": "CS101",
            "semester": "Fall 2026",
            "marks": 82.0,
            "letter_grade": "B",
            "grade_points": 3.0,
            "recorded_at": "2026-09-27T15:00:00"
        })
        self.grades.append({
            "grade_id": "GRD-0004",
            "student_id": "S103",
            "course_id": "CS103",
            "semester": "Fall 2026",
            "marks": 96.0,
            "letter_grade": "A",
            "grade_points": 4.0,
            "recorded_at": "2026-09-28T16:00:00"
        })

    def reset(self):
        """Helper to restore state during unit testing teardowns."""
        with self._lock:
            self.students.clear()
            self.courses.clear()
            self.faculty.clear()
            self.enrollments.clear()
            self.grades.clear()
            self._seed_initial_data()


db = Database()
