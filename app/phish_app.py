# phish_app.py 
import streamlit as st
import re
import csv
import json
from urllib.parse import urlparse
from datetime import datetime
import uuid
import os

# ---------------------------
st.set_page_config(page_title="PhishGuardian — Rule-based Detector", page_icon="🛡️", layout="wide")
st.title("🛡️ PhishGuardian — Rule-based Phishing Detector (Version A)")
st.write("Paste an email (headers + body helpful). The detector highlights red flags, gives a risk score, and creates a downloadable report.")

# --- helpers ---
def extract_urls(text):
    return re.findall(r'(https?://[^\s]+)', text)

def check_urgency(text):
    urgency_phrases = [
        "act now", "urgent", "immediately", "verify now", "will be closed",
        "suspended", "click to verify", "your account has been suspended"
    ]
    found = [p for p in urgency_phrases if p in text.lower()]
    return found

def check_links(urls):
    flags = []
    for u in urls:
        parsed = urlparse(u)
        domain = parsed.netloc.lower()
        if domain.endswith(".ru") or domain.endswith(".xyz") or domain.endswith(".top"):
            flags.append(f"Suspicious TLD: {domain}")
        if any(part.isdigit() for part in domain.split('.')):
            flags.append(f"Numeric domain parts: {domain}")
        if len(domain.split('.')) > 3:
            flags.append(f"Long subdomain/domain: {domain}")
    return flags

def check_attachments(text):
    exts = ['.exe', '.scr', '.zip', '.rar', '.js', '.vbs', '.bat', '.msi']
    found = [e for e in exts if e in text.lower()]
    return found

def check_personal_requests(text):
    phrases = ["password", "otp", "one-time", "credit card", "bank account", "ssn", "social security", "pin"]
    found = [p for p in phrases if p in text.lower()]
    return found

def score_email(text, sender):
    urls = extract_urls(text)
    url_score = len(urls)
    urgency = check_urgency(text)
    attach = check_attachments(text)
    personal = check_personal_requests(text)
    link_flags = check_links(urls)

    score = 0
    score += min(url_score * 2, 6)
    score += min(len(urgency) * 2, 6)
    if attach: score += 3
    if personal: score += 2
    score += min(len(link_flags), 4)

    return {
        "score": score,
        "urls": urls,
        "urgency_phrases": urgency,
        "link_flags": link_flags,
        "personal_requests": personal,
        "attachments": attach
    }

def highlight_email(text, highlights):
    # highlights
    safe_text = st.markdown 
    escaped = text.replace("<", "&lt;").replace(">", "&gt;")
    
    highlights = sorted(set(h for h in highlights if h.strip()), key=lambda s: -len(s))
    for h in highlights:
        esc_h = h.replace("<", "&lt;").replace(">", "&gt;")
        # simple case-insensitive replacement 
        try:
            escaped = re.sub(re.escape(esc_h), f"<mark style='background: #ffb3b3'>{esc_h}</mark>", escaped, flags=re.IGNORECASE)
        except re.error:
            pass
    return escaped

def append_log(report, log_path="phish_logs.csv"):
    header = ["id","timestamp","score","level","sender","short_summary","report_json"]
    exists = os.path.exists(log_path)
    with open(log_path, "a", newline='', encoding='utf-8') as fh:
        writer = csv.writer(fh)
        if not exists:
            writer.writerow(header)
        writer.writerow([report["id"], report["timestamp"], report["score"], report["level"], report["sender"], report["summary"], json.dumps(report)])

# ---------------------------
# Layout: two columns
col1, col2 = st.columns([1, 1.3])

