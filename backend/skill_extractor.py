"""
skill_extractor.py
Skill Extraction & Normalization Module for AI-Resume-Matcher
Features:
- Canonical deduplication: Maps variants (e.g. React.js, ReactJS, React) to single canonical names.
- 150+ skill taxonomy across 7 domains.
- Context-aware boundaries for short terms (Go, C, R).
- Equivalence clusters for alternative requirements (e.g., PostgreSQL / MySQL, AWS / GCP / Azure).
"""

import re
from typing import Dict, List, Set, Tuple

# Canonical mapping: { normalized_pattern : canonical_display_name }
SKILL_TAXONOMY: Dict[str, Dict[str, str]] = {
    "Programming Languages": {
        "python": "Python",
        "java": "Java",
        "javascript": "JavaScript",
        "js": "JavaScript",
        "typescript": "TypeScript",
        "ts": "TypeScript",
        "c++": "C++",
        "cpp": "C++",
        "c#": "C#",
        "csharp": "C#",
        "c language": "C",
        "golang": "Go",
        "rust": "Rust",
        "ruby": "Ruby",
        "php": "PHP",
        "swift": "Swift",
        "kotlin": "Kotlin",
        "scala": "Scala",
        "dart": "Dart",
        "bash": "Bash",
        "shell scripting": "Shell Scripting",
        "powershell": "PowerShell",
        "sql": "SQL",
        "html": "HTML5",
        "html5": "HTML5",
        "css": "CSS3",
        "css3": "CSS3",
        "sass": "SASS/SCSS",
        "scss": "SASS/SCSS",
    },
    "Frameworks & Libraries": {
        "react": "React",
        "react.js": "React",
        "reactjs": "React",
        "react native": "React Native",
        "next.js": "Next.js",
        "nextjs": "Next.js",
        "next": "Next.js",
        "angular": "Angular",
        "angularjs": "Angular",
        "vue": "Vue.js",
        "vue.js": "Vue.js",
        "vuejs": "Vue.js",
        "node.js": "Node.js",
        "nodejs": "Node.js",
        "node": "Node.js",
        "express": "Express.js",
        "express.js": "Express.js",
        "expressjs": "Express.js",
        "fastapi": "FastAPI",
        "django": "Django",
        "flask": "Flask",
        "spring boot": "Spring Boot",
        "spring": "Spring Boot",
        "asp.net": "ASP.NET",
        ".net core": ".NET Core",
        ".net": ".NET",
        "dotnet": ".NET",
        "tailwind": "Tailwind CSS",
        "tailwind css": "Tailwind CSS",
        "tailwindcss": "Tailwind CSS",
        "bootstrap": "Bootstrap",
        "redux": "Redux",
        "graphql": "GraphQL",
        "rest api": "RESTful APIs",
        "restful api": "RESTful APIs",
        "restful apis": "RESTful APIs",
        "rest apis": "RESTful APIs",
        "rest": "RESTful APIs",
        "websocket": "WebSockets",
        "websockets": "WebSockets",
        "jquery": "jQuery",
    },
    "Data Science & AI/ML": {
        "machine learning": "Machine Learning",
        "deep learning": "Deep Learning",
        "artificial intelligence": "Artificial Intelligence",
        "ai": "Artificial Intelligence",
        "nlp": "Natural Language Processing",
        "natural language processing": "Natural Language Processing",
        "computer vision": "Computer Vision",
        "scikit-learn": "Scikit-Learn",
        "sklearn": "Scikit-Learn",
        "tensorflow": "TensorFlow",
        "pytorch": "PyTorch",
        "keras": "Keras",
        "pandas": "Pandas",
        "numpy": "NumPy",
        "scipy": "SciPy",
        "opencv": "OpenCV",
        "matplotlib": "Matplotlib",
        "seaborn": "Seaborn",
        "hugging face": "Hugging Face",
        "huggingface": "Hugging Face",
        "transformers": "Transformers",
        "llm": "Large Language Models (LLMs)",
        "llms": "Large Language Models (LLMs)",
        "large language models": "Large Language Models (LLMs)",
        "langchain": "LangChain",
        "generative ai": "Generative AI",
        "spacy": "spaCy",
        "nltk": "NLTK",
        "xgboost": "XGBoost",
        "data visualization": "Data Visualization",
        "data structures": "Data Structures & Algorithms",
        "algorithms": "Algorithms",
    },
    "Cloud & DevOps": {
        "aws": "AWS",
        "amazon web services": "AWS",
        "azure": "Microsoft Azure",
        "microsoft azure": "Microsoft Azure",
        "gcp": "Google Cloud (GCP)",
        "google cloud": "Google Cloud (GCP)",
        "google cloud platform": "Google Cloud (GCP)",
        "docker": "Docker",
        "kubernetes": "Kubernetes",
        "k8s": "Kubernetes",
        "terraform": "Terraform",
        "ansible": "Ansible",
        "jenkins": "Jenkins",
        "ci/cd": "CI/CD",
        "continuous integration": "CI/CD",
        "continuous deployment": "CI/CD",
        "github actions": "GitHub Actions",
        "gitlab ci": "GitLab CI",
        "linux": "Linux",
        "nginx": "Nginx",
        "apache": "Apache",
        "serverless": "Serverless",
        "microservices": "Microservices",
        "cloud computing": "Cloud Computing",
    },
    "Databases & Storage": {
        "postgresql": "PostgreSQL",
        "postgres": "PostgreSQL",
        "mysql": "MySQL",
        "mongodb": "MongoDB",
        "sqlite": "SQLite",
        "redis": "Redis",
        "elasticsearch": "Elasticsearch",
        "cassandra": "Apache Cassandra",
        "dynamodb": "DynamoDB",
        "oracle": "Oracle DB",
        "sql server": "MS SQL Server",
        "mssql": "MS SQL Server",
        "firebase": "Firebase",
        "neo4j": "Neo4j",
    },
    "Tools & Methodologies": {
        "git": "Git",
        "github": "GitHub",
        "gitlab": "GitLab",
        "jira": "Jira",
        "agile": "Agile",
        "scrum": "Scrum",
        "kanban": "Kanban",
        "unit testing": "Unit Testing",
        "pytest": "PyTest",
        "jest": "Jest",
        "cypress": "Cypress",
        "selenium": "Selenium",
        "tdd": "Test-Driven Development (TDD)",
        "test driven development": "Test-Driven Development (TDD)",
        "oop": "OOP",
        "clean code": "Clean Code",
        "design patterns": "Design Patterns",
        "postman": "Postman",
    },
    "Soft Skills": {
        "communication": "Communication",
        "leadership": "Leadership",
        "problem solving": "Problem Solving",
        "critical thinking": "Critical Thinking",
        "teamwork": "Team Collaboration",
        "collaboration": "Team Collaboration",
        "team collaboration": "Team Collaboration",
        "time management": "Time Management",
        "mentoring": "Mentoring",
        "adaptability": "Adaptability",
        "analytical skills": "Analytical Skills",
        "cross-functional": "Cross-Functional Collaboration",
    }
}

