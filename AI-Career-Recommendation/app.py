import streamlit as st
import pandas as pd
import re
import io
from collections import Counter
from pypdf import PdfReader
from docx import Document


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="AI Career & Job Recommendation",
    page_icon="🚀",
    layout="wide"
)


# --------------------------------------------------
# SKILLS DATABASE
# --------------------------------------------------

SKILLS = [
    "Python", "Java", "C++", "JavaScript", "SQL",
    "HTML", "CSS", "React", "Node.js",
    "Machine Learning", "Deep Learning", "Artificial Intelligence",
    "Data Science", "Data Analysis", "Statistics",
    "Pandas", "NumPy", "Matplotlib", "Power BI", "Tableau",
    "TensorFlow", "PyTorch", "Scikit-learn",
    "NLP", "Computer Vision", "Generative AI",
    "Excel", "AWS", "Azure", "Google Cloud",
    "MongoDB", "MySQL", "PostgreSQL",
    "Git", "Docker", "Flask", "Django", "Streamlit",
    "Communication", "Problem Solving", "Teamwork",
    "Leadership", "Critical Thinking"
]


# --------------------------------------------------
# SAMPLE JOB ROLE DATABASE
# These are example role templates, not live vacancies.
# --------------------------------------------------

JOBS = [
    {
        "role": "AI/ML Intern",
        "category": "Artificial Intelligence",
        "skills": [
            "Python", "Machine Learning", "Statistics",
            "Pandas", "NumPy", "Scikit-learn"
        ],
        "interests": ["Artificial Intelligence", "Machine Learning", "Research"],
        "experience": "Fresher",
        "education": ["B.Tech", "B.Sc", "M.Tech"],
        "locations": ["Pune", "Mumbai", "Bangalore", "Remote"],
        "description": "Work on machine learning models, data preparation and AI applications.",
        "level": "Internship"
    },
    {
        "role": "Data Analyst",
        "category": "Data Science",
        "skills": [
            "Python", "SQL", "Excel", "Power BI",
            "Statistics", "Data Analysis"
        ],
        "interests": ["Data Analysis", "Business Analytics"],
        "experience": "Fresher",
        "education": ["B.Tech", "B.Sc", "B.Com", "M.Tech"],
        "locations": ["Pune", "Mumbai", "Bangalore", "Remote"],
        "description": "Analyze data, prepare reports and create business dashboards.",
        "level": "Entry Level"
    },
    {
        "role": "Python Developer",
        "category": "Software Development",
        "skills": [
            "Python", "SQL", "Git", "Django", "Flask",
            "Problem Solving"
        ],
        "interests": ["Software Development", "Backend Development"],
        "experience": "Fresher",
        "education": ["B.Tech", "BCA", "MCA", "M.Tech"],
        "locations": ["Pune", "Mumbai", "Bangalore", "Remote"],
        "description": "Develop Python applications, APIs and backend services.",
        "level": "Entry Level"
    },
    {
        "role": "Data Scientist",
        "category": "Data Science",
        "skills": [
            "Python", "Machine Learning", "Statistics",
            "Pandas", "NumPy", "Scikit-learn",
            "Data Science"
        ],
        "interests": ["Data Science", "Machine Learning", "Research"],
        "experience": "1-2 Years",
        "education": ["B.Tech", "M.Tech", "M.Sc"],
        "locations": ["Pune", "Mumbai", "Bangalore", "Remote"],
        "description": "Build predictive models and extract insights from complex datasets.",
        "level": "Entry Level"
    },
    {
        "role": "Frontend Developer",
        "category": "Web Development",
        "skills": [
            "HTML", "CSS", "JavaScript", "React",
            "Git", "Problem Solving"
        ],
        "interests": ["Web Development", "Software Development"],
        "experience": "Fresher",
        "education": ["B.Tech", "BCA", "MCA", "B.Sc"],
        "locations": ["Pune", "Mumbai", "Bangalore", "Remote"],
        "description": "Create responsive websites and interactive user interfaces.",
        "level": "Entry Level"
    },
    {
        "role": "Data Engineer",
        "category": "Data Engineering",
        "skills": [
            "Python", "SQL", "AWS", "Azure",
            "MongoDB", "Docker"
        ],
        "interests": ["Data Engineering", "Cloud Computing"],
        "experience": "1-2 Years",
        "education": ["B.Tech", "M.Tech", "MCA"],
        "locations": ["Pune", "Mumbai", "Bangalore", "Remote"],
        "description": "Build data pipelines and manage data infrastructure.",
        "level": "Entry Level"
    },
    {
        "role": "NLP Engineer",
        "category": "Artificial Intelligence",
        "skills": [
            "Python", "NLP", "Machine Learning",
            "Deep Learning", "Generative AI", "PyTorch"
        ],
        "interests": ["Artificial Intelligence", "Research", "Machine Learning"],
        "experience": "1-2 Years",
        "education": ["B.Tech", "M.Tech", "M.Sc"],
        "locations": ["Pune", "Mumbai", "Bangalore", "Remote"],
        "description": "Develop applications that understand and process human language.",
        "level": "Entry Level"
    },
    {
        "role": "Business Intelligence Analyst",
        "category": "Business Analytics",
        "skills": [
            "SQL", "Excel", "Power BI",
            "Tableau", "Statistics", "Data Analysis"
        ],
        "interests": ["Business Analytics", "Data Analysis"],
        "experience": "Fresher",
        "education": ["B.Tech", "B.Com", "B.Sc", "MBA"],
        "locations": ["Pune", "Mumbai", "Bangalore", "Remote"],
        "description": "Create business reports, dashboards and analytical insights.",
        "level": "Entry Level"
    }
]


