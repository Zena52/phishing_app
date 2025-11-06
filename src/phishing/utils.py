import re
from PyPDF2 import PdfReader

# -------------------
# TEXT UTILITIES
# -------------------
def clean_text(text):
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# -------------------
# SUMMARIZATION
# -------------------
def summarize(text):
    sentences = text.split('. ')
    summary = '. '.join(sentences[:5])  # first 5 sentences
    return summary

# -------------------
# FLASHCARDS
# -------------------
def generate_flashcards(text):
    sentences = text.split('. ')
    flashcards = []
    for i, sent in enumerate(sentences[:5], 1):
        question = f"What is the main idea of sentence {i}?"
        answer = sent
        flashcards.append({'question': question, 'answer': answer})
    return flashcards

# -------------------
# QUIZ
# -------------------
def generate_quiz(text):
    sentences = text.split('. ')
    quiz = []
    for i, sent in enumerate(sentences[:3], 1):
        question = f"What does sentence {i} convey?"
        choices = [sent, "Option B", "Option C", "Option D"]
        answer = sent
        quiz.append({'question': question, 'choices': choices, 'answer': answer})
    return quiz

# -------------------
# ASK QUESTION
# -------------------
def answer_question(text, question):
    keyword = question.split()[0]
    sentences = text.split('. ')
    for sent in sentences:
        if keyword.lower() in sent.lower():
            return sent
    return "Sorry, I could not find an answer."

# -------------------
# FILE HANDLING
# -------------------
def extract_text_from_pdf(file):
    pdf = PdfReader(file)
    text = ""
    for page in pdf.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + " "
    return text
