import streamlit as st
from fpdf import FPDF
import spacy


# ------------------- Load NLP Tools -------------------
nlp = spacy.load('en_core_web_sm')

# ------------------- Page Setup -------------------
st.set_page_config(page_title="AI Resume Builder", layout="wide")
st.title("AI Resume Builder with Smart AI Features")
st.write("Fill out your details to generate a professional resume. Skills and experiences will be enhanced automatically.")

# ------------------- User Input Form -------------------
with st.form("resume_form"):
    st.subheader("Personal Information")
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone")
    linkedin = st.text_input("LinkedIn URL")
    github = st.text_input("GitHub URL")

    st.subheader("Education")
    education = st.text_area("List your degrees / certifications (one per line)")

    st.subheader("Skills (Optional)")
    skills = st.text_area("List your skills (comma separated)")

    st.subheader("Projects")
    projects = st.text_area("Describe your projects (one per line)")

    st.subheader("Experience")
    experience = st.text_area("Describe your work experience")

    st.subheader("Achievements / Awards")
    achievements = st.text_area("List your achievements (one per line)")

    submitted = st.form_submit_button("Generate Resume")

# ------------------- AI Helper Functions -------------------
def suggest_skills(text):
    """Extract nouns/proper nouns as suggested skills"""
    doc = nlp(text)
    extracted = set()
    for token in doc:
        if token.pos_ in ['NOUN', 'PROPN']:
            extracted.add(token.text)
    return extracted

def grammar_correct(text):
    """Correct text grammar using language_tool_python"""
    matches = tool.check(text)
    corrected = language_tool_python.utils.correct(text, matches)
    return corrected

def auto_bullet_points(text):
    """Split by lines, correct grammar, and prefix with dash"""
    bullets = []
    for line in text.split('\n'):
        line = line.strip()
        if line:
            line = grammar_correct(line)
            bullets.append(f"- {line}")
    return '\n'.join(bullets)

# ------------------- PDF Generation -------------------
if submitted:
    pdf = FPDF()
    pdf.add_page()

    # Header
    pdf.set_font("Arial", 'B', 24)
    pdf.cell(0, 15, name, ln=True, align='C')
    pdf.ln(5)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 8, f"Email: {email} | Phone: {phone}", ln=True, align='C')
    pdf.cell(0, 8, f"LinkedIn: {linkedin} | GitHub: {github}", ln=True, align='C')
    pdf.ln(10)

    # Function to add sections
    def add_section(title, content_lines):
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 8, title, ln=True)
        pdf.ln(2)
        pdf.set_font("Arial", '', 12)
        pdf.multi_cell(0, 8, content_lines)
        pdf.ln(3)

    # ------------------- AI Skill Suggestion -------------------
    ai_skills = set()
    if experience.strip():
        ai_skills |= suggest_skills(experience)
    if projects.strip():
        ai_skills |= suggest_skills(projects)
    if skills.strip():
        ai_skills |= set([s.strip() for s in skills.split(',')])
    skills_text = ', '.join(sorted(ai_skills))

    # ------------------- Sections with AI Enhancement -------------------
    if education.strip():
        add_section("Education", auto_bullet_points(education))
    if skills_text:
        add_section("Skills", skills_text)
    if projects.strip():
        add_section("Projects", auto_bullet_points(projects))
    if experience.strip():
        add_section("Experience", auto_bullet_points(experience))
    if achievements.strip():
        add_section("Achievements", auto_bullet_points(achievements))

    # Generate PDF as bytes
    pdf_bytes = pdf.output(dest='S').encode('latin-1')

    st.success("✅ Resume generated successfully with AI enhancements!")
    st.download_button(
        label="Download AI-Enhanced Resume PDF",
        data=pdf_bytes,
        file_name=f"{name.replace(' ', '_')}_AI_Resume.pdf",
        mime="application/pdf"
    )
