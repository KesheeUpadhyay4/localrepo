import streamlit as st
import re
from datetime import datetime
from collections import Counter

# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="AI Meeting Assistant",
    page_icon="📋",
    layout="wide"
)

# ---------------- CUSTOM DESIGN ----------------

st.markdown("""
<style>
.main {
    background-color: #f5f7fb;
}
.title {
    font-size: 38px;
    font-weight: bold;
    color: #243b64;
}
.subtitle {
    color: #64748b;
    font-size: 17px;
}
.stButton button {
    background-color: #2457a7;
    color: white;
    border-radius: 8px;
    height: 45px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HELPER FUNCTIONS ----------------

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def split_sentences(text):
    return [
        sentence.strip()
        for sentence in re.split(r'(?<=[.!?])\s+', text)
        if len(sentence.strip()) > 15
    ]


def generate_summary(text):
    sentences = split_sentences(text)

    if not sentences:
        return "Not enough text to generate a summary."

    important_words = [
        "important", "discussed", "decided", "plan",
        "project", "deadline", "budget", "problem",
        "complete", "meeting", "result", "target",
        "launch", "development", "team"
    ]

    scored = []

    for index, sentence in enumerate(sentences):
        score = 0
        lower = sentence.lower()

        for word in important_words:
            if word in lower:
                score += 2

        if index == 0:
            score += 1

        scored.append((score, index, sentence))

    selected = sorted(
        sorted(scored, key=lambda x: x[0], reverse=True)[:5],
        key=lambda x: x[1]
    )

    return "\n\n".join(item[2] for item in selected)


def extract_action_items(text):
    sentences = split_sentences(text)

    action_words = [
        "will", "must", "need to", "needs to",
        "should", "assigned", "responsible",
        "complete", "prepare", "send",
        "submit", "create", "develop",
        "review", "finish", "follow up",
        "deadline", "action item"
    ]

    tasks = []

    for sentence in sentences:
        lower = sentence.lower()

        if any(word in lower for word in action_words):
            tasks.append(sentence)

    return list(dict.fromkeys(tasks))


def extract_decisions(text):
    sentences = split_sentences(text)

    decision_words = [
        "decided", "decision", "approved",
        "agreed", "selected", "finalized",
        "confirmed", "will proceed",
        "concluded"
    ]

    decisions = []

    for sentence in sentences:
        lower = sentence.lower()

        if any(word in lower for word in decision_words):
            decisions.append(sentence)

    return list(dict.fromkeys(decisions))


def extract_dates(text):
    patterns = [
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        r'\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b',
        r'\b(?:today|tomorrow|next week|next month)\b'
    ]

    found = []

    for pattern in patterns:
        found.extend(
            re.findall(pattern, text, flags=re.IGNORECASE)
        )

    return list(dict.fromkeys(found))


def generate_keywords(text):
    stop_words = {
        "the", "and", "for", "are", "was", "were",
        "this", "that", "with", "from", "have",
        "has", "had", "will", "would", "should",
        "could", "their", "there", "they", "them",
        "you", "your", "our", "about", "into",
        "meeting", "during", "then", "than",
        "also", "been", "being", "what", "when",
        "where", "which", "while", "who", "how",
        "can", "not", "but", "all", "any", "its"
    }

    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())

    filtered = [
        word for word in words
        if word not in stop_words
    ]

    return Counter(filtered).most_common(10)


# ---------------- APPLICATION HEADER ----------------

st.markdown(
    '<div class="title">📋 AI Meeting Assistant</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Convert meeting transcripts into '
    'organized summaries, decisions and action items.</div>',
    unsafe_allow_html=True
)

st.divider()

# ---------------- SIDEBAR ----------------

st.sidebar.title("⚙️ Meeting Settings")

meeting_title = st.sidebar.text_input(
    "Meeting Title",
    "Project Discussion Meeting"
)

attendees = st.sidebar.text_input(
    "Attendees",
    "Team Members"
)

meeting_date = st.sidebar.date_input(
    "Meeting Date",
    datetime.today()
)

st.sidebar.info(
    "Upload a .txt transcript or paste meeting text "
    "to generate your report."
)

# ---------------- TRANSCRIPT INPUT ----------------

st.subheader("📝 Meeting Transcript")

uploaded_file = st.file_uploader(
    "Upload a meeting transcript (.txt)",
    type=["txt"]
)

uploaded_text = ""

if uploaded_file is not None:
    uploaded_text = uploaded_file.read().decode(
        "utf-8-sig",
        errors="replace"
    )

transcript = st.text_area(
    "Paste your meeting conversation here:",
    value=uploaded_text,
    height=250,
    placeholder=(
        "Example: Today we discussed the project. "
        "Rahul will prepare the report by Friday. "
        "The team decided to launch the website next week."
    )
)

# ---------------- GENERATE REPORT ----------------

if st.button("🚀 Generate Meeting Report", use_container_width=True):

    transcript = clean_text(transcript)

    if not transcript:
        st.warning("Please upload or paste a meeting transcript.")

    else:
        with st.spinner("Analyzing your meeting transcript..."):

            summary = generate_summary(transcript)
            actions = extract_action_items(transcript)
            decisions = extract_decisions(transcript)
            dates = extract_dates(transcript)
            keywords = generate_keywords(transcript)

        st.session_state["report"] = {
            "title": meeting_title,
            "attendees": attendees,
            "date": str(meeting_date),
            "transcript": transcript,
            "summary": summary,
            "actions": actions,
            "decisions": decisions,
            "dates": dates,
            "keywords": keywords
        }

        st.success("Meeting report generated successfully!")

# ---------------- DISPLAY REPORT ----------------

if "report" in st.session_state:

    report = st.session_state["report"]

    st.divider()
    st.header("📊 Meeting Dashboard")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Sentences",
        len(split_sentences(report["transcript"]))
    )

    col2.metric(
        "Action Items",
        len(report["actions"])
    )

    col3.metric(
        "Decisions",
        len(report["decisions"])
    )

    st.divider()

    # SUMMARY

    st.subheader("📌 Meeting Summary")
    st.write(report["summary"])

    # ACTION ITEMS

    st.subheader("✅ Action Items")

    if report["actions"]:
        for i, task in enumerate(report["actions"], 1):
            st.write(f"{i}. {task}")
    else:
        st.info("No clear action items were detected.")

    # DECISIONS

    st.subheader("🎯 Important Decisions")

    if report["decisions"]:
        for i, decision in enumerate(report["decisions"], 1):
            st.write(f"{i}. {decision}")
    else:
        st.info("No clear decisions were detected.")

    # DATES

    st.subheader("📅 Dates and Deadlines")

    if report["dates"]:
        for date in report["dates"]:
            st.write(f"• {date}")
    else:
        st.info("No dates were detected.")

    # KEYWORDS

    st.subheader("🔑 Important Keywords")

    if report["keywords"]:
        keyword_text = ", ".join(
            word for word, count in report["keywords"]
        )
        st.write(keyword_text)

    # DOWNLOAD REPORT

    st.divider()
    st.subheader("📥 Download Meeting Report")

    report_text = f"""
AI MEETING ASSISTANT REPORT
================================

Meeting Title: {report['title']}
Meeting Date: {report['date']}
Attendees: {report['attendees']}

MEETING SUMMARY
---------------
{report['summary']}

ACTION ITEMS
------------
{chr(10).join('- ' + x for x in report['actions']) or 'None detected'}

IMPORTANT DECISIONS
-------------------
{chr(10).join('- ' + x for x in report['decisions']) or 'None detected'}

DATES AND DEADLINES
-------------------
{chr(10).join('- ' + x for x in report['dates']) or 'None detected'}

IMPORTANT KEYWORDS
------------------
{', '.join(x[0] for x in report['keywords'])}

ORIGINAL TRANSCRIPT
-------------------
{report['transcript']}
"""

    st.download_button(
        label="⬇️ Download Meeting Report",
        data=report_text,
        file_name="meeting_report.txt",
        mime="text/plain",
        use_container_width=True
    )

# ---------------- FOOTER ----------------

st.divider()

st.caption(
    "AI Meeting Assistant | Python + Streamlit | "
    "Educational meeting-analysis prototype"
)
