from flask import Blueprint, render_template
from app.services.student_service import StudentService

views_bp = Blueprint("views", __name__)


@views_bp.route("/", methods=["GET"])
def dashboard():
    """Enterprise Student Record & Academic Management Dashboard View."""
    stats = StudentService.get_dashboard_stats()
    students = StudentService.list_students()
    courses = StudentService.list_courses()
    return render_template("index.html", stats=stats, students=students, courses=courses)
