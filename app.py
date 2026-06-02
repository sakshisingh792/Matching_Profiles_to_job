
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

def clean_report(report):

    remove_patterns = [

        r"=+.*",
        r"RESUME TEXT",
        r"JOB DESCRIPTION",
        r"EXTRACTED RESUME SKILLS",
        r"REQUIRED JOB SKILLS",
        r"IMPORTANT RULES",
        r"ONLY use skills.*",
        r"Do NOT invent.*",
        r"Be accurate.*",
        r"Keep response concise.*"
    ]

    cleaned_lines = []

    for line in report.splitlines():

        should_skip = False

        for pattern in remove_patterns:

            if re.search(pattern, line):

                should_skip = True
                break

        if not should_skip:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)



# -----------------------------------
# PAGE CONFIG
# -----------------------------------
st.set_page_config(
    page_title="AI CV Matcher",
    page_icon="🤖",
    layout="wide"
)

# -----------------------------------
# CUSTOM CSS
# -----------------------------------

st.markdown("""
<style>

.stApp {
    background-color: #020617;
    color: white;
}

header {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

.block-container {
    padding-top: 2rem;
    padding-left: 4rem;
    padding-right: 4rem;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(
        135deg,
        #8b5cf6,
        #6366f1
    );

    color: white;
    border: none;
    border-radius: 12px;

    padding: 14px 24px;

    font-size: 16px;
    font-weight: 600;

    transition: 0.3s;
}

.stButton > button:hover {
    transform: scale(1.03);
    background: linear-gradient(
        135deg,
        #7c3aed,
        #4f46e5
    );
}
            
 
/* Navbar */
.navbar {
    display:flex;
    justify-content:space-between;
    align-items:center;

    padding:18px 40px;

    background: rgba(15,23,42,0.7);

    border:1px solid #1e293b;

    border-radius:20px;

    backdrop-filter: blur(12px);

    margin-bottom:40px;
}

/* Logo */
.logo {
    font-size:28px;
    font-weight:800;
    color:white;
}

/* Nav Links */
.nav-links {
    display:flex;
    gap:35px;
    align-items:center;
}

.nav-links a {
    color:#cbd5e1;
    text-decoration:none;
    font-size:16px;
    font-weight:500;
}

/* CTA Button */
.nav-btn {
    background: linear-gradient(
        135deg,
        #8b5cf6,
        #6366f1
    );

    padding:10px 22px;

    border-radius:12px;

    color:white !important;

    font-weight:600;
}
            
            
/* ATS Floating Card */

.ats-card {

    background: rgba(15,23,42,0.85);

    padding:25px;

    border-radius:24px;

    width:280px;

    border:1px solid #334155;

    box-shadow:0 8px 24px rgba(0,0,0,0.45);

    margin-top:-120px;

    margin-left:40px;

    position:relative;

    z-index:999;
}

.ats-success {

    color:#4ade80;

    font-size:14px;

    margin-bottom:10px;

    font-weight:600;
}

.ats-score {

    font-size:58px;

    font-weight:800;

    color:white;

    line-height:1;
}

.ats-label {

    color:#cbd5e1;

    margin-top:12px;

    font-size:18px;
}

.ats-role {

    color:#94a3b8;

    margin-top:8px;

    font-size:15px;
}
            
   
/* Upload Section */

.upload-wrapper {

    background: rgba(15,23,42,0.75);

    padding:40px;

    border-radius:30px;

    border:1px solid #1e293b;

    margin-top:60px;

    backdrop-filter: blur(12px);
}

.upload-title {

    font-size:42px;

    font-weight:800;

    color:white;

    margin-bottom:12px;
}

.upload-subtitle {

    color:#94a3b8;

    font-size:18px;

    margin-bottom:35px;
}

         

/* Candidate Cards */

.candidate-card {

    background: rgba(15,23,42,0.75);

    border:1px solid #1e293b;

    border-radius:28px;

    padding:35px;

    margin-top:30px;

    backdrop-filter: blur(12px);

    box-shadow:0 8px 24px rgba(0,0,0,0.35);

    transition:0.3s;
}

.candidate-card:hover {

    transform: translateY(-5px);
}

.rank-badge {

    display:inline-block;

    background:#8b5cf6;

    color:white;

    padding:8px 18px;

    border-radius:20px;

    font-size:14px;

    font-weight:700;

    margin-bottom:20px;
}

.candidate-name {

    font-size:34px;

    font-weight:800;

    color:white;

    margin-bottom:20px;
}

.score-text {

    font-size:64px;

    font-weight:900;

    color:#4ade80;

    line-height:1;
}

.score-label {

    color:#94a3b8;

    margin-top:10px;

    font-size:18px;
}




           

</style>
""", unsafe_allow_html=True)



# -----------------------------------
# NAVBAR
# -----------------------------------

