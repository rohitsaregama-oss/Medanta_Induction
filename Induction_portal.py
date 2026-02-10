import streamlit as st
import requests
import time
import random
from datetime import datetime, timedelta

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
st.set_page_config(page_title="Medanta Induction Portal", layout="wide")

API_URL = "https://script.google.com/macros/s/AKfycbwJwTeEhOPd1U2nxn0Mu9tc9WSZIkjyCLZ6XhiCwYPFovcTQF_gs4ys1cEbKZzRYpmP/exec"

TOTAL_ASSESSMENTS = 17
PASS_PERCENT = 80
GLOBAL_TIMER_MIN = 60
QUESTION_TIMER_SEC = 60

ASSESSMENT_ORDER = [f"A{str(i).zfill(2)}" for i in range(1, 18)]

# -------------------------------------------------
# HELPERS
# -------------------------------------------------
def api(payload):
    return requests.post(API_URL, json=payload, timeout=20).json()

def init_timer():
    if "global_end" not in st.session_state:
        st.session_state.global_end = datetime.now() + timedelta(minutes=GLOBAL_TIMER_MIN)

def global_time_left():
    return max(0, int((st.session_state.global_end - datetime.now()).total_seconds()))

def reset_question_timer():
    st.session_state.q_start = time.time()

def question_time_left():
    return max(0, QUESTION_TIMER_SEC - int(time.time() - st.session_state.q_start))

# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------
if "pid" not in st.session_state:
    st.session_state.pid = None
    st.session_state.idx = 0
    st.session_state.questions = []
    st.session_state.answers = {}
    st.session_state.completed = {}

# -------------------------------------------------
# EMBED UI (VISUAL ONLY)
# -------------------------------------------------
with open("ui.html", "r", encoding="utf-8") as f:
    st.components.v1.html(f.read(), height=900)

st.divider()

# -------------------------------------------------
# REGISTRATION
# -------------------------------------------------
if st.session_state.pid is None:
    st.subheader("Participant Registration")

    with st.form("register"):
        name = st.text_input("Full Name")
        mobile = st.text_input("Mobile Number")
        dob = st.date_input("Date of Birth")
        qual = st.text_input("Qualification")
        category = st.selectbox("Category", ["Administration", "Nursing", "Clinical", "Paramedical"])
        sub = st.text_input("Sub-Department")

        if st.form_submit_button("Generate Induction Kit"):
            res = api({
                "action": "register_participant",
                "full_name": name,
                "mobile": mobile,
                "dob": str(dob),
                "qualification": qual,
                "category": category,
                "sub_department": sub
            })

            st.session_state.pid = res["participant_id"]
            init_timer()
            st.rerun()

    st.stop()

# -------------------------------------------------
# GLOBAL TIMER DISPLAY
# -------------------------------------------------
gt = global_time_left()
st.warning(f"⏱ Global Time Remaining: {gt//60:02d}:{gt%60:02d}")

if gt <= 0:
    st.error("Global assessment time expired. Session closed.")
    st.stop()

# -------------------------------------------------
# ASSESSMENT ENGINE
# -------------------------------------------------
aid = ASSESSMENT_ORDER[st.session_state.idx]

st.subheader(f"Assessment {st.session_state.idx + 1} of {TOTAL_ASSESSMENTS}")
st.markdown(f"### Assessment ID: {aid}")

if not st.session_state.questions:
    data = api({
        "action": "get_questions",
        "assessment_id": aid
    })
    st.session_state.questions = data["questions"]
    st.session_state.answers = {}
    reset_question_timer()

# -------------------------------------------------
# QUESTIONS LOOP
# -------------------------------------------------
qt = question_time_left()
st.info(f"⏱ Question Time Remaining: {qt} sec")

if qt <= 0:
    st.warning("Time up for this question. Moving forward.")
    reset_question_timer()
    st.rerun()

for q in st.session_state.questions:
    st.markdown(f"**{q['question']}**")
    opts = {o["key"]: o["val"] for o in q["options"]}

    choice = st.radio(
        "",
        list(opts.keys()),
        format_func=lambda x: f"{x}. {opts[x]}",
        key=q["question_id"]
    )

    st.session_state.answers[q["question_id"]] = choice

# -------------------------------------------------
# SUBMIT
# -------------------------------------------------
if st.button("Submit Assessment"):
    result = api({
        "action": "submit_assessment",
        "participant_id": st.session_state.pid,
        "assessment_id": aid,
        "answers": [
            {"question_id": k, "selected": v}
            for k, v in st.session_state.answers.items()
        ]
    })

    if not result["passed"]:
        st.warning(
            "You did great however your score is below 80%. "
            "Concentrate hard, clarify your doubts and attempt again."
        )
        st.session_state.questions = []
        st.rerun()
    else:
        st.success(f"Passed with {result['score']}%")
        st.session_state.completed[aid] = result["score"]
        st.session_state.idx += 1
        st.session_state.questions = []

        if st.session_state.idx >= TOTAL_ASSESSMENTS:
            st.success("🎉 All assessments completed!")
            st.stop()

        st.rerun()
