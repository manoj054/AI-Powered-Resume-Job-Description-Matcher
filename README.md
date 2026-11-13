# AI-Powered Resume & Job Description Matcher

![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)
![React](https://img.shields.io/badge/React-19-61DAFB.svg)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-TF--IDF-F7931E.svg)
![SQLite](https://img.shields.io/badge/SQLite-History_DB-003B57.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

An intelligent full-stack web application that compares a candidate's resume (PDF or raw text) against a target job description using Natural Language Processing (NLP), tokenization, and Scikit-learn's TF-IDF cosine similarity.

---

## 🌟 Key Features

1. **Resume PDF Upload & Parsing**
   - Upload any standard PDF resume or paste raw text.
   - Robust extraction of resume text and standard sections (Summary, Skills, Experience, Education) using `pypdf`.
   - Pre-loaded with a realistic, high-fidelity sample resume (`sample_resume.pdf`).

2. **NLP Text Cleaning Pipeline**
   - Lowercasing, URL/email/phone stripping, and whitespace normalization.
   - Preserves critical technical terms like `C++`, `C#`, `.NET`, `Node.js`, `React.js`, and `CI/CD`.
   - Comprehensive stop-word removal and word tokenization.

3. **Domain-Specific Skill & Keyword Extraction**
   - High-precision taxonomy covering 150+ skills across Programming Languages, Web Frameworks, AI/ML, Cloud/DevOps, Databases, Tools, and Soft Skills.
   - Multi-word n-gram extraction (e.g., `machine learning`, `natural language processing`, `restful apis`).
   - Boundary-safe matching preventing false positives (e.g. `Go` vs English verb `go`).

4. **Multi-Factor Compatibility Scoring**
   - **TF-IDF Cosine Similarity:** Evaluates semantic vocabulary overlap between resume and job description.
   - **Skill Alignment Ratio:** Compares explicit required skills vs skills present in the candidate's profile.
   - **Weighted Composite Score:** Combined index ($55\%$ Skill Match + $45\%$ TF-IDF) presented as a clear percentage.

5. **Actionable Improvement Recommendations**
   - Specific missing skill identification prioritized by importance.
   - ATS keyword optimization hints.
   - Action verb strength detection.
   - Google X-Y-Z formula recommendations for quantifiable impact metrics.

6. **SQLite History Database**
   - Automatically records all analysis runs in SQLite (`analyses.db`).
   - History viewer with 1-click reload of past reports and record management.

7. **Interactive React 19 Dashboard**
   - Circular animated score gauge with dynamic threshold colors.
   - Categorized skills badges (Matched, Missing, Additional).
   - Top job description keywords matrix with TF-IDF weights.
   - Export reports as JSON or formatted print/PDF view.

---

## 📁 Project Structure

```
AI-Resume-Matcher/
│
├── backend/
│   ├── main.py                  # FastAPI server & SQLite database management
│   ├── resume_parser.py         # PDF text extraction and section segmentation
│   ├── text_cleaning.py         # NLP cleaning, tokenization & stopwords filtering
│   ├── skill_extractor.py       # 150+ skill taxonomy & multi-word extraction
│   ├── matcher.py               # TF-IDF cosine similarity & recommendation engine
│   ├── generate_sample_resume.py# Script to generate sample PDF resume
│   └── analyses.db              # SQLite database (auto-created on first run)
│
├── frontend/                    # Modern React 19 + Vite web application
│   ├── src/
│   │   ├── App.jsx              # Main interactive matching dashboard
│   │   ├── App.css              # Glassmorphic component styles & animations
│   │   ├── index.css            # Design tokens & color system
│   │   └── main.jsx             # React DOM root
│   ├── package.json             # Frontend dependencies
│   └── vite.config.js           # Vite configuration & API proxy
│
├── sample_data/
│   └── sample_resume.pdf        # Ready-to-use sample PDF resume
│
├── tests/
│   └── test_matcher.py          # 16-test unit & integration test suite
│
├── prompt_history.md            # Detailed engineering log & workflow history
├── requirements.txt             # Python dependencies
└── README.md                    # Project documentation
```

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python:** 3.10 or higher
- **Node.js:** v18 or higher (v20+ recommended)
- **npm:** v9 or higher

---

### 1. Backend Setup with `uv` (Recommended)

From the project root directory:

```bash
# 1. Sync dependencies and generate lockfile automatically with uv
uv sync

# 2. Run the FastAPI backend server
cd backend
uv run python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Alternatively, with traditional `pip`:
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
cd backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The backend API will be available at:
- **API URL:** `http://127.0.0.1:8000`
- **Interactive Swagger Docs:** `http://127.0.0.1:8000/docs`
- **ReDoc:** `http://127.0.0.1:8000/redoc`

---

### 2. Frontend Setup

In a new terminal window:

```bash
cd AI-Resume-Matcher/frontend

# 1. Install dependencies
npm install

# 2. Start the Vite development server
npm run dev
```

Open your browser at **`http://localhost:5173`**.

---

### 3. Running All Tests

Run the complete 16-test suite using `uv`:

```bash
uv run python -m pytest tests/test_matcher.py -v
```

---

## 📡 API Endpoints Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check endpoint |
| `POST` | `/api/analyze` | Upload resume file (PDF/TXT) + job description (multipart/form-data) |
| `POST` | `/api/analyze-text` | Analyze raw resume text and job description (JSON payload) |
| `GET` | `/api/history` | List previous analyses from SQLite |
| `GET` | `/api/history/{id}` | Retrieve full report of a specific previous analysis |
| `DELETE` | `/api/history/{id}` | Delete a specific analysis record |
| `DELETE` | `/api/history` | Clear all history records |
| `GET` | `/api/sample-job-descriptions` | Retrieve pre-configured sample job postings (Full Stack, AI, DevOps) |
| `GET` | `/api/sample-resume-download` | Download the bundled `sample_resume.pdf` |

---

## 🧪 Scoring Algorithm

The matching engine uses a weighted composite scoring formula:

$$\text{Composite Score} = (0.55 \times \text{Skill Match Ratio}) + (0.45 \times \text{TF-IDF Cosine Similarity})$$

- **TF-IDF Cosine Similarity:**
  Vectorizes unigrams and bigrams (`ngram_range=(1, 2)`) to evaluate contextual and semantic keyword closeness between resume and job posting.
- **Skill Alignment Ratio:**
  $$\text{Skill Match Ratio} = \frac{|\text{Resume Skills} \cap \text{Job Description Skills}|}{\max(|\text{Job Description Skills}|, 1)}$$
- **Dynamic Suggestions:**
  Evaluates missing skills, action verbs, and quantifiable metrics (e.g. percentages, scale, traffic) to provide actionable bullet points for resume enhancement.

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).

