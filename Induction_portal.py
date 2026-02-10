/***********************
 * CONFIG
 ***********************/
const PASS_PERCENT = 80;
const TOTAL_ASSESSMENTS = 17;

const SHEETS = {
  PARTICIPANTS: "Participants_Master",
  ASSESSMENTS: "Assessment_Master",
  QUESTIONS: "Question_Bank",
  RESPONSES: "Assessment_Responses",
  DOWNLOADS: "Marksheet_Download_Log"
};

const ASSESSMENT_ORDER = [
  "A01","A02","A03","A04","A05","A06","A07","A08","A09",
  "A10","A11","A12","A13","A14","A15","A16","A17"
];

/***********************
 * ENTRY POINT
 ***********************/
function doPost(e) {
  const data = JSON.parse(e.postData.contents || "{}");
  const action = data.action;

  switch (action) {
    case "register_participant": return registerParticipant(data);
    case "get_questions": return getQuestions(data);
    case "submit_assessment": return submitAssessment(data);
    case "check_eligibility": return checkEligibility(data);
    case "generate_marksheet": return generateMarksheet(data);
    case "admin_summary": return adminSummary();
    case "admin_override": return adminOverride(data);
    default:
      return respond({ status: "error", message: "Invalid action" });
  }
}

/***********************
 * UTILITIES
 ***********************/
function respond(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

function sheet(name) {
  return SpreadsheetApp.getActive().getSheetByName(name);
}

function now() {
  return new Date();
}

/***********************
 * 1️⃣ REGISTER PARTICIPANT
 ***********************/
function registerParticipant(d) {
  sheet(SHEETS.PARTICIPANTS).appendRow([
    d.participant_id,
    d.full_name,
    d.mobile,
    d.category || "",
    d.sub_department || "",
    "ACTIVE",
    now()
  ]);

  return respond({ status: "ok" });
}

/***********************
 * 2️⃣ ELIGIBILITY CHECK
 ***********************/
function checkEligibility(d) {
  const aid = d.assessment_id;
  const pid = d.participant_id;

  const index = ASSESSMENT_ORDER.indexOf(aid);
  if (index === -1) {
    return respond({ status: "error", message: "Invalid assessment" });
  }

  // First assessment always allowed
  if (index === 0) {
    return respond({ status: "allowed" });
  }

  const prevAid = ASSESSMENT_ORDER[index - 1];
  const best = getBestScore(pid, prevAid);

  if (best >= PASS_PERCENT) {
    return respond({ status: "allowed" });
  }

  return respond({
    status: "blocked",
    message: "Previous assessment not passed"
  });
}

/***********************
 * 3️⃣ FETCH QUESTIONS
 ***********************/
function getQuestions(d) {
  const rows = sheet(SHEETS.QUESTIONS).getDataRange().getValues();
  rows.shift();

  const questions = rows
    .filter(r => r[0] === d.assessment_id && r[9] === "YES")
    .map(r => ({
      question_id: r[2],
      question: r[3],
      options: shuffle([
        { key: "A", val: r[4] },
        { key: "B", val: r[5] },
        { key: "C", val: r[6] },
        { key: "D", val: r[7] }
      ]),
      correct: r[8]
    }));

  return respond({ status: "ok", questions });
}

/***********************
 * 4️⃣ SUBMIT ASSESSMENT
 ***********************/
function submitAssessment(d) {
  const pid = d.participant_id;
  const aid = d.assessment_id;
  const answers = d.answers;

  const qRows = sheet(SHEETS.QUESTIONS).getDataRange().getValues();
  let correct = 0;

  answers.forEach(a => {
    const q = qRows.find(r => r[2] === a.question_id);
    if (q && q[8] === a.selected) correct++;

    sheet(SHEETS.RESPONSES).appendRow([
      pid, aid, a.question_id, a.selected, q ? q[8] : "", now()
    ]);
  });

  const percent = Math.round((correct / answers.length) * 100);

  return respond({
    status: "ok",
    score: percent,
    passed: percent >= PASS_PERCENT,
    best_score: Math.max(percent, getBestScore(pid, aid))
  });
}

/***********************
 * 5️⃣ BEST SCORE LOGIC
 ***********************/
function getBestScore(pid, aid) {
  const rows = sheet(SHEETS.RESPONSES).getDataRange().getValues();
  let best = 0;

  rows.forEach(r => {
    if (r[0] === pid && r[1] === aid) {
      const score = r[6] || 0;
      if (score > best) best = score;
    }
  });

  return best;
}

/***********************
 * 6️⃣ MARKSHEET DOWNLOAD GATE
 ***********************/
function generateMarksheet(d) {
  const pid = d.participant_id;
  const rows = sheet(SHEETS.DOWNLOADS).getDataRange().getValues();
  const count = rows.filter(r => r[0] === pid).length;

  if (count >= 3) {
    return respond({ status: "blocked" });
  }

  sheet(SHEETS.DOWNLOADS).appendRow([
    pid, now(), "MARKSHEET_DOWNLOADED"
  ]);

  return respond({ status: "ok" });
}

/***********************
 * 7️⃣ ADMIN SUMMARY
 ***********************/
function adminSummary() {
  const rows = sheet(SHEETS.PARTICIPANTS).getDataRange().getValues();
  rows.shift();
  return respond({ status: "ok", participants: rows });
}

/***********************
 * 8️⃣ ADMIN OVERRIDE
 ***********************/
function adminOverride(d) {
  sheet(SHEETS.RESPONSES).appendRow([
    d.participant_id,
    d.assessment_id,
    "ADMIN_OVERRIDE",
    "PASS",
    "PASS",
    now(),
    100
  ]);

  return respond({ status: "ok" });
}

/***********************
 * SHUFFLE
 ***********************/
function shuffle(arr) {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}
