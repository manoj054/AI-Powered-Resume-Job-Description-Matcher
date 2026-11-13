"""
test_matcher.py
Comprehensive Unit and Integration Test Suite for AI-Resume-Matcher
Tests text cleaning, skill extraction, PDF parsing, TF-IDF matching, and FastAPI endpoints.
"""

import os
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Add backend directory to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = BASE_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from text_cleaning import clean_text, tokenize, extract_keywords
from skill_extractor import extract_skills, compare_skills
from resume_parser import ResumeParser
from matcher import ResumeMatcher
from main import app, init_db


@pytest.fixture(scope="module")
def client():
    init_db()
    return TestClient(app)


# ---------------------------------------------------------------------------
# 1. Text Cleaning Tests
# ---------------------------------------------------------------------------

def test_clean_text_basic():
    raw = "Hello World! Visit https://example.com or email test@example.com."
    cleaned = clean_text(raw, remove_stopwords=True)
    assert "https" not in cleaned
    assert "test@example.com" not in cleaned
    assert "world" in cleaned


def test_clean_text_preserve_tech_terms():
    raw = "Expert in C++, C#, .NET, Node.js, React.js, and CI/CD pipelines."
    cleaned = clean_text(raw, remove_stopwords=False)
    assert "c++" in cleaned
    assert "c#" in cleaned
    assert ".net" in cleaned
    assert "node.js" in cleaned
    assert "react.js" in cleaned
    assert "ci/cd" in cleaned


def test_tokenize():
    text = "Building APIs using FastAPI and Python 3.12"
    tokens = tokenize(text)
    assert "fastapi" in tokens
    assert "python" in tokens


def test_extract_keywords():
    text = "Machine learning models and deep learning models require strong machine learning expertise."
    kw = extract_keywords(text, top_n=3)
    assert "learning" in kw
    assert "models" in kw or "machine" in kw


# ---------------------------------------------------------------------------
# 2. Skill Extraction Tests
# ---------------------------------------------------------------------------

def test_extract_skills_technical():
    sample_text = """
    Software Engineer skilled in Python, React, PostgreSQL, Docker, Kubernetes,
    FastAPI, Tailwind CSS, and Git. Experience with Natural Language Processing.
    """
    skills_data = extract_skills(sample_text)
    skills = skills_data["all_skills"]
    assert "Python" in skills
    assert "React" in skills
    assert "PostgreSQL" in skills
    assert "Docker" in skills
    assert "Kubernetes" in skills
    assert "FastAPI" in skills
    assert "Tailwind CSS" in skills
    assert "Natural Language Processing" in skills
    assert skills_data["count"] >= 8


def test_extract_skills_categorization():
    text = "Python, AWS, PostgreSQL, PyTest, Team Collaboration"
    result = extract_skills(text)
    categories = result["by_category"]
    assert "Programming Languages" in categories
    assert "Cloud & DevOps" in categories
    assert "Databases & Storage" in categories
    assert "Tools & Methodologies" in categories


def test_compare_skills():
    resume_skills = ["Python", "FastAPI", "Docker", "Git", "PostgreSQL"]
    jd_skills = ["Python", "FastAPI", "Kubernetes", "AWS", "PostgreSQL"]

    comparison = compare_skills(resume_skills, jd_skills)
    assert set(comparison["matched"]) == {"Python", "FastAPI", "PostgreSQL"}
    assert set(comparison["missing"]) == {"Kubernetes", "AWS"}
    assert set(comparison["additional"]) == {"Docker", "Git"}
    # 3 out of 5 matched = 60.0%
    assert comparison["match_percentage"] == 60.0


# ---------------------------------------------------------------------------
# 3. Resume Parser Tests
# ---------------------------------------------------------------------------

def test_parse_sample_pdf_resume():
    sample_pdf_path = BASE_DIR / "sample_data" / "sample_resume.pdf"
    assert sample_pdf_path.exists(), f"Sample PDF missing at {sample_pdf_path}"

    parsed = ResumeParser.parse(str(sample_pdf_path))
    assert parsed["word_count"] > 100
    assert "alex morgan" in parsed["cleaned_text"].lower()
    assert "python" in parsed["cleaned_text"].lower()
    assert len(parsed["sections"]) > 0


def test_parse_empty_stream_raises():
    with pytest.raises(ValueError):
        ResumeParser.extract_text_from_pdf(b"")


# ---------------------------------------------------------------------------
# 4. Matcher & TF-IDF Scoring Tests
# ---------------------------------------------------------------------------

def test_matcher_high_similarity():
    matcher = ResumeMatcher()
    resume_text = "Experienced Senior Python developer specializing in FastAPI, PostgreSQL, Docker, and React applications."
    jd_text = "Seeking Senior Python engineer with hands-on FastAPI, PostgreSQL, Docker, and React frontend experience."

    result = matcher.match(resume_text, jd_text)
    assert result["match_percentage"] > 70.0
    assert "Python" in result["matched_skills"]
    assert "FastAPI" in result["matched_skills"]
    assert len(result["keywords"]) > 0


def test_matcher_low_similarity_suggestions():
    matcher = ResumeMatcher()
    resume_text = "Accountant with 5 years experience in GAAP audits, payroll tax, QuickBooks, and Excel balance sheets."
    jd_text = "Senior Machine Learning Engineer needed with PyTorch, TensorFlow, NLP, CUDA, and Kubernetes."

    result = matcher.match(resume_text, jd_text)
    assert result["match_percentage"] < 30.0
    assert len(result["missing_skills"]) > 0
    # Suggestions must include skill gap
    suggestion_types = [s["type"] for s in result["suggestions"]]
    assert "skills_gap" in suggestion_types


# ---------------------------------------------------------------------------
# 5. FastAPI Endpoints Integration Tests
# ---------------------------------------------------------------------------

def test_health_endpoint(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"


def test_sample_job_descriptions(client):
    res = client.get("/api/sample-job-descriptions")
    assert res.status_code == 200
    jds = res.json()
    assert len(jds) >= 3
    assert any("Python" in j["description"] for j in jds)


def test_analyze_text_endpoint(client):
    payload = {
        "resume_text": "Experienced Python and React developer with PostgreSQL and Docker skills.",
        "job_description": "We need a Python developer with React and AWS knowledge.",
        "job_title": "Full Stack Developer"
    }
    res = client.post("/api/analyze-text", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "match_percentage" in data
    assert "Python" in data["matched_skills"]
    assert "AWS" in data["missing_skills"]
    assert "id" in data


def test_analyze_pdf_file_upload(client):
    sample_pdf_path = BASE_DIR / "sample_data" / "sample_resume.pdf"
    with open(sample_pdf_path, "rb") as f:
        pdf_bytes = f.read()

    jd = "Looking for Senior Full Stack Engineer proficient in Python, FastAPI, React, Redis, and Kubernetes."
    res = client.post(
        "/api/analyze",
        data={"job_description": jd, "job_title": "Senior Engineer"},
        files={"file": ("sample_resume.pdf", pdf_bytes, "application/pdf")}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["match_percentage"] > 50.0
    assert "FastAPI" in data["matched_skills"]
    assert "Kubernetes" in data["missing_skills"]
    assert data["id"] is not None


def test_history_and_detail(client):
    # Fetch history
    history_res = client.get("/api/history")
    assert history_res.status_code == 200
    records = history_res.json()
    assert len(records) > 0
    record_id = records[0]["id"]

    # Fetch detail of first record
    detail_res = client.get(f"/api/history/{record_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["id"] == record_id
    assert "matched_skills" in detail
    assert "suggestions" in detail

