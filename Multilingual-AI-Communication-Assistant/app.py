
import re
import time
import streamlit as st
from deep_translator import GoogleTranslator

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Multilingual AI Communication Assistant",
    page_icon="🌐",
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
.title {
    text-align: center;
    color: #243b64;
    font-size: 34px;
    font-weight: bold;
}
.subtitle {
    text-align: center;
    color: #64748b;
    font-size: 16px;
}
.stButton > button {
    width: 100%;
    border-radius: 10px;
    height: 45px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "history" not in st.session_state:
    st.session_state.history = []

if "translated_text" not in st.session_state:
    st.session_state.translated_text = ""

if "improved_text" not in st.session_state:
    st.session_state.improved_text = ""

if "generated_reply" not in st.session_state:
    st.session_state.generated_reply = ""

# --------------------------------------------------
# LANGUAGE LIST
# --------------------------------------------------

LANGUAGES = {
    "English": "en",
    "Hindi": "hi",
    "Marathi": "mr",
    "French": "fr",
    "German": "de",
    "Spanish": "es",
    "Italian": "it",
    "Japanese": "ja",
    "Chinese (Simplified)": "zh-CN",
    "Arabic": "ar",
    "Portuguese": "pt",
    "Russian": "ru",
    "Bengali": "bn",
    "Gujarati": "gu",
    "Tamil": "ta",
    "Telugu": "te",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Punjabi": "pa",
    "Urdu": "ur"
}

# --------------------------------------------------
# TRANSLATION FUNCTION
# --------------------------------------------------

def translate_text(text, source, target):

    if not text or not text.strip():
        raise ValueError("Please enter some text.")

    if source == target:
        return text

    translator = GoogleTranslator(
        source=source,
        target=target
    )

    # Divide long text into smaller chunks
    chunks = [
        text[i:i + 3000]
        for i in range(0, len(text), 3000)
    ]

    translated_chunks = []

    for chunk in chunks:

        last_error = None

        for attempt in range(3):

            try:
                result = translator.translate(chunk)

                if not result:
                    raise Exception("Empty translation received.")

                translated_chunks.append(result)
                break

            except Exception as error:

                last_error = error

                if attempt < 2:
                    time.sleep(3 * (attempt + 1))

        else:
            raise Exception(
                "Translation service is temporarily unavailable. "
                "Please wait a few minutes and try again. "
                f"Details: {last_error}"
            )

        # Reduce request frequency
        time.sleep(1.5)

    return "\n".join(translated_chunks)


# --------------------------------------------------
# TEXT IMPROVEMENT FUNCTION
# --------------------------------------------------

def improve_text(text):

    if not text or not text.strip():
        return ""

    text = re.sub(r"\s+", " ", text).strip()

    replacements = {
        r"\bu\b": "you",
        r"\bur\b": "your",
        r"\br\b": "are",
        r"\bpls\b": "please",
        r"\bplz\b": "please",
        r"\bthx\b": "thanks",
        r"\bthanks alot\b": "thanks a lot",
        r"\bi\b": "I",
        r"\bcant\b": "cannot",
        r"\bdont\b": "do not",
        r"\bwont\b": "will not",
        r"\bdoesnt\b": "does not",
        r"\bdidnt\b": "did not"
    }

    for pattern, replacement in replacements.items():
        text = re.sub(
            pattern,
            replacement,
            text,
            flags=re.IGNORECASE
        )

    text = text[0].upper() + text[1:]

    if text[-1] not in ".!?":
        text += "."

    return text


# --------------------------------------------------
# REPLY GENERATOR
# --------------------------------------------------

def generate_reply(category, tone, name):

    name = name.strip()

    greeting = f"Dear {name}," if name else "Hello,"

    replies = {

        "Greeting": {
            "Professional":
                f"{greeting}\n\nI hope you are doing well. "
                "Wishing you a wonderful day.",

            "Friendly":
                f"Hi {name or 'there'}!\n\n"
                "Hope you are doing great. Have a fantastic day!",

            "Formal":
                f"{greeting}\n\n"
                "I hope this message finds you well."
        },

        "Meeting Request": {
            "Professional":
                f"{greeting}\n\n"
                "I would like to schedule a meeting to discuss "
                "the relevant topics. Please let me know your availability.",

            "Friendly":
                f"Hi {name or 'there'}!\n\n"
                "Can we schedule a meeting sometime? "
                "Please let me know when you are free.",

            "Formal":
                f"{greeting}\n\n"
                "I would appreciate the opportunity to arrange "
                "a meeting at your convenience."
        },

        "Thank You": {
            "Professional":
                f"{greeting}\n\n"
                "Thank you for your valuable time, support, "
                "and assistance. I sincerely appreciate it.",

            "Friendly":
                f"Hi {name or 'there'}!\n\n"
                "Thank you so much for your help. "
                "I really appreciate it!",

            "Formal":
                f"{greeting}\n\n"
                "I would like to express my sincere gratitude "
                "for your assistance."
        },

        "Apology": {
            "Professional":
                f"{greeting}\n\n"
                "I sincerely apologize for the inconvenience. "
                "I appreciate your understanding.",

            "Friendly":
                f"Hi {name or 'there'}!\n\n"
                "I'm really sorry about that. "
                "I hope you understand.",

            "Formal":
                f"{greeting}\n\n"
                "Please accept my sincere apologies "
                "for the inconvenience caused."
        },

        "Job Application": {
            "Professional":
                f"{greeting}\n\n"
                "I am writing to express my interest in the "
                "available opportunity. I would welcome the "
                "chance to discuss how my skills and experience "
                "could contribute to your organization.\n\n"
                "Thank you for your consideration.",

            "Friendly":
                f"Hi {name or 'there'}!\n\n"
                "I am interested in the job opportunity and "
                "would love to learn more about the role. "
                "Thank you for your time.",

            "Formal":
                f"{greeting}\n\n"
                "I wish to formally express my interest in the "
                "position. I would be grateful for the opportunity "
                "to discuss my qualifications.\n\n"
                "Thank you for your consideration."
        },

        "Follow-up": {
            "Professional":
                f"{greeting}\n\n"
                "I am following up on my previous message. "
                "I would appreciate an update when convenient.",

            "Friendly":
                f"Hi {name or 'there'}!\n\n"
                "Just checking in to see if there are any updates. "
                "Looking forward to hearing from you!",

            "Formal":
                f"{greeting}\n\n"
                "I am writing to kindly follow up on my previous "
                "communication. I look forward to your response."
        }
    }

    return replies[category][tone]


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown(
    '<div class="title">🌐 Multilingual AI Communication Assistant</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Translate, improve and generate messages in multiple languages.</div>',
    unsafe_allow_html=True
)

st.divider()

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("📌 Navigation")

page = st.sidebar.radio(
    "Select Feature",
    [
        "Home",
        "Language Translator",
        "Text Improver",
        "Reply Generator",
        "Translation History"
    ]
)

st.sidebar.divider()

st.sidebar.info(
    "This is an educational communication assistant. "
    "Translation uses an online third-party service."
)

# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

if page == "Home":

    st.header("Welcome!")

    st.write(
        "This application helps users communicate across "
        "different languages and prepare better messages."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.success("🌍 Multiple Language Translation")
        st.success("✍️ Text Improvement")

    with col2:
        st.success("💬 Smart Reply Templates")
        st.success("📥 Download Your Results")

    st.subheader("How to use")

    st.write("""
    1. Select a feature from the sidebar.
    2. Enter your text or message.
    3. Select the required language or tone.
    4. Click the relevant action button.
    5. View or download your result.
    """)

# --------------------------------------------------
# TRANSLATOR PAGE
# --------------------------------------------------

elif page == "Language Translator":

    st.header("🌍 Language Translator")

    col1, col2 = st.columns(2)

    with col1:
        source_language = st.selectbox(
            "Translate From",
            list(LANGUAGES.keys()),
            index=0
        )

    with col2:
        target_language = st.selectbox(
            "Translate To",
            list(LANGUAGES.keys()),
            index=2
        )

    input_text = st.text_area(
        "Enter your text",
        height=180,
        placeholder="Type your message here..."
    )

    if st.button("Translate Now", type="primary"):

        if not input_text.strip():
            st.warning("Please enter some text first.")

        else:
            with st.spinner("Translating your text..."):

                try:

                    translated = translate_text(
                        input_text,
                        LANGUAGES[source_language],
                        LANGUAGES[target_language]
                    )

                    st.session_state.translated_text = translated

                    st.session_state.history.append({
                        "source": source_language,
                        "target": target_language,
                        "original": input_text,
                        "translated": translated
                    })

                    st.success("Translation completed!")

                except Exception as error:
                    st.error(f"Translation failed: {error}")

    if st.session_state.translated_text:

        st.subheader("Translated Result")

        st.text_area(
            "Translation",
            value=st.session_state.translated_text,
            height=180
        )

        st.download_button(
            "📥 Download Translation",
            data=st.session_state.translated_text,
            file_name="translated_text.txt",
            mime="text/plain"
        )

# --------------------------------------------------
# TEXT IMPROVER PAGE
# --------------------------------------------------

elif page == "Text Improver":

    st.header("✍️ Text Improver")

    original_text = st.text_area(
        "Enter text to improve",
        height=180,
        placeholder="Enter your message..."
    )

    if st.button("Improve Text", type="primary"):

        if not original_text.strip():
            st.warning("Please enter some text.")

        else:

            improved = improve_text(original_text)

            st.session_state.improved_text = improved

    if st.session_state.improved_text:

        st.subheader("Improved Text")

        st.text_area(
            "Result",
            value=st.session_state.improved_text,
            height=180
        )

        st.download_button(
            "📥 Download Improved Text",
            data=st.session_state.improved_text,
            file_name="improved_text.txt",
            mime="text/plain"
        )

# --------------------------------------------------
# REPLY GENERATOR PAGE
# --------------------------------------------------

elif page == "Reply Generator":

    st.header("💬 Professional Reply Generator")

    name = st.text_input(
        "Recipient Name (Optional)",
        placeholder="Enter recipient name"
    )

    category = st.selectbox(
        "Select Message Type",
        [
            "Greeting",
            "Meeting Request",
            "Thank You",
            "Apology",
            "Job Application",
            "Follow-up"
        ]
    )

    tone = st.selectbox(
        "Select Tone",
        ["Professional", "Friendly", "Formal"]
    )

    if st.button("Generate Reply", type="primary"):

        st.session_state.generated_reply = generate_reply(
            category,
            tone,
            name
        )

    if st.session_state.generated_reply:

        st.subheader("Generated Message")

        st.text_area(
            "Your Reply",
            value=st.session_state.generated_reply,
            height=220
        )

        st.download_button(
            "📥 Download Reply",
            data=st.session_state.generated_reply,
            file_name="generated_reply.txt",
            mime="text/plain"
        )

# --------------------------------------------------
# TRANSLATION HISTORY PAGE
# --------------------------------------------------

elif page == "Translation History":

    st.header("🕘 Translation History")

    if st.session_state.history:

        for index, item in enumerate(
            reversed(st.session_state.history),
            start=1
        ):

            with st.expander(f"Translation {index}"):

                st.write(
                    f"**From:** {item['source']}"
                )

                st.write(
                    f"**To:** {item['target']}"
                )

                st.write("**Original Text:**")
                st.write(item["original"])

                st.write("**Translated Text:**")
                st.write(item["translated"])

        if st.button("Clear History"):

            st.session_state.history = []
            st.success("History cleared.")
            st.rerun()

    else:
        st.info("No translation history available yet.")

# --------------------------------------------------
# TEXT TO SPEECH
# --------------------------------------------------

st.sidebar.divider()
st.sidebar.subheader("🔊 Text to Speech")

speech_text = st.sidebar.text_area(
    "Enter text to speak",
    key="speech_input"
)

if st.sidebar.button("Speak Text"):

    if speech_text.strip():

        safe_text = speech_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("'", "&#39;").replace('"', "&quot;")

        st.components.v1.html(
            f"""
            <script>
            const text = "{safe_text}";
            const speech = new SpeechSynthesisUtterance(text);
            window.speechSynthesis.cancel();
            window.speechSynthesis.speak(speech);
            </script>
            """,
            height=50
        )

    else:
        st.sidebar.warning("Enter text before speaking.")

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.markdown(
    "<center>Multilingual AI Communication Assistant | Python + Streamlit</center>",
    unsafe_allow_html=True
)
