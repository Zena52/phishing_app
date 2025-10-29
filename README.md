$txt = @'
# 🧩 Phishing App Suite

A collection of lightweight, local Python tools for studying, detecting, and analyzing phishing content — all designed to run privately on your machine with no external API calls.

## 🚀 Apps Included

| App | Description | Run Command |
|-----|--------------|--------------|
| 🧠 **AI Study Companion** | Summarizes text, creates flashcards, and quizzes from notes. | `streamlit run app/app.py` |
| 🛡️ **PhishGuardian** | Rule-based phishing URL and email detector. | `streamlit run app/phish_app.py` |
| 🤖 **PhishGuardian AI** | Lightweight AI analyzer for suspicious content. | `streamlit run app/phish_app_ai.py` |

## 🧰 Tech Stack
Python · Streamlit · PyPDF2 · NLTK · scikit-learn

## 📁 Folder Structure

phishing_app/
├─ app/
│ ├─ app.py
│ ├─ phish_app.py
│ ├─ phish_app_ai.py
│ ├─ utils.py
│ ├─ README_app.md
│ ├─ README_phish_app.md
│ ├─ README_phish_app_ai.md
│ └─ phish_ai_logs/
├─ phish_logs.csv
├─ phish_ai_summary.csv
└─ LICENSE


## 🪪 License
All rights reserved.  
This project is for personal, educational, or demo use only.  
No code may be copied, modified, or redistributed without explicit permission from the author.
'@
Set-Content -Path README.md -Value $txt -Encoding UTF8