with col1:
    email_text = st.text_area("Paste email (body + links). Include headers if possible:", height=360)
    sender = st.text_input("Sender email (optional):")
    if st.button("Analyze"):
        if not email_text.strip():
            st.warning("Please paste the email text before analyzing.")
        else:
            res = score_email(email_text, sender)
            score = res["score"]
            if score >= 8:
                level = "HIGH RISK"
                color_emoji = "🔴"
                color_hex = "#ff4b4b"
            elif score >= 4:
                level = "MEDIUM RISK"
                color_emoji = "🟠"
                color_hex = "#ffb74d"
            else:
                level = "LOW RISK"
                color_emoji = "🟢"
                color_hex = "#8be58b"

            # prepare report
            uid = str(uuid.uuid4())[:8]
            report = {
                "id": uid,
                "timestamp": datetime.utcnow().isoformat(),
                "sender": sender or "unknown",
                "score": score,
                "level": level,
                "details": res,
                "raw_email_preview": (email_text[:1000] + "...") if len(email_text) > 1000 else email_text,
                "summary": f"{level} — score {score}"
            }

            
            append_log(report)

            
            highlights = []
            highlights.extend(res.get("urgency_phrases", []))
            highlights.extend(res.get("personal_requests", []))
            highlights.extend(res.get("link_flags", []))
            highlights.extend(res.get("urls", []))
            highlights.extend(res.get("attachments", []))

            
            st.session_state["last_report"] = report
            st.session_state["last_highlights"] = highlights

with col2:
    st.subheader("Result")
    if "last_report" not in st.session_state:
        st.info("Analyze an email on the left to see results here. Example emails available below.")
    else:
        r = st.session_state["last_report"]
        highlights = st.session_state.get("last_highlights", [])
        st.markdown(f"### {r['level']} { '🔴' if r['level']=='HIGH RISK' else '🟠' if r['level']=='MEDIUM RISK' else '🟢'}")
        st.metric("Risk score", r["score"])
        st.write("**Sender:**", r["sender"])
        st.write("**When analyzed (UTC):**", r["timestamp"])

        st.markdown("**Highlights (what caused flags):**")
        if r["details"]["urgency_phrases"]:
            st.write("- Urgency phrases:", ", ".join(r["details"]["urgency_phrases"]))
        if r["details"]["personal_requests"]:
            st.write("- Personal/financial requests:", ", ".join(r["details"]["personal_requests"]))
        if r["details"]["attachments"]:
            st.write("- Attachment mentions:", ", ".join(r["details"]["attachments"]))
        if r["details"]["link_flags"]:
            st.write("- Link warnings:", ", ".join(r["details"]["link_flags"]))
        if r["details"]["urls"]:
            st.write("- Links found:")
            for u in r["details"]["urls"]:
                st.write("  - " + u)

        st.markdown("---")
        st.markdown("**Email preview with highlights:**")
        highlighted_html = highlight_email(r["raw_email_preview"], highlights)
        st.markdown(f"<div style='white-space: pre-wrap; font-family: monospace; padding:10px; border-radius:6px; background:#fafafa'>{highlighted_html}</div>", unsafe_allow_html=True)

        st.markdown("---")
        
        json_bytes = json.dumps(r, indent=2).encode("utf-8")
        st.download_button("Download JSON report", data=json_bytes, file_name=f"phish_report_{r['id']}.json", mime="application/json")
        st.write("Saved to local log: phish_logs.csv")

# ---------------------------
# Example emails for testing
with st.expander("Examples (click to expand) — contains 2 samples"):
    st.markdown("**Sample 1 — phishing (red flags)**")
    sample1 = """From: support@bank-secure.example.com
Subject: Your account will be suspended - verify now
Hello,
We detected suspicious activity. Act now to verify your account by clicking https://bank-secure.example-login.xyz/verify
Failure to verify will result in account suspension.
Provide your password and OTP on the page.
Regards,
Bank Security Team"""
    st.code(sample1, language="text")
    st.markdown("**Sample 2 — likely legitimate**")
    sample2 = """From: newsletter@store.example.com
Subject: Your monthly receipt
Hello,
Thanks for your purchase. View your order here: https://store.example.com/orders/12345
This is an automated receipt. No action required."""
    st.code(sample2, language="text")

# footer / notes
st.markdown("---")
st.caption("Built for portfolio demo. Rule-based detection — do not use as only defense. Next: add AI zero-shot model for stronger detection.")
