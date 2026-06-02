
import uuid
import re
import streamlit as st

from tools.skill_extractor import extract_skills
from tools.pdf_report import generate_pdf_report
from tools.pdf_reader import extract_text_from_pdf
from tools.embedding_tool import create_embedding
from tools.vector_store import (
    store_cv,
    search_similar_cvs
)

from tasks.match_task import create_matching_task
from crew import create_crew

# -----------------------------------
# PAGE CONFIG
# -----------------------------------
st.set_page_config(
    page_title="AI CV Matcher",
    page_icon="🤖",
    layout="wide"
)

# -----------------------------------
# SIDEBAR
# -----------------------------------
st.sidebar.title("⚙ Filters")

minimum_score = st.sidebar.slider(
    "Minimum Match Score",
    0,
    100,
    60
)

# -----------------------------------
# TITLE
# -----------------------------------
st.title("🤖 AI Candidate Ranking System")

st.markdown("""
Upload multiple resumes and compare them
against a job description using local AI.
""")

# -----------------------------------
# FILE UPLOAD
# -----------------------------------
uploaded_files = st.file_uploader(
    "Upload Resume PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

# -----------------------------------
# JOB DESCRIPTION
# -----------------------------------
job_description = st.text_area(
    "Enter Job Description",
    height=200
)

# -----------------------------------
# ANALYZE BUTTON
# -----------------------------------
if st.button("Analyze Candidates"):

    if uploaded_files and job_description:

        all_candidates = []

        for uploaded_file in uploaded_files:

            try:

                st.divider()

                st.subheader(
                    f"Processing: {uploaded_file.name}"
                )

                # -----------------------------------
                # SAVE PDF
                # -----------------------------------
                pdf_path = f"uploads/{uploaded_file.name}"

                with open(pdf_path, "wb") as f:
                    f.write(uploaded_file.read())

                # -----------------------------------
                # EXTRACT TEXT
                # -----------------------------------
                with st.spinner(
                    f"Extracting text from {uploaded_file.name}..."
                ):

                    cv_text = extract_text_from_pdf(
                        pdf_path
                    )

                    skills = extract_skills(cv_text)

                    st.subheader("🛠 Extracted Skills")
                    st.write(skills)

                # -----------------------------------
                # CREATE EMBEDDING
                # -----------------------------------
                cv_embedding = create_embedding(
                    cv_text
                )

                # -----------------------------------
                # STORE CV
                # -----------------------------------
                candidate_id = str(uuid.uuid4())

                store_cv(
                    cv_id=candidate_id,
                    cv_text=cv_text,
                    embedding=cv_embedding
                )

                # -----------------------------------
                # JOB EMBEDDING
                # -----------------------------------
                job_embedding = create_embedding(
                    job_description
                )

                # -----------------------------------
                # SEARCH SIMILAR CVS
                # -----------------------------------
                results = search_similar_cvs(
                    job_embedding
                )

                print("\nMATCH RESULTS:\n")
                print(results)

                # -----------------------------------
                # AI ANALYSIS
                # -----------------------------------
                with st.spinner(
                    f"Analyzing {uploaded_file.name}..."
                ):

                    resume_skills = extract_skills(cv_text)

                    jd_skills = extract_skills(job_description)

                    task = create_matching_task(
                        cv_text,
                        job_description,
                        resume_skills,
                        jd_skills
                    )

                    crew = create_crew(task)

                    result = crew.kickoff()

                    print("\nCrewAI Result:\n")
                    print(result)

                # -----------------------------------
                # SAFE RESULT HANDLING
                # -----------------------------------
                report_text = getattr(
                    result,
                    "raw",
                    str(result)
                )

                # -----------------------------------
                # EXTRACT SCORE
                # -----------------------------------
                score = 0

                match = re.search(
                    r'(\d+)%',
                    report_text
                )

                if match:
                    score = int(match.group(1))

                # -----------------------------------
                # STORE RESULTS
                # -----------------------------------
                all_candidates.append({

                    "name": uploaded_file.name,

                    "score": score,

                    "report": report_text
                })

            except Exception as e:

                st.error(
                    f"Error processing {uploaded_file.name}: {str(e)}"
                )

                print(f"ERROR: {str(e)}")

        # -----------------------------------
        # SORT CANDIDATES
        # -----------------------------------
        all_candidates.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        # -----------------------------------
        # FINAL RANKING
        # -----------------------------------
        st.divider()

        st.header("🏆 Candidate Rankings")

        for idx, candidate in enumerate(
            all_candidates,
            start=1
        ):

            # FILTER LOW SCORES
            if candidate['score'] < minimum_score:
                continue

            with st.container():

                st.markdown(f"""
                ## 🏆 Rank #{idx}

                ### 📄 {candidate['name']}

                ### 🎯 Match Score: {candidate['score']}%
                """)

                # -----------------------------------
                # SCORE BAR
                # -----------------------------------
                st.progress(
                    candidate['score'] / 100
                )

                # -----------------------------------
                # SCORE STATUS
                # -----------------------------------
                if candidate['score'] >= 80:

                    st.success(
                        f"Excellent ATS Match: {candidate['score']}%"
                    )

                elif candidate['score'] >= 60:

                    st.warning(
                        f"Moderate ATS Match: {candidate['score']}%"
                    )

                else:

                    st.error(
                        f"Low ATS Match: {candidate['score']}%"
                    )

                # -----------------------------------
                # AI REPORT
                # -----------------------------------
                st.subheader("📋 AI Analysis Report")

                st.write(candidate["report"])

                # -----------------------------------
                # PDF GENERATION
                # -----------------------------------
                try:

                    pdf_path = generate_pdf_report(
                        candidate['name'],
                        candidate['report']
                    )

                    with open(pdf_path, "rb") as pdf_file:

                        st.download_button(
                            label="📥 Download PDF Report",
                            data=pdf_file,
                            file_name=f"{candidate['name']}.pdf",
                            mime="application/pdf",
                            key=f"download_{idx}"
                        )

                except Exception as pdf_error:

                    st.error(
                        f"PDF generation failed: {str(pdf_error)}"
                    )

                st.divider()

    else:

        st.warning(
            "Please upload resumes and enter a job description."
        )

