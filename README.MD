# ------------------- README.md -------------------

# AI Resume Builder

An AI-powered Resume Builder web app built with **Streamlit**. Users can input personal details, education, skills, and experience to generate a professional resume in PDF format.

## Features
- Form-based input for personal information, education, skills, and experience
- Automatic resume formatting
- PDF download
- Optional AI-powered skill suggestions (can be added later)

## Tech Stack
- Python
- Streamlit
- FPDF (PDF generation)
- Pandas (optional for data handling)

## Installation
1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-resume-builder.git
cd ai-resume-builder
```
2. Create a virtual environment and activate it:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage
```bash
streamlit run f.py
```
- The app will open in your browser at `http://localhost:8501`
- Fill out the form and click **Generate Resume** to download the PDF

## Deployment
- Push your code to GitHub
- Go to [Streamlit Cloud](https://streamlit.io/cloud)
- Click **New App → Select GitHub repo → Branch → Main file (`app.py`) → Deploy**

## Optional Enhancements
- Add AI-powered skill suggestions using `spaCy` or `NLTK`
- Automatic experience bullet generation based on job keywords

---

# ------------------- requirements.txt -------------------

streamlit
fpdf
pandas
# Optional for NLP features
spacy