st.markdown("""
<div class="navbar">

<div class="logo">
🤖 MatchSphere
</div>

<div class="nav-links">

<a href="#">Home</a>

<a href="#">Upload</a>

<a href="#">Dashboard</a>

<a href="#">Results</a>

<a href="#" class="nav-btn">
Get Started
</a>

</div>

</div>
""", unsafe_allow_html=True)



# -----------------------------------
# HERO SECTION
# -----------------------------------

left_col, right_col = st.columns([1.2, 1])

with left_col:

    st.markdown("""
    <div style="
        padding-top:40px;
    ">

    <div style="
        background:#1e1b4b;
        color:#c4b5fd;
        display:inline-block;
        padding:8px 16px;
        border-radius:20px;
        font-size:14px;
        margin-bottom:25px;
        font-weight:600;
    ">
    ✨ AI Powered ATS Matching
    </div>

    <h1 style="
        font-size:68px;
        line-height:1.1;
        color:white;
        font-weight:800;
        margin-bottom:25px;
    ">
    Find Your Perfect <br>
    Candidate Match <br>
    With AI
    </h1>

    <p style="
        color:#cbd5e1;
        font-size:22px;
        line-height:1.7;
        margin-bottom:35px;
    ">
    Analyze resumes using AI-powered ATS matching,
    semantic search, and intelligent candidate ranking
    for recruiters and hiring teams.
    </p>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.button(
            "🚀 Get Started",
            use_container_width=True
        )

    with col2:
        st.button(
            "📊 Learn More",
            use_container_width=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    metric1, metric2, metric3 = st.columns(3)

    with metric1:
        st.metric(
            "ATS Accuracy",
            "95%"
        )

    with metric2:
        st.metric(
            "Resume Match",
            "10x Faster"
        )

    with metric3:
        st.metric(
            "AI Analysis",
            "Realtime"
        )





with right_col:

    st.image(
        "https://images.unsplash.com/photo-1552664730-d307ca884978?q=80&w=1200&auto=format&fit=crop",
        width=700
    )

    card_col1, card_col2 = st.columns(2)

    with card_col1:

        st.markdown("""
        <div class="ats-card" 
                    style="margin-top:-70px;
                    margin-left:60px;">

        <div class="ats-success">
        ✅ Perfect Match Found
        </div>

        <div class="ats-score">
        98%
        </div>

        <div class="ats-label">
        ATS Match Score
        </div>

        <div class="ats-role">
        Senior Python Developer
        </div>

        </div>
        """, unsafe_allow_html=True)

    with card_col2:

        st.markdown("""
            <div class="ats-card" style="
            margin-top:-10px;
            margin-left:-20px;
            width:240px;
        ">
                

        <div class="ats-label">
        🚀 AI Ranking
        </div>

        <div class="ats-score" style="
            font-size:34px;
            color:#8b5cf6;
        ">
        #1 Candidate
        </div>

        </div>
        """, unsafe_allow_html=True)




    

    
    





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


# -----------------------------------
# UPLOAD SECTION
# -----------------------------------

st.markdown("""
<div class="upload-wrapper">

<div class="upload-title">
Upload & Analyze Candidates
</div>

<div class="upload-subtitle">
Upload resumes and compare candidates
using AI-powered ATS matching.
</div>

""", unsafe_allow_html=True)


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
st.markdown(
    "</div>",
    unsafe_allow_html=True
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

                    skill_html = ""

                    for skill in skills:

                        skill_html += f"""
                        <span style="
                            background:#111827;
                            color:#8b5cf6;
                            padding:8px 16px;
                            border-radius:20px;
                            margin:6px;
                            display:inline-block;
                            font-size:14px;
                            font-weight:600;
                            border:1px solid #312e81;
                        ">
                            {skill}
                        </span>
                        """

                    st.markdown(
                        skill_html,
                        unsafe_allow_html=True
                    )



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
                
                report_text = clean_report(report_text)



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
                <div class="candidate-card">

                <div class="rank-badge">
                🏆 Rank #{idx}
                </div>

                <div class="candidate-name">
                📄 {candidate['name']}
                </div>

                <div class="score-text">
                {candidate['score']}%
                </div>

                <div class="score-label">
                ATS Match Score
                </div>

                </div>
                """, unsafe_allow_html=True)



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
                 
            
            with st.expander(
                "📋 View AI Analysis Report",
                expanded=False
            ):

                st.markdown("""
                <style>
                .report-box {
                    background: rgba(15,23,42,0.6);
                    padding: 25px;
                    border-radius: 20px;
                    border: 1px solid #1e293b;
                    margin-top: 10px;
                }
                </style>
                """, unsafe_allow_html=True)

                st.markdown(
                    f"""
                    <div class="report-box">
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                
                st.markdown(
                    clean_report(candidate["report"])
                )





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

