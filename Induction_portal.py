import streamlit as st
import requests
from urllib.parse import urlencode

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Medanta Induction Portal",
    layout="wide"
)

APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwJwTeEhOPd1U2nxn0Mu9tc9WSZIkjyCLZ6XhiCwYPFovcTQF_gs4ys1cEbKZzRYpmP/exec"

ASSESSMENTS = [
    "A01_HR_ADMIN_PROCESS",
    "A02_SECOND_VICTIM",
    "A03_MEDICATION_SAFETY",
    "A04_BLOOD_BLOOD_PRODUCT",
    "A05_BASIC_LIFE_SUPPORT",
    "A06_FIRE_SAFETY",
    "A07_INFECTION_PREVENTION",
    "A08_QUALITY_TRAINING",
    "A09_CYBERSECURITY_ASSESSMENT"
]

# ---------------- HEADER ----------------
col1, col2 = st.columns([1, 6])
with col1:
    st.image("MHPL Logo 2.png", width=90)

with col2:
    st.markdown("## MEDANTA HOSPITAL LUCKNOW")
    st.markdown("### Onboarding & Induction Dashboard")

st.divider()

# ---------------- SINGLE FORM ----------------
st.markdown("## Participant Registration")

with st.form("participant_form"):
    full_name = st.text_input("Full Name", value="")
    mobile = st.text_input("Mobile Number", value="")
    dob = st.date_input("Date of Birth")
    qualification = st.text_input("Qualification")
    category = st.selectbox(
        "Category",
        ["Administration", "Clinical", "Nursing", "Technical", "Support"]
    )
    sub_department = st.text_input("Sub-Department")

    submit = st.form_submit_button("Generate Induction Kit")

# ---------------- FORM SUBMIT ----------------
if submit:
    if not full_name or not mobile:
        st.error("Full Name and Mobile Number are mandatory.")
        st.stop()

    participant_id = f"{mobile}_{dob}"

    payload = {
        "action": "register_participant",
        "participant_id": participant_id,
        "full_name": full_name,
        "mobile": mobile,
        "category": category,
        "sub_department": sub_department
    }

    try:
        r = requests.post(APPS_SCRIPT_URL, json=payload, timeout=10)
        r.raise_for_status()
    except Exception as e:
        st.error("Registration failed. Please try again.")
        st.stop()

    st.success("Registration successful")

    st.markdown("## Your Induction Assessments")

    for a in ASSESSMENTS:
        params = urlencode({
            "pid": participant_id,
            "aid": a
        })
        link = f"https://medanta-assessment-tool.streamlit.app/?{params}"
        st.link_button(a.replace("_", " "), link)
