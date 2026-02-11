import streamlit as st
import requests

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(page_title="Medanta Induction Portal", layout="centered")

APP_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxl6f2x62l_1D54ZdMPT9ZML3wMDEMIxzPi9tH8aK9v1FSbiiXJNmzFB4nIDrUjO37O/exec"

# =====================================================
# CUSTOM HEADER
# =====================================================
st.markdown("""
    <div style='background:linear-gradient(135deg,#c00,#800);
                padding:20px;border-radius:12px;color:white;
                margin-bottom:20px'>
        <h2 style='margin:0'>MEDANTA HOSPITAL LUCKNOW</h2>
        <p style='margin:0;font-size:14px'>Onboarding & Induction Portal</p>
    </div>
""", unsafe_allow_html=True)

# =====================================================
# SESSION STATE INIT
# =====================================================
if "page" not in st.session_state:
    st.session_state.page = "form"

if "questions" not in st.session_state:
    st.session_state.questions = []

if "q_index" not in st.session_state:
    st.session_state.q_index = 0

if "score" not in st.session_state:
    st.session_state.score = 0

# =====================================================
# PAGE 1 – DEMOGRAPHIC FORM
# =====================================================
if st.session_state.page == "form":

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("Full Name")
        contact = st.text_input("Contact Number")
        qualification = st.text_input("Qualification")

    with col2:
        category = st.selectbox(
            "Category",
            ["Administration", "Nursing", "Doctor / Consultant", "Paramedical"]
        )
        sub_department = st.text_input("Sub-Department")

        assessment = st.selectbox(
            "Select Assessment",
            {
                "A01 – HR Admin Process": "A01",
                "A02 – Second Victim": "A02",
                "A03 – Medication Safety": "A03",
                "A04 – Blood & Blood Product Safety": "A04",
                "A05 – Basic Life Support": "A05",
                "A06 – Fire Safety": "A06",
                "A07 – Infection Prevention": "A07",
                "A08 – Quality Training": "A08",
                "A09 – IPSG": "A09",
                "A10 – Radiation Training": "A10",
                "A11 – Facility Management Safety": "A11",
                "A12 – Emergency Codes": "A12",
                "A13 – Cybersecurity": "A13",
                "A14 – Workplace Violence": "A14",
                "A15 – EMR Training": "A15",
                "A16 – HIS Training": "A16",
                "A17 – Medical Documentation": "A17"
            }
        )

    st.markdown("")

    if st.button("Start Assessment", use_container_width=True):

        if not name:
            st.warning("Please enter Full Name.")
            st.stop()

        # Load Questions
        try:
            resp = requests.get(
                APP_SCRIPT_URL,
                params={"assessment": assessment},
                timeout=10
            )

            if resp.status_code != 200:
                st.error("Unable to connect to server.")
                st.stop()

            data = resp.json()

        except Exception:
            st.error("Server error. Try again later.")
            st.stop()

        if not data or "questions" not in data or not data["questions"]:
            st.error("No questions found for selected assessment.")
            st.stop()

        st.session_state.questions = data["questions"]
        st.session_state.q_index = 0
        st.session_state.score = 0
        st.session_state.page = "assessment"
        st.rerun()

# =====================================================
# PAGE 2 – ASSESSMENT ENGINE
# =====================================================
elif st.session_state.page == "assessment":

    questions = st.session_state.questions
    q_index = st.session_state.q_index
    total_q = len(questions)

    # Completion
    if q_index >= total_q:

        st.success("Assessment Completed Successfully")
        st.info(f"Final Score: {st.session_state.score} / {total_q}")

        if st.button("Return to Home"):
            st.session_state.page = "form"
            st.session_state.questions = []
            st.session_state.q_index = 0
            st.session_state.score = 0
            st.rerun()

        st.stop()

    # Display Question
    q = questions[q_index]

    st.markdown(f"### Question {q_index + 1} of {total_q}")
    st.markdown(q["question"])

    choice = st.radio(
        "Select your answer",
        ["A", "B", "C", "D"],
        format_func=lambda x: q[f"option_{x.lower()}"]
    )

    if st.button("Next", use_container_width=True):

        if choice.upper() == q["correct"].upper():
            st.session_state.score += 1

        st.session_state.q_index += 1
        st.rerun()
