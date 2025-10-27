
import os
import re
import io
import json
import streamlit as st
from pathlib import Path
from typing import Tuple, Dict

# Optional dependencies which may not be installed in minimal envs
try:
    import openai
except Exception:
    openai = None

try:
    import docx
except Exception:
    docx = None

try:
    from pdfminer.high_level import extract_text as pdf_extract_text
except Exception:
    pdf_extract_text = None

# PDF generation
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
except Exception:
    letter = None
    canvas = None

# ---------------- Config ----------------
DEFAULT_MODEL = "gpt-4o-mini"  # change to a model you have access to
st.set_page_config(page_title="AI Resume Builder", layout="wide")
SECTION_HEADINGS = ["experience", "education", "skills", "projects", "certifications",
                    "summary", "objective", "contact", "awards", "publications"]

# ---------------- Utils / LLM wrapper ----------------
def call_llm(prompt: str, system: str = "You are a helpful assistant.", temperature: float = 0.2, max_tokens: int = 800) -> str:
    """
    Call OpenAI ChatCompletion and return text.
    Falls back to a stub if openai library or API key missing.
    """
    key = os.environ.get("OPENAI_API_KEY") or (st.secrets.get("OPENAI_API_KEY") if "OPENAI_API_KEY" in st.secrets else None)
    if not key or openai is None:
        return "[LLM not configured — set OPENAI_API_KEY in environment or Streamlit secrets]"
    openai.api_key = key
    try:
        resp = openai.ChatCompletion.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"[LLM call error: {e}]"

# ---------------- Parsing uploaded files ----------------
def extract_text_from_file(uploaded_file) -> str:
    if uploaded_file is None:
        return ""
    fname = uploaded_file.name.lower()
    data = uploaded_file.read()
    if fname.endswith('.pdf'):
        if pdf_extract_text is None:
            return "[pdfminer.six not installed: please add pdfminer.six to requirements]"
        try:
            # pdfminer accepts bytes-like; pass BytesIO
            return pdf_extract_text(io.BytesIO(data))
        except Exception as e:
            return f"[PDF parse error: {e}]"
    elif fname.endswith('.docx'):
        if docx is None:
            return "[python-docx not installed: please add python-docx to requirements]"
        try:
            doc = docx.Document(io.BytesIO(data))
            paragraphs = [p.text for p in doc.paragraphs]
            return '\n'.join(paragraphs)
        except Exception as e:
            return f"[DOCX parse error: {e}]"
    else:
        try:
            return data.decode('utf-8', errors='ignore')
        except Exception:
            return "[unsupported file type]"

def split_into_sections(text: str) -> Dict[str, str]:
    text = re.sub(r'\r', '\n', text or "")
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    sections = {h: "" for h in SECTION_HEADINGS}
    current = 'summary'
    buffer = []
    for line in lines:
        l = line.lower()
        heading = None
        for h in SECTION_HEADINGS:
            # match lines like "Experience", "Experience:" etc.
            if re.match(rf'^{re.escape(h)}[:\-\s]*$', l) or l.startswith(h + ':'):
                heading = h
                break
        if heading:
            sections[current] = '\n'.join(buffer).strip()
            buffer = []
            current = heading
        else:
            buffer.append(line)
    sections[current] = '\n'.join(buffer).strip()
    return sections

# ---------------- ATS scoring ----------------
def ats_score(resume_text: str, jd_text: str) -> Tuple[float, Dict[str, int]]:
    resume_text = resume_text or ""
    jd_text = jd_text or ""
    if not jd_text.strip():
        return 0.0, {}
    jd_words = re.findall(r"[A-Za-z0-9_+#]+", jd_text.lower())
    jd_keywords = set([w for w in jd_words if len(w) > 2])
    resume_words = re.findall(r"[A-Za-z0-9_+#]+", resume_text.lower())
    resume_set = set(resume_words)
    matched = [kw for kw in jd_keywords if kw in resume_set]
    score = (len(matched) / max(1, len(jd_keywords))) * 100.0
    counts = {kw: (1 if kw in resume_set else 0) for kw in jd_keywords}
    return score, counts

# ---------------- PDF generation ----------------
def generate_pdf_from_text(text: str) -> bytes:
    if canvas is None or letter is None:
        return b""
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)
    width, height = letter
    margin = 50
    y = height - margin
    for line in (text or "").split('\n'):
        # simple wrap at ~90 chars
        while len(line) > 90:
            piece = line[:90]
            c.drawString(margin, y, piece)
            line = line[90:]
            y -= 12
            if y < margin + 20:
                c.showPage()
                y = height - margin
        c.drawString(margin, y, line)
        y -= 12
        if y < margin + 20:
            c.showPage()
            y = height - margin
    c.save()
    packet.seek(0)
    return packet.read()

# ---------------- UI ----------------
st.title("AI Resume Builder — Streamlit Prototype")
st.markdown("Create, optimize, and export ATS-friendly resumes using AI. **Advanced features:** job-tailoring, bullet optimization, cover letter generation, ATS scoring, templates.")

with st.sidebar:
    st.header("Settings")
    model = st.selectbox("LLM Model", options=[DEFAULT_MODEL, "gpt-4", "gpt-3.5-turbo"], index=0)
    temp = st.slider("Temperature", 0.0, 1.0, 0.2)
    st.write("")
    st.markdown("**Upload / API**")
    oaikey_input = st.text_input("OpenAI API Key (optional for session)", type="password", key="oaikey_input")
    st.caption("If set, this will only persist in this session. For Streamlit Cloud, set OPENAI_API_KEY in Secrets.")

