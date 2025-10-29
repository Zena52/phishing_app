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

# -------------------------------
# Page config
# -------------------------------
st.set_page_config(
    page_title="AI Study Companion",
    layout="centered",
    initial_sidebar_state="expanded"
)

# -------------------------------
# Welcome UI
# -------------------------------
st.markdown("## Welcome to AI Study Companion")
st.markdown(
    '<lottie-player src="https://assets3.lottiefiles.com/packages/lf20_touohxv0.json" '
    'background="transparent" speed="1" style="width: 100px; height: 100px;" loop autoplay></lottie-player>',
    unsafe_allow_html=True
)

# -------------------------------
# Input selection
# -------------------------------
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
            time.sleep(0.5)

if text:
    clean = clean_text(text)

    # -------------------------------
    # Persistent question input
    # -------------------------------
    user_question = st.text_input("Ask a question about the text:")

    # -------------------------------
    # Action buttons
    # -------------------------------
    col1, col2, col3, col4 = st.columns(4)

    # Summary
    with col1:
        if st.button("Generate Summary"):
            with st.spinner("Generating summary..."):
                summary = summarize(clean)
                st.markdown("### Summary:")
                st.write(summary)
                st.download_button("Download Summary", summary, file_name="summary.txt")

    # Flashcards
    with col2:
        if st.button("Generate Flashcards"):
            with st.spinner("Generating flashcards..."):
                flashcards = generate_flashcards(clean)
                st.markdown("### Flashcards:")
                for fc in flashcards:
                    st.write(f"Q: {fc['question']}")
                    st.write(f"A: {fc['answer']}\n")
                st.download_button("Download Flashcards", str(flashcards), file_name="flashcards.txt")

    # Quiz
    with col3:
        if st.button("Generate Quiz"):
            with st.spinner("Generating quiz..."):
                quiz = generate_quiz(clean)
                st.markdown("### Quiz:")
                for q in quiz:
                    st.write(f"Q: {q['question']}")
                    st.write("Choices:")
                    for choice in q['choices']:
                        st.write(f"- {choice}")
                    st.write(f"Answer: {q['answer']}\n")
                st.download_button("Download Quiz", str(quiz), file_name="quiz.txt")

    # Question answering
    with col4:
        if st.button("Submit Question"):
            if user_question.strip():
                with st.spinner("Searching answer..."):
                    answer = answer_question(clean, user_question)
                    st.markdown("### Answer:")
                    st.write(answer)
            else:
                st.warning("Please type a question before submitting.")
