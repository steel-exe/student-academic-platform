from flask import Blueprint, request, jsonify
from app.services.student_service import StudentService

api_bp = Blueprint("api", __name__)


@api_bp.route("/health", methods=["GET"])
def healthcheck():
    """Liveness and readiness endpoint for Kubernetes & Docker healthchecks."""
    return jsonify({
        "status": "UP",
        "service": "Enterprise Student Record & Academic Management Platform",
        "version": "1.0.0"
    }), 200


@api_bp.route("/dashboard", methods=["GET"])
def get_dashboard():
    """High-level metrics and system summary."""
    stats = StudentService.get_dashboard_stats()
    return jsonify({"status": "SUCCESS", "metrics": stats}), 200


@api_bp.route("/students", methods=["GET"])
def list_students():
    """List or search registered students."""
    q = request.args.get("q", "")
    students = StudentService.search_students(q)
    return jsonify({"count": len(students), "students": students}), 200


@api_bp.route("/students", methods=["POST"])
def register_student():
    """Register a new student."""
    data = request.get_json() or {}
    try:
        student = StudentService.add_student(
            student_id=data.get("student_id"),
            name=data.get("name"),
            email=data.get("email"),
            department=data.get("department", "Computer Science"),
            semester=data.get("semester", 1)
        )
        return jsonify({"message": "Student registered successfully", "student": student}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@api_bp.route("/students/<student_id>", methods=["GET"])
def get_student(student_id):
    """Retrieve individual student profile."""
    student = StudentService.get_student(student_id)
    if not student:
        return jsonify({"error": f"Student '{student_id}' not found"}), 404
    return jsonify(student), 200


@api_bp.route("/students/<student_id>", methods=["DELETE"])
def delete_student(student_id):
    """Delete a student record if no active enrollments exist."""
    try:
        StudentService.delete_student(student_id)
        return jsonify({"message": f"Student '{student_id}' deleted successfully"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@api_bp.route("/students/<student_id>/transcript", methods=["GET"])
def get_transcript(student_id):
    """Generate official academic transcript with GPA and standing."""
    try:
        transcript = StudentService.get_student_transcript(student_id)
        return jsonify(transcript), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


@api_bp.route("/courses", methods=["GET"])
def list_courses():
    """List or search academic course catalog."""
    q = request.args.get("q", "")
    courses = StudentService.search_courses(q)
    return jsonify({"count": len(courses), "courses": courses}), 200


@api_bp.route("/courses", methods=["POST"])
def add_course():
    """Create a new course entry."""
    data = request.get_json() or {}
    try:
        course = StudentService.add_course(
            course_id=data.get("course_id"),
            title=data.get("title"),
            credits=data.get("credits"),
            faculty_id=data.get("faculty_id"),
            max_capacity=data.get("max_capacity", 30),
            semester=data.get("semester", "Fall 2026")
        )
        return jsonify({"message": "Course added successfully", "course": course}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@api_bp.route("/courses/<course_id>", methods=["GET"])
def get_course(course_id):
    """Retrieve course details."""
    course = StudentService.get_course(course_id)
    if not course:
        return jsonify({"error": f"Course '{course_id}' not found"}), 404
    return jsonify(course), 200


@api_bp.route("/enroll", methods=["POST"])
def enroll_student():
    """Enroll student in a course with credit limit and capacity enforcement."""
    data = request.get_json() or {}
    try:
        enrollment = StudentService.enroll_student(
            student_id=data.get("student_id"),
            course_id=data.get("course_id"),
            semester=data.get("semester", "Fall 2026")
        )
        return jsonify({"message": "Enrollment completed successfully", "enrollment": enrollment}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@api_bp.route("/drop", methods=["POST"])
def drop_course():
    """Drop course registration."""
    data = request.get_json() or {}
    try:
        drop_record = StudentService.drop_course(
            student_id=data.get("student_id"),
            course_id=data.get("course_id"),
            semester=data.get("semester", "Fall 2026")
        )
        return jsonify({"message": "Course dropped successfully", "enrollment": drop_record}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@api_bp.route("/grades", methods=["POST"])
@api_bp.route("/marks", methods=["POST"])
def record_marks():
    """Record marks/grades and update GPA/academic standing."""
    data = request.get_json() or {}
    try:
        grade = StudentService.record_marks(
            student_id=data.get("student_id"),
            course_id=data.get("course_id"),
            semester=data.get("semester", "Fall 2026"),
            marks=data.get("marks")
        )
        return jsonify({"message": "Marks recorded successfully", "grade": grade}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
