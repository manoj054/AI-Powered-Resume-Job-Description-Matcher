"""
main.py
FastAPI Backend Application for AI-Resume-Matcher
Provides RESTful APIs for resume parsing, TF-IDF matching, skill gap analysis,
SQLite analysis history storage, and sample data.
"""

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from resume_parser import ResumeParser
from matcher import ResumeMatcher

# Initialize FastAPI application
app = FastAPI(
    title="AI-Powered Resume & Job Description Matcher API",
    description="NLP and TF-IDF powered Resume Matching and Skills Gap Analysis API",
    version="1.0.0"
)

# Enable CORS for local development and standard frontend ports
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SQLite Database Setup
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "analyses.db"
SAMPLE_DATA_DIR = BASE_DIR.parent / "sample_data"


def init_db():
    """Initializes SQLite database schema."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            job_title TEXT,
            match_percentage REAL,
            tfidf_score REAL,
            skill_score REAL,
            matched_skills TEXT,
            missing_skills TEXT,
            additional_skills TEXT,
            resume_skills TEXT,
            jd_skills TEXT,
            suggestions TEXT,
            keywords TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


init_db()


def save_analysis(
    filename: str,
    job_title: str,
    match_result: Dict[str, any]
) -> int:
    """Stores an analysis run in the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO analyses (
            filename, job_title, match_percentage, tfidf_score, skill_score,
            matched_skills, missing_skills, additional_skills, resume_skills,
            jd_skills, suggestions, keywords, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        filename,
        job_title or "Position Analysis",
        match_result["match_percentage"],
        match_result["tfidf_score"],
        match_result["skill_score"],
        json.dumps(match_result["matched_skills"]),
        json.dumps(match_result["missing_skills"]),
        json.dumps(match_result["additional_skills"]),
        json.dumps(match_result["resume_skills"]),
        json.dumps(match_result["jd_skills"]),
        json.dumps(match_result["suggestions"]),
        json.dumps(match_result["keywords"]),
        datetime.now(timezone.utc).isoformat()
    ))
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return record_id


# Pydantic Models
class AnalyzeTextRequest(BaseModel):
    resume_text: str
    job_description: str
    job_title: Optional[str] = "Custom Position"


# Instantiate matcher
matcher = ResumeMatcher(tfidf_weight=0.45, skill_weight=0.55)


@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "AI-Resume-Matcher", "version": "1.0.0"}


@app.post("/api/analyze")
async def analyze_resume_file(
    file: UploadFile = File(...),
    job_description: str = Form(...),
    job_title: Optional[str] = Form("Target Role")
):
    """
    Main analysis endpoint: Accepts an uploaded PDF (or text) resume file
    and a pasted job description, performs full NLP and TF-IDF matching,
    stores the result in SQLite, and returns the analysis.
    """
    if not job_description or not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty.")

    filename = file.filename or "uploaded_resume.pdf"
    content = await file.read()

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # Extract text from file
    try:
        if filename.lower().endswith(".pdf"):
            resume_data = ResumeParser.parse(content)
            resume_text = resume_data["raw_text"]
        else:
            # Plain text fallback
            resume_text = content.decode("utf-8", errors="replace")
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")

    if not resume_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract readable text from the resume.")

    # Execute matching
    result = matcher.match(resume_text, job_description)

    # Store analysis record in SQLite
    record_id = save_analysis(filename, job_title, result)
    result["id"] = record_id
    result["filename"] = filename
    result["job_title"] = job_title

    return JSONResponse(content=result)


@app.post("/api/analyze-text")
def analyze_resume_raw_text(payload: AnalyzeTextRequest):
    """
    Direct text analysis endpoint: Accepts raw resume text and job description text.
    """
    if not payload.resume_text.strip():
        raise HTTPException(status_code=400, detail="Resume text cannot be empty.")
    if not payload.job_description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty.")

    result = matcher.match(payload.resume_text, payload.job_description)
    record_id = save_analysis("Direct_Text_Input.txt", payload.job_title, result)
    result["id"] = record_id
    result["filename"] = "Direct_Text_Input.txt"
    result["job_title"] = payload.job_title

    return JSONResponse(content=result)


