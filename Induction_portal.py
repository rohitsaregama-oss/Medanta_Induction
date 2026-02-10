import streamlit as st
import requests
import random
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
st.set_page_config(page_title="Medanta Induction Portal", layout="wide")

API_URL = "https://script.google.com/macros/s/AKfycbwJwTeEhOPd1U2nxn0Mu9tc9WSZIkjyCLZ6XhiCwYPFovcTQF_gs4ys1cEbKZzRYpmP/exec"

PASS_PERCENT = 80
TOTAL_ASSESSMENTS = 17

ASSESSMENT_ORDER = [
    "A01","A02","A03","A04","A05","A06","A07","A08","A09",
    "A10","A11","A12","A13","A14","A15","A16","A17"
]

ASSESSMENT_NAMES = {
    "A01": "HR Admin Process",
    "A02": "Second Victim",
    "A03": "Medication Safety",
    "A04": "Blood & Blood Product Safety",
    "A05": "Basic Life Support (BLS)",
    "A06": "Fire Safety",
    "A07": "Infection Prevention",
    "A08": "Quality Training",
    "A09": "IPSG",
    "A10": "Radiation Training",
    "A11": "Facility Management Safety",
    "A12": "Emergency Codes",
    "A13": "Cybersecurity Assessment",
    "A14": "Workplace Violence",
    "A15": "EMR Training",
    "A16": "HIS Training",
    "A17": "Medical Documentation"
}

# --------------------------------------------------
# HELPERS
# --------------------------------------------------
def call_api(payload):
    r = requests.post(API_URL, json=payload, timeout=20)
    return r.json()

def reset_assessment_state():
    st.session_state.current_questions = []
    st.session_state.answers = {}

# --------------------------------------------------
# SESSION STATE INIT
# --------------------------------------------------
if "participant_id" not in st.session_state:
    st.session_state.participant_id = None
    st.session_state.current_index = 0
    st.session_state.completed = {}
    st.session_state.current_questions = []
    st.session_state.answers = {}
    st.session_state.final_scores = {}

# --------------------------------------------------
# UI – HEADER
# --------------------------------------------------
st.markdown(
    """
    <h1 style="color:#c00;">Medanta Hospital Lucknow</h1>
    <p>Onboarding & Induction Assessment Portal</p>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# STEP 1: PARTICIPANT REGISTRATION
# --------------------------------------------------
if st.session_state.participant_id is None:
    st.subheader("Participant Details")

    with st.form("register"):
        name = st.text_input("Full Name")
        mobile = st.text_input("Mobile Number")
        dob = st.date_input("Date of Birth")
        qual = st.text_input("Qualification")
        category = st.selectbox("Category", ["Administration", "Nursing", "Clinical", "Paramedical"])
        sub_dept = st.text_input("Sub-Department")

        submitted = st.form_submit_button("Generate Induction Kit")

    if submitted:
        res = call_api({
            "action": "register_participant",
            "full_name": name,
            "mobile": mobile,
            "dob": str(dob),
            "qualification": qual,
            "category": category,
            "sub_department": sub_dept
        })

        st.session_state.participant_id = res["participant_id"]
        st.success("Registration successful. Please start your assessments.")
        st.rerun()

    st.stop()

# --------------------------------------------------
# STEP 2: ASSESSMENT ENGINE
# --------------------------------------------------
pid = st.session_state.participant_id
current_idx = st.session_state.current_index

if current_idx < TOTAL_ASSESSMENTS:
    aid = ASSESSMENT_ORDER[current_idx]
    st.subheader(f"Assessment {current_idx + 1} of {TOTAL_ASSESSMENTS}")
    st.markdown(f"### {ASSESSMENT_NAMES[aid]}")

    if not st.session_state.current_questions:
        data = call_api({
            "action": "get_questions",
            "assessment_id": aid
        })
        st.session_state.current_questions = data["questions"]
        reset_assessment_state()

    for q in st.session_state.current_questions:
        st.markdown(f"**{q['question']}**")
        opts = {o["key"]: o["val"] for o in q["options"]}
        choice = st.radio(
            "",
            options=list(opts.keys()),
            format_func=lambda x: f"{x}. {opts[x]}",
            key=q["question_id"]
        )
        st.session_state.answers[q["question_id"]] = choice

    if st.button("Submit Assessment"):
        payload = {
            "action": "submit_assessment",
            "participant_id": pid,
            "assessment_id": aid,
            "answers": [
                {"question_id": k, "selected": v}
                for k, v in st.session_state.answers.items()
            ]
        }

        result = call_api(payload)
        score = result["score"]

        if not result["passed"]:
            st.warning(
                "You did great however your score is below 80%. "
                "Concentrate hard, clarify your doubts and attempt again."
            )
            reset_assessment_state()
        else:
            st.success(f"Passed with {score}%")
            st.session_state.completed[aid] = True
            st.session_state.final_scores[aid] = score
            st.session_state.current_index += 1
            reset_assessment_state()
            st.rerun()

    st.stop()

# --------------------------------------------------
# STEP 3: FINAL MARKSHEET
# --------------------------------------------------
st.success("🎉 All assessments completed!")

avg_score = round(sum(st.session_state.final_scores.values()) / TOTAL_ASSESSMENTS, 2)

st.markdown(f"### Final Score: **{avg_score}%**")

if st.button("Download Final Marksheet"):
    res = call_api({
        "action": "generate_marksheet",
        "participant_id": pid
    })

    if res["status"] == "blocked":
        st.error("Download limit reached. Maximum 3 downloads allowed.")
    else:
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, "Medanta Hospital Lucknow")

        c.setFont("Helvetica", 12)
        c.drawString(50, height - 90, f"Participant ID: {pid}")
        c.drawString(50, height - 110, f"Date: {datetime.now().strftime('%d-%m-%Y')}")

        y = height - 150
        for aid, score in st.session_state.final_scores.items():
            c.drawString(50, y, f"{ASSESSMENT_NAMES[aid]} : {score}%")
            y -= 18

        c.drawString(50, y - 20, f"Overall Score: {avg_score}%")

        c.setFont("Helvetica-Oblique", 9)
        c.drawString(
            50, 40,
            "This is an assessment preview strictly for internal purposes. "
            "Sharing of this document outside of Medanta Hospital, Lucknow "
            "for any other purpose is strictly Prohibited."
        )

        c.showPage()
        c.save()
        buffer.seek(0)

        st.download_button(
            "Download PDF",
            buffer,
            file_name="Medanta_Induction_Marksheet.pdf",
            mime="application/pdf"
        )
