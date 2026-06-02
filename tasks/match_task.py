
from crewai import Task
from agents.ranking import ranking_agent

def create_matching_task(
    cv_text,
    job_description,
    resume_skills,
    jd_skills
):

    return Task(

        description=f"""
You are an expert ATS recruiter and resume evaluator.

Your task is to compare the candidate resume
with the job description carefully.

==============================
RESUME TEXT
==============================

{cv_text}

==============================
JOB DESCRIPTION
==============================

{job_description}

==============================
EXTRACTED RESUME SKILLS
==============================

{resume_skills}

==============================
REQUIRED JOB SKILLS
==============================

{jd_skills}

IMPORTANT RULES:

- ONLY use skills from the extracted skill lists
- Do NOT invent technologies
- Do NOT mark a skill missing if it exists in resume skills
- Be accurate and strict
- Keep response concise
- Use bullet points only
- ATS Score must be realistic
- Give higher ATS score if most required skills exist

==============================
OUTPUT FORMAT
==============================

# Candidate Match Report

## ATS Score
85%

## Matching Skills
- Python
- SQL
- Git

## Missing Skills
- Docker
- AWS

## Strengths
- Strong backend development
- Good database knowledge

## Weaknesses
- Limited cloud exposure
- Missing deployment experience

## Recommendation
Strong Fit

## Final Summary
Candidate matches most backend requirements with strong technical skills.

```python id="x3p9vq"
IMPORTANT:
Do NOT include:
- RESUME TEXT
- JOB DESCRIPTION
- EXTRACTED RESUME SKILLS
- REQUIRED JOB SKILLS
- IMPORTANT RULES
- separators like =======
- debugging information

Only return the final ATS report.
```

""",

        expected_output="""
Structured ATS evaluation report.
""",

        agent=ranking_agent
    )

