import pytest
from database.db import db
from app.services.student_service import StudentService


@pytest.fixture(autouse=True)
def run_around_tests():
    db.reset()
    yield
    db.reset()


def test_record_marks_letter_grade_mapping():
    # S104 has 0 initial grades
    # Test Grade A: 95.0
    grade_a = StudentService.record_marks("S104", "CS101", "Fall 2026", 95.0)
    assert grade_a["letter_grade"] == "A"
    assert grade_a["grade_points"] == 4.0

    # Test Grade B: 85.0
    grade_b = StudentService.record_marks("S104", "CS102", "Fall 2026", 85.0)
    assert grade_b["letter_grade"] == "B"
    assert grade_b["grade_points"] == 3.0

    # Test Grade C: 75.0
    grade_c = StudentService.record_marks("S104", "CS104", "Fall 2026", 75.0)
    assert grade_c["letter_grade"] == "C"
    assert grade_c["grade_points"] == 2.0

    # Test Grade D: 62.0
    grade_d = StudentService.record_marks("S104", "CS105", "Fall 2026", 62.0)
    assert grade_d["letter_grade"] == "D"
    assert grade_d["grade_points"] == 1.0

    # Test Grade F: 45.0
    grade_f = StudentService.record_marks("S104", "CS106", "Fall 2026", 45.0)
    assert grade_f["letter_grade"] == "F"
    assert grade_f["grade_points"] == 0.0


def test_record_marks_out_of_bounds_fails():
    with pytest.raises(ValueError, match="between 0.0 and 100.0"):
        StudentService.record_marks("S101", "CS101", "Fall 2026", 105.0)

    with pytest.raises(ValueError, match="between 0.0 and 100.0"):
        StudentService.record_marks("S101", "CS101", "Fall 2026", -5.0)


def test_gpa_calculation_weighted_credits():
    """Verify weighted GPA formula: sum(credits * grade_points) / sum(credits)."""
    # Clear S104 state
    # CS101 (4 credits): Marks 90 (Grade A, 4.0 points) -> 4 * 4.0 = 16.0
    # CS102 (3 credits): Marks 80 (Grade B, 3.0 points) -> 3 * 3.0 = 9.0
    # Total quality points = 25.0, Total credits = 7
    # Expected GPA = 25.0 / 7 = 3.57
    StudentService.record_marks("S104", "CS101", "Fall 2026", 90.0)
    StudentService.record_marks("S104", "CS102", "Fall 2026", 80.0)

    res = StudentService.calculate_student_gpa("S104")
    assert res["gpa"] == 3.57
    assert res["academic_standing"] == "Dean's List"
    assert res["total_credits"] == 7
    assert db.students["S104"]["cumulative_gpa"] == 3.57


def test_academic_probation_evaluation():
    # S104 gets failing grades
    # CS101 (4 credits): Marks 50 (Grade F, 0.0 points) -> 0.0
    StudentService.record_marks("S104", "CS101", "Fall 2026", 50.0)
    res = StudentService.calculate_student_gpa("S104")
    assert res["gpa"] == 0.0
    assert res["academic_standing"] == "Academic Probation"


def test_student_transcript_completeness():
    transcript = StudentService.get_student_transcript("S101")
    assert transcript["student"]["student_id"] == "S101"
    assert len(transcript["grades"]) >= 2
    assert transcript["gpa"] > 0.0
    assert transcript["academic_standing"] in ["Dean's List", "Good Standing"]
    assert transcript["total_credits_completed"] > 0
