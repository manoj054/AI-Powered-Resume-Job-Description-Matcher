# AI-Powered Resume & Job Description Matcher — Prompt & Engineering History

## Project Genesis & Objectives
**User Prompt:**
> Build a simple web application where users upload their resumes and paste a job description.
> The application analyzes both documents and displays:
> - Resume matching percentage.
> - Skills already available in the resume.
> - Missing skills required for the job.
> - Relevant keywords.
> - Suggestions to improve the resume.
>
> Technologies:
> - Python: Core programming
> - NLP (Regex, Tokenization): Text processing
> - Scikit-learn: TF-IDF similarity
> - FastAPI: Backend APIs
> - React: Frontend
> - SQLite: Store analysis history

---

## 1. System Architecture & Workflow Pipeline

```
                                 [ User Interaction ]
                                           │
                    ┌──────────────────────┴──────────────────────┐
                    ▼                                             ▼
       Upload Resume (PDF / TXT)                      Paste Job Description
                    │                                             │
                    ▼                                             ▼
       ResumeParser (pypdf)                           Raw JD Text Extraction
                    │                                             │
                    └──────────────────────┬──────────────────────┘
                                           ▼
                               NLP Text Cleaning Pipeline
                   • Lowercase normalization
                   • URL, email & phone number removal
                   • Preservation of tech tokens (C++, C#, .NET, Node.js)
                   • Punctuation stripping & Whitespace normalization
                   • Stopword filtering & Word Tokenization
                                           │
                    ┌──────────────────────┴──────────────────────┐
                    ▼                                             ▼
       Skill Extraction & Taxonomy                   TF-IDF Vectorization
       • Multi-word n-gram matching                  • TfidfVectorizer (ngram_range 1-2)
       • Canonical skill mapping                     • Cosine similarity calculation
       • Categorized domains                         • Feature weight ranking for keywords
                    │                                             │
                    └──────────────────────┬──────────────────────┘
                                           ▼
                               Composite Match Engine
                Score = (0.55 * Skill Match %) + (0.45 * TF-IDF Cosine %)
                                           │
                                           ▼
                             Actionable Recommendations
                • Critical missing skills
                • Missing target keywords
                • Quantifiable metrics check (Google X-Y-Z formula)
                • Action verbs & formatting guidance
                                           │
                                           ▼
                              SQLite Database Persistence
                Records stored in `analyses` table for historical tracking
                                           │
                                           ▼
                               Interactive React Dashboard
                • Circular Animated Match Gauge
                • Skills breakdown (Matched, Missing, Additional)
                • TF-IDF Keyword relevance chips
                • Actionable suggestion priority cards
                • History drawer & PDF/JSON Export
```

---

## 2. Technical Decisions & Implementation Details

### A. NLP Text Cleaning (`text_cleaning.py`)
- **Challenge:** Standard punctuation stripping destroys technical skill names like `C++`, `C#`, `.NET`, `Node.js`, and `CI/CD`.
- **Solution:** Implemented token preservation masks (`__cplusplus__`, `__csharp__`, `__dotnet__`, `__nodejs__`, `__cicd__`) before punctuation regex stripping, and restored them during tokenization.
- **Stopwords:** Built a self-contained zero-dependency English stopword set to ensure deterministic execution without external network downloads (e.g. NLTK corpora).

### B. Skill Extraction & Taxonomy (`skill_extractor.py`)
- **Taxonomy:** Over 150 industry skills across 7 domains:
  1. Programming Languages (Python, Java, TypeScript, Go, C++, Rust, etc.)
  2. Frameworks & Libraries (React, FastAPI, Django, Spring Boot, etc.)
  3. AI & Data Science (PyTorch, TensorFlow, Scikit-learn, NLP, LLMs, etc.)
  4. Cloud & DevOps (AWS, Azure, Docker, Kubernetes, CI/CD, etc.)
  5. Databases & Storage (PostgreSQL, MongoDB, Redis, SQLite, etc.)
  6. Tools & Methodologies (Git, PyTest, Agile, Scrum, TDD, etc.)
  7. Soft Skills (Leadership, Communication, Problem Solving, etc.)
