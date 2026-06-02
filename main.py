from tools.pdf_reader import extract_text_from_pdf
from tools.embedding_tool import create_embedding
from tools.vector_store import (
    store_cv,
    search_similar_cvs
)

from tasks.match_task import create_matching_task
from crew import create_crew

# STEP 1 — Extract CV text
cv_text = extract_text_from_pdf(
    "uploads/sample.pdf"
)

print("\nCV TEXT EXTRACTED\n")

# STEP 2 — Create embedding
cv_embedding = create_embedding(cv_text)

# STEP 3 — Store in ChromaDB
store_cv(
    cv_id="candidate_1",
    cv_text=cv_text,
    embedding=cv_embedding
)

print("\nCV STORED IN DATABASE\n")

# STEP 4 — Job description
job_description = """
Looking for a Python Backend Developer
with Django, REST API, SQL, and Git experience.
"""

# STEP 5 — Create job embedding
job_embedding = create_embedding(
    job_description
)

# STEP 6 — Search similar CVs
results = search_similar_cvs(
    job_embedding
)

print("\nMATCH RESULTS:\n")
print(results)

# STEP 7 — AI analysis using CrewAI
resume_skills = extract_skills(cv_text) 
jd_skills = extract_skills(job_description) 
task = create_matching_task( cv_text, job_description, resume_skills, jd_skills )
crew = create_crew(task) 
result = crew.kickoff()
print("\nFINAL AI REPORT:\n") 
print(result)