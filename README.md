# Enterprise Student Record & Academic Management Platform

[![CI/CD Pipeline](https://img.shields.io/badge/CI%2FCD-Jenkins%20Declarative-blue.svg)](Jenkinsfile)
[![Tests](https://img.shields.io/badge/pytest-35%20passed%20%7C%2091%25%20coverage-brightgreen.svg)](reports/test-results.xml)
[![Docker](https://img.shields.io/badge/docker-student--academic--platform%3Av1.0.0-blue.svg)](Dockerfile)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Minikube%20NodePort%2030090-326ce5.svg)](k8s/)

An enterprise-grade, cloud-native student record and academic grading microservice built with Python, Flask, Pytest, Docker, Jenkins, and Kubernetes (Minikube).

---

## 1. System Architecture & Multi-Tier Project Structure

The platform is architected according to modern enterprise multi-tier software engineering standards:

```
devops/
├── app/
│   ├── __init__.py               # Flask Application Factory pattern (create_app)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── api.py                # REST API Endpoints (Health, Students, Courses, Enroll, Grades)
│   │   └── views.py              # Web Dashboard Controller (HTML/Jinja2 view)
│   ├── services/
│   │   ├── __init__.py
│   │   └── student_service.py    # Core Business Logic, Credit Limits & GPA Formula
│   ├── models/
│   │   ├── __init__.py
│   │   ├── student.py            # Student entity schema & validation
│   │   ├── course.py             # Course catalog entity schema & capacity rules
│   │   ├── enrollment.py         # Enrollment transactional record model
│   │   └── grade.py              # Grade/marks evaluation & letter mapping model
│   ├── static/
│   │   └── style.css             # Responsive enterprise dark/light theme CSS
│   └── templates/
│       └── index.html            # Web UI dashboard with live metric cards & forms
├── database/
│   ├── __init__.py
│   └── db.py                     # Thread-safe in-memory database store with seed data
├── tests/
│   ├── __init__.py
│   ├── test_student_service.py   # Unit tests for student registry operations
│   ├── test_course_enrollment.py # Unit tests for course capacity & 18-credit limit rule
│   ├── test_marks_mgmt.py        # Unit tests for marks entry, GPA & standing evaluation
│   └── test_api_endpoints.py     # HTTP integration tests via Flask test_client
├── k8s/
│   ├── deployment.yaml           # Kubernetes Deployment (3 replicas, RollingUpdate, probes)
│   └── service.yaml              # Kubernetes Service (NodePort 30090)
├── Jenkinsfile                   # Declarative Multi-Stage CI/CD Pipeline
├── Dockerfile                    # Multi-layer secure container build recipe
├── .dockerignore                 # Container build exclusions
├── requirements.txt              # Pinned Python package dependencies
├── run.py                        # Production application server entrypoint
├── .gitignore                    # Version control exclusion rules
└── README.md                     # Comprehensive architecture and runbook
```

---

## 2. Core Business Entities & Validation Rules

### 2.1 Database Schema (Thread-Safe In-Memory Store)
The platform implements a singleton database pattern protected by `threading.Lock()` to ensure atomic, race-condition-free reads and writes across concurrent HTTP worker threads:
- **Students**: Tracks `student_id`, `name`, `email`, `department`, `semester`, `enrolled_credits`, `cumulative_gpa`, and `academic_standing`.
- **Courses**: Tracks `course_id`, `title`, `credits`, `faculty_id`, `max_capacity`, `enrolled_count`, and `semester`.
- **Enrollments**: Transactional log with `enrollment_id`, `student_id`, `course_id`, `semester`, `status` (`ENROLLED`, `DROPPED`, `COMPLETED`), and timestamp.
- **Grades**: Evaluated records containing `grade_id`, `student_id`, `course_id`, `semester`, `marks`, `letter_grade`, `grade_points`, and timestamp.
- **Faculty**: Directory of academic advisors and course instructors.

### 2.2 Enterprise Validation & Business Rules
1. **Semester Credit Limit**: A student cannot register for more than **18 credits** in a given semester. Attempting to enroll in a course that pushes active credits over 18 throws an immediate rejection (`ValueError: Semester credit limit exceeded (Max: 18 credits)`).
2. **Duplicate Prevention**: Students cannot enroll in the same course for the same semester more than once.
3. **Course Capacity Governance**: Enrollments are automatically capped by `max_capacity`.
4. **Weighted GPA Calculation**:
   $$\text{GPA} = \frac{\sum (\text{Course Credits} \times \text{Grade Points})}{\sum \text{Total Graded Credits}}$$
5. **Grading Matrix**:
   - 90.0 - 100.0: **Grade A** (4.0 quality points)
   - 80.0 - 89.9: **Grade B** (3.0 quality points)
   - 70.0 - 79.9: **Grade C** (2.0 quality points)
   - 60.0 - 69.9: **Grade D** (1.0 quality point)
   - 0.0 - 59.9: **Grade F** (0.0 quality points)
6. **Academic Standing Evaluation**:
   - $\text{GPA} \ge 3.50$: **Dean's List**
   - $2.00 \le \text{GPA} < 3.50$: **Good Standing**
   - $\text{GPA} < 2.00$: **Academic Probation**

---

## 3. REST API Endpoint Reference

| Method | Endpoint | Description | Status Codes |
|---|---|---|---|
| `GET` | `/api/health` | Liveness & Readiness health probe | `200` |
| `GET` | `/api/dashboard` | Aggregated system metrics & stats | `200` |
| `GET` | `/api/students` | List all students or filter with `?q=` | `200` |
| `POST` | `/api/students` | Register a new student | `201`, `400` |
| `GET` | `/api/students/<id>` | Fetch individual student record | `200`, `404` |
| `DELETE` | `/api/students/<id>` | Remove student (fails if active courses) | `200`, `400` |
| `GET` | `/api/students/<id>/transcript` | Generate complete academic transcript | `200`, `404` |
| `GET` | `/api/courses` | List course catalog or filter with `?q=` | `200` |
| `POST` | `/api/courses` | Create a new course entry | `201`, `400` |
| `GET` | `/api/courses/<id>` | Fetch single course metadata | `200`, `404` |
| `POST` | `/api/enroll` | Register student into course (validates credit limit) | `200`, `400` |
| `POST` | `/api/drop` | Drop an active course registration | `200`, `400` |
| `POST` | `/api/grades` | Submit marks (0-100), assign grade, update GPA | `200`, `400` |

---

## 4. Automated Testing & Code Quality Gates

The test suite contains **35 tests** across 4 dedicated test modules with **91% overall statement coverage**:

```bash
# Execute full test suite with coverage report and JUnit XML export
python -m pytest -v --cov=app --cov-report=term-missing --junitxml=reports/test-results.xml tests/

# Execute static code analysis syntax gate via Flake8
python -m flake8 app/ database/ --count --select=E9,F63,F7,F82 --show-source --statistics
```

---

## 5. Containerization & Kubernetes Orchestration

### 5.1 Docker Container Image
- Multi-layer image built on `python:3.11-slim`.
- Runs as dedicated non-root user `appuser` (UID 1000).
- Exposes port `5000` with internal `HEALTHCHECK` probe targeting `/api/health`.

### 5.2 Kubernetes (Minikube) Deployment
- **Deployment**: `student-deployment` (3 replicas, RollingUpdate strategy, resource limits: 250m CPU, 256Mi RAM).
- **Self-Healing Probes**: Configured with `livenessProbe` and `readinessProbe` checking `/api/health`.
- **Service**: `student-service` exposed via **NodePort 30090**.