# --------------------------------------------------
# RESUME TEXT EXTRACTION
# --------------------------------------------------

def extract_resume_text(uploaded_file):

    if uploaded_file is None:
        return ""

    file_name = uploaded_file.name.lower()

    try:
        if file_name.endswith(".txt"):
            return uploaded_file.getvalue().decode(
                "utf-8", errors="ignore"
            )

        elif file_name.endswith(".pdf"):
            pdf = PdfReader(io.BytesIO(uploaded_file.getvalue()))

            text = ""
            for page in pdf.pages:
                text += (page.extract_text() or "") + "\n"

            return text

        elif file_name.endswith(".docx"):
            document = Document(
                io.BytesIO(uploaded_file.getvalue())
            )

            return "\n".join(
                paragraph.text for paragraph in document.paragraphs
            )

        else:
            return ""

    except Exception as error:
        st.error(f"Unable to read resume: {error}")
        return ""


# --------------------------------------------------
# DETECT SKILLS FROM RESUME
# --------------------------------------------------

def detect_resume_skills(resume_text):

    detected = []

    text = resume_text.lower()

    for skill in SKILLS:
        pattern = r"(?<!\w)" + re.escape(skill.lower()) + r"(?!\w)"

        if re.search(pattern, text):
            detected.append(skill)

    return detected


# --------------------------------------------------
# JOB RECOMMENDATION ENGINE
# --------------------------------------------------

