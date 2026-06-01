
from crewai import Task
from agents.ranking import ranking_agent

def create_matching_task(cv_text, job_description):

    return Task(

        description=f"""
You are an expert technical recruiter.

Analyze this candidate resume:

{cv_text}

Compare it with this job description:

{job_description}

STRICT RULES:
- Keep response concise
- Use short bullet points
- Avoid long explanations
- Do NOT create unnecessary sections
- Only mention skills explicitly present
- Avoid repeating information

Return output EXACTLY in this format:

# Candidate Match Report

## Match Percentage
Example: 78%

## Matching Skills
- Python
- Django
- SQL

## Missing Skills
- AWS
- Docker

## Strengths
- Strong backend projects
- Good problem-solving

## Recommendation
Choose ONLY ONE:
- Strong Fit
- Moderate Fit
- Weak Fit
## Final Summary
Maximum 3 concise lines.
""",

        expected_output="""
Concise recruiter-style evaluation report.
""",

        agent=ranking_agent
    )

