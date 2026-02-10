<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Medanta Induction Portal</title>

<style>
:root {
  --medanta-red:#c00;
  --bg:#f4f7f6;
}

body {
  font-family: "Segoe UI", Tahoma, sans-serif;
  background:#e9ecef;
  margin:0;
  padding:20px;
}

.container {
  max-width:1000px;
  margin:auto;
  background:white;
  border-radius:18px;
  box-shadow:0 15px 35px rgba(0,0,0,0.15);
  overflow:hidden;
  border-top:10px solid var(--medanta-red);
}

.header {
  display:flex;
  align-items:center;
  gap:20px;
  padding:20px 30px;
  background:linear-gradient(135deg,#c00,#800);
  color:white;
}

.header img {
  height:65px;
}

.header h1 {
  margin:0;
  font-size:24px;
}

.header p {
  margin:4px 0 0;
  font-size:14px;
  opacity:0.9;
}

.content {
  display:grid;
  grid-template-columns:1.2fr 1fr;
  gap:30px;
  padding:30px;
}

.section {
  background:white;
  border:1px solid #eee;
  border-radius:14px;
  padding:22px;
}

h3 {
  margin-top:0;
  color:var(--medanta-red);
  border-bottom:2px solid #f8d7da;
  padding-bottom:8px;
}

label {
  display:block;
  font-size:11px;
  font-weight:bold;
  margin-bottom:4px;
  text-transform:uppercase;
  color:#666;
}

input, select {
  width:100%;
  padding:10px;
  border-radius:8px;
  border:1.5px solid #ddd;
  font-size:14px;
  margin-bottom:12px;
}

.btn {
  width:100%;
  padding:14px;
  border:none;
  border-radius:10px;
  background:var(--medanta-red);
  color:white;
  font-size:16px;
  font-weight:bold;
  cursor:pointer;
}

.btn:hover {
  background:#a00;
}

.note {
  font-size:13px;
  color:#555;
  margin-top:10px;
}

</style>
</head>

<body>

<div class="container">

  <!-- HEADER -->
  <div class="header">
    <img src="mhpl_logo.png" alt="Medanta Logo">
    <div>
      <h1>MEDANTA HOSPITAL LUCKNOW</h1>
      <p>Onboarding & Induction Portal</p>
    </div>
  </div>

  <!-- MAIN CONTENT -->
  <div class="content">

    <!-- PARTICIPANT DETAILS -->
    <div class="section">
      <h3>Participant Details</h3>

      <label>Full Name</label>
      <input id="fullName" type="text" placeholder="Enter full name">

      <label>Mobile Number</label>
      <input id="contact" type="text" placeholder="10-digit mobile">

      <label>Date of Birth</label>
      <input id="dob" type="date">

      <label>Category</label>
      <select id="category">
        <option value="">Select</option>
        <option>Administration</option>
        <option>Nursing</option>
        <option>Clinical</option>
        <option>Paramedical</option>
      </select>

      <label>Sub-Department</label>
      <input id="subDept" type="text" placeholder="ICU / Radiology / Finance">
    </div>

    <!-- ASSESSMENT PANEL -->
    <div class="section">
      <h3>Assessments</h3>

      <label>Select Assessment</label>
      <select id="assessmentSelect">
        <option value="">-- Select Assessment --</option>
        <option value="A01">HR Admin Process</option>
        <option value="A02">Second Victim</option>
        <option value="A03">Medication Safety</option>
        <option value="A04">Blood & Blood Product Safety</option>
        <option value="A05">Basic Life Support</option>
        <option value="A06">Fire Safety</option>
        <option value="A07">Infection Prevention</option>
        <option value="A08">Quality Training</option>
        <option value="A09">IPSG</option>
        <option value="A10">Cybersecurity</option>
        <option value="A11">Facility Safety</option>
        <option value="A12">Emergency Codes</option>
        <option value="A13">Workplace Violence</option>
        <option value="A14">Radiation Safety</option>
        <option value="A15">EMR Training</option>
        <option value="A16">HIS Training</option>
        <option value="A17">Medical Documentation</option>
      </select>

      <button class="btn" onclick="launchAssessment()">Launch Assessment</button>

      <div class="note">
        • Minimum pass score: 80%<br>
        • Retry allowed until pass<br>
        • Assessments must be completed sequentially
      </div>
    </div>

  </div>
</div>

<!-- SCRIPT -->
<script>
const BRIDGE_URL =
  "https://script.google.com/macros/s/AKfycbwJwTeEhOPd1U2nxn0Mu9tc9WSZIkjyCLZ6XhiCwYPFovcTQF_gs4ys1cEbKZzRYpmP/exec";

function launchAssessment() {
  const name = document.getElementById("fullName").value;
  const mobile = document.getElementById("contact").value;
  const dob = document.getElementById("dob").value;
  const assessment = document.getElementById("assessmentSelect").value;

  if (!name || !mobile || !dob) {
    alert("Please fill participant details first");
    return;
  }

  if (!assessment) {
    alert("Please select an assessment");
    return;
  }

  const url =
    `${BRIDGE_URL}` +
    `?action=start_assessment` +
    `&name=${encodeURIComponent(name)}` +
    `&mobile=${encodeURIComponent(mobile)}` +
    `&dob=${encodeURIComponent(dob)}` +
    `&aid=${assessment}`;

  window.open(url, "_blank");
}
</script>

</body>
</html>
