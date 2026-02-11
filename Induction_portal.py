import streamlit as st
import requests
import time
import uuid

# ================= CONFIG =================
APP_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzjQ78e_01wpVXn6xW7TQ58F3f1odAfFSTYmKFm-fGT4onixz7-bZEI9h9M_ceU0OL-/exec"
PASS_PERCENTAGE = 80

st.set_page_config(page_title="Medanta Induction Portal", layout="centered")

# ================= SAFE JSON REQUEST =================
def safe_get(url, params=None):
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Server error: {e}")
        return None

# ================= SESSION INIT =================
if "participant_id" not in st.session_state:
    st.session_state.participant_id = str(uuid.uuid4())

if "questions" not in st.session_state:
    st.session_state.questions = []

if "started" not in st.session_state:
    st.session_state.started = False

if "q_index" not in st.session_state:
    st.session_state.q_index = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "attempt" not in st.session_state:
    st.session_state.attempt = 1

if "start_time" not in st.session_state:
    st.session_state.start_time = None


# ================= HEADER =================
st.markdown("""
<div style='background:#b30000;padding:25px;border-radius:15px;color:white;text-align:center'>
<h2>MEDANTA HOSPITAL LUCKNOW</h2>
<p>Onboarding & Induction Portal</p>
</div>
""", unsafe_allow_html=True)

st.write("")

# ================= ASSESSMENT MAP =================
assessment_map = {
    "HR Admin Process": "A01",
    "Second Victim": "A02",
    "Medication Safety": "A03",
    "Blood & Blood Product Safety": "A04",
    "Basic Life Support": "A05",
    "Fire Safety": "A06",
    "Infection Prevention": "A07",
    "Quality Training": "A08",
    "IPSG": "A09",
    "Radiation Training": "A10",
    "Facility Management Safety": "A11",
    "Emergency Codes": "A12",
    "Cybersecurity": "A13",
    "Workplace Violence": "A14",
    "EMR Training": "A15",
    "HIS Training": "A16",
    "Medical Documentation": "A17"
}

# ================= FORM =================
if not st.session_state.started:

    name = st.text_input("Full Name")
    department = st.text_input("Department")
    role = st.text_input("Role / Designation")
    qualification = st.text_input("Qualification")
    dob = st.date_input("Date of Birth")
    email = st.text_input("Email")
    employee_id = st.text_input("Employee ID (Optional)")

    selected_name = st.selectbox(
        "Select Assessment",
        list(assessment_map.keys())
    )

    if st.button("Start Assessment"):

        if not name or not department or not role or not email:
            st.error("Please complete required fields.")
            st.stop()

        assessment_code = assessment_map[selected_name]

        data = safe_get(APP_SCRIPT_URL, {"assessment": assessment_code})

        if not data or "questions" not in data or not data["questions"]:
            st.error("Unable to load assessment questions.")
            st.stop()

        st.session_state.questions = data["questions"]
        st.session_state.selected_name = selected_name
        st.session_state.selected_code = assessment_code
        st.session_state.q_index = 0
        st.session_state.score = 0
        st.session_state.start_time = time.time()
        st.session_state.started = True
        st.rerun()


# ================= ASSESSMENT =================
else:

    questions = st.session_state.questions
    index = st.session_state.q_index
    total = len(questions)

    if index >= total:

        percentage = round((st.session_state.score / total) * 100, 2)
        passed = percentage >= PASS_PERCENTAGE

        if not passed:
            st.error(
                "You did great however the qualification criteria is yet not met. "
                "Score 80% to move on."
            )

            if st.button("Retake Assessment"):
                st.session_state.q_index = 0
                st.session_state.score = 0
                st.session_state.attempt += 1
                st.session_state.start_time = time.time()
                st.rerun()

            st.stop()

        st.success("Assessment Passed ✅")
        st.write(f"Final Score: {percentage}%")

        if st.button("Finish"):
            st.session_state.started = False
            st.rerun()

        st.stop()

    # ================= QUESTION =================
    q = questions[index]

    st.markdown(f"### Question {index + 1} of {total}")
    st.write(q.get("question", ""))

    options = {
        "A": q.get("option_a", ""),
        "B": q.get("option_b", ""),
        "C": q.get("option_c", ""),
        "D": q.get("option_d", "")
    }

    # filter empty options (prevents radio crash)
    valid_options = {k: v for k, v in options.items() if v}

    choice = st.radio(
        "Select your answer",
        list(valid_options.keys()),
        format_func=lambda x: valid_options[x]
    )

    if st.button("Next"):

        correct = q.get("correct", "").strip().upper()

        if choice == correct:
            st.session_state.score += 1

        st.session_state.q_index += 1
        st.rerun()
