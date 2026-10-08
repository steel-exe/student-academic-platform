import pytest
from app import create_app
from database.db import db


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        db.reset()
        yield client
        db.reset()


def test_healthcheck_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["status"] == "UP"
    assert "Enterprise Student Record & Academic Management Platform" in json_data["service"]
    assert json_data["version"] == "1.0.0"


def test_dashboard_endpoint(client):
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["status"] == "SUCCESS"
    assert "metrics" in json_data
    assert json_data["metrics"]["total_students"] >= 4
    assert json_data["metrics"]["total_courses"] >= 6


def test_list_students_api(client):
    response = client.get("/api/students")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["count"] >= 4
    assert len(json_data["students"]) >= 4


def test_register_student_api(client):
    payload = {
        "student_id": "S301",
        "name": "Tim Berners-Lee",
        "email": "tim@cern.ch",
        "department": "Computer Science",
        "semester": 1
    }
    response = client.post("/api/students", json=payload)
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data["message"] == "Student registered successfully"
    assert json_data["student"]["student_id"] == "S301"


def test_register_student_invalid_fails(client):
    payload = {
        "student_id": "",
        "name": "Invalid",
        "email": "not-an-email"
    }
    response = client.post("/api/students", json=payload)
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_get_student_api(client):
    response = client.get("/api/students/S101")
    assert response.status_code == 200
    assert response.get_json()["name"] == "Jane Doe"

    not_found = client.get("/api/students/S9999")
    assert not_found.status_code == 404


def test_list_courses_api(client):
    response = client.get("/api/courses")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["count"] >= 6


def test_add_course_api(client):
    payload = {
        "course_id": "CS201",
        "title": "Compiler Design",
        "credits": 4,
        "faculty_id": "F201",
        "max_capacity": 30,
        "semester": "Fall 2026"
    }
    response = client.post("/api/courses", json=payload)
    assert response.status_code == 201
    assert response.get_json()["course"]["course_id"] == "CS201"


def test_api_enroll_and_drop_flow(client):
    enroll_payload = {
        "student_id": "S104",
        "course_id": "CS104",
        "semester": "Fall 2026"
    }
    response = client.post("/api/enroll", json=enroll_payload)
    assert response.status_code == 200
    assert "Enrollment completed successfully" in response.get_json()["message"]

    drop_payload = {
        "student_id": "S104",
        "course_id": "CS104",
        "semester": "Fall 2026"
    }
    drop_res = client.post("/api/drop", json=drop_payload)
    assert drop_res.status_code == 200
    assert "Course dropped successfully" in drop_res.get_json()["message"]


def test_api_enroll_credit_limit_rejection(client):
    # Enroll S104 in courses up to 16 credits
    client.post("/api/enroll", json={"student_id": "S104", "course_id": "CS101", "semester": "Fall 2026"})
    client.post("/api/enroll", json={"student_id": "S104", "course_id": "CS103", "semester": "Fall 2026"})
    client.post("/api/enroll", json={"student_id": "S104", "course_id": "CS105", "semester": "Fall 2026"})
    client.post("/api/enroll", json={"student_id": "S104", "course_id": "CS106", "semester": "Fall 2026"})

    # Attempt to enroll in CS102 (3 credits) -> total 19 > 18
    resp = client.post("/api/enroll", json={"student_id": "S104", "course_id": "CS102", "semester": "Fall 2026"})
    assert resp.status_code == 400
    assert "credit limit exceeded" in resp.get_json()["error"]


def test_api_record_marks_and_transcript(client):
    payload = {
        "student_id": "S104",
        "course_id": "CS101",
        "semester": "Fall 2026",
        "marks": 94.0
    }
    resp = client.post("/api/grades", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["grade"]["letter_grade"] == "A"
    assert data["grade"]["grade_points"] == 4.0

    # Verify transcript reflects new grade
    trans_resp = client.get("/api/students/S104/transcript")
    assert trans_resp.status_code == 200
    trans_data = trans_resp.get_json()
    assert trans_data["gpa"] == 4.0
    assert trans_data["academic_standing"] == "Dean's List"


def test_delete_student_api(client):
    # S104 has no active enrollments
    del_resp = client.delete("/api/students/S104")
    assert del_resp.status_code == 200
    assert "deleted successfully" in del_resp.get_json()["message"]

    # S101 has active enrollments -> 400
    fail_del = client.delete("/api/students/S101")
    assert fail_del.status_code == 400

    # Nonexistent -> 400
    not_found_del = client.delete("/api/students/S9999")
    assert not_found_del.status_code == 400


def test_get_course_api_and_add_failure(client):
    res = client.get("/api/courses/CS101")
    assert res.status_code == 200
    assert res.get_json()["title"] == "Cloud Native DevOps Architecture"

    not_found = client.get("/api/courses/CS9999")
    assert not_found.status_code == 404

    # Add course with missing field -> 400
    bad_course = client.post("/api/courses", json={"course_id": ""})
    assert bad_course.status_code == 400


def test_web_ui_dashboard_route(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Enterprise Student Record" in response.data