# Use session key if provided
if oaikey_input:
    os.environ["OPENAI_API_KEY"] = oaikey_input

col1, col2 = st.columns([2,1])
with col1:
    st.subheader("1) Upload or paste your resume")
    uploaded = st.file_uploader("Upload resume (PDF, DOCX, TXT)", type=['pdf','docx','txt'])
    resume_text = ""
    if uploaded:
        resume_text = extract_text_from_file(uploaded)
        st.success("Uploaded and parsed file (preview below)")
    resume_text = st.text_area("Or paste your resume text here", value=resume_text, height=300)

    st.subheader("2) Paste the job description (optional)")
    job_description = st.text_area("Paste job description to tailor resume / compute ATS score", height=220)

    st.subheader("3) Choose template")
    template = st.selectbox("Template", options=["Plain", "Modern", "Clean"])

with col2:
    st.subheader("Quick actions")
    if st.button("Extract sections"):
        sections = split_into_sections(resume_text)
        st.session_state['sections'] = sections
        st.success("Sections extracted — open 'Sections' panel below")

    if st.button("Run ATS score"):
        score, counts = ats_score(resume_text, job_description)
        st.session_state['ats_score'] = score
        st.session_state['ats_counts'] = counts
        st.success(f"ATS Score computed: {score:.1f}%")

    if st.button("Auto-optimize bullets (LLM)"):
        prompt = (
            "Rewrite the following resume bullets to be concise, quantify achievements where possible, "
            "and use action verbs. Keep formatting as bullets when appropriate. Return only the rewritten resume text.\n\n"
            f"{resume_text}\n\n"
        )
        res = call_llm(prompt, temperature=temp)
        st.session_state['optimized'] = res
        st.success("Optimization complete — open 'Optimized Resume' panel")

    if st.button("Generate tailored cover letter"):
        prompt = (
            "Write a one-page professional cover letter tailored to the following job description:\n\n"
            f"{job_description}\n\n"
            "And based on this resume text:\n\n"
            f"{resume_text}\n\n"
            "Keep it concise and persuasive."
        )
        cl = call_llm(prompt, temperature=0.4)
        st.session_state['cover_letter'] = cl
        st.success("Cover letter generated — open 'Cover Letter' panel")

st.markdown("---")
cols = st.columns(3)
with cols[0]:
    st.header("Sections")
    if 'sections' in st.session_state:
        for k,v in st.session_state['sections'].items():
            st.subheader(k.title())
            st.write(v[:500] + ('...' if len(v) > 500 else ''))
    else:
        st.write("No sections yet. Click 'Extract sections' to parse the resume.")
with cols[1]:
    st.header("Optimized Resume")
    if 'optimized' in st.session_state:
        st.text_area("Optimized resume (LLM output)", value=st.session_state['optimized'], height=300)
    else:
        st.write("No optimized resume yet. Click 'Auto-optimize bullets (LLM)'")
with cols[2]:
    st.header("Cover Letter")
    if 'cover_letter' in st.session_state:
        st.text_area("Cover Letter", value=st.session_state['cover_letter'], height=300)
    else:
        st.write("No cover letter yet. Click 'Generate tailored cover letter'")

st.markdown("---")
st.subheader("Export")
export_text = st.session_state.get('optimized') or resume_text

if st.button("Generate PDF"):
    pdf_bytes = generate_pdf_from_text(export_text)
    if pdf_bytes:
        st.session_state['pdf_bytes'] = pdf_bytes
        st.success("PDF generated — use the download button below")
    else:
        st.error("PDF generation libraries missing (reportlab). Install reportlab for PDF exports.")

if 'pdf_bytes' in st.session_state:
    st.download_button("Download PDF", data=st.session_state['pdf_bytes'], file_name="resume.pdf", mime='application/pdf')

if 'ats_score' in st.session_state:
    st.metric("ATS Score", f"{st.session_state['ats_score']:.1f}%")
    counts = st.session_state.get('ats_counts', {})
    matched = [k for k,v in counts.items() if v]
    st.write("Top matched keywords:", ', '.join(matched[:20]))

st.markdown("---")
if st.button("Extract skills & keywords (LLM)"):
    prompt = (
        "Extract a JSON array of skills and keywords from the following resume text. "
        "Return only a valid JSON array (e.g. [\"skill1\",\"skill2\"]).\n\n"
        f"{resume_text}"
    )
    res = call_llm(prompt, temperature=0.0)
    skills = []
    try:
        skills = json.loads(res)
    except Exception:
        # best-effort fallback
        skills = re.findall(r"[A-Za-z0-9+\-#]+", res)
    st.session_state['skills'] = skills
    st.success("Skills extracted — open 'Skills & Keywords' below")

if 'skills' in st.session_state:
    st.header("Skills & Keywords")
    st.write(st.session_state['skills'])

st.info("Tips: For best LLM results, provide a focused job description. To deploy to Streamlit Cloud, add OPENAI_API_KEY to secrets and push the repository to GitHub.")
st.caption("Prototype by ChatGPT — customize heavily before production use. This demo performs LLM calls and PDF generation; check your environment for required packages.")

