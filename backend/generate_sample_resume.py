"""
generate_sample_resume.py
Generates a realistic, professional sample PDF resume using ReportLab.
"""

from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def build_sample_resume_pdf(output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    header_name_style = ParagraphStyle(
        'HeaderName',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1E293B'),
        alignment=1  # Centered
    )

    sub_header_style = ParagraphStyle(
        'SubHeader',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#475569'),
        alignment=1  # Centered
    )

    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=4
    )

    job_title_style = ParagraphStyle(
        'JobTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#1E293B')
    )

    company_date_style = ParagraphStyle(
        'CompanyDate',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#64748B'),
        alignment=2  # Right-aligned
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#334155')
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12.5,
        textColor=colors.HexColor('#334155'),
        leftIndent=14,
        firstLineIndent=-10
    )

    elements = []

    # 1. Header
    elements.append(Paragraph("ALEX MORGAN", header_name_style))
    elements.append(Spacer(1, 3))
    elements.append(Paragraph("alex.morgan@email.com • (555) 019-2834 • San Francisco, CA • linkedin.com/in/alexmorgan • github.com/alexmorgan", sub_header_style))
    elements.append(Spacer(1, 8))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2563EB'), spaceAfter=8))

    # 2. Professional Summary
    elements.append(Paragraph("PROFESSIONAL SUMMARY", section_title_style))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#CBD5E1'), spaceAfter=4))
    elements.append(Paragraph(
        "Results-driven Full Stack & AI Software Engineer with 4+ years of industry experience architecting "
        "high-throughput backend microservices, intuitive modern web applications, and NLP-driven intelligence systems. "
        "Proficient in Python, FastAPI, React, PostgreSQL, Docker, and AWS. Proven track record of improving system latency "
        "by 45% and leading cross-functional engineering teams in agile environments.",
        body_style
    ))
    elements.append(Spacer(1, 8))

    # 3. Technical Skills
    elements.append(Paragraph("TECHNICAL SKILLS", section_title_style))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#CBD5E1'), spaceAfter=4))
    skills_text = (
        "<b>Programming Languages:</b> Python, JavaScript, TypeScript, SQL, HTML5, CSS3, Bash<br/>"
        "<b>Web Frameworks & Libraries:</b> FastAPI, Django, React.js, Next.js, Tailwind CSS, RESTful APIs, WebSockets<br/>"
        "<b>Machine Learning & Data:</b> Scikit-Learn, Pandas, NumPy, Natural Language Processing (NLP), PyTorch<br/>"
        "<b>Cloud & DevOps:</b> Docker, AWS (S3, EC2, Lambda), CI/CD, GitHub Actions, Linux, Nginx<br/>"
        "<b>Databases & Caching:</b> PostgreSQL, Redis, SQLite, MongoDB<br/>"
        "<b>Testing & Methodologies:</b> PyTest, Unit Testing, Git, Agile, Scrum, Microservices"
    )
    elements.append(Paragraph(skills_text, body_style))
    elements.append(Spacer(1, 8))

    # 4. Work Experience
    elements.append(Paragraph("WORK EXPERIENCE", section_title_style))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#CBD5E1'), spaceAfter=6))

    # Job 1
    job1_table_data = [[
        Paragraph("<b>Senior Full Stack Engineer</b> • <i>Nexus Tech Solutions</i>", job_title_style),
        Paragraph("San Francisco, CA • 2022 – Present", company_date_style)
    ]]
    t1 = Table(job1_table_data, colWidths=[360, 180])
    t1.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0,0), (-1,-1), 0), ('RIGHTPADDING', (0,0), (-1,-1), 0)]))
    elements.append(t1)
    elements.append(Spacer(1, 3))
    elements.append(Paragraph("• Architected and deployed scalable RESTful microservices using Python and FastAPI, serving 2M+ daily active requests with 99.9% uptime.", bullet_style))
    elements.append(Paragraph("• Built dynamic, responsive user interfaces with React, TypeScript, and Tailwind CSS, increasing user engagement metrics by 35%.", bullet_style))
    elements.append(Paragraph("• Implemented distributed caching and session management using Redis, cutting average database response latency from 180ms to 40ms.", bullet_style))
    elements.append(Paragraph("• Orchestrated containerized deployments via Docker and automated CI/CD pipelines with GitHub Actions, reducing deployment time by 75%.", bullet_style))
    elements.append(Paragraph("• Mentored junior engineers, established code review standards, and authored unit testing suites in PyTest with 90%+ code coverage.", bullet_style))
    elements.append(Spacer(1, 6))

    # Job 2
    job2_table_data = [[
        Paragraph("<b>Software Developer</b> • <i>DataSphere Analytics</i>", job_title_style),
        Paragraph("San Jose, CA • 2020 – 2022", company_date_style)
    ]]
    t2 = Table(job2_table_data, colWidths=[360, 180])
    t2.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0,0), (-1,-1), 0), ('RIGHTPADDING', (0,0), (-1,-1), 0)]))
    elements.append(t2)
    elements.append(Spacer(1, 3))
    elements.append(Paragraph("• Developed data extraction and NLP preprocessing pipelines using Python, Pandas, and Scikit-Learn to process over 500,000 text documents.", bullet_style))
    elements.append(Paragraph("• Designed relational schemas and optimized queries in PostgreSQL, achieving a 30% reduction in query execution times.", bullet_style))
    elements.append(Paragraph("• Collaborated with product managers in bi-weekly Agile/Scrum sprints to ship 12 client-facing features on schedule.", bullet_style))
    elements.append(Spacer(1, 8))

    # 5. Education
    elements.append(Paragraph("EDUCATION", section_title_style))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#CBD5E1'), spaceAfter=4))
    edu_table_data = [[
        Paragraph("<b>University of California, Berkeley</b> — B.S. in Computer Science", job_title_style),
        Paragraph("Berkeley, CA • Graduated 2020", company_date_style)
    ]]
    t_edu = Table(edu_table_data, colWidths=[360, 180])
    t_edu.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0,0), (-1,-1), 0), ('RIGHTPADDING', (0,0), (-1,-1), 0)]))
    elements.append(t_edu)
    elements.append(Paragraph("Relevant Coursework: Data Structures & Algorithms, Artificial Intelligence, Database Management Systems, Software Engineering.", body_style))
    elements.append(Spacer(1, 8))

    # 6. Projects & Certifications
    elements.append(Paragraph("PROJECTS & CERTIFICATIONS", section_title_style))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#CBD5E1'), spaceAfter=4))
    elements.append(Paragraph("• <b>AWS Certified Solutions Architect – Associate</b> (Amazon Web Services)", bullet_style))
    elements.append(Paragraph("• <b>AI Resume & Job Matcher:</b> Built open-source TF-IDF and NLP skill gap analysis web application with FastAPI and React.", bullet_style))

    doc.build(elements)
    print(f"Sample resume PDF generated successfully at: {output_path}")


if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent / "sample_data"
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = str(out_dir / "sample_resume.pdf")
    build_sample_resume_pdf(pdf_path)

