import streamlit as st
import pandas as pd
import uuid
import random
from datetime import datetime
from io import BytesIO

import gspread
from google.oauth2.service_account import Credentials
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# ======================================================
# STREAMLIT CONFIG
# ======================================================
st.set_page_config(
    page_title="Medanta Induction Portal",
    layout="wide"
)

PASS_PERCENTAGE = 80
TOTAL_ASSESSMENTS = 17
SHEET_NAME = "Medanta_Induction_Assessments"

# ======================================================
# GOOGLE SHEETS AUTH
# ======================================================
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=SCOPES
)
gc = gspread.authorize(creds)
sh = gc.open(SHEET_NAME)

ws_participants = sh.worksheet("Participants_Master")
ws_questions = sh.worksheet("Question_Bank")
ws_assessment_master = sh.worksheet("Assessment_Master")
ws_responses = sh.worksheet("Assessment_Responses")
ws_downloads = sh.worksheet("Marksheet_Download_Log")

# ======================================================
# SESSION STATE
# ======================================================
if "participant_id" not in st.session_state:
    st.session_state.participant_id = None
if "current_assessment" not in st.session_state:
    st.session_state.current_assessment = None
if "participant_name" not in st.session_state:
    st.session_state.participant_name = None

# ======================================================
# EMBED YOUR EXISTING UI (UNCHANGED)
# ======================================================
with open("ui.html", "r", encoding="utf-8") as f:
    st.components.v1.html(f.read(), height=950)

st.divider()

# ======================================================
# PARTICIPANT REGISTRATION (BACKEND)
# ======================================================
st.subheader("Participant Registration")

with st.form("register_form"):
    full_name = st.text_input("Full Name")
    mobile = st.text_input("Mobile Number")
    dob = st.date_input("Date of Birth")
    qualification = st.text_input("Qualification")
    category = st.selectbox("Category", ["Administration", "Nursing", "Clinical", "Paramedical"])
    sub_dept = st.text_input("Sub Department")
    submit = st.form_submit_button("Generate Induction Kit")

if submit:
    participant_id = f"PID-{uuid.uuid4().hex[:8].upper()}"

    ws_participants.append_row([
        participant_id,
        full_name,
        mobile,
        dob.strftime("%Y-%m-%d"),
        qualification,
        category,
        sub_dept,
        datetime.now().date().isoformat(),
        datetime.now().time().strftime("%H:%M:%S"),
        "Active"
    ])

    st.session_state.participant_id = participant_id
    st.session_state.participant_name = full_name
    st.session_state.current_assessment = "A01"

    st.success(f"Induction started successfully. Participant ID: {participant_id}")

# ======================================================
# ASSESSMENT ENGINE
# ======================================================
def run_assessment(assessment_id):
    st.subheader(f"Assessment {assessment_id}")

    qdf = pd.DataFrame(ws_questions.get_all_records())
    qdf = qdf[
        (qdf["Assessment_ID"] == assessment_id) &
        (qdf["Active"] == "YES")
    ]

    user_answers = {}
    start_time = datetime.now()

    for _, row in qdf.iterrows():
        options = [
            ("A", str(row["Option_A"])),
            ("B", str(row["Option_B"])),
            ("C", str(row["Option_C"])),
            ("D", str(row["Option_D"]))
        ]
        random.shuffle(options)

        choice = st.radio(
            row["Question_Text"],
            options,
            format_func=lambda x: x[1],
            key=row["Question_ID"]
        )
        user_answers[row["Question_ID"]] = (choice[0], row["Correct_Option"])

    if st.button("Submit Assessment"):
        correct = sum(1 for v in user_answers.values() if v[0] == v[1])
        total = len(user_answers)
        score = round((correct / total) * 100, 2)
        status = "PASS" if score >= PASS_PERCENTAGE else "FAIL"
        time_taken = int((datetime.now() - start_time).total_seconds())

        # Attempt number
        existing = pd.DataFrame(ws_responses.get_all_records())
        prev = existing[
            (existing["Participant_ID"] == st.session_state.participant_id) &
            (existing["Assessment_ID"] == assessment_id)
        ]
        attempt_no = len(prev) + 1

        ws_responses.append_row([
            datetime.now().isoformat(),
            st.session_state.participant_id,
            assessment_id,
            qdf.iloc[0]["Assessment_Name"],
            attempt_no,
            total,
            correct,
            score,
            status,
            time_taken
        ])

        st.info(f"Your Score: {score}%")

        if status == "PASS":
            st.success("Assessment passed. Next assessment unlocked.")
            next_id = f"A{int(assessment_id[1:]) + 1:02d}"
            if int(next_id[1:]) <= TOTAL_ASSESSMENTS:
                st.session_state.current_assessment = next_id
            else:
                st.session_state.current_assessment = "COMPLETED"
        else:
            st.warning(
                "You did great however your score is below 80%. "
                "Concentrate hard, clarify your doubts and attempt again."
            )

# ======================================================
# RUN CURRENT ASSESSMENT
# ======================================================
if st.session_state.current_assessment and st.session_state.current_assessment not in ["COMPLETED"]:
    run_assessment(st.session_state.current_assessment)

# ======================================================
# FINAL MARKSHEET PDF
# ======================================================
def generate_marksheet(participant_id):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 800, "MEDANTA HOSPITAL, LUCKNOW")
    c.setFont("Helvetica", 11)
    c.drawString(50, 780, "Induction Assessment – Final Marksheet")

    c.drawString(50, 750, f"Participant ID: {participant_id}")
    c.drawString(50, 735, f"Name: {st.session_state.participant_name}")

    df = pd.DataFrame(ws_responses.get_all_records())
    df = df[df["Participant_ID"] == participant_id]

    y = 700
    c.setFont("Helvetica", 10)

    for aid in sorted(df["Assessment_ID"].unique()):
        row = df[(df["Assessment_ID"] == aid) & (df["Pass_Fail"] == "PASS")].iloc[0]
        c.drawString(
            50, y,
            f"{row['Assessment_Name']}  |  Attempts: {row['Attempt_Number']}  |  Score: {row['Score_Percentage']}%"
        )
        y -= 18

    c.setFont("Helvetica-Oblique", 9)
    c.drawString(
        50, 60,
        "This is an assessment preview strictly for internal purposes. "
        "Sharing of this document outside of Medanta Hospital, Lucknow "
        "for any other purpose is strictly prohibited."
    )

    c.save()
    buffer.seek(0)
    return buffer

# ======================================================
# DOWNLOAD LOGIC (MAX 3)
# ======================================================
if st.session_state.current_assessment == "COMPLETED":
    st.success("All 17 assessments completed successfully.")

    log_df = pd.DataFrame(ws_downloads.get_all_records())
    row = log_df[log_df["Participant_ID"] == st.session_state.participant_id]

    count = int(row["Download_Count"].values[0]) if not row.empty else 0

    if count < 3:
        if st.download_button(
            "⬇️ Download Final Assessment Marksheet (PDF)",
            generate_marksheet(st.session_state.participant_id),
            file_name="Medanta_Induction_Marksheet.pdf"
        ):
            if row.empty:
                ws_downloads.append_row([
                    st.session_state.participant_id,
                    st.session_state.participant_name,
                    1,
                    datetime.now().isoformat()
                ])
            else:
                idx = row.index[0] + 2
                ws_downloads.update_cell(idx, 3, count + 1)
                ws_downloads.update_cell(idx, 4, datetime.now().isoformat())
    else:
        st.error(
            "Download limit reached (3/3). "
            "Please contact HR for further assistance."
        )
