import streamlit as st
import requests

# ================================
# CONFIG
# ================================
st.set_page_config(page_title="Medanta Induction Portal", layout="centered")

# 🔴 PUT YOUR REAL EXEC URL BELOW
APP_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyl0Nv81sr0xqKfiDyuDaAey_nOrj88qPggtUnbSDqK1OZKhbr4hctXf1bmCN80ECcn/exec"


# ================================
# HEADER
# ================================
st.markdown("""
<div style='background:linear-gradient(135deg,#c00,#800);
            padding:25px;border-radius:15px;color:white;margin-bottom:25px'>
<h2 style='margin:0'>MEDANTA HOSPITAL LUCKNOW</h2>
<p style='margin:0'>Onboarding & Induction Portal</p>
</div>
""", unsafe_allow_html=True)


# ================================
# SESSION INIT
# ================================
if "page" not in st.session_state:
    st.session_state.page = "form"

if "questions" not in st.session_state:
    st.session_state.questions = []

if "q_index" not in st.session_state:
    st.session_state.q_index = 0

if "score" not in st.session_state:
    st.session_state.score = 0


# ================================
# FORM PAGE
# ================================
if st.session_state.page == "form":

    name = st.text_input("Full Name")
    category = st.selectbox(
        "Category",
        ["Administration", "Nursing", "Doctor / Consultant", "Paramedical"]
    )

    assessment_map = {
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

    selected_label = st.selectbox("Select Assessment", list(assessment_map.keys()))
    selected_assessment = assessment_map[selected_label]

    if st.button("Start Assessment"):

        if not name.strip():
            st.warning("Please enter your name.")
            st.stop()

        try:
            response = requests.get(
                APP_SCRIPT_URL,
                params={"assessment": selected_assessment},
                timeout=15
            )

            if response.status_code != 200:
                st.error("Server error.")
                st.stop()

            data = response.json()

        except Exception as e:
            st.error("Connection failed.")
            st.write(e)
            st.stop()

        if not data.get("questions"):
            st.error("No questions found.")
            st.stop()

        st.session_state.questions = data["questions"]
        st.session_state.q_index = 0
        st.session_state.score = 0
        st.session_state.page = "assessment"
        st.rerun()


# ================================
# ASSESSMENT PAGE
# ================================
elif st.session_state.page == "assessment":

    questions = st.session_state.questions
    index = st.session_state.q_index
    total = len(questions)

    if index >= total:
        st.success("Assessment Completed")
        st.info(f"Score: {st.session_state.score} / {total}")

        if st.button("Return Home"):
            st.session_state.page = "form"
            st.session_state.questions = []
            st.session_state.q_index = 0
            st.session_state.score = 0
            st.rerun()

        st.stop()

    q = questions[index]

    st.markdown(f"### Question {index + 1} of {total}")
    st.write(q.get("question", "Question missing"))

    # Safe option handling
    options = {
        "A": str(q.get("option_a", "") or ""),
        "B": str(q.get("option_b", "") or ""),
        "C": str(q.get("option_c", "") or ""),
        "D": str(q.get("option_d", "") or "")
    }

    valid_options = [k for k, v in options.items() if v.strip() != ""]

    if not valid_options:
        st.error("Invalid question configuration.")
        st.stop()

    choice = st.radio(
        "Select your answer",
        valid_options,
        format_func=lambda x: options[x]
    )

    if st.button("Next"):

        if choice.upper() == str(q.get("correct", "")).upper():
            st.session_state.score += 1

        st.session_state.q_index += 1
        st.rerun()