def recommend_jobs(
    user_skills,
    user_interests,
    education,
    experience,
    location
):

    recommendations = []

    for job in JOBS:

        required_skills = job["skills"]

        matched_skills = [
            skill for skill in required_skills
            if skill.lower() in [s.lower() for s in user_skills]
        ]

        missing_skills = [
            skill for skill in required_skills
            if skill.lower() not in [s.lower() for s in user_skills]
        ]

        # Skill match: 70%
        skill_score = (
            len(matched_skills) / len(required_skills)
        ) * 70

        # Interest match: 15%
        if user_interests:
            interest_matches = [
                interest for interest in user_interests
                if interest in job["interests"]
            ]

            interest_score = (
                len(interest_matches) / len(user_interests)
            ) * 15
        else:
            interest_score = 0

        # Experience match: 10%
        if experience == "Fresher" and job["experience"] == "Fresher":
            experience_score = 10
        elif experience == "1-2 Years":
            experience_score = 7
        else:
            experience_score = 4

        # Education match: 5%
        education_score = (
            5 if education in job["education"] else 0
        )

        # Location filter
        location_match = (
            location == "Any location"
            or location in job["locations"]
            or "Remote" in job["locations"]
        )

        total_score = (
            skill_score
            + interest_score
            + experience_score
            + education_score
        )

        if location_match:
            recommendations.append({
                "Job Role": job["role"],
                "Category": job["category"],
                "Match Score": round(total_score, 1),
                "Level": job["level"],
                "Matched Skills": ", ".join(matched_skills) or "None yet",
                "Missing Skills": ", ".join(missing_skills) or "None",
                "Description": job["description"],
                "Required Skills": required_skills
            })

    recommendations.sort(
        key=lambda item: item["Match Score"],
        reverse=True
    )

    return recommendations


# --------------------------------------------------
# APPLICATION HEADER
# --------------------------------------------------

st.title("🚀 AI-Powered Career & Job Recommendation Platform")

st.write(
    "Discover suitable career paths and job roles "
    "based on your skills, education and interests."
)

st.divider()


# --------------------------------------------------
# SIDEBAR: USER PROFILE
# --------------------------------------------------

st.sidebar.header("👤 Create Your Profile")

name = st.sidebar.text_input(
    "Your Name",
    placeholder="Enter your name"
)

education = st.sidebar.selectbox(
    "Education",
    [
        "B.Tech",
        "B.Sc",
        "BCA",
        "M.Tech",
        "MCA",
        "M.Sc",
        "B.Com",
        "MBA"
    ]
)

experience = st.sidebar.selectbox(
    "Experience",
    [
        "Fresher",
        "1-2 Years",
        "3-5 Years",
        "5+ Years"
    ]
)

location = st.sidebar.selectbox(
    "Preferred Job Location",
    [
        "Any location",
        "Pune",
        "Mumbai",
        "Bangalore",
        "Remote"
    ]
)

st.sidebar.divider()

st.sidebar.subheader("💻 Select Your Skills")

selected_skills = st.sidebar.multiselect(
    "Choose your skills",
    SKILLS
)

manual_skills = st.sidebar.text_input(
    "Add other skills (comma separated)",
    placeholder="Example: Python, SQL"
)

st.sidebar.subheader("🎯 Career Interests")

interests = st.sidebar.multiselect(
    "Select your interests",
    [
        "Artificial Intelligence",
        "Machine Learning",
        "Data Science",
        "Data Analysis",
        "Business Analytics",
        "Software Development",
        "Backend Development",
        "Web Development",
        "Cloud Computing",
        "Data Engineering",
        "Research"
    ]
)


# --------------------------------------------------
# RESUME UPLOAD
# --------------------------------------------------

st.header("📄 Upload Your Resume")

uploaded_resume = st.file_uploader(
    "Upload PDF, DOCX or TXT resume",
    type=["pdf", "docx", "txt"]
)

resume_text = extract_resume_text(uploaded_resume)

resume_skills = detect_resume_skills(resume_text)

if uploaded_resume:
    st.success("Resume uploaded and text extracted successfully!")

    with st.expander("View extracted resume text"):
        st.text_area(
            "Resume Content",
            resume_text,
            height=180
        )

    if resume_skills:
        st.write("**Skills detected in your resume:**")
        st.write(", ".join(resume_skills))
    else:
        st.info(
            "No recognized skills were detected. "
            "You can select your skills manually in the sidebar."
        )


# --------------------------------------------------
# COMBINE USER SKILLS
# --------------------------------------------------

all_skills = list(selected_skills)

if manual_skills.strip():
    extra_skills = [
        skill.strip()
        for skill in manual_skills.split(",")
        if skill.strip()
    ]

    all_skills.extend(extra_skills)

all_skills.extend(resume_skills)

