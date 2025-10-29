# phish_app_ai.py
import streamlit as st
import re
import json
import csv
import os
from urllib.parse import urlparse
from datetime import datetime
import uuid


from transformers import pipeline


st.set_page_config(page_title="PhishAI — Local AI Detector", page_icon="🤖", layout="centered")
st.title("🤖 PhishAI — Local AI + Rules (Version B)")
st.subheader("Zero-shot classification (local). No API keys. First run downloads the model — please be patient.")

# ---------------- Helpers (rules)
def extract_urls(text):
    return re.findall(r'(https?://[^\s]+)', text)

def rule_flags(text):
    flags = []
    text_l = text.lower()
    # urgency
    urg = ["act now","urgent","immediately","verify now","suspended","will be closed","click to verify"]
    found_urg = [p for p in urg if p in text_l]
    if found_urg:
        flags.append({"type":"urgency","items": found_urg})
    # personal requests
    per = ["password","otp","one-time","credit card","bank account","ssn","social security","pin"]
    found_per = [p for p in per if p in text_l]
    if found_per:
        flags.append({"type":"personal_request","items": found_per})
    # attachments
    exts = ['.exe','.scr','.zip','.rar','.js','.vbs','.bat','.msi']
    found_ext = [e for e in exts if e in text_l]
    if found_ext:
        flags.append({"type":"attachments","items": found_ext})
    # links
    urls = extract_urls(text)
    link_warnings = []
    for u in urls:
        domain = urlparse(u).netloc.lower()
        if domain.endswith((".ru",".xyz",".top")):
            link_warnings.append(f"suspicious tld: {domain}")
        if any(part.isdigit() for part in domain.split('.')):
            link_warnings.append(f"numeric domain parts: {domain}")
        if len(domain.split('.')) > 3:
            link_warnings.append(f"long subdomain: {domain}")
    if link_warnings:
        flags.append({"type":"links","items": link_warnings})
    return flags, urls

# ---------------- Model loader 
@st.cache_resource(show_spinner=False)
def load_zs():
    # Downloads model on first run; runs on CPU
    return pipeline("zero-shot-classification", model="facebook/bart-large-mnli", device=-1)


try:
    zs = load_zs()
except Exception as e:
    zs = None
    st.error("Model not loaded yet. If this is first run, wait for the download. If error persists, see terminal.")
    st.write(f"Debug: {e}")

# ---------------- Input area
email_text = st.text_area("Paste full email (headers + body help):", height=340)
sender = st.text_input("Sender email (optional)")

col1, col2 = st.columns([1,1])
with col1:
    if st.button("Analyze (AI + Rules)"):
        if not email_text.strip():
            st.warning("Paste an email first.")
        else:
            # 1) Rules
            flags, urls = rule_flags(email_text)
            # 2) AI zero-shot
            labels = ["phishing","legitimate","scam","promotion","notification"]
            ai_label = "unknown"
            ai_score = 0.0
            if zs is None:
                st.warning("AI model not available yet. Try again in a moment.")
            else:
                try:
                    res = zs(email_text, candidate_labels=labels, multi_label=False)
                    ai_label = res["labels"][0]
                    ai_score = float(res["scores"][0])
                except Exception as e:
                    st.error(f"Model inference error: {e}")
            # 3) Combine verdict logic
            rule_danger = any(f["type"] in ("urgency","personal_request","attachments","links") for f in flags)
            final_suspicious = (ai_label in ["phishing","scam"] and ai_score > 0.5) or rule_danger
            # score for display (simple)
            visual_score = int(ai_score*100) if ai_score else (80 if rule_danger else 10)
            level = "SUSPICIOUS" if final_suspicious else "LIKELY LEGITIMATE"

            # report
            rid = str(uuid.uuid4())[:8]
            report = {
                "id": rid,
                "timestamp": datetime.utcnow().isoformat(),
                "sender": sender or "unknown",
                "ai_label": ai_label,
                "ai_score": ai_score,
                "rule_flags": flags,
                "urls": urls,
                "final_verdict": level,
                "raw_preview": email_text[:1500]
            }

            # save local logs
            os.makedirs("phish_ai_logs", exist_ok=True)
            json_path = os.path.join("phish_ai_logs", f"report_{rid}.json")
            with open(json_path, "w", encoding="utf-8") as fh:
                json.dump(report, fh, indent=2)
            csv_path = "phish_ai_summary.csv"
            exists = os.path.exists(csv_path)
            with open(csv_path, "a", newline='', encoding='utf-8') as fh:
                writer = csv.writer(fh)
                if not exists:
                    writer.writerow(["id","timestamp","sender","ai_label","ai_score","final_verdict"])
                writer.writerow([rid, report["timestamp"], report["sender"], ai_label, ai_score, level])

            
            st.session_state["last_ai_report"] = report

with col2:
    st.markdown("### AI result panel")
    if "last_ai_report" not in st.session_state:
        st.info("Analyze an email to see AI label, confidence, and combined verdict.")
    else:
        r = st.session_state["last_ai_report"]
        st.metric("Final verdict", r["final_verdict"])
        st.write("**AI label:**", r["ai_label"], " — **confidence:**", f"{r['ai_score']:.2f}")
        # visual bar
        bar = int(r["ai_score"]*100)
        st.progress(bar)
        st.markdown("**Rule-based flags (explainability):**")
        if r["rule_flags"]:
            for f in r["rule_flags"]:
                st.write(f"- {f['type']}: {', '.join(f['items'])}")
        else:
            st.write("- None detected by rules.")
        st.markdown("**Links found:**")
        if r["urls"]:
            for u in r["urls"]:
                st.write("- " + u)
        else:
            st.write("- No links detected.")
        st.markdown("---")
        st.markdown("**Email preview (first 1000 chars)**")
        snippet = r["raw_preview"]
        # highlight simple important keywords
        highlights = []
        for grp in r["rule_flags"]:
            highlights.extend(grp["items"])
        # naive highlight (replace ignoring case)
        safe = snippet.replace("<", "&lt;").replace(">", "&gt;")
        for h in sorted(set(highlights), key=lambda s: -len(s)):
            try:
                safe = re.sub(re.escape(h), f"<mark style='background: #ffd6a5'>{h}</mark>", safe, flags=re.IGNORECASE)
            except re.error:
                pass
        st.markdown(f"<div style='white-space: pre-wrap; font-family: monospace; padding:8px; border-radius:6px; background:#fafafa'>{safe}</div>", unsafe_allow_html=True)
        st.download_button("Download AI JSON report", data=json.dumps(r, indent=2).encode("utf-8"),
                           file_name=f"ai_report_{r['id']}.json", mime="application/json")
        st.write("Saved locally to `phish_ai_logs/` and `phish_ai_summary.csv`")

# quick help / examples
with st.expander("Quick test examples"):
    st.write("Use the example from Version A or paste a real sample email. Try inserting 'verify', 'password', or a suspicious link.")
    st.code("""Subject: Your account will be suspended - verify now
Hello,
We detected suspicious activity. Act now to verify your account by clicking https://bank-secure.example-login.xyz/verify
Provide your password and OTP on the page.""")
