import re
from pathlib import Path
from typing import List, Dict
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer, util
from transformers import pipeline

# -------------------------------
# Load models (free Hugging Face)
# -------------------------------

# Summarization model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Sentence embeddings for semantic similarity
embed_model = SentenceTransformer('all-MiniLM-L6-v2')


# -------------------------------
# File handling
# -------------------------------
def extract_text_from_pdf(uploaded_file) -> str:
    """
    Extract text from PDF file.
    """
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text


def clean_text(text: str) -> str:
    """
    Clean raw text: remove extra spaces and normalize line breaks.
    """
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# -------------------------------
# Summarization
# -------------------------------
def summarize(text: str, max_length=300) -> str:
    """
    Summarize input text using Hugging Face summarization model.
    """
    if len(text.split()) < 50:
        return text  # short text, no need to summarize
    summary = summarizer(text, max_length=max_length, min_length=50, do_sample=False)
    return summary[0]['summary_text']


# -------------------------------
# Flashcards generation
# -------------------------------
def generate_flashcards(text: str, max_cards=10) -> List[Dict]:
    """
    Generate flashcards from text:
    - Extract key sentences using embeddings
    - Form Q&A: "What is X?" / answer = sentence
    """
    sentences = [s.strip() for s in re.split(r'(?<=[.!?]) +', text) if len(s.strip()) > 20]
    if not sentences:
        return []

    # Embed sentences
    embeddings = embed_model.encode(sentences, convert_to_tensor=True)

    flashcards = []
    used = set()
    for i, sent in enumerate(sentences):
        # Skip duplicates
        if sent in used:
            continue
        used.add(sent)

        # Choose keyword(s) for Q
        keywords = re.findall(r"\b[A-Z][a-z]{2,}\b", sent)  # proper nouns
        if not keywords:
            keywords = sent.split()[:2]  # fallback: first 2 words

        question = f"What is {' '.join(keywords)} in this context?"
        flashcards.append({"question": question, "answer": sent})

        if len(flashcards) >= max_cards:
            break

    return flashcards


# -------------------------------
# Quiz generation
# -------------------------------
def generate_quiz(text: str, max_questions=5) -> List[Dict]:
    """
    Generate multiple-choice quiz:
    - Randomly select key sentences
    - Generate 3 wrong choices from other sentences
    """
    sentences = [s.strip() for s in re.split(r'(?<=[.!?]) +', text) if len(s.strip()) > 20]
    if len(sentences) < 4:
        return []  # not enough content for quiz

    quiz = []
    used_sentences = set()
    for sent in sentences:
        if sent in used_sentences:
            continue

        used_sentences.add(sent)

        # Question: main idea of sentence
        question = f"What is the main idea of this sentence?\n\"{sent[:80]}...\""
        # Correct answer
        answer = sent

        # Choices: pick 3 random other sentences
        other_choices = [s for s in sentences if s != sent]
        other_choices = other_choices[:3] if len(other_choices) >=3 else other_choices
        choices = other_choices + [answer]
        import random
        random.shuffle(choices)

        quiz.append({"question": question, "choices": choices, "answer": answer})
        if len(quiz) >= max_questions:
            break

    return quiz


# -------------------------------
# Question Answering
# -------------------------------
def answer_question(text: str, question: str) -> str:
    """
    Answer user question using semantic similarity:
    - Compare question embedding with sentence embeddings
    - Return sentence with highest similarity
    """
    if not text.strip():
        return "No content to answer from."

    sentences = [s.strip() for s in re.split(r'(?<=[.!?]) +', text) if len(s.strip()) > 20]
    if not sentences:
        return "No meaningful sentences found in the text."

    # Encode question and sentences
    question_emb = embed_model.encode(question, convert_to_tensor=True)
    sentence_embs = embed_model.encode(sentences, convert_to_tensor=True)

    # Compute cosine similarity
    similarities = util.pytorch_cos_sim(question_emb, sentence_embs)[0]
    best_idx = similarities.argmax().item()
    best_sentence = sentences[best_idx]

    return best_sentence
