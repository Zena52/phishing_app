import re
import random

def clean_text(text):
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def summarize(text, sentences=3):
    parts = text.split(".")
    summary = ". ".join(parts[:sentences])
    return summary + "."

def generate_flashcards(text, count=5):
    lines = text.split(".")
    cards = random.sample(lines, min(count, len(lines)))
    return [("Concept:", c.strip()) for c in cards]

def generate_quiz(text, count=5):
    lines = [l.strip() for l in text.split(".") if len(l.split()) > 4]
    questions = random.sample(lines, min(count, len(lines)))
    quiz = []
    for q in questions:
        quiz.append({
            "question": f"What does this refer to: '{q[:50]}...'",
            "answer": q
        })
    return quiz

def answer_question(text, question):
    words = question.lower().split()
    best = ""
    for sentence in text.split("."):
        if any(w in sentence.lower() for w in words):
            best = sentence
            break
    return best if best else "I couldn't find an answer in your notes."

def get_word_count(text):
    words = text.split()
    return len(words)

def get_read_time(word_count, wpm=200):
    # average reading speed = 200 words per minute
    minutes = word_count / wpm
    return round(minutes, 2)
