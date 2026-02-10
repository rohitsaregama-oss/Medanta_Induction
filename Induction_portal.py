import streamlit as st
import uuid
import requests
from datetime import datetime

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Medanta Induction Portal",
    layout="wide"
)

BRIDGE_URL = "https://script.google.com/macros/s/AKfycbwJwTeEhOPd1U2nxn0Mu9tc9WSZIkjyCLZ6XhiCwYPFovcTQF_gs4ys1cEbKZzRYpmP/exec"

ASSESSMENTS = [
    ("A01", "HR Admin Process"),
    ("A02", "Second Victim"),
    ("A03", "Medication Safety"),
    ("A04", "Blood & Blood Product"),
    ("A05", "Basic Life Support"),
    ("A06", "Fire Safety"),
    ("A07", "Infection Prevention"),
    ("A08", "Quality Training"),
    ("A09", "IPSG"),
    ("A10", "Radiation Safety"),
    ("A11", "Facility Management Safety"),
    ("A12", "Emergency Codes"),
    ("A13", "Cybersecurity"),
    ("A14", "Workplace Violence"),
    ("A15", "EMR Training"),
    ("A16", "HIS Training"),
    ("A17", "Medical Documentation")
]

ASSESSMENT_BASE_URL = st.secrets.get(
    "assessment_base_url",
    "https://medanta-assessment-tool-3wjjkaj7zzzzwjwajcvcst.streamlit.app"
)

# ---------------- LOAD UI ----------------
with open("ui.html", "r", encoding="utf-8") as f:
    ui_html = f.read()

st.components.v1.html(ui_html, height=950, scrolling=True)

st.markdown("---")

# ---------------- SINGLE BACKEND CONTROL ----------------
st.subheader("Finalize Induction")

full_name = st.text_input("Confirm Full Name")
mobile = st.text_input("Confirm Mobile Number")

if st.button("Confirm & Generate Assessment Links"):

    if not full_name or not mobile:
        st.error("Full Name and Mobile Number are required.")
        st.stop()

    participant_id = f"MDT-{uuid.uuid4().hex[:8].upper()}"
    induction_date = datetime.now().strftime("%Y-%m-%d")

    # Save participant master
    payload = {
        "action": "register_participant",
        "participant_id": participant_id,
        "full_name": full_name,
        "mobile": mobile,
        "induction_date": induction_date
    }

    try:
        requests.post(BRIDGE_URL, json=payload, timeout=10)
    except Exception as e:
        st.error("Unable to save participant data.")
        st.stop()

    st.success(f"Participant Registered: {participant_id}")

    st.markdown("### Your Assessments")

    for aid, aname in ASSESSMENTS:
        assessment_link = (
            f"{ASSESSMENT_BASE_URL}"
            f"?pid={participant_id}"
            f"&aid={aid}"
            f"&qt=60"
            f"&tt=60"
            f"&admin=0"
        )

        st.markdown(
            f"🔗 **{aname}**  \n"
            f"[Start Assessment]({assessment_link})",
            unsafe_allow_html=True
        )
