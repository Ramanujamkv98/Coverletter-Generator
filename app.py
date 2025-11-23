import os
import streamlit as st
from openai import OpenAI
import re
import textwrap
import io
from fpdf import FPDF


# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Cover Letter Generator", layout="wide")


# ------------------ BRANDING + THEME ------------------
st.markdown("""
<style>
body {
    background-color: #f8f9fc;
    font-family: 'Helvetica', sans-serif;
}
.sidebar .sidebar-content {
    background-color: #ffffff;
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
### 🚀 **AI Cover Letter Generator**
Built by **Ramanujamkv98**

Generate tailored cover letters from job descriptions + resume text.
Remove personal info before entering.
---
""")


# ------------------ OPENAI CLIENT ------------------
def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("❌ OPENAI_API_KEY environment variable is missing.")
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


# ------------------ PDF CREATOR (UNICODE SAFE) ------------------
def create_pdf(text: str, full_name: str) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Load embedded unicode font from local file
    pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
    pdf.set_font("DejaVu", size=11)

    # Add Name Header
    if full_name:
        pdf.set_font("DejaVu", size=14)
        pdf.cell(0, 10, txt=full_name, ln=1)
        pdf.ln(5)

    # Body content
    pdf.set_font("DejaVu", size=11)
    for line in text.split("\n"):
        wrapped = textwrap.wrap(line, width=90) or [""]
        for seg in wrapped:
            pdf.cell(0, 6, txt=seg, ln=1)

    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer.read()


# ------------------ PRIVACY WARNING ------------------
with st.expander("⚠ BEFORE YOU START"):
    st.warning(
        """
**IMPORTANT — Privacy Safety**

🔹 Paste ONLY resume text after removing:  
- Name  
- Phone number  
- Email  
- LinkedIn / Address  

This app uses session-only processing and does not store your data.
"""
    )


# ------------------ INPUT SECTION ------------------

st.subheader("📌 Step 1: Paste Job Description")

job_description = st.text_area(
    "Paste full job description:",
    height=300,
    placeholder="Paste JD here including role title + company name..."
)

role_name = extract_role(job_description) if job_description else None


# ------------------ SIDEBAR FIELDS ------------------

st.sidebar.header("🔧 Customize Output")

full_name = st.sidebar.text_input(
    "Your Name (For PDF Header)",
    placeholder="e.g., Sajal Jain"
)

company_name = st.sidebar.text_input(
    "Company Name",
    placeholder="e.g., Adobe, Deloitte, Amazon"
)

role_input = st.sidebar.text_input(
    "Role Title (Auto-Detected)",
    value=role_name if role_name else "",
    placeholder="e.g., Senior Analyst"
)


# ------------------ VALIDATIONS ------------------
if job_description and not role_name:
    st.error("❌ Role title NOT detected in job description. Please include it or enter manually.")

if job_description and company_name:
    if company_name.lower() not in job_description.lower():
        st.warning("⚠ Company name NOT found in JD. Paste full JD including company title.")


# ------------------ RESUME INPUT ------------------
st.subheader("📌 Step 2: Paste Resume Bullet Points (NO PII)")

resume_text = st.text_area(
    "Paste ONLY bullet points & achievements:",
    height=250,
    placeholder="Screenshot → copy text → paste here…"
)


# ------------------ GENERATE BUTTON ------------------
generate = st.button("🚀 Generate Cover Letter")


if generate:
    if not job_description.strip():
        st.error("❌ Paste job description first.")
    elif not company_name.strip():
        st.error("❌ Enter company name.")
    elif not role_input.strip():
        st.error("❌ Role title required.")
    elif not resume_text.strip():
        st.error("❌ Paste resume content.")
    else:
        client = get_openai_client()

        system_msg = """
You are a professional cover letter writer.

Rules:
- Use ONLY experience from resume text provided.
- DO NOT add personal contact info, names, phone numbers, or emails.
- If a required skill is missing, bridge using transferable experience.
- Tone: professional, concise, impact-driven.
- Max 5 short paragraphs.
"""

        user_msg = f"""
RESUME:
{resume_text}

ROLE: {role_input}
COMPANY: {company_name}

JOB DESCRIPTION:
{job_description}

Write a cover letter addressed to "Hiring Manager".
Do NOT fabricate experience or add personal info.
"""

        with st.spinner("✍ Generating your cover letter..."):
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg},
                ],
                temperature=0.6,
            )

        letter = response.choices[0].message.content
        st.success("🎉 Cover letter generated!")


        # ------------------ OUTPUT ------------------
        st.subheader("📎 Final Cover Letter")
        st.write(letter)

        pdf_bytes = create_pdf(letter, full_name)

        st.download_button(
            "⬇ Download PDF",
            data=pdf_bytes,
            file_name=f"Cover_Letter_{company_name.replace(' ','_')}.pdf",
            mime="application/pdf",
        )
