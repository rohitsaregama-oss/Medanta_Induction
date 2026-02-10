import streamlit as st
import uuid
import requests
from datetime import datetime
from pathlib import Path

# ========================= CONFIG =========================
st.set_page_config(page_title="Medanta Induction Portal", layout="wide")

APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwJwTeEhOPd1U2nxn0Mu9tc9WSZIkjyCLZ6XhiCwYPFovcTQF_gs4ys1cEbKZzRYpmP/exec"

ASSESSMENTS = [
    ("A01", "HR Admin Process"),
    ("A02", "Second Victim"),
    ("A03", "Medication Safety"),
    ("A04", "Blood & Blood Product Safety"),
    ("A05", "Basic Life Support"),
    ("A06", "Fire Safety"),
    ("A07", "Infection Prevention"),
    ("A08", "Quality Training"),
    ("A09", "IPSG"),
    ("A10", "Radiation Training"),
    ("A11", "Facility Management Safety"),
    ("A12", "Emergency Codes"),
    ("A13", "Cybersecurity Assessment"),
    ("A14", "Workplace Violence"),
    ("A15", "EMR Training"),
    ("A16", "HIS Training"),
    ("A17", "Medical Documentation"),
]

# ========================= LOAD HTML UI =========================
ui_html = Path("ui.html").read_text(encoding="utf-8")
st.components.v1.html(ui_html, height=950, scrolling=False)

st.markdown("---")

# ========================= STREAMLIT CONTROL PANEL =========================
st.subheader("Finalize & Generate Induction Kit")

with st.form("induction_form"):
    col1, col2 = st.columns(2)

    with col1:
        full_name = st.text_input("Full Name")
        mobile = st.text_input("Mobile Number")
        dob = st.date_input("Date of Birth")
        qualification = st.text_input("Qualification")

    with col2:
        category = st.selectbox(
            "Category",
            ["Administration", "Nursing", "Doctor / Consultant", "Paramedical"]
        )
        sub_dept = st.text_input("Sub-Department")

    submit = st.form_submit_button("Generate Induction Kit")

# ========================= SUBMIT LOGIC =========================
if submit:
    if not full_name or not mobile:
        st.error("Name and Mobile Number are mandatory.")
        st.stop()

    participant_id = f"PID-{uuid.uuid4().hex[:8].upper()}"

    payload = {
        "action": "register_participant",
        "participant_id": participant_id,
        "full_name": full_name,
        "mobile": mobile,
        "dob": str(dob),
        "qualification": qualification,
        "category": category,
        "sub_department": sub_dept,
        "induction_date": datetime.now().strftime("%Y-%m-%d"),
        "status": "IN_PROGRESS"
    }

    try:
        r = requests.post(APPS_SCRIPT_URL, json=payload, timeout=15)
        r.raise_for_status()
    except Exception as e:
        st.error("Failed to save participant data.")
        st.stop()

    st.success("Induction Kit Generated Successfully")

    st.markdown("### 📝 Your Assessments")

    for aid, name in ASSESSMENTS:
        assessment_link = (
            f"{APPS_SCRIPT_URL}"
            f"?action=start_assessment"
            f"&pid={participant_id}"
            f"&aid={aid}"
        )
        st.markdown(f"🔗 **{name}**  \n{assessment_link}")

    st.info("You must score **80% or above** in each assessment to proceed.")

