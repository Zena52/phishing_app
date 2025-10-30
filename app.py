import streamlit as st
from utils import (
    clean_text,
    summarize,
    generate_flashcards,
    generate_quiz,
    answer_question,
    extract_text_from_pdf
)
import time

# -------------------
# PAGE CONFIG
# -------------------
st.set_page_config(
    page_title="AI Study Companion",
    layout="centered",
    initial_sidebar_state="expanded"
)

# -------------------
# CUSTOM CSS FOR THEME & BUTTON HOVER
# -------------------
st.markdown("""
    <style>
    body {
        background-color: #f5f5f5;
        color: #333333;
    }
    h1 {
        color: #ff69b4; /* Pink */
    }
    h2 {
        color: #1e90ff; /* Blue */
    }
    h3 {
        color: #808080; /* Grey */
    }
    .stButton>button {
        background-color: #ffb6c1; /* Light pink */
        color: black;
        border-radius: 8px;
        padding: 0.5em 1em;
        transition: 0.2s;
    }
    .stButton>button:hover {
        background-color: #ff69b4; /* Darker pink */
        color: white;
    }
    .stTextInput>div>input {
        border-radius: 8px;
        padding: 0.5em;
    }
    .stTextArea>div>textarea {
        border-radius: 8px;
        padding: 0.5em;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------
# WELCOME SECTION
# -------------------
st.markdown("## Welcome to AI Study Companion")
st.markdown(
    '<lottie-player src="https://assets3.lottiefiles.com/packages/lf20_touohxv0.json" '
    'background="transparent" speed="1" style="width: 100px; height: 100px;" loop autoplay></lottie-player>',
    unsafe_allow_html=True
)

# -------------------
# INPUT SECTION
# -------------------
st.subheader("Your Input")
input_option = st.radio("Choose input method:", ["Paste Text", "Upload File"])

text = ""
if input_option == "Paste Text":
    text = st.text_area("Paste your text here:", height=150)
elif input_option == "Upload File":
    uploaded_file = st.file_uploader("Upload a PDF or TXT file", type=["pdf", "txt"])
    if uploaded_file is not None:
        with st.spinner("Extracting text from file..."):
            if uploaded_file.name.endswith(".pdf"):
                text = extract_text_from_pdf(uploaded_file)
            elif uploaded_file.name.endswith(".txt"):
                text = str(uploaded_file.read(), "utf-8")
            time.sleep(0.5)  # slight delay for smoother spinner experience

if text:
    clean = clean_text(text)

    # -------------------
    # PROCESSING BUTTONS
    # -------------------
    st.subheader("Actions")
    col1, col2, col3, col4 = st.columns(4)

    # Summary
    if col1.button("Generate Summary"):
        with st.spinner("Generating summary..."):
            summary = summarize(clean)
            time.sleep(0.5)
            st.markdown("### Summary:")
            st.write(summary)
            st.download_button("Download Summary", summary, file_name="summary.txt")

    # Flashcards
    if col2.button("Generate Flashcards"):
        with st.spinner("Generating flashcards..."):
            flashcards = generate_flashcards(clean)
            time.sleep(0.5)
            st.markdown("### Flashcards:")
            for fc in flashcards:
                st.write(f"Q: {fc['question']}")
                st.write(f"A: {fc['answer']}\n")
            st.download_button("Download Flashcards", str(flashcards), file_name="flashcards.txt")

    # Quiz
    if col3.button("Generate Quiz"):
        with st.spinner("Generating quiz..."):
            quiz = generate_quiz(clean)
            time.sleep(0.5)
            st.markdown("### Quiz:")
            for q in quiz:
                st.write(f"Q: {q['question']}")
                st.write("Choices:")
                for choice in q['choices']:
                    st.write(f"- {choice}")
                st.write(f"Answer: {q['answer']}\n")
            st.download_button("Download Quiz", str(quiz), file_name="quiz.txt")

    # Ask a Question
    if col4.button("Ask a Question"):
        user_question = st.text_input("Enter your question:")
        if user_question:
            with st.spinner("Searching answer..."):
                answer = answer_question(clean, user_question)
                time.sleep(0.5)
                st.markdown("### Answer:")
                st.write(answer)
