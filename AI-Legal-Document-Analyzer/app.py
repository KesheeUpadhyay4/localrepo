
import streamlit as st
import re
from pypdf import PdfReader
from collections import Counter
from io import BytesIO
from datetime import datetime

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="AI Legal Document Analyzer",
    page_icon="⚖️",
    layout="wide"
)

# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>
.main {
    background-color: #f5f7fb;
}
.heading {
    color: #19345c;
    font-size: 36px;
    font-weight: bold;
}
.subheading {
    color: #64748b;
    font-size: 16px;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# LEGAL CLAUSE CATEGORIES
# --------------------------------------------------

CLAUSE_CATEGORIES = {
    "Payment": [
        "payment", "invoice", "fee", "salary",
        "compensation", "refund", "interest",
        "late payment"
    ],
    "Termination": [
        "termination", "terminate", "cancel",
        "cancellation", "end this agreement",
        "expiry", "expiration"
    ],
    "Confidentiality": [
        "confidential", "non-disclosure",
        "proprietary information", "trade secret"
    ],
    "Liability": [
        "liability", "liable", "damages",
        "indemnify", "indemnification",
        "responsibility"
    ],
    "Dispute Resolution": [
        "dispute", "arbitration", "jurisdiction",
        "mediation", "court", "litigation"
    ],
    "Intellectual Property": [
        "intellectual property", "copyright",
        "patent", "trademark", "ownership",
        "license", "licence"
    ],
    "Obligations": [
        "shall", "must", "responsible for",
        "obligation", "undertake", "required to"
    ],
    "Data Protection": [
        "personal data", "data protection",
        "privacy", "data processing",
        "consent", "data breach"
    ]
}

# --------------------------------------------------
# POTENTIAL RISK PHRASES
# --------------------------------------------------

RISK_PHRASES = {
    "Unlimited liability": [
        "unlimited liability",
        "without limitation of liability"
    ],
    "Automatic renewal": [
        "automatically renew",
        "automatic renewal",
        "shall automatically renew"
    ],
    "Non-refundable payment": [
        "non-refundable",
        "nonrefundable"
    ],
    "Unilateral termination": [
        "terminate at any time",
        "terminate without notice",
        "without prior notice"
    ],
    "Broad indemnity": [
        "indemnify and hold harmless",
        "indemnify against all claims"
    ],
    "Penalty clause": [
        "penalty",
        "liquidated damages",
        "penalty charges"
    ],
    "Confidentiality restriction": [
        "perpetual confidentiality",
        "indefinitely confidential"
    ]
}

# --------------------------------------------------
# DOCUMENT EXTRACTION
# --------------------------------------------------

def extract_pdf_text(uploaded_file):
    try:
        pdf = PdfReader(BytesIO(uploaded_file.getvalue()))

        if pdf.is_encrypted:
            return None, "This PDF is password-protected."

        pages_text = []

        for page_number, page in enumerate(pdf.pages, start=1):
            page_text = page.extract_text() or ""
            if page_text.strip():
                pages_text.append(page_text)

        text = "\n".join(pages_text)

        if not text.strip():
            return None, (
                "No selectable text found. This may be a scanned PDF. "
                "OCR support is not included in this version."
            )

        return text, None

    except Exception as error:
        return None, f"Could not read PDF: {error}"


def extract_document_text(uploaded_file):
    filename = uploaded_file.name.lower()

    if filename.endswith(".pdf"):
        return extract_pdf_text(uploaded_file)

    if filename.endswith(".txt"):
        try:
            text = uploaded_file.getvalue().decode(
                "utf-8-sig",
                errors="replace"
            )
            return text, None
        except Exception as error:
            return None, f"Could not read text file: {error}"

    return None, "Unsupported file format."


# --------------------------------------------------
# TEXT PROCESSING
# --------------------------------------------------

def clean_text(text):
    text = re.sub(r'\r\n?', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def split_sentences(text):
    sentences = re.split(
        r'(?<=[.!?])\s+|\n+',
        text
    )

    return [
        sentence.strip()
        for sentence in sentences
        if len(sentence.strip()) > 20
    ]


# --------------------------------------------------
# SUMMARY GENERATION
# --------------------------------------------------

def generate_summary(text, maximum=6):
    sentences = split_sentences(text)

    if not sentences:
        return ["Not enough readable text for a summary."]

    stop_words = {
        "this", "that", "with", "from", "have",
        "will", "shall", "been", "being", "their",
        "there", "they", "them", "which", "where",
        "when", "what", "such", "into", "under",
        "upon", "hereby", "herein", "thereof",
        "between", "after", "before", "party"
    }

    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())

    filtered_words = [
        word for word in words
        if word not in stop_words
    ]

    frequencies = Counter(filtered_words)

    scored_sentences = []

    for index, sentence in enumerate(sentences):
        sentence_words = re.findall(
            r'\b[a-zA-Z]{3,}\b',
            sentence.lower()
        )

        score = sum(
            frequencies[word]
            for word in sentence_words
        )

        score = score / max(len(sentence_words), 1)

        scored_sentences.append(
            (score, index, sentence)
        )

    top_sentences = sorted(
        scored_sentences,
        key=lambda item: item[0],
        reverse=True
    )[:maximum]

    top_sentences.sort(key=lambda item: item[1])

    return [
        item[2] for item in top_sentences
    ]


# --------------------------------------------------
# CLAUSE DETECTION
# --------------------------------------------------

def detect_clauses(text):
    sentences = split_sentences(text)

    results = {}

    for category, keywords in CLAUSE_CATEGORIES.items():

        matches = []

        for sentence in sentences:
            lower_sentence = sentence.lower()

            found_keywords = [
                keyword for keyword in keywords
                if keyword in lower_sentence
            ]

            if found_keywords:
                matches.append({
                    "sentence": sentence,
                    "keywords": found_keywords
                })

        results[category] = matches

    return results


# --------------------------------------------------
# POTENTIAL RISK DETECTION
# --------------------------------------------------

def detect_risks(text):
    lower_text = text.lower()
    risks = []

    for risk_name, phrases in RISK_PHRASES.items():

        found = [
            phrase for phrase in phrases
            if phrase in lower_text
        ]

        if found:
            risks.append({
                "name": risk_name,
                "phrases": found,
                "severity": "Review required"
            })

    return risks


# --------------------------------------------------
# KEYWORD EXTRACTION
# --------------------------------------------------

def extract_keywords(text):
    stop_words = {
        "the", "and", "for", "are", "was", "were",
        "this", "that", "with", "from", "have",
        "has", "had", "will", "would", "should",
        "could", "their", "there", "they", "them",
        "you", "your", "our", "about", "into",
        "which", "shall", "such", "hereby",
        "herein", "thereof", "between", "under",
        "after", "before", "party", "agreement"
    }

    words = re.findall(
        r'\b[a-zA-Z]{4,}\b',
        text.lower()
    )

    words = [
        word for word in words
        if word not in stop_words
    ]

    return Counter(words).most_common(12)


# --------------------------------------------------
# DATE DETECTION
# --------------------------------------------------

def extract_dates(text):
    patterns = [
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        r'\b\d{4}-\d{2}-\d{2}\b',
        r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b'
    ]

    dates = []

    for pattern in patterns:
        dates.extend(
            re.findall(pattern, text, flags=re.IGNORECASE)
        )

    return list(dict.fromkeys(dates))


# --------------------------------------------------
# REPORT GENERATION
# --------------------------------------------------

def create_report(filename, analysis):

    report = f"""
AI LEGAL DOCUMENT ANALYZER
========================================

File Name: {filename}
Analysis Date: {datetime.now().strftime("%d-%m-%Y %H:%M")}

DOCUMENT STATISTICS
----------------------------------------
Word Count: {analysis['word_count']}
Sentence Count: {analysis['sentence_count']}

DOCUMENT SUMMARY
----------------------------------------
"""

    for item in analysis["summary"]:
        report += f"\n- {item}\n"

    report += "\nPOTENTIAL RISK PHRASES\n"
    report += "----------------------------------------\n"

    if analysis["risks"]:
        for risk in analysis["risks"]:
            report += (
                f"\n{risk['name']}: "
                f"{', '.join(risk['phrases'])}\n"
            )
    else:
        report += "\nNo configured risk phrases detected.\n"

    report += "\nCLAUSE ANALYSIS\n"
    report += "----------------------------------------\n"

    for category, matches in analysis["clauses"].items():
        report += f"\n{category}: {len(matches)} matches\n"

        for match in matches:
            report += f"- {match['sentence']}\n"

    report += "\nKEYWORDS\n"
    report += "----------------------------------------\n"

    for keyword, count in analysis["keywords"]:
        report += f"{keyword}: {count}\n"

    report += "\nDATES FOUND\n"
    report += "----------------------------------------\n"

    for date in analysis["dates"]:
        report += f"- {date}\n"

    report += """

IMPORTANT DISCLAIMER
----------------------------------------
This is an educational, rule-based document
analysis tool. It does not provide legal advice,
determine legal validity, or replace a lawyer.
All findings require human verification.
"""

    return report


# --------------------------------------------------
# APPLICATION HEADER
# --------------------------------------------------

st.markdown(
    '<div class="heading">⚖️ AI Legal Document Analyzer</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subheading">Upload legal documents and '
    'identify important clauses and potential review points.</div>',
    unsafe_allow_html=True
)

st.divider()

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("⚙️ Settings")

st.sidebar.write("Supported formats:")
st.sidebar.write("- PDF")
st.sidebar.write("- TXT")

st.sidebar.info(
    "Your document is processed within this application. "
    "This prototype does not send it to an external AI service."
)

st.sidebar.warning(
    "Do not upload confidential or sensitive legal documents "
    "to an untrusted or publicly accessible deployment."
)

# --------------------------------------------------
# DOCUMENT UPLOAD
# --------------------------------------------------

st.header("📁 Upload Legal Document")

uploaded_file = st.file_uploader(
    "Choose a legal document",
    type=["pdf", "txt"]
)

if uploaded_file:

    st.success(f"Uploaded: {uploaded_file.name}")

    if st.button(
        "🔍 Analyze Legal Document",
        use_container_width=True
    ):

        with st.spinner("Analyzing document..."):

            document_text, error = extract_document_text(
                uploaded_file
            )

            if error:
                st.error(error)
                st.session_state.pop("analysis", None)

            elif not document_text.strip():
                st.error("The document is empty.")
                st.session_state.pop("analysis", None)

            else:
                document_text = clean_text(document_text)

                words = re.findall(
                    r'\b[a-zA-Z]+\b',
                    document_text
                )

                analysis = {
                    "word_count": len(words),
                    "sentence_count": len(
                        split_sentences(document_text)
                    ),
                    "summary": generate_summary(document_text),
                    "clauses": detect_clauses(document_text),
                    "risks": detect_risks(document_text),
                    "keywords": extract_keywords(document_text),
                    "dates": extract_dates(document_text),
                    "filename": uploaded_file.name
                }

                st.session_state["analysis"] = analysis

                st.success("Document analysis completed!")


# --------------------------------------------------
# DISPLAY ANALYSIS
# --------------------------------------------------

if "analysis" in st.session_state:

    analysis = st.session_state["analysis"]

    st.divider()

    st.header("📊 Document Dashboard")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Words",
        analysis["word_count"]
    )

    col2.metric(
        "Total Sentences",
        analysis["sentence_count"]
    )

    col3.metric(
        "Potential Risk Categories",
        len(analysis["risks"])
    )

    # SUMMARY

    st.divider()
    st.subheader("📌 Document Summary")

    for sentence in analysis["summary"]:
        st.write("•", sentence)

    # CLAUSE DETECTION

    st.divider()
    st.subheader("📑 Detected Legal Clauses")

    for category, matches in analysis["clauses"].items():

        with st.expander(
            f"{category} ({len(matches)} matches)"
        ):

            if matches:
                for match in matches:
                    st.write("•", match["sentence"])
                    st.caption(
                        "Matched terms: "
                        + ", ".join(match["keywords"])
                    )
            else:
                st.write("No matching text detected.")

    # RISK DETECTION

    st.divider()
    st.subheader("⚠️ Potential Risk Phrases")

    if analysis["risks"]:

        st.warning(
            "The following phrases may deserve additional "
            "legal review. Their presence does not prove "
            "that the document is legally risky."
        )

        for risk in analysis["risks"]:

            st.markdown(
                f"**{risk['name']}**"
            )

            st.write(
                "Detected wording: "
                + ", ".join(risk["phrases"])
            )

            st.caption("Status: Review required")

    else:
        st.success(
            "No phrases from the configured risk list were detected."
        )

    # KEYWORDS

    st.divider()
    st.subheader("🔑 Important Keywords")

    if analysis["keywords"]:

        keyword_data = {
            "Keyword": [
                item[0] for item in analysis["keywords"]
            ],
            "Frequency": [
                item[1] for item in analysis["keywords"]
            ]
        }

        st.dataframe(
            keyword_data,
            use_container_width=True
        )

    # DATES

    st.divider()
    st.subheader("📅 Dates Found")

    if analysis["dates"]:
        for date in analysis["dates"]:
            st.write("•", date)
    else:
        st.info("No supported date patterns detected.")

    # DOWNLOAD REPORT

    st.divider()
    st.header("📥 Download Analysis Report")

    report = create_report(
        analysis["filename"],
        analysis
    )

    st.download_button(
        label="Download Legal Analysis Report",
        data=report,
        file_name="legal_analysis_report.txt",
        mime="text/plain",
        use_container_width=True
    )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "AI Legal Document Analyzer | Python + Streamlit + PyPDF | "
    "Educational prototype — not legal advice."
)
