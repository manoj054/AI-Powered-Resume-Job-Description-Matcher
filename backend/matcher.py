"""
matcher.py
Matching Engine Module for AI-Resume-Matcher
Features:
- Calibrated TF-IDF cosine similarity: S-curve mapping calibrated for natural resume-JD pairs.
- Keyword presence & coverage calculation.
- Skill overlap with equivalence awareness.
- Actionable, prioritized resume recommendations.
"""

import math
import re
from typing import Dict, List, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from text_cleaning import clean_text, tokenize
from skill_extractor import extract_skills, compare_skills

POWER_ACTION_VERBS = [
    "accelerated", "achieved", "architected", "automated", "built", "collaborated",
    "delivered", "deployed", "designed", "developed", "engineered", "established",
    "executed", "implemented", "improved", "increased", "initiated", "launched",
    "led", "managed", "mentored", "optimized", "orchestrated", "overhauled",
    "reduced", "refactored", "resolved", "scaled", "spearheaded", "streamlined"
]


class ResumeMatcher:
    """
    Computes calibrated semantic similarity, skill gap analysis,
    keyword coverage, and tailored resume optimization suggestions.
    """

    def __init__(self, skill_weight: float = 0.50, tfidf_weight: float = 0.30, keyword_weight: float = 0.20):
        self.skill_weight = skill_weight
        self.tfidf_weight = tfidf_weight
        self.keyword_weight = keyword_weight

    def calculate_raw_tfidf_similarity(self, resume_cleaned: str, jd_cleaned: str) -> float:
        """Computes raw cosine similarity using TF-IDF."""
        if not resume_cleaned.strip() or not jd_cleaned.strip():
            return 0.0

        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words="english",
            max_features=5000,
            token_pattern=r"(?u)\b\w[\w-]*\w\b|\b\w\b"
        )

        try:
            tfidf_matrix = vectorizer.fit_transform([resume_cleaned, jd_cleaned])
            raw_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(np.clip(raw_sim, 0.0, 1.0))
        except Exception:
            return 0.0

    @staticmethod
    def calibrate_semantic_score(raw_cosine: float) -> float:
        """
        Calibrates raw document cosine similarity into a standard 0-100% semantic score.
        In natural language document pairs (resume vs JD), raw cosine rarely exceeds 0.35.
        Uses a smooth progressive mapping:
        - raw 0.05 -> ~30%
        - raw 0.12 -> ~55%
        - raw 0.20 -> ~75%
        - raw 0.30 -> ~90%
        - raw >= 0.35 -> 95-100%
        """
        if raw_cosine <= 0.0:
            return 0.0
        if raw_cosine < 0.05:
            score = (raw_cosine / 0.05) * 30.0
        elif raw_cosine < 0.15:
            score = 30.0 + ((raw_cosine - 0.05) / 0.10) * 30.0
        elif raw_cosine < 0.28:
            score = 60.0 + ((raw_cosine - 0.15) / 0.13) * 25.0
        else:
            score = 85.0 + ((raw_cosine - 0.28) / 0.12) * 15.0

        return round(float(np.clip(score, 0.0, 100.0)), 1)

    def extract_top_keywords(self, jd_raw: str, resume_raw: str, top_n: int = 15) -> List[Dict[str, any]]:
        """
        Extracts salient keywords from job description with TF-IDF importance scores
        and checks if they appear in the resume.
        """
        jd_clean = clean_text(jd_raw, remove_stopwords=True)
        resume_clean = clean_text(resume_raw, remove_stopwords=False).lower()

        if not jd_clean:
            return []

        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words="english",
            max_features=120
        )

        try:
            matrix = vectorizer.fit_transform([jd_clean])
            feature_names = vectorizer.get_feature_names_out()
            scores = matrix.toarray()[0]

            sorted_indices = np.argsort(scores)[::-1]
            keywords = []

            for idx in sorted_indices:
                word = feature_names[idx]
                # Filter out single-letter or overly generic words
                if len(word) <= 2 and word not in ["ai", "ml", "ui", "ux", "ci", "cd", "db", "qa"]:
                    continue

                pattern = rf"\b{re.escape(word)}\b"
                in_resume = bool(re.search(pattern, resume_clean))

                keywords.append({
                    "keyword": word,
                    "importance": round(float(scores[idx]), 3),
                    "in_resume": in_resume
                })

                if len(keywords) >= top_n:
                    break

            return keywords
        except Exception:
            return []

    def generate_suggestions(
        self,
        resume_raw: str,
        missing_skills: List[str],
        matched_skills: List[str],
        missing_keywords: List[str],
        match_score: float
    ) -> List[Dict[str, str]]:
        """Generates actionable, prioritized improvement recommendations."""
        suggestions: List[Dict[str, str]] = []
        resume_lower = resume_raw.lower()

        # 1. Missing Core Skills
        if missing_skills:
            top_missing = missing_skills[:6]
            formatted = ", ".join(top_missing)
            suggestions.append({
                "type": "skills_gap",
                "severity": "high" if len(missing_skills) >= 4 else "medium",
                "title": "Address Key Missing Skills",
                "description": f"The job description highlights requirements not detected in your resume: {formatted}.",
                "action": f"Add concrete projects, certifications, or bullet points demonstrating experience with {formatted}."
            })

        # 2. Missing ATS Keywords
        if missing_keywords:
            top_kw = missing_keywords[:5]
            kw_str = ", ".join(f"'{k}'" for k in top_kw)
            suggestions.append({
                "type": "keyword_optimization",
                "severity": "medium",
                "title": "Incorporate Relevant Keywords",
                "description": f"Target keywords from the job posting are missing from your resume: {kw_str}.",
                "action": f"Naturally integrate keywords like {kw_str} into your work experience or project summaries."
            })

        # 3. Quantifiable Impact & Metrics Check
        has_metrics = bool(re.search(r"\b(?:\d+%(?: increase| reduction| growth)?|\$\d+[\d,]*|\d+\+?\s*(?:users|clients|projects|features|engineers|team members))\b", resume_raw, re.IGNORECASE))
        if not has_metrics:
            suggestions.append({
                "type": "impact_metrics",
                "severity": "medium",
                "title": "Add Measurable Metrics & Results",
                "description": "Your bullet points lack quantifiable numbers (percentages, scale, dollar savings, user metrics).",
                "action": "Use the Google X-Y-Z formula: 'Accomplished [X], as measured by [Y], by doing [Z]' (e.g. 'Boosted API performance by 35% with Redis caching')."
            })

        # 4. Action Verbs Check
        verbs_found = [verb for verb in POWER_ACTION_VERBS if re.search(rf"\b{verb}\b", resume_lower)]
        if len(verbs_found) < 4:
            suggestions.append({
                "type": "action_verbs",
                "severity": "low",
                "title": "Strengthen Bullet Points with Dynamic Action Verbs",
                "description": "Start bullet points with strong active verbs instead of passive phrases like 'Responsible for' or 'Worked on'.",
                "action": "Begin achievements with verbs such as 'Architected', 'Spearheaded', 'Optimized', 'Automated', or 'Deployed'."
            })

        # 5. Tailored Summary Check
        has_summary = bool(re.search(r"\b(summary|objective|profile|about me)\b", resume_lower))
        if not has_summary:
            suggestions.append({
                "type": "formatting",
                "severity": "low",
                "title": "Add a Tailored Professional Summary",
                "description": "No dedicated summary section detected at the top of the resume.",
                "action": f"Include a 2-3 sentence executive summary tailored to this position highlighting your core strengths."
            })

        return suggestions

    def match(self, resume_text: str, jd_text: str) -> Dict[str, any]:
        """
        Executes complete multi-factor matching analysis.
        Returns composite score, skill breakdowns, keyword coverage, and suggestions.
        """
        resume_clean = clean_text(resume_text, remove_stopwords=True)
        jd_clean = clean_text(jd_text, remove_stopwords=True)

        # 1. TF-IDF Cosine Similarity & Calibration
        raw_tfidf = self.calculate_raw_tfidf_similarity(resume_clean, jd_clean)
        calibrated_tfidf = self.calibrate_semantic_score(raw_tfidf)

        # 2. Extract Skills
        resume_skills_data = extract_skills(resume_text)
        jd_skills_data = extract_skills(jd_text)

        resume_skills = resume_skills_data["all_skills"]
        jd_skills = jd_skills_data["all_skills"]

        # 3. Compare Skills with equivalence awareness
        skill_comparison = compare_skills(resume_skills, jd_skills, raw_jd_text=jd_text)
        skill_percentage = skill_comparison["match_percentage"]

        # 4. Keyword Analysis & Coverage Score
        keywords_matrix = self.extract_top_keywords(jd_text, resume_text, top_n=15)
        if keywords_matrix:
            present_kw_count = sum(1 for k in keywords_matrix if k["in_resume"])
            keyword_coverage = round((present_kw_count / len(keywords_matrix)) * 100.0, 1)
            missing_keywords = [k["keyword"] for k in keywords_matrix if not k["in_resume"]]
        else:
            keyword_coverage = skill_percentage
            missing_keywords = []

        # 5. Weighted Composite Score
        if len(jd_skills) == 0:
            composite_score = calibrated_tfidf
        else:
            composite_score = round(
                (self.skill_weight * skill_percentage) +
                (self.tfidf_weight * calibrated_tfidf) +
                (self.keyword_weight * keyword_coverage),
                1
            )
            composite_score = float(np.clip(composite_score, 0.0, 100.0))

        # 6. Suggestions
        suggestions = self.generate_suggestions(
            resume_raw=resume_text,
            missing_skills=skill_comparison["missing"],
            matched_skills=skill_comparison["matched"],
            missing_keywords=missing_keywords,
            match_score=composite_score
        )

        return {
            "match_percentage": composite_score,
            "tfidf_score": calibrated_tfidf,
            "raw_cosine": round(raw_tfidf, 4),
            "skill_score": skill_percentage,
            "keyword_coverage": keyword_coverage,
            "matched_skills": skill_comparison["matched"],
            "missing_skills": skill_comparison["missing"],
            "additional_skills": skill_comparison["additional"],
            "alternative_credited": skill_comparison.get("alternative_credited", []),
            "resume_skills": resume_skills,
            "jd_skills": jd_skills,
            "skills_by_category": resume_skills_data["by_category"],
            "jd_skills_by_category": jd_skills_data["by_category"],
            "keywords": keywords_matrix,
            "suggestions": suggestions,
            "summary_stats": {
                "resume_skill_count": len(resume_skills),
                "jd_skill_count": len(jd_skills),
                "matched_skill_count": len(skill_comparison["matched"]),
                "missing_skill_count": len(skill_comparison["missing"])
            }
        }