# Equivalence clusters: If a job mentions multiple alternatives (e.g. PostgreSQL or MySQL),
# satisfying any one gives credit for the cluster.
TECH_EQUIVALENCE_CLUSTERS = [
    {"name": "Relational Databases", "skills": {"PostgreSQL", "MySQL", "SQLite", "Oracle DB", "MS SQL Server"}},
    {"name": "Cloud Providers", "skills": {"AWS", "Google Cloud (GCP)", "Microsoft Azure"}},
    {"name": "Backend Python Frameworks", "skills": {"FastAPI", "Django", "Flask"}},
    {"name": "Container & Orchestration", "skills": {"Docker", "Kubernetes"}},
    {"name": "Testing Frameworks", "skills": {"PyTest", "Jest", "Unit Testing"}},
    {"name": "Frontend Frameworks", "skills": {"React", "Vue.js", "Angular"}},
]


def extract_skills(text: str) -> Dict[str, any]:
    """
    Extracts canonical unique skills from text across all categories.
    Eliminates duplicates (e.g., React.js and React both map to 'React').
    """
    if not text or not isinstance(text, str):
        return {"all_skills": [], "by_category": {}, "count": 0}

    text_lower = text.lower()
    found_skills: Set[str] = set()
    categorized: Dict[str, Set[str]] = {category: set() for category in SKILL_TAXONOMY}

    for category, skills_dict in SKILL_TAXONOMY.items():
        # Sort pattern keys by length descending to match longer multi-word phrases first
        sorted_patterns = sorted(skills_dict.keys(), key=len, reverse=True)
        for pattern_str in sorted_patterns:
            canonical_name = skills_dict[pattern_str]
            if canonical_name in found_skills:
                continue

            escaped = re.escape(pattern_str)
            if pattern_str in ["c++", "c#", ".net", "node.js", "vue.js", "react.js", "ci/cd"]:
                regex = rf"(?:^|[\s,;:(/\[]){escaped}(?:$|[\s,;:)/\]])"
            elif len(pattern_str) <= 3:
                # Short terms need strict word boundaries
                regex = rf"\b{escaped}\b"
            else:
                regex = rf"\b{escaped}\b"

            if re.search(regex, text_lower):
                found_skills.add(canonical_name)
                categorized[category].add(canonical_name)

    # Contextual check for Go & R languages
    if re.search(r"\b(golang|go\s+(?:programming|developer|backend|code))\b", text_lower):
        found_skills.add("Go")
        categorized["Programming Languages"].add("Go")

    if re.search(r"\b(r\s+(?:programming|package|statistical|scripting|language))\b", text_lower):
        found_skills.add("R")
        categorized["Programming Languages"].add("R")

    # Clean up empty categories and sort
    cleaned_categorized = {k: sorted(list(v)) for k, v in categorized.items() if v}

    return {
        "all_skills": sorted(list(found_skills)),
        "by_category": cleaned_categorized,
        "count": len(found_skills)
    }


