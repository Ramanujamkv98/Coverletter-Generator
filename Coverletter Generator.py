import os
import streamlit as st
from openai import OpenAI
import re
import textwrap
import io
from fpdf import FPDF

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Cover Letter Generator", layout="wide")
st.title("📄 AI Cover Letter Generator (Paste-Safe Mode)")


# ------------------ OPENAI CLIENT ------------------
def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("OPENAI_API_KEY environment variable is missing.")
        return None
    return OpenAI(api_key=api_key)


# ------------------ ROLE EXTRACTION ------------------
def extract_role(job_description):
    patterns = [
        r"(?:Senior|Sr\.?|Lead|Associate|Principal|Junior|Entry|Head)\s+[A-Za-z0-9 ,\-]+",
        r"[A-Z][A-Za-z]+ Analyst[ A-Za-z0-9,\-]*",
        r"[A-Z][A-Za-z]+ Manager[ A-Za-z0-9,\-]*",
        r"[A-Z][A-Za-z]+ Engineer[ A-Za-z0-9,\-]*",
        r"[A-Z][A-Za-z]+ Specialist[ A-Za-z0-9,\-]*",
        r"[A-Z][A-Za-z]+ Scientist[ A-Za-z0-9,\-]*",
    ]

    for pattern in patterns:
        match = re.search(pattern, job_description)
        if match:
            return match.group().strip()

    return None



# ------------------ PDF Export ------------------
def create_pdf(text):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=11)

    for line in text.split("\n"):
        for seg in textwrap.wrap(line, 90):
            pdf.cell(0, 6, txt=seg, ln=1)

    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer


# ------------------ SAFETY NOTICE ------------------
with st.expander("⚠ BEFORE YOU START"):
    st.warning(
        """
**IMPORTANT:**
- Paste ONLY resume text *without personal details*
- Remove phone number, email, address, LinkedIn
- This tool does NOT store your text, but protect yourself
"""
    )


# ------------------ STEP 1: JOB DESCRIPTION ------------------
st.subheader("📌 Step 1: Paste Job Description (Must Include Role + Company)")

job_description = st.text_area(
    "Paste complete job description:",
    height=300,
    placeholder="Paste JD here with full role title + company name..."
)

# Extract role automatically
role_name = extract_role(job_description) if job_description else None

# Warn if missing company mention later when input given
st.sidebar.header("Job Details")

company_name = st.sidebar.text_input(
    "Company Name",
    placeholder="e.g., Adobe, Deloitte, Amazon"
)

# Company validation
if job_description and company_name:
    if company_name.lower() not in job_description.lower():
        st.warning("⚠ Company name not found in JD. Please paste full JD text.")


# ------------------ Editable Role Name ------------------
role_input = st.sidebar.text_input(
    "Role Title (Auto-Detected)",
    value=role_name if role_name else "",
    placeholder="e.g., Senior Marketing Analyst"
)

# Warn if role didn't get extracted
if job_description and not role_name:
    st.error("❌ Role title not detected in JD. Please include it or type it manually.")


# ------------------ STEP 2: RESUME TEXT ------------------
st.subheader("📌 Step 2: Paste Screenshot Text (No PII)")

resume_text = st.text_area(
    "Paste ONLY bullet points & achievements (no name/email/phone):",
    height=280,
    placeholder="Copy text from resume screenshot here…"
)


# ------------------ GENERATE BUTTON ------------------
generate = st.button("🚀 Generate Cover Letter")

if generate:

    if not job_description.strip():
        st.error("Paste job description first.")
    elif not company_name.strip():
        st.error("Enter company name.")
    elif not role_input.strip():
        st.error("Role title required. Ensure it is present in JD.")
    elif not resume_text.strip():
        st.error("Paste resume text.")
    else:
        client = get_openai_client()

        system_msg = """
You are a professional cover letter writer.

Rules:
- Use only information provided in resume text.
- Do NOT add names, phone numbers, or emails.
- If skill mismatch, bridge with transferable experience.
- Tone: professional, concise, impact-driven.
"""

        user_msg = f"""
RESUME:
{resume_text}

ROLE: {role_input}
COMPANY: {company_name}

JOB DESCRIPTION:
{job_description}

Write a cover letter addressed to Hiring Manager.
Do not fabricate experience.
"""

        with st.spinner("Writing your cover letter..."):
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg},
                ],
                temperature=0.6,
            )

        letter = response.choices[0].message.content
        st.success("Cover letter generated!")

        st.subheader("📎 Cover Letter Output")
        st.write(letter)

        pdf_bytes = create_pdf(letter)

        st.download_button(
            "⬇ Download PDF",
            data=pdf_bytes,
            file_name=f"Cover_Letter_{company_name.replace(' ','_')}.pdf",
            mime="application/pdf",
        )
