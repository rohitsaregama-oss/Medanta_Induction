import streamlit as st
import requests
import time

# ================= CONFIG =================
st.set_page_config(page_title="Medanta Induction Portal", layout="centered")

APP_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwHn3NT6p3IaSjxjREH6Fly0eYhVn-vJOug0uzcclLCGJ8FSHQypzNgPkZWCbxE8maN/exec"

# ================= SESSION =================
if "started" not in st.session_state:
    st.session_state.started = False
if "questions" not in st.session_state:
    st.session_state.questions = []
if "q_index" not in st.session_state:
    st.session_state.q_index = 0
if "score" not in st.session_state:
    st.session_state.score = 0

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

# ================= START SCREEN =================
if not st.session_state.started:

    selected_name = st.selectbox("Select Assessment", list(assessment_map.keys()))

    if st.button("Start Assessment"):

        selected_id = assessment_map[selected_name]

        try:
            response = requests.get(
                APP_SCRIPT_URL,
                params={"assessment": selected_id},
                timeout=15
            )

            data = response.json()

        except Exception as e:
            st.error("Unable to load assessment.")
            st.stop()

        if "questions" not in data or not data["questions"]:
            st.error("No questions found.")
            st.stop()

        st.session_state.questions = data["questions"]
        st.session_state.started = True
        st.session_state.q_index = 0
        st.session_state.score = 0
        st.rerun()

# ================= QUESTION SCREEN =================
else:

    questions = st.session_state.questions
    q_index = st.session_state.q_index
    total = len(questions)

    if q_index >= total:

        percentage = round((st.session_state.score / total) * 100, 2)

        st.success("Assessment Completed ✅")
        st.write(f"Score: {percentage}%")

        if st.button("Restart"):
            st.session_state.started = False
            st.rerun()

        st.stop()

    q = questions[q_index]

    st.markdown(f"### Question {q_index + 1} of {total}")
    st.write(q.get("question", "Question Missing"))

    # Build safe options dictionary
    options = {}
    for key in ["A", "B", "C", "D"]:
        text = q.get(f"option_{key.lower()}", "")
        if text and str(text).strip() != "":
            options[key] = text

    if not options:
        st.error("Invalid question format.")
        st.stop()

    choice = st.radio(
        "Select your answer",
        list(options.keys()),
        format_func=lambda x: options[x]
    )

    if st.button("Next"):

        correct = str(q.get("correct", "")).strip().upper()

        if choice == correct:
            st.session_state.score += 1

        st.session_state.q_index += 1
        st.rerun()