def compare_skills(resume_skills: List[str], jd_skills: List[str], raw_jd_text: str = "") -> Dict[str, any]:
    """
    Compares resume skills with job description skills.
    Accounts for 'or' alternatives (e.g. 'PostgreSQL or MySQL') using equivalence clusters.
    """
    resume_set = set(resume_skills)
    jd_set = set(jd_skills)

    matched = sorted(list(resume_set.intersection(jd_set)))
    missing = sorted(list(jd_set.difference(resume_set)))
    additional = sorted(list(resume_set.difference(jd_set)))

    # Check for cluster credit when job description implies alternative skills ("X or Y")
    jd_lower = raw_jd_text.lower() if raw_jd_text else ""
    bonus_cluster_matches: Set[str] = set()

    if " or " in jd_lower or "/" in jd_lower:
        for cluster in TECH_EQUIVALENCE_CLUSTERS:
            cluster_skills = cluster["skills"]
            jd_cluster_present = cluster_skills.intersection(jd_set)
            resume_cluster_present = cluster_skills.intersection(resume_set)

            # If JD asks for skills in this cluster and candidate has at least one equivalent,
            # don't unduly penalize alternative missing ones
            if len(jd_cluster_present) > 1 and len(resume_cluster_present) >= 1:
                for alt_skill in jd_cluster_present:
                    if alt_skill in missing:
                        # Candidate already fulfilled the cluster requirement (e.g. has Postgres, JD asked Postgres or MySQL)
                        bonus_cluster_matches.add(alt_skill)

    # Filter out secondary alternatives from critical missing
    adjusted_missing = [s for s in missing if s not in bonus_cluster_matches]

    if len(jd_set) == 0:
        match_percentage = 100.0 if len(resume_set) > 0 else 0.0
    else:
        # Effective matched skills count including alternative credits
        effective_matched = len(matched) + len(bonus_cluster_matches)
        match_percentage = round(min(100.0, (effective_matched / len(jd_set)) * 100.0), 1)

    return {
        "matched": matched,
        "missing": adjusted_missing,
        "alternative_credited": sorted(list(bonus_cluster_matches)),
        "additional": additional,
        "match_percentage": match_percentage
    }
