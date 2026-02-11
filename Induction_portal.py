import streamlit as st
import requests
import time
import uuid

# ================= CONFIG =================
st.set_page_config(page_title="Medanta Induction Portal", layout="centered")

APP_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyTKLHY4be3-9n53oNnpKY--m5YdlloFI0szxEa1q96AsAlATnuufmWGa40k5xP-Gxz/exec"
PASS_PERCENTAGE = 80


# ================= SESSION INIT =================
def init_session():
    defaults = {
        "participant_id": str(uuid.uuid4()),
        "assessment_started": False,
        "questions": [],
        "q_index": 0,
        "score": 0,
        "attempt_number": 1,
        "start_time": None,
        "selected_assessment_code": "",
        "selected_assessment_name": ""
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session()


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


# ================= HELPER: CLEAN QUESTIONS =================
def clean_questions(raw_questions):
    cleaned = []
    for q in raw_questions:

        if not q.get("question"):
            continue

        options = {
            "A": q.get("option_a"),
            "B": q.get("option_b"),
            "C": q.get("option_c"),
            "D": q.get("option_d")
        }

        # Remove empty options
        options = {k: v for k, v in options.items() if v and str(v).strip() != ""}

        if len(options) < 2:
            continue

        correct = str(q.get("correct", "")).strip().upper()
        if correct not in options:
            continue

        cleaned.append({
            "question": str(q["question"]).strip(),
            "options": options,
            "correct": correct
        })

    return cleaned


# ================= PARTICIPANT FORM =================
if not st.session_state.assessment_started:

    name = st.text_input("Full Name")
    department = st.text_input("Department")
    role = st.text_input("Role / Designation")
    qualification = st.text_input("Qualification")
    dob = st.date_input("Date of Birth")
    email = st.text_input("Email")
    employee_id = st.text_input("Employee ID (Optional)")

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

    selected_name = st.selectbox("Select Assessment", list(assessment_map.keys()))
    selected_code = assessment_map[selected_name]

    if st.button("Start Assessment"):

        if not name or not department or not role or not email:
            st.error("Please complete required fields.")
            st.stop()

        # Save participant
        requests.post(APP_SCRIPT_URL, json={
            "action": "save_participant",
            "participant_id": st.session_state.participant_id,
            "name": name,
            "department": department,
            "role": role,
            "qualification": qualification,
            "dob": str(dob),
            "email": email,
            "employee_id": employee_id
        })

        # Load questions
        response = requests.get(
            APP_SCRIPT_URL,
            params={"assessment": selected_code},
            timeout=15
        )

        if response.status_code != 200:
            st.error("Unable to load assessment.")
            st.stop()

        data = response.json()

        if "questions" not in data:
            st.error("Invalid response from server.")
            st.stop()

        cleaned_questions = clean_questions(data["questions"])

        if not cleaned_questions:
            st.error("No valid questions found in Question_Bank.")
            st.stop()

        st.session_state.questions = cleaned_questions
        st.session_state.selected_assessment_code = selected_code
        st.session_state.selected_assessment_name = selected_name
        st.session_state.q_index = 0
        st.session_state.score = 0
        st.session_state.start_time = time.time()
        st.session_state.assessment_started = True
        st.rerun()


# ================= ASSESSMENT =================
else:

    questions = st.session_state.questions
    q_index = st.session_state.q_index
    total_q = len(questions)

    # ---------- COMPLETION ----------
    if q_index >= total_q:

        time_taken = int(time.time() - st.session_state.start_time)
        percentage = round((st.session_state.score / total_q) * 100, 2)
        passed = percentage >= PASS_PERCENTAGE

        requests.post(APP_SCRIPT_URL, json={
            "action": "save_assessment",
            "participant_id": st.session_state.participant_id,
            "assessment_id": st.session_state.selected_assessment_code,
            "assessment_name": st.session_state.selected_assessment_name,
            "attempt_number": st.session_state.attempt_number,
            "total_questions": total_q,
            "correct_answers": st.session_state.score,
            "score_percentage": percentage,
            "pass_fail": "PASS" if passed else "FAIL",
            "time_taken_seconds": time_taken
        })

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
        st.write(f"Final Score: {percentage}%")

        if st.button("Finish"):
            st.session_state.assessment_started = False
            st.rerun()

        st.stop()

    # ---------- QUESTION ----------
    current = questions[q_index]

    st.markdown(f"### Question {q_index + 1} of {total_q}")
    st.write(current["question"])

    choice = st.radio(
        "Select your answer",
        list(current["options"].keys()),
        format_func=lambda x: current["options"][x]
    )

    if st.button("Next"):
        if choice == current["correct"]:
            st.session_state.score += 1

        st.session_state.q_index += 1
        st.rerun()