- **Multi-Word Matching:** Handles compound phrases such as `"natural language processing"`, `"machine learning"`, `"restful apis"`, and `"tailwind css"`.
- **Boundary Precision:** Context-aware boundary matching ensures short acronyms (e.g., `C`, `R`, `Go`) do not trigger false positive matches on common English words.

### C. Matching Engine (`matcher.py`)
- **TF-IDF Vectorizer:** Computes semantic cosine similarity over cleaned unigrams and bigrams (`ngram_range=(1, 2)`).
- **Skill Alignment Ratio:** `len(matched_skills) / max(len(jd_skills), 1)`.
- **Composite Score Formula:** Balanced weighted scoring:
  $$\text{Composite Score} = 0.55 \times \text{Skill Match \%} + 0.45 \times \text{TF-IDF Cosine \%}$$
- **Dynamic Suggestions:** Analyzes presence of measurable metrics, strong action verbs, and skill deficiencies to generate customized, actionable bullet-point advice.

### D. SQLite Database History (`main.py`)
- Automatically initializes `analyses.db` on startup.
- Stores every analysis with:
  - `id`: Unique identifier
  - `filename`: Resume file name
  - `job_title`: Target position title
  - `match_percentage`: Overall score
  - `tfidf_score` & `skill_score`: Sub-scores
  - `matched_skills`, `missing_skills`, `additional_skills`: JSON lists
  - `suggestions`: JSON list of actionable items
  - `keywords`: JSON list of TF-IDF keyword weights
  - `created_at`: UTC ISO timestamp
- Full CRUD support: list, detail, delete, clear all.

### E. Frontend Application (`frontend/`)
- Built with React 19, Vite, and Lucide icons.
- Two-column split layout for Resume input (PDF drag-and-drop or raw text paste) and Job Description (custom text or 1-click industry role presets).
- Top interactive SVG progress gauge with dynamic threshold colors (Green $\ge 75\%$, Amber $50\% - 74\%$, Rose $< 50\%$).
- Confetti celebration effect on high scores ($\ge 70\%$).
- Complete SQLite history modal with 1-click reload of previous reports.
- Export options: Download JSON report or formatted print view.

---

## 3. Verification & Test Execution
- Comprehensive 16-test unit and integration test suite (`tests/test_matcher.py`):
  - `test_clean_text_basic`: Verified URL, email, and phone filtering.
  - `test_clean_text_preserve_tech_terms`: Verified preservation of `C++`, `C#`, `.NET`, `Node.js`, `CI/CD`.
  - `test_tokenize` & `test_extract_keywords`: Verified tokenization and TF-IDF frequency.
  - `test_extract_skills_technical`: Verified skill detection across categories.
  - `test_extract_skills_categorization`: Verified category mapping.
  - `test_compare_skills`: Verified math on matched, missing, and additional skills.
  - `test_parse_sample_pdf_resume`: Verified end-to-end PDF parsing from `sample_data/sample_resume.pdf`.
  - `test_parse_empty_stream_raises`: Verified error boundaries.
  - `test_matcher_high_similarity`: Verified score $\ge 70\%$ for matching engineer roles.
  - `test_matcher_low_similarity_suggestions`: Verified low similarity scores and skill gap detection.
  - `test_health_endpoint`: Verified `/api/health`.
  - `test_sample_job_descriptions`: Verified sample JD retrieval.
  - `test_analyze_text_endpoint`: Verified raw text matching API.
  - `test_analyze_pdf_file_upload`: Verified multipart/form-data PDF upload endpoint.
  - `test_history_and_detail`: Verified SQLite insert, list, and single-record query endpoints.
- Result: **16 passed in 1.58s** with 100% pass rate.

