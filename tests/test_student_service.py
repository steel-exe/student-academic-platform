import pytest
from database.db import db
from app.services.student_service import StudentService


@pytest.fixture(autouse=True)
def run_around_tests():
    db.reset()
    yield
    db.reset()


def test_add_student_success():
    student = StudentService.add_student(
        student_id="S200",
        name="Ada Lovelace",
        email="ada@computing.edu",
        department="Computer Science",
        semester=1
    )
    assert student["student_id"] == "S200"
    assert student["name"] == "Ada Lovelace"
    assert student["enrolled_credits"] == 0
    assert student["cumulative_gpa"] == 0.0
    assert student["academic_standing"] == "Good Standing"


def test_add_duplicate_student_raises_error():
    with pytest.raises(ValueError, match="already exists"):
        StudentService.add_student("S101", "Duplicate Jane", "jane2@university.edu")


def test_add_student_invalid_email_fails():
    with pytest.raises(ValueError, match="valid university email"):
        StudentService.add_student("S999", "Invalid Email", "invalid-email-string")


def test_add_student_missing_fields_fails():
    with pytest.raises(ValueError, match="Student ID is mandatory"):
        StudentService.add_student("", "No ID", "noid@edu.com")


def test_delete_student_success():
    # S104 has 0 active enrollments in seed data
    assert StudentService.delete_student("S104") is True
    assert StudentService.get_student("S104") is None


def test_delete_student_with_active_enrollments_fails():
    # S101 has active enrollments in seed data
    with pytest.raises(ValueError, match="active course enrollments"):
        StudentService.delete_student("S101")


def test_delete_nonexistent_student_fails():
    with pytest.raises(ValueError, match="not found"):
        StudentService.delete_student("S9999")


def test_search_students():
    results = StudentService.search_students("Jane")
    assert len(results) >= 1
    assert any(s["student_id"] == "S101" for s in results)

    results_dept = StudentService.search_students("Software Engineering")
    assert len(results_dept) >= 1
    assert any(s["student_id"] == "S102" for s in results_dept)

    # Empty query returns all
    all_students = StudentService.search_students("")
    assert len(all_students) >= 4


def test_course_models_and_validations():
    # Course validations
    with pytest.raises(ValueError, match="Course ID is mandatory"):
        StudentService.add_course("", "Title", 3, "F201")

    with pytest.raises(ValueError, match="Course title is mandatory"):
        StudentService.add_course("CS777", "", 3, "F201")

    with pytest.raises(ValueError, match="between 1 and 6"):
        StudentService.add_course("CS777", "Invalid Credits", 0, "F201")

    with pytest.raises(ValueError, match="Faculty ID assignment is mandatory"):
        StudentService.add_course("CS777", "No Faculty", 3, "")

    with pytest.raises(ValueError, match="greater than 0"):
        StudentService.add_course("CS777", "Zero Cap", 3, "F201", max_capacity=0)

    # Duplicate course error
    with pytest.raises(ValueError, match="already exists"):
        StudentService.add_course("CS101", "Duplicate CS101", 4, "F201")

    # Search courses
    assert len(StudentService.search_courses("")) >= 6
    assert len(StudentService.search_courses("DevOps")) >= 1
    assert len(StudentService.list_courses()) >= 6


def test_models_to_dict():
    from app.models.student import Student
    from app.models.course import Course
    from app.models.enrollment import Enrollment
    from app.models.grade import Grade

    st = Student("S888", "Student Eight", "eight@uni.edu", "CS", 2)
    st_dict = st.to_dict()
    assert st_dict["student_id"] == "S888"

    cr = Course("CS888", "Advanced Systems", 4, "F201", 30)
    cr_dict = cr.to_dict()
    assert cr_dict["course_id"] == "CS888"

    enr = Enrollment("ENR-8888", "S888", "CS888")
    assert enr.to_dict()["enrollment_id"] == "ENR-8888"

    grd = Grade("GRD-8888", "S888", "CS888", "Fall 2026", 88.0)
    assert grd.to_dict()["letter_grade"] == "B"

