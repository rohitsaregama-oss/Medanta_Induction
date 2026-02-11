import streamlit as st
import requests
import time
import uuid

# ================= CONFIG =================
st.set_page_config(page_title="Medanta Induction Portal", layout="centered")

APP_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyTKLHY4be3-9n53oNnpKY--m5YdlloFI0szxEa1q96AsAlATnuufmWGa40k5xP-Gxz/exec"

PASS_PERCENTAGE = 80

# ================= SESSION INIT =================
if "participant_id" not in st.session_state:
    st.session_state.participant_id = str(uuid.uuid4())

if "assessment_started" not in st.session_state:
    st.session_state.assessment_started = False

if "questions" not in st.session_state:
    st.session_state.questions = []

if "q_index" not in st.session_state:
    st.session_state.q_index = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "attempt_number" not in st.session_state:
    st.session_state.attempt_number = 1

if "start_time" not in st.session_state:
    st.session_state.start_time = None


# ================= HEADER =================
st.markdown(
    """
    <div style='background:#b30000;padding:25px;border-radius:15px;color:white;text-align:center'>
        <h2>MEDANTA HOSPITAL LUCKNOW</h2>
        <p>Onboarding & Induction Portal</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.write("")

# ================= PARTICIPANT FORM =================
if not st.session_state.assessment_started:

    name = st.text_input("Full Name")
    department = st.text_input("Department")
    role = st.text_input("Role / Designation")
    qualification = st.text_input("Qualification")
    dob = st.date_input("Date of Birth")
    email = st.text_input("Email")
    employee_id = st.text_input("Employee ID (Optional)")

    assessment_list = [
        "A01","A02","A03","A04","A05","A06","A07",
        "A08","A09","A10","A11","A12","A13",
        "A14","A15","A16","A17"
    ]

    selected_assessment = st.selectbox("Select Assessment", assessment_list)

    if st.button("Start Assessment"):

        if not name or not department or not role or not email:
            st.error("Please complete required fields.")
            st.stop()

        # Save participant
        payload = {
            "action": "save_participant",
            "participant_id": st.session_state.participant_id,
            "name": name,
            "department": department,
            "role": role,
            "qualification": qualification,
            "dob": str(dob),
            "email": email,
            "employee_id": employee_id
        }

        try:
            requests.post(APP_SCRIPT_URL, json=payload, timeout=10)
        except:
            st.error("Unable to save participant.")
            st.stop()

        # Load Questions
        try:
            resp = requests.get(APP_SCRIPT_URL,
                                params={"assessment": selected_assessment},
                                timeout=15)
            data = resp.json()
        except:
            st.error("Unable to load assessment.")
            st.stop()

        if not data or "questions" not in data or not data["questions"]:
            st.error("No questions found for this assessment.")
            st.stop()

        st.session_state.questions = data["questions"]
        st.session_state.selected_assessment = selected_assessment
        st.session_state.q_index = 0
        st.session_state.score = 0
        st.session_state.start_time = time.time()
        st.session_state.assessment_started = True
        st.rerun()


# ================= ASSESSMENT SECTION =================
else:

    questions = st.session_state.questions
    q_index = st.session_state.q_index
    total_q = len(questions)

    if q_index >= total_q:

        time_taken = int(time.time() - st.session_state.start_time)
        percentage = round((st.session_state.score / total_q) * 100, 2)
        passed = percentage >= PASS_PERCENTAGE

        # Save assessment attempt
        payload = {
            "action": "save_assessment",
            "participant_id": st.session_state.participant_id,
            "assessment_id": st.session_state.selected_assessment,
            "assessment_name": st.session_state.selected_assessment,
            "attempt_number": st.session_state.attempt_number,
            "total_questions": total_q,
            "correct_answers": st.session_state.score,
            "score_percentage": percentage,
            "pass_fail": "PASS" if passed else "FAIL",
            "time_taken_seconds": time_taken
        }

        try:
            requests.post(APP_SCRIPT_URL, json=payload, timeout=10)
        except:
            st.error("Error saving assessment.")
            st.stop()

        if not passed:
            st.error(
                "You did great however the qualification criteria is yet not met. "
                "Score 80% to move on."
            )

            if st.button("Retake Assessment"):
                st.session_state.q_index = 0
                st.session_state.score = 0
                st.session_state.attempt_number += 1
                st.session_state.start_time = time.time()
                st.rerun()

            st.stop()

        st.success("Assessment Passed ✅")
        st.write(f"Score: {percentage}%")

        if st.button("Finish"):
            st.session_state.assessment_started = False
            st.rerun()

        st.stop()

    # Show Question
    q = questions[q_index]

    st.markdown(f"### Question {q_index + 1} of {total_q}")
    st.write(q.get("question", "Question Missing"))

    options = {
        "A": q.get("option_a", "Option Missing"),
        "B": q.get("option_b", "Option Missing"),
        "C": q.get("option_c", "Option Missing"),
        "D": q.get("option_d", "Option Missing")
    }

    choice = st.radio(
        "Select your answer",
        list(options.keys()),
        format_func=lambda x: options[x]
    )

    if st.button("Next"):

        correct_answer = str(q.get("correct", "")).strip().upper()

        if choice == correct_answer:
            st.session_state.score += 1

        st.session_state.q_index += 1
        st.rerun()
