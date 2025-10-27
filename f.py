import streamlit as st
from fpdf import FPDF

# ------------------- Page Setup -------------------
st.set_page_config(page_title="AI Resume Builder", layout="wide")
st.title("🎨 AI Resume Builder with Colors")
st.write("Fill out your details to generate a professional, colorful resume.")

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

    st.subheader("Skills")
    skills = st.text_area("List your skills (comma separated)")

    st.subheader("Experience")
    experience = st.text_area("Describe your work experience")

    submitted = st.form_submit_button("Generate Resume")

# ------------------- PDF Generation -------------------
if submitted:
    pdf = FPDF()
    pdf.add_page()

    # Header with color
    pdf.set_fill_color(0, 102, 204)  # Blue
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 26)
    pdf.cell(0, 15, name, ln=True, align='C', fill=True)
    pdf.ln(5)

    # Contact info
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 8, f"Email: {email} | Phone: {phone}", ln=True, align='C')
    pdf.cell(0, 8, f"LinkedIn: {linkedin} | GitHub: {github}", ln=True, align='C')
    pdf.ln(10)

    # Education
    pdf.set_fill_color(0, 102, 204)  # Blue section header
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 8, "Education", ln=True, fill=True)
    pdf.ln(2)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", '', 12)
    for line in education.split('\n'):
        pdf.multi_cell(0, 8, f"- {line}")
    pdf.ln(5)

    # Skills
    pdf.set_fill_color(0, 102, 204)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 8, "Skills", ln=True, fill=True)
    pdf.ln(2)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", '', 12)
    skill_list = [s.strip() for s in skills.split(',')]
    # Print skills as comma-separated with some spacing
    pdf.multi_cell(0, 8, ', '.join(skill_list))
    pdf.ln(5)

    # Experience
    pdf.set_fill_color(0, 102, 204)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 8, "Experience", ln=True, fill=True)
    pdf.ln(2)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", '', 12)
    for line in experience.split('\n'):
        pdf.multi_cell(0, 8, f"- {line}")
    pdf.ln(5)

    # Convert PDF to bytes for Streamlit download
    pdf_bytes = pdf.output(dest='S').encode('latin-1')

    st.success("✅ Resume generated successfully!")
    st.download_button(
        label="Download Colorful Resume PDF",
        data=pdf_bytes,
        file_name=f"{name.replace(' ', '_')}_Resume.pdf",
        mime="application/pdf"
    )
