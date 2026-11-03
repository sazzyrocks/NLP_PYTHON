"""Unit and integration tests for FastAPI server endpoints."""

from fastapi.testclient import TestClient
from server import app

client = TestClient(app)


def test_health_check():
    """Verify /api/health returns 200 and healthy status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["models_loaded"] is True


def test_get_skills():
    """Verify /api/skills returns taxonomy skills list."""
    response = client.get("/api/skills")
    assert response.status_code == 200
    data = response.json()
    assert "skills" in data
    assert data["count"] > 50
    assert "Python" in data["skills"] or "python" in [s.lower() for s in data["skills"]]


def test_get_weights():
    """Verify /api/weights returns default scoring weights."""
    response = client.get("/api/weights")
    assert response.status_code == 200
    data = response.json()
    assert "weights" in data
    assert "semantic_score" in data["weights"]


def test_rank_candidates_endpoint_success():
    """Verify /api/rank ranks candidate resumes against a text JD."""
    jd_text = (
        "We are looking for a Senior Python Developer with experience in FastAPI, Docker, and AWS."
    )
    resume1 = (
        "Alice Smith\n"
        "Skills: Python, FastAPI, Docker, AWS, PostgreSQL\n"
        "Experience: 5 years backend development building REST APIs."
    )
    resume2 = (
        "Bob Jones\n"
        "Skills: Photoshop, Illustrator, Graphic Design\n"
        "Experience: 2 years designing logos and banners."
    )

    files = [
        ("resumes", ("alice.txt", resume1.encode("utf-8"), "text/plain")),
        ("resumes", ("bob.txt", resume2.encode("utf-8"), "text/plain")),
    ]
    data = {
        "jd_text": jd_text,
    }

    response = client.post("/api/rank", data=data, files=files)
    assert response.status_code == 200
    body = response.json()

    assert "results" in body
    assert len(body["results"]) == 2
    # Alice should rank first
    assert body["results"][0]["filename"] == "alice.txt"
    assert body["results"][0]["final_score"] > body["results"][1]["final_score"]
    assert "Python" in body["results"][0]["matched_skills"]


def test_export_csv_and_json():
    """Verify /api/export/csv and /api/export/json return valid files."""
    payload = {
        "results": [
            {
                "rank": 1,
                "filename": "alice.txt",
                "final_score": 85.0,
                "semantic_score": 90.0,
                "skill_score": 80.0,
                "experience_section_score": 85.0,
                "lexical_score": 75.0,
                "matched_skills": ["Python", "FastAPI"],
                "missing_skills": ["AWS"],
                "extra_skills": ["PostgreSQL"],
                "section_scores": {},
                "suggestions": ["Add metrics."],
            }
        ]
    }

    csv_res = client.post("/api/export/csv", json=payload)
    assert csv_res.status_code == 200
    assert "alice.txt" in csv_res.text
    assert "Candidate File" in csv_res.text

    json_res = client.post("/api/export/json", json=payload)
    assert json_res.status_code == 200
    assert "alice.txt" in json_res.text