@app.get("/api/history")
def get_analysis_history(limit: int = 20):
    """
    Retrieves previous analysis records from SQLite.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, filename, job_title, match_percentage, tfidf_score,
               skill_score, matched_skills, missing_skills, created_at
        FROM analyses
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()

    history = []
    for r in rows:
        matched_list = json.loads(r["matched_skills"]) if r["matched_skills"] else []
        missing_list = json.loads(r["missing_skills"]) if r["missing_skills"] else []
        history.append({
            "id": r["id"],
            "filename": r["filename"],
            "job_title": r["job_title"],
            "match_percentage": r["match_percentage"],
            "tfidf_score": r["tfidf_score"],
            "skill_score": r["skill_score"],
            "matched_count": len(matched_list),
            "missing_count": len(missing_list),
            "created_at": r["created_at"]
        })

    return history


@app.get("/api/history/{analysis_id}")
def get_analysis_detail(analysis_id: int):
    """
    Retrieves the full report of a specific previous analysis.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM analyses WHERE id = ?", (analysis_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Analysis record not found.")

    return {
        "id": row["id"],
        "filename": row["filename"],
        "job_title": row["job_title"],
        "match_percentage": row["match_percentage"],
        "tfidf_score": row["tfidf_score"],
        "skill_score": row["skill_score"],
        "matched_skills": json.loads(row["matched_skills"]) if row["matched_skills"] else [],
        "missing_skills": json.loads(row["missing_skills"]) if row["missing_skills"] else [],
        "additional_skills": json.loads(row["additional_skills"]) if row["additional_skills"] else [],
        "resume_skills": json.loads(row["resume_skills"]) if row["resume_skills"] else [],
        "jd_skills": json.loads(row["jd_skills"]) if row["jd_skills"] else [],
        "suggestions": json.loads(row["suggestions"]) if row["suggestions"] else [],
        "keywords": json.loads(row["keywords"]) if row["keywords"] else [],
        "created_at": row["created_at"]
    }


@app.delete("/api/history/{analysis_id}")
def delete_history_record(analysis_id: int):
    """Deletes a specific history record."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM analyses WHERE id = ?", (analysis_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()

    if not deleted:
        raise HTTPException(status_code=404, detail="Record not found.")
    return {"status": "success", "message": f"Deleted record {analysis_id}"}


@app.delete("/api/history")
def clear_all_history():
    """Clears all historical analyses from SQLite."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM analyses")
    conn.commit()
    conn.close()
    return {"status": "success", "message": "All history records cleared."}


class CustomJdRequest(BaseModel):
    job_title: str
    experience_level: Optional[str] = "Mid-Level (2-4 yrs)"
    company_name: Optional[str] = "Tech Innovations Inc."
    skills: List[str] = []
    responsibilities: Optional[str] = None


@app.post("/api/generate-job-description")
def generate_custom_job_description(req: CustomJdRequest):
    """
    Generates a realistic, tailored job description based on user-selected
    role, experience level, and tech stack.
    """
    title = req.job_title.strip() or "Software Engineer"
    skills_formatted = ", ".join(req.skills) if req.skills else "modern software development tools and frameworks"
    exp = req.experience_level or "2+ years"
    company = req.company_name or "Innovative Tech Corp"

    skills_bullets = "\n".join([f"- Hands-on proficiency with {skill}." for skill in req.skills[:8]]) if req.skills else "- Experience with software development best practices."

    description = (
        f"{company} is hiring a {title} ({exp}) to design, develop, and deploy scalable solutions.\n\n"
        f"Key Responsibilities:\n"
        f"- Build reliable, efficient, and maintainable software components aligned with project specifications.\n"
        f"- Collaborate with cross-functional engineering and product teams in an agile delivery lifecycle.\n"
        f"- Write clean, well-tested code with comprehensive unit testing and peer code reviews.\n"
        f"- Participate in architecture discussions, API design, and system optimization.\n\n"
        f"Requirements & Core Skills:\n"
        f"- Experience level: {exp} of relevant software development experience.\n"
        f"{skills_bullets}\n"
        f"- Strong problem-solving, analytical thinking, and team communication skills.\n"
        f"- Familiarity with Git version control and modern deployment workflows."
    )

    return {
        "job_title": title,
        "company": company,
        "description": description
    }


