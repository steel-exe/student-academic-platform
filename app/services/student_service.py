from datetime import datetime, timezone
from database.db import db
from app.models.student import Student
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.grade import Grade


class StudentService:
    """Core enterprise business logic for Student Record & Academic Management Platform."""

    @staticmethod
    def add_student(student_id, name, email, department="Computer Science", semester=1):
        Student.validate(student_id, name, email, department, semester)
        if student_id in db.students:
            raise ValueError(f"Student with ID '{student_id}' already exists.")

        student_record = {
            "student_id": student_id,
            "name": name,
            "email": email,
            "department": department,
            "semester": int(semester),
            "enrolled_credits": 0,
            "cumulative_gpa": 0.0,
            "academic_standing": "Good Standing"
        }
        db.students[student_id] = student_record
        return student_record

    @staticmethod
    def get_student(student_id):
        return db.students.get(student_id)

    @staticmethod
    def list_students():
        return list(db.students.values())

    @staticmethod
    def delete_student(student_id):
        student = db.students.get(student_id)
        if not student:
            raise ValueError(f"Student '{student_id}' not found.")

        # Check for active course enrollments
        active_enrollments = [
            e for e in db.enrollments
            if e["student_id"] == student_id and e["status"] == "ENROLLED"
        ]
        if active_enrollments:
            raise ValueError(f"Cannot delete student '{student_id}' with active course enrollments.")

        del db.students[student_id]
        return True

    @staticmethod
    def search_students(query=""):
        q = (query or "").lower().strip()
        if not q:
            return list(db.students.values())
        return [
            s for s in db.students.values()
            if q in s["name"].lower()
            or q in s["student_id"].lower()
            or q in s["email"].lower()
            or q in s.get("department", "").lower()
        ]

    @staticmethod
    def add_course(course_id, title, credits, faculty_id, max_capacity=30, semester="Fall 2026"):
        Course.validate(course_id, title, credits, faculty_id, max_capacity)
        if course_id in db.courses:
            raise ValueError(f"Course with ID '{course_id}' already exists.")

        course_record = {
            "course_id": course_id,
            "title": title,
            "credits": int(credits),
            "faculty_id": faculty_id,
            "max_capacity": int(max_capacity),
            "enrolled_count": 0,
            "semester": semester
        }
        db.courses[course_id] = course_record
        return course_record

    @staticmethod
    def get_course(course_id):
        return db.courses.get(course_id)

    @staticmethod
    def list_courses():
        return list(db.courses.values())

    @staticmethod
    def search_courses(query=""):
        q = (query or "").lower().strip()
        if not q:
            return list(db.courses.values())
        return [
            c for c in db.courses.values()
            if q in c["title"].lower()
            or q in c["course_id"].lower()
            or q in c.get("faculty_id", "").lower()
        ]

    @staticmethod
    def enroll_student(student_id, course_id, semester="Fall 2026"):
        Enrollment.validate(student_id, course_id, semester)

        student = db.students.get(student_id)
        if not student:
            raise ValueError(f"Student '{student_id}' not found in registry.")

        course = db.courses.get(course_id)
        if not course:
            raise ValueError(f"Course '{course_id}' not found in catalog.")

        # Check for duplicate active enrollment
        for enr in db.enrollments:
            if enr["student_id"] == student_id and enr["course_id"] == course_id \
               and enr["semester"] == semester and enr["status"] == "ENROLLED":
                raise ValueError(
                    f"Student '{student_id}' is already enrolled in course '{course_id}' for semester '{semester}'."
                )

        # Check course capacity
        if course["enrolled_count"] >= course["max_capacity"]:
            raise ValueError(
                f"Course '{course['title']}' has reached maximum enrollment capacity ({course['max_capacity']})."
            )

        # Calculate current active semester credits
        active_credits = sum(
            db.courses[e["course_id"]]["credits"]
            for e in db.enrollments
            if e["student_id"] == student_id and e["semester"] == semester and e["status"] == "ENROLLED"
            and e["course_id"] in db.courses
        )

        # Business Rule: Maximum 18 credits per semester
        if active_credits + course["credits"] > 18:
            raise ValueError(
                f"Semester credit limit exceeded (Max: 18 credits). "
                f"Current: {active_credits}, Course: {course['credits']}, Projected: {active_credits + course['credits']}."
            )

        # Update course and student records
        course["enrolled_count"] += 1
        student["enrolled_credits"] += course["credits"]

        enrollment_record = {
            "enrollment_id": f"ENR-{len(db.enrollments) + 1:04d}",
            "student_id": student_id,
            "course_id": course_id,
            "semester": semester,
            "status": "ENROLLED",
            "enrolled_at": datetime.now(timezone.utc).isoformat()
        }
        db.enrollments.append(enrollment_record)
        return enrollment_record

    @staticmethod
    def drop_course(student_id, course_id, semester="Fall 2026"):
        student = db.students.get(student_id)
        course = db.courses.get(course_id)
        if not student or not course:
            raise ValueError("Invalid student or course identifier.")

        active_enrollment = None
        for enr in db.enrollments:
            if enr["student_id"] == student_id and enr["course_id"] == course_id \
               and enr["semester"] == semester and enr["status"] == "ENROLLED":
                active_enrollment = enr
                break

        if not active_enrollment:
            raise ValueError(
                f"No active enrollment found for student '{student_id}' in course '{course_id}' for semester '{semester}'."
            )

        active_enrollment["status"] = "DROPPED"
        active_enrollment["dropped_at"] = datetime.now(timezone.utc).isoformat()

        course["enrolled_count"] = max(0, course["enrolled_count"] - 1)
        student["enrolled_credits"] = max(0, student["enrolled_credits"] - course["credits"])
        return active_enrollment

    @staticmethod
    def record_marks(student_id, course_id, semester, marks):
        Grade.validate(student_id, course_id, semester, marks)

        student = db.students.get(student_id)
        if not student:
            raise ValueError(f"Student '{student_id}' not found.")

        course = db.courses.get(course_id)
        if not course:
            raise ValueError(f"Course '{course_id}' not found.")

        letter_grade, grade_points = Grade.calculate_grade(marks)

        # Update enrollment status to COMPLETED if active
        for enr in db.enrollments:
            if enr["student_id"] == student_id and enr["course_id"] == course_id \
               and enr["semester"] == semester and enr["status"] == "ENROLLED":
                enr["status"] = "COMPLETED"
                student["enrolled_credits"] = max(0, student["enrolled_credits"] - course["credits"])
                break

        # Check if existing grade needs update
        existing_grade = None
        for g in db.grades:
            if g["student_id"] == student_id and g["course_id"] == course_id and g["semester"] == semester:
                existing_grade = g
                break

        if existing_grade:
            existing_grade["marks"] = float(marks)
            existing_grade["letter_grade"] = letter_grade
            existing_grade["grade_points"] = grade_points
            existing_grade["recorded_at"] = datetime.now(timezone.utc).isoformat()
            grade_record = existing_grade
        else:
            grade_record = {
                "grade_id": f"GRD-{len(db.grades) + 1:04d}",
                "student_id": student_id,
                "course_id": course_id,
                "semester": semester,
                "marks": float(marks),
                "letter_grade": letter_grade,
                "grade_points": grade_points,
                "recorded_at": datetime.now(timezone.utc).isoformat()
            }
            db.grades.append(grade_record)

        # Recompute GPA and standing
        StudentService.calculate_student_gpa(student_id)
        return grade_record

    @staticmethod
    def calculate_student_gpa(student_id):
        student = db.students.get(student_id)
        if not student:
            raise ValueError(f"Student '{student_id}' not found.")

        student_grades = [g for g in db.grades if g["student_id"] == student_id]
        if not student_grades:
            student["cumulative_gpa"] = 0.0
            student["academic_standing"] = "Good Standing"
            return {"gpa": 0.0, "academic_standing": "Good Standing", "total_credits": 0}

        total_quality_points = 0.0
        total_credits = 0

        for g in student_grades:
            course = db.courses.get(g["course_id"])
            credits = course["credits"] if course else 3
            total_quality_points += g["grade_points"] * credits
            total_credits += credits

        gpa = round(total_quality_points / total_credits, 2) if total_credits > 0 else 0.0

        if gpa >= 3.5:
            standing = "Dean's List"
        elif gpa >= 2.0:
            standing = "Good Standing"
        else:
            standing = "Academic Probation"

        student["cumulative_gpa"] = gpa
        student["academic_standing"] = standing
        return {
            "gpa": gpa,
            "academic_standing": standing,
            "total_credits": total_credits
        }

    @staticmethod
    def get_student_transcript(student_id):
        student = db.students.get(student_id)
        if not student:
            raise ValueError(f"Student '{student_id}' not found.")

        grades = []
        for g in db.grades:
            if g["student_id"] == student_id:
                course = db.courses.get(g["course_id"], {})
                grades.append({
                    "grade_id": g["grade_id"],
                    "course_id": g["course_id"],
                    "course_title": course.get("title", "Unknown"),
                    "credits": course.get("credits", 0),
                    "semester": g["semester"],
                    "marks": g["marks"],
                    "letter_grade": g["letter_grade"],
                    "grade_points": g["grade_points"]
                })

        gpa_info = StudentService.calculate_student_gpa(student_id)

        return {
            "student": student,
            "grades": grades,
            "gpa": gpa_info["gpa"],
            "academic_standing": gpa_info["academic_standing"],
            "total_credits_completed": gpa_info["total_credits"]
        }

    @staticmethod
    def get_dashboard_stats():
        students = list(db.students.values())
        courses = list(db.courses.values())
        enrollments = [e for e in db.enrollments if e["status"] == "ENROLLED"]
        grades = list(db.grades)

        avg_gpa = 0.0
        graded_students = [s["cumulative_gpa"] for s in students if s["cumulative_gpa"] > 0]
        if graded_students:
            avg_gpa = round(sum(graded_students) / len(graded_students), 2)

        return {
            "total_students": len(students),
            "total_courses": len(courses),
            "active_enrollments": len(enrollments),
            "total_grades_recorded": len(grades),
            "average_gpa": avg_gpa,
            "deans_list_count": len([s for s in students if s.get("academic_standing") == "Dean's List"]),
            "probation_count": len([s for s in students if s.get("academic_standing") == "Academic Probation"])
        }
