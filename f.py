import streamlit as st
from fpdf import FPDF
import qrcode
from io import BytesIO

# ------------------- Page Setup -------------------
st.set_page_config(page_title="AI Resume Builder", layout="wide")
st.title("🎨 AI Resume Builder - Colorful & Feature-Rich")
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

    st.subheader("Projects")
    projects = st.text_area("List your projects (one per line)")

    st.subheader("Experience")
    experience = st.text_area("Describe your work experience")

    st.subheader("Achievements / Awards")
    achievements = st.text_area("List your achievements (one per line)")

    submitted = st.form_submit_button("Generate Resume")

# ------------------- PDF Generation -------------------
if submitted:
    pdf = FPDF()
    pdf.add_page()

    # ------------------- Header -------------------
    pdf.set_fill_color(0, 102, 204)  # Blue header
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 26)
    pdf.cell(0, 15, name, ln=True, align='C', fill=True)
    pdf.ln(5)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 8, f"Email: {email} | Phone: {phone}", ln=True, align='C')
    pdf.cell(0, 8, f"LinkedIn: {linkedin} | GitHub: {github}", ln=True, align='C')
    pdf.ln(10)

    # ------------------- Function to add sections -------------------
    def add_section(title, content_lines):
        pdf.set_fill_color(0, 102, 204)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 8, title, ln=True, fill=True)
        pdf.ln(2)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", '', 12)
        for line in content_lines.split('\n'):
            if line.strip():
                pdf.multi_cell(0, 8, f"- {line}")
        pdf.ln(3)

    # ------------------- Sections -------------------
    if education.strip():
        add_section("Education", education)

    if skills.strip():
        add_section("Skills", ', '.join([s.strip() for s in skills.split(',')]))

    if projects.strip():
        add_section("Projects", projects)

    if experience.strip():
        add_section("Experience", experience)

    if achievements.strip():
        add_section("Achievements", achievements)

    # ------------------- Add QR Codes -------------------
    qr_buffer = BytesIO()
    qr = qrcode.QRCode(box_size=2, border=1)
    if linkedin.strip():
        qr.add_data(linkedin)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(qr_buffer)
        pdf.image(qr_buffer, x=10, y=pdf.get_y(), w=25)
        pdf.ln(30)
        qr_buffer.seek(0)
    qr_buffer.close()

    # ------------------- Generate PDF as bytes -------------------
    pdf_bytes = pdf.output(dest='S').encode('latin-1')

    st.success("✅ Resume generated successfully!")
    st.download_button(
        label="Download Colorful Resume PDF",
        data=pdf_bytes,
        file_name=f"{name.replace(' ', '_')}_Resume.pdf",
        mime="application/pdf"
    )