# Remove duplicate skills
all_skills = list({
    skill.lower(): skill for skill in all_skills
}.values())


# --------------------------------------------------
# GENERATE RECOMMENDATIONS
# --------------------------------------------------

st.divider()

st.header("🔍 Find Your Best Career Opportunities")

if st.button(
    "Generate Job Recommendations",
    type="primary",
    use_container_width=True
):

    if not name.strip():
        st.warning("Please enter your name in the sidebar.")

    elif not all_skills:
        st.warning(
            "Please select at least one skill or upload a resume "
            "containing recognized skills."
        )

    else:

        recommendations = recommend_jobs(
            all_skills,
            interests,
            education,
            experience,
            location
        )

        st.session_state["recommendations"] = recommendations
        st.session_state["user_name"] = name


# --------------------------------------------------
# DISPLAY RESULTS
# --------------------------------------------------

if "recommendations" in st.session_state:

    recommendations = st.session_state["recommendations"]

    st.subheader(
        f"Hello, {st.session_state['user_name']}! 👋"
    )

    if recommendations:

        best_job = recommendations[0]

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Recommended Roles",
            len(recommendations)
        )

        col2.metric(
            "Best Match",
            f"{best_job['Match Score']}%"
        )

        col3.metric(
            "Your Skills",
            len(all_skills)
        )

        st.divider()

        st.subheader("🏆 Your Job Recommendations")

        for index, job in enumerate(recommendations, start=1):

            with st.container(border=True):

                st.markdown(
                    f"### {index}. {job['Job Role']}"
                )

                st.write(
                    f"**Category:** {job['Category']}"
                )

                st.write(
                    f"**Experience Level:** {job['Level']}"
                )

                st.progress(
                    min(job["Match Score"] / 100, 1.0)
                )

                st.write(
                    f"**Profile Match: {job['Match Score']}%**"
                )

                st.write(job["Description"])

                st.write(
                    "**Matched Skills:** "
                    + job["Matched Skills"]
                )

                st.write(
                    "**Skills to Improve:** "
                    + job["Missing Skills"]
                )

                with st.expander("View required skills"):
                    st.write(", ".join(job["Required Skills"]))

        # ------------------------------------------
        # CAREER ROADMAP
        # ------------------------------------------

        st.divider()

        st.header("📚 Your Career Improvement Roadmap")

        top_job = recommendations[0]

        missing = [
            skill for skill in top_job["Required Skills"]
            if skill.lower() not in [s.lower() for s in all_skills]
        ]

        st.write(
            f"Based on your strongest match, "
            f"**{top_job['Job Role']}**, focus on these skills:"
        )

        if missing:

            for number, skill in enumerate(missing, start=1):
                st.write(f"{number}. Learn {skill}")

            st.info(
                "Practice these skills through small projects, "
                "online courses and practical exercises."
            )

        else:
            st.success(
                "You have all the listed skills for this sample role. "
                "Build projects and prepare for interviews."
            )

        # ------------------------------------------
        # DOWNLOAD RECOMMENDATIONS
        # ------------------------------------------

        st.divider()

        st.subheader("📥 Download Your Recommendations")

        download_df = pd.DataFrame([
            {
                "Job Role": job["Job Role"],
                "Category": job["Category"],
                "Match Score": job["Match Score"],
                "Level": job["Level"],
                "Matched Skills": job["Matched Skills"],
                "Missing Skills": job["Missing Skills"]
            }
            for job in recommendations
        ])

        csv_data = download_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="Download Job Recommendations CSV",
            data=csv_data,
            file_name="career_recommendations.csv",
            mime="text/csv",
            use_container_width=True
        )

    else:
        st.warning(
            "No roles matched your selected location. "
            "Try choosing Any location or Remote."
        )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "AI-Powered Career & Job Recommendation Platform | "
    "Developed using Python, Streamlit and skill-based matching."
)

st.caption(
    "Note: Recommendations are based on sample job-role templates. "
    "They are not verified live job vacancies or hiring guarantees."
)