@app.get("/api/sample-job-descriptions")
def get_sample_job_descriptions():
    """
    Returns curated, realistic sample job descriptions across multiple domains:
    Frontend, Backend, Junior Full Stack, Senior Full Stack, AI/ML, Cloud/DevOps, and Data Science.
    """
    return [
        {
            "id": "junior-fullstack",
            "title": "Junior Full Stack Developer",
            "category": "Full Stack",
            "level": "Junior (0-2 yrs)",
            "company": "NextGen Software",
            "description": (
                "NextGen Software is looking for an enthusiastic Junior Full Stack Developer to join our engineering team.\n\n"
                "Responsibilities:\n"
                "- Assist in developing web application features across both frontend and backend.\n"
                "- Build responsive UI components using React.js, HTML5, and CSS3 / Tailwind CSS.\n"
                "- Write backend API endpoints with Python (FastAPI or Django) and interact with SQL databases.\n"
                "- Utilize Git for version control and participate in team Agile/Scrum standups.\n"
                "- Write basic unit tests and debug client and server issues.\n\n"
                "Requirements:\n"
                "- 0-2 years experience or strong project portfolio in software development.\n"
                "- Foundational knowledge of Python and JavaScript/TypeScript.\n"
                "- Experience with React, RESTful APIs, and relational databases (PostgreSQL or SQLite).\n"
                "- Eagerness to learn Docker, CI/CD, and modern cloud deployment practices.\n"
                "- Strong team collaboration, curiosity, and problem-solving mindset."
            )
        },
        {
            "id": "frontend-dev",
            "title": "Frontend Developer (React & TypeScript)",
            "category": "Frontend",
            "level": "Mid-Level (2-4 yrs)",
            "company": "PixelCraft Digital",
            "description": (
                "PixelCraft is seeking a talented Frontend Developer to craft sleek, responsive user interfaces.\n\n"
                "Requirements & Responsibilities:\n"
                "- 2+ years of experience with modern frontend web technologies.\n"
                "- Deep proficiency in React.js, TypeScript, Next.js, and modern JavaScript (ES6+).\n"
                "- Expert in crafting responsive layouts with Tailwind CSS, CSS3, and HTML5.\n"
                "- Experience managing application state with Redux or React Context.\n"
                "- Integrating backend RESTful APIs and real-time WebSockets.\n"
                "- Writing automated frontend unit tests using Jest or Cypress.\n"
                "- Understanding of web performance optimization, accessibility, and Git version control."
            )
        },
        {
            "id": "backend-dev",
            "title": "Backend Developer (Python & FastAPI)",
            "category": "Backend",
            "level": "Mid-Level (2-5 yrs)",
            "company": "DataCore Systems",
            "description": (
                "DataCore Systems is hiring a Backend Developer to architect scalable APIs and distributed services.\n\n"
                "Requirements & Responsibilities:\n"
                "- 2+ years experience building backend services with Python, FastAPI, or Django.\n"
                "- Strong database modeling and query optimization in PostgreSQL or MySQL.\n"
                "- In-memory caching and message queuing using Redis.\n"
                "- Building and maintaining RESTful APIs and microservices architecture.\n"
                "- Containerizing applications with Docker and configuring CI/CD automation.\n"
                "- Writing comprehensive test suites using PyTest.\n"
                "- Familiarity with Linux server environments and AWS cloud basics."
            )
        },
        {
            "id": "senior-fullstack",
            "title": "Senior Full Stack Engineer (Python & React)",
            "category": "Full Stack",
            "level": "Senior (4+ yrs)",
            "company": "TechVanguard Innovations",
            "description": (
                "TechVanguard is seeking a Senior Full Stack Engineer to lead the architecture "
                "of our next-generation cloud platforms.\n\n"
                "Requirements & Responsibilities:\n"
                "- 4+ years experience building web applications with Python, FastAPI, or Django.\n"
                "- Strong proficiency in modern JavaScript/TypeScript, React.js, and Tailwind CSS.\n"
                "- Solid knowledge of relational databases such as PostgreSQL or MySQL and Redis caching.\n"
                "- Experience with containerization using Docker, Kubernetes, and CI/CD automation.\n"
                "- Proficiency deploying and maintaining microservices on AWS or Google Cloud Platform.\n"
                "- Demonstrated ability in writing unit testing with PyTest or Jest.\n"
                "- Strong team collaboration, communication, and agile mindset."
            )
        },
        {
            "id": "ai-engineer",
            "title": "AI & NLP Machine Learning Engineer",
            "category": "AI & Data",
            "level": "Mid-Senior (3+ yrs)",
            "company": "CognitiveAI Labs",
            "description": (
                "CognitiveAI Labs is looking for a talented Machine Learning Engineer specializing in NLP "
                "and Generative AI to design cutting-edge intelligent applications.\n\n"
                "Key Qualifications:\n"
                "- Strong foundation in Python, NumPy, Pandas, and Scikit-Learn.\n"
                "- Hands-on experience developing deep learning models with PyTorch or TensorFlow.\n"
                "- Practical expertise in Natural Language Processing (NLP), tokenization, and Transformers.\n"
                "- Familiarity with LLMs, Hugging Face, LangChain, and vector embeddings.\n"
                "- Experience designing RESTful APIs with FastAPI or Flask and deploying with Docker.\n"
                "- Ability to communicate complex analytical findings and mentor junior team members."
            )
        },
        {
            "id": "devops-engineer",
            "title": "Cloud Platform & DevOps Engineer",
            "category": "Cloud & DevOps",
            "level": "Mid-Senior (3+ yrs)",
            "company": "CloudScale Global",
            "description": (
                "CloudScale is hiring a Cloud DevOps Engineer to scale infrastructure and automate deployments.\n\n"
                "Key Requirements:\n"
                "- Deep hands-on experience with AWS cloud computing and Linux administration.\n"
                "- Expertise in Docker containerization and Kubernetes cluster orchestration.\n"
                "- Infrastructure as Code (IaC) with Terraform and Ansible.\n"
                "- Building automated CI/CD pipelines with GitHub Actions or Jenkins.\n"
                "- Experience with monitoring, logging, and Nginx web server configuration.\n"
                "- Knowledge of Bash scripting, Python automation, and Git version control."
            )
        },
        {
            "id": "data-scientist",
            "title": "Data Scientist & Analytics Engineer",
            "category": "AI & Data",
            "level": "Mid-Level (2-4 yrs)",
            "company": "InsightEdge Analytics",
            "description": (
                "InsightEdge is hiring a Data Scientist to extract predictive insights from complex datasets.\n\n"
                "Requirements & Responsibilities:\n"
                "- Strong proficiency in Python, SQL, Pandas, NumPy, and Scikit-Learn.\n"
                "- Experience developing statistical models, regression, and classification algorithms.\n"
                "- Querying large datasets with PostgreSQL, MySQL, or BigQuery.\n"
                "- Data visualization and reporting with Matplotlib, Seaborn, or Tableau.\n"
                "- Designing end-to-end data analytics pipelines and communicating insights to stakeholders."
            )
        }
    ]


@app.get("/api/sample-resume-download")
def download_sample_resume():
    """Provides the generated sample resume PDF for direct download."""
    sample_pdf_path = SAMPLE_DATA_DIR / "sample_resume.pdf"
    if sample_pdf_path.exists():
        return FileResponse(
            path=str(sample_pdf_path),
            filename="sample_resume.pdf",
            media_type="application/pdf"
        )
    raise HTTPException(status_code=404, detail="Sample resume PDF not found.")


# Mount React Frontend static files if built
FRONTEND_DIST = BASE_DIR.parent / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
