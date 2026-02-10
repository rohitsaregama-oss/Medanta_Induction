import streamlit as st
import uuid
import requests
from datetime import datetime

st.set_page_config(
    page_title="Medanta Induction Portal",
    layout="wide"
)

# ---------------- CONFIG ----------------
BRIDGE_URL = "https://script.google.com/macros/s/AKfycbwJwTeEhOPd1U2nxn0Mu9tc9WSZIkjyCLZ6XhiCwYPFovcTQF_gs4ys1cEbKZzRYpmP/exec"

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
    ("A10", "Radiation Safety"),
    ("A11", "Facility Management Safety"),
    ("A12", "Emergency Codes"),
    ("A13", "Cybersecurity"),
    ("A14", "Workplace Violence"),
    ("A15", "EMR Training"),
    ("A16", "HIS Training"),
    ("A17", "Medical Documentation")
]

ASSESSMENT_BASE_URL = "https://medanta-assessment-tool-3wjjkaj7zzzzwjwajcvcst.streamlit.app"

# ---------------- LOAD HTML UI ----------------
with open("ui.html", "r", encoding="utf-8") as f:
    ui_html = f.read()

st.components.v1.html(ui_html, height=950, scrolling=True)

# ---------------- READ DATA FROM URL ----------------
params = st.query_params

if "fullName" in params and "mobile" in params:

    full_name = params.get("fullName")
    mobile = params.get("mobile")
    category = params.get("category", "")
    sub_dept = params.get("subDept", "")

    participant_id = f"MDT-{uuid.uuid4().hex[:8].upper()}"

    # Save to Google Sheet
    payload = {
        "action": "register_participant",
        "participant_id": participant_id,
        "full_name": full_name,
        "mobile": mobile,
        "category": category,
        "sub_department": sub_dept,
        "timestamp": datetime.now().isoformat()
    }

    try:
        requests.post(BRIDGE_URL, json=payload, timeout=10)
    except:
        st.error("Failed to save participant data.")
        st.stop()

    st.markdown("---")
    st.success(f"Participant ID: {participant_id}")

    st.markdown("### Assigned Assessments")

    for aid, name in ASSESSMENTS:
        link = (
            f"{ASSESSMENT_BASE_URL}"
            f"?pid={participant_id}"
            f"&aid={aid}"
            f"&qt=60"
            f"&tt=60"
            f"&admin=0"
        )

        st.markdown(f"🔗 **{name}**  \n[Start Assessment]({link})")
