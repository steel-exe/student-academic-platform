import pytest
from database.db import db
from app.services.student_service import StudentService


@pytest.fixture(autouse=True)
def run_around_tests():
    db.reset()
    yield
    db.reset()


def test_enroll_student_success():
    # S104 has 0 credits initially
    initial_credits = db.students["S104"]["enrolled_credits"]
    initial_capacity = db.courses["CS104"]["enrolled_count"]

    enrollment = StudentService.enroll_student("S104", "CS104", "Fall 2026")
    assert enrollment["status"] == "ENROLLED"
    assert db.students["S104"]["enrolled_credits"] == initial_credits + 3
    assert db.courses["CS104"]["enrolled_count"] == initial_capacity + 1


def test_duplicate_course_enrollment_fails():
    with pytest.raises(ValueError, match="already enrolled in course"):
        # S101 is already enrolled in CS101 for Fall 2026 in seed data
        StudentService.enroll_student("S101", "CS101", "Fall 2026")


def test_course_capacity_enforcement():
    # Create a course with capacity of 1
    StudentService.add_course("CS999", "Special Seminar", 1, "F201", max_capacity=1)
    StudentService.enroll_student("S104", "CS999", "Fall 2026")

    # Second student enrolling should fail due to capacity
    with pytest.raises(ValueError, match="maximum enrollment capacity"):
        StudentService.enroll_student("S102", "CS999", "Fall 2026")


def test_credit_limit_18_enforcement():
    """Validates core enterprise business rule: maximum 18 credits per semester."""
    # S104 starts with 0 credits.
    # CS101 (4 cr) -> 4
    StudentService.enroll_student("S104", "CS101", "Fall 2026")
    # CS103 (4 cr) -> 8
    StudentService.enroll_student("S104", "CS103", "Fall 2026")
    # CS105 (4 cr) -> 12
    StudentService.enroll_student("S104", "CS105", "Fall 2026")
    # CS106 (4 cr) -> 16
    StudentService.enroll_student("S104", "CS106", "Fall 2026")

    assert db.students["S104"]["enrolled_credits"] == 16

    # Attempting to enroll in CS102 (3 cr) would bring total to 19 (> 18 limit)
    with pytest.raises(ValueError, match="credit limit exceeded"):
        StudentService.enroll_student("S104", "CS102", "Fall 2026")

    # Ensure state remained clean
    assert db.students["S104"]["enrolled_credits"] == 16


def test_drop_course_restores_credits_and_capacity():
    # S104 enrolls in CS104 (3 credits)
    StudentService.enroll_student("S104", "CS104", "Fall 2026")
    assert db.students["S104"]["enrolled_credits"] == 3
    assert db.courses["CS104"]["enrolled_count"] == 1

    # Now drop the course
    drop_rec = StudentService.drop_course("S104", "CS104", "Fall 2026")
    assert drop_rec["status"] == "DROPPED"
    assert db.students["S104"]["enrolled_credits"] == 0
    assert db.courses["CS104"]["enrolled_count"] == 0


def test_drop_nonexistent_enrollment_fails():
    with pytest.raises(ValueError, match="No active enrollment found"):
        StudentService.drop_course("S104", "CS105", "Fall 2026")
