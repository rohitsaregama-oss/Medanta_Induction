import streamlit as st
import requests
import time
from datetime import datetime, timedelta
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

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

DISCLAIMER_TEXT = (
    "This is an assessment preview strictly for internal purposes. "
    "Sharing of this document outside of Medanta Hospital, Lucknow "
    "for any other purpose is strictly Prohibited."
)

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
    st.session_state.final_scores = {}

# -------------------------------------------------
# ADMIN MODE (PHASE 4)
# -------------------------------------------------
query = st.query_params
ADMIN_MODE = query.get("admin") == "1"

if ADMIN_MODE:
    st.title("🛡 Admin Dashboard")
    data = api({"action": "admin_summary"})
    for row in data.get("participants", []):
        st.write(row)
    st.stop()

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
            st.session_state.participant_name = name
            init_timer()
            st.rerun()

    st.stop()

# -------------------------------------------------
# GLOBAL TIMER
# -------------------------------------------------
gt = global_time_left()
st.warning(f"⏱ Global Time Remaining: {gt//60:02d}:{gt%60:02d}")

if gt <= 0:
    st.error("Global assessment time expired. Session closed.")
    st.stop()

# -------------------------------------------------
# ASSESSMENT ENGINE
# -------------------------------------------------
if st.session_state.idx < TOTAL_ASSESSMENTS:
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

    qt = question_time_left()
    st.info(f"⏱ Question Time Remaining: {qt} sec")

    if qt <= 0:
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
            st.session_state.completed[aid] = True
            st.session_state.final_scores[aid] = result["score"]
            st.session_state.idx += 1
            st.session_state.questions = []
            st.rerun()

# -------------------------------------------------
# PHASE 3: FINAL MARKSHEET
# -------------------------------------------------
if st.session_state.idx >= TOTAL_ASSESSMENTS:
    st.success("🎉 All assessments completed successfully!")

    avg_score = round(sum(st.session_state.final_scores.values()) / TOTAL_ASSESSMENTS, 2)
    st.markdown(f"### Final Score: **{avg_score}%**")

    if st.button("Download Final Marksheet"):
        gate = api({
            "action": "generate_marksheet",
            "participant_id": st.session_state.pid
        })

        if gate["status"] == "blocked":
            st.error("Download limit reached (maximum 3 downloads). Please contact HR.")
        else:
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            width, height = A4

            # Header
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height - 50, "MEDANTA HOSPITAL, LUCKNOW")

            c.setFont("Helvetica", 12)
            c.drawString(50, height - 80, "Induction Assessment – Final Marksheet")

            c.drawString(50, height - 110, f"Participant ID: {st.session_state.pid}")
            c.drawString(50, height - 130, f"Name: {st.session_state.participant_name}")
            c.drawString(50, height - 150, f"Date: {datetime.now().strftime('%d-%m-%Y')}")

            y = height - 190
            c.setFont("Helvetica", 11)

            for aid, score in st.session_state.final_scores.items():
                c.drawString(50, y, f"{aid} : {score}%")
                y -= 16

            c.drawString(50, y - 10, f"Final Score: {avg_score}%")

            # Watermark
            c.setFont("Helvetica-Oblique", 40)
            c.setFillGray(0.9)
            c.drawCentredString(width / 2, height / 2, "MEDANTA")

            # Disclaimer
            c.setFillGray(0)
            c.setFont("Helvetica-Oblique", 9)
            c.drawString(50, 40, DISCLAIMER_TEXT)

            c.showPage()
            c.save()
            buffer.seek(0)

            st.download_button(
                "Download PDF",
                buffer,
                file_name="Medanta_Induction_Marksheet.pdf",
                mime="application/pdf"
            )
