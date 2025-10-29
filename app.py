import streamlit as st
from PyPDF2 import PdfReader

from utils import (
    summarize,
    generate_quiz,
    generate_flashcards,
    get_word_count,
    get_read_time,
    answer_question
)



st.set_page_config(page_title="AI Study Companion", layout="centered")

st.title("AI Study Companion 📘")
st.write("Upload your notes (TXT or PDF), get summaries, flashcards, quizzes, and ask questions — all offline and free.")

# Sidebar for uploads
with st.sidebar:
    st.header("Upload your notes")
    uploaded_file = st.file_uploader("Choose a .txt or .pdf file", type=["txt", "pdf"])

# Display uploaded content
# Display uploaded content
if uploaded_file is not None:
    # read text
    if uploaded_file.name.endswith(".txt"):
        text = uploaded_file.read().decode("utf-8")
    else:
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()

    st.subheader("Notes Preview")
    st.text_area("Preview", text[:1000], height=200)

    clean = clean_text(text)

    # Summary
    st.subheader("Summary")
    st.write(summarize(clean))

    # Flashcards
    st.subheader("Flashcards")
    cards = generate_flashcards(clean)
    for c in cards:
        st.write(f"- {c[1]}")

    # Quiz
    st.subheader("Quiz")
    quiz = generate_quiz(clean)
    for q in quiz:
        st.write(f"Q: {q[0]}")
        st.write(f"A: {q[1]}")
        st.write("---")

    # Word Count
    st.subheader("Word Count")
    st.write(get_word_count(clean))

    # Read Time
    st.subheader("Estimated Read Time")
    st.write(get_read_time(clean))

    # Ask a question
    st.subheader("Ask a Question")
    user_q = st.text_input("Ask about these notes:")
    if user_q:
        answer = answer_question(clean, user_q)
        st.write(answer)
