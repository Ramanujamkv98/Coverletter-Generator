# 📄 AI Cover Letter Generator

A Streamlit app that creates tailored cover letters using pasted job descriptions and resume bullet points. No file uploads, no personal data stored. Generates downloadable PDFs using an embedded Unicode font.

### 🚀 Features
- Paste-only inputs (privacy-safe)
- Manual company & role entry
- OpenAI-powered cover letter generation
- Export to PDF (Unicode-safe)
- Deployable on Google Cloud Run

### 🧠 Tech Stack
- Streamlit
- OpenAI API
- FPDF2 (PDF generation)
- Docker + Cloud Run

### 🔧 Setup
```bash
pip install -r requirements.txt
export OPENAI_API_KEY="your-key"
streamlit run app.py
