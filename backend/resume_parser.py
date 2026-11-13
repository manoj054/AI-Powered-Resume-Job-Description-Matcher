"""
resume_parser.py
Resume Parser Module for AI-Resume-Matcher
Extracts text and key sections from PDF resumes using pypdf.
"""

import io
import re
from typing import Dict, List, Optional, Union
import pypdf

from text_cleaning import clean_text


class ResumeParser:
    """
    Parses resume documents (PDF, text) and extracts raw text, clean text,
    and identified sections (Experience, Skills, Education, Projects).
    """

    # Section header detection patterns
    SECTION_PATTERNS = {
        "summary": r"(?:summary|professional summary|profile|about me|objective)",
        "skills": r"(?:skills|technical skills|technologies|core competencies|expertise|tools)",
        "experience": r"(?:work experience|experience|employment history|work history|professional experience)",
        "education": r"(?:education|academic background|qualifications|degrees)",
        "projects": r"(?:projects|personal projects|technical projects|key projects)",
        "certifications": r"(?:certifications|certificates|licenses|courses)"
    }

    @staticmethod
    def extract_text_from_pdf(pdf_source: Union[str, bytes, io.BytesIO]) -> str:
        """
        Extracts raw text from a PDF file path, byte stream, or BytesIO object.
        """
        extracted_pages: List[str] = []

        try:
            if isinstance(pdf_source, (bytes, bytearray)):
                stream = io.BytesIO(pdf_source)
                reader = pypdf.PdfReader(stream)
            elif isinstance(pdf_source, io.BytesIO):
                reader = pypdf.PdfReader(pdf_source)
            else:
                reader = pypdf.PdfReader(pdf_source)

            # Check if encrypted
            if reader.is_encrypted:
                try:
                    reader.decrypt("")
                except Exception:
                    raise ValueError("The provided PDF file is password protected.")

            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                if page_text.strip():
                    extracted_pages.append(page_text.strip())

        except Exception as e:
            if "password" in str(e).lower():
                raise
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")

        full_text = "\n\n".join(extracted_pages)
        if not full_text.strip():
            raise ValueError("The PDF document does not contain any extractable text (it might be an image or scanned document).")

        return full_text

    @classmethod
    def extract_sections(cls, text: str) -> Dict[str, str]:
        """
        Attempts to segment resume text into sections based on header patterns.
        """
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        sections: Dict[str, List[str]] = {sec: [] for sec in cls.SECTION_PATTERNS}
        current_section: Optional[str] = None

        for line in lines:
            line_lower = line.lower().strip(" :#-_*")
            
            # Check if this line matches any section header
            matched_header = None
            if len(line.split()) <= 4:  # Headers are usually short
                for sec_name, pattern in cls.SECTION_PATTERNS.items():
                    if re.fullmatch(pattern, line_lower):
                        matched_header = sec_name
                        break
            
            if matched_header:
                current_section = matched_header
            elif current_section:
                sections[current_section].append(line)

        return {k: "\n".join(v) for k, v in sections.items() if v}

    @classmethod
    def parse(cls, pdf_source: Union[str, bytes, io.BytesIO]) -> Dict[str, any]:
        """
        Full parse pipeline for a resume PDF:
        - Extracts raw text
        - Cleans text
        - Extracts sections
        """
        raw_text = cls.extract_text_from_pdf(pdf_source)
        cleaned = clean_text(raw_text, remove_stopwords=False)
        nlp_cleaned = clean_text(raw_text, remove_stopwords=True)
        sections = cls.extract_sections(raw_text)

        return {
            "raw_text": raw_text,
            "cleaned_text": cleaned,
            "nlp_tokens_text": nlp_cleaned,
            "sections": sections,
            "char_count": len(raw_text),
            "word_count": len(raw_text.split())
        }

