"""HTML UI pages for prediction and metrics dashboard."""

from __future__ import annotations


def prediction_page_html() -> str:
    """Return the interactive prediction UI."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Churn Predictor</title>
  <style>
    :root {
      --bg: #f3efe4;
      --panel: rgba(255, 252, 246, 0.92);
      --ink: #132a23;
      --muted: #587064;
      --accent: #c45b2d;
      --accent-soft: #efc3a8;
      --line: rgba(19, 42, 35, 0.12);
      --good: #1f7a5d;
      --bad: #a63d40;
      --shadow: 0 18px 50px rgba(40, 51, 45, 0.12);
    }

    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(196, 91, 45, 0.18), transparent 25%),
        radial-gradient(circle at bottom right, rgba(31, 122, 93, 0.12), transparent 24%),
        linear-gradient(135deg, #f6f2e8 0%, #ede4d3 100%);
      min-height: 100vh;
    }

    .shell {
      width: min(1180px, calc(100% - 32px));
      margin: 28px auto;
      display: grid;
      grid-template-columns: 1.2fr 0.8fr;
      gap: 24px;
    }

    .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 24px;
      box-shadow: var(--shadow);
      backdrop-filter: blur(10px);
    }

    .hero {
      padding: 28px;
      margin-bottom: 20px;
      position: relative;
      overflow: hidden;
    }

    .hero::after {
      content: "";
      position: absolute;
      width: 220px;
      height: 220px;
      top: -40px;
      right: -50px;
      background: linear-gradient(135deg, rgba(196, 91, 45, 0.22), rgba(239, 195, 168, 0.1));
      border-radius: 50%;
    }

    h1 {
      margin: 0 0 10px;
      font-size: clamp(2.4rem, 4vw, 4.2rem);
      line-height: 0.96;
      letter-spacing: -0.04em;
      max-width: 540px;
      position: relative;
      z-index: 1;
    }

    .subhead {
      max-width: 620px;
      margin: 0;
      color: var(--muted);
      font-size: 1rem;
      line-height: 1.6;
      position: relative;
      z-index: 1;
    }

    .nav {
      display: flex;
      gap: 12px;
      margin-top: 18px;
      position: relative;
      z-index: 1;
    }

    .nav a, button {
      border: 0;
      border-radius: 999px;
      padding: 12px 18px;
      font-size: 0.95rem;
      cursor: pointer;
      text-decoration: none;
      transition: transform 160ms ease, opacity 160ms ease;
    }

    .nav a:hover, button:hover { transform: translateY(-1px); }

    .primary {
      background: var(--ink);
      color: #fff8f0;
    }

    .secondary {
      background: transparent;
      color: var(--ink);
      border: 1px solid var(--line);
    }

    .form-card { padding: 24px; }
    .grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px 16px;
    }

    label {
      display: block;
      font-size: 0.82rem;
      margin-bottom: 7px;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }

    input, select {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 13px 14px;
      background: rgba(255, 255, 255, 0.72);
      font-size: 0.98rem;
      color: var(--ink);
    }

    .sidebar {
      display: grid;
      gap: 20px;
      align-content: start;
    }

    .result-card, .notes-card {
      padding: 24px;
    }

    .pill {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      border-radius: 999px;
      background: rgba(196, 91, 45, 0.12);
      color: var(--accent);
      font-size: 0.85rem;
      margin-bottom: 16px;
    }

    .metric {
      margin: 0 0 14px;
    }

    .metric .value {
      font-size: 3.2rem;
      line-height: 1;
      letter-spacing: -0.05em;
      margin-bottom: 4px;
    }

    .metric .label {
      color: var(--muted);
      font-size: 0.95rem;
    }

    .verdict {
      border-radius: 18px;
      padding: 14px 16px;
      font-weight: 600;
      margin-top: 16px;
      background: rgba(31, 122, 93, 0.12);
      color: var(--good);
    }

    .verdict.bad {
      background: rgba(166, 61, 64, 0.12);
      color: var(--bad);
    }

    .status {
      min-height: 24px;
      margin-top: 14px;
      color: var(--muted);
      font-size: 0.95rem;
    }

    ul {
      padding-left: 18px;
      margin: 0;
      color: var(--muted);
      line-height: 1.6;
    }

    @media (max-width: 960px) {
      .shell { grid-template-columns: 1fr; }
      .grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="shell">
    <section>
      <div class="panel hero">
        <h1>Churn Scoring Workbench</h1>
        <p class="subhead">
          Reload the page to get a fresh synthetic customer profile, tweak the inputs,
          and score the customer through the production inference API.
        </p>
        <div class="nav">
          <button id="randomize" class="primary" type="button">Randomize Sample</button>
          <a href="/dashboard" class="secondary">Open Metrics Dashboard</a>
        </div>
      </div>

      <form id="predict-form" class="panel form-card">
        <div class="grid">
          <div><label for="Customer_Age">Customer Age</label><input id="Customer_Age" name="Customer_Age" type="number" min="18" max="100" /></div>
          <div><label for="Gender">Gender</label><select id="Gender" name="Gender"><option value="M">M</option><option value="F">F</option></select></div>
          <div><label for="Dependent_count">Dependent Count</label><input id="Dependent_count" name="Dependent_count" type="number" min="0" max="20" /></div>
          <div><label for="Education_Level">Education Level</label><select id="Education_Level" name="Education_Level"><option>Graduate</option><option>High School</option><option>College</option><option>Post-Graduate</option><option>Doctorate</option><option>Uneducated</option><option>Unknown</option></select></div>
          <div><label for="Marital_Status">Marital Status</label><select id="Marital_Status" name="Marital_Status"><option>Married</option><option>Single</option><option>Divorced</option><option>Unknown</option></select></div>
          <div><label for="Income_Category">Income Category</label><select id="Income_Category" name="Income_Category"><option>Less than $40K</option><option>$40K - $60K</option><option>$60K - $80K</option><option>$80K - $120K</option><option>$120K +</option><option>Unknown</option></select></div>
          <div><label for="Card_Category">Card Category</label><select id="Card_Category" name="Card_Category"><option>Blue</option><option>Silver</option><option>Gold</option><option>Platinum</option></select></div>
          <div><label for="Months_on_book">Months on Book</label><input id="Months_on_book" name="Months_on_book" type="number" min="0" max="120" /></div>
          <div><label for="Total_Relationship_Count">Relationship Count</label><input id="Total_Relationship_Count" name="Total_Relationship_Count" type="number" min="0" max="20" /></div>
          <div><label for="Months_Inactive_12_mon">Inactive Months</label><input id="Months_Inactive_12_mon" name="Months_Inactive_12_mon" type="number" min="0" max="12" /></div>
          <div><label for="Contacts_Count_12_mon">Contacts Count</label><input id="Contacts_Count_12_mon" name="Contacts_Count_12_mon" type="number" min="0" max="20" /></div>
          <div><label for="Credit_Limit">Credit Limit</label><input id="Credit_Limit" name="Credit_Limit" type="number" min="0" step="0.01" /></div>
          <div><label for="Total_Revolving_Bal">Revolving Balance</label><input id="Total_Revolving_Bal" name="Total_Revolving_Bal" type="number" min="0" step="0.01" /></div>
          <div><label for="Avg_Open_To_Buy">Avg Open To Buy</label><input id="Avg_Open_To_Buy" name="Avg_Open_To_Buy" type="number" min="0" step="0.01" /></div>
          <div><label for="Total_Amt_Chng_Q4_Q1">Amount Change Q4/Q1</label><input id="Total_Amt_Chng_Q4_Q1" name="Total_Amt_Chng_Q4_Q1" type="number" min="0" step="0.01" /></div>
          <div><label for="Total_Trans_Amt">Total Transaction Amount</label><input id="Total_Trans_Amt" name="Total_Trans_Amt" type="number" min="0" step="0.01" /></div>
          <div><label for="Total_Trans_Ct">Total Transaction Count</label><input id="Total_Trans_Ct" name="Total_Trans_Ct" type="number" min="0" /></div>
          <div><label for="Total_Ct_Chng_Q4_Q1">Count Change Q4/Q1</label><input id="Total_Ct_Chng_Q4_Q1" name="Total_Ct_Chng_Q4_Q1" type="number" min="0" step="0.01" /></div>
          <div><label for="Avg_Utilization_Ratio">Utilization Ratio</label><input id="Avg_Utilization_Ratio" name="Avg_Utilization_Ratio" type="number" min="0" max="1" step="0.01" /></div>
        </div>
        <div class="nav" style="margin-top: 20px;">
          <button class="primary" type="submit">Score Customer</button>
          <button id="reset-defaults" class="secondary" type="button">Regenerate Defaults</button>
        </div>
        <div id="status" class="status"></div>
      </form>
    </section>

    <aside class="sidebar">
      <section class="panel result-card">
        <div class="pill">Live prediction output</div>
        <div class="metric">
          <div id="probability-value" class="value">0.0000</div>
          <div class="label">Predicted churn probability</div>
        </div>
        <div class="metric">
          <div id="prediction-value" class="value">0</div>
          <div class="label">Binary prediction</div>
        </div>
        <div id="verdict" class="verdict">Low churn risk</div>
      </section>

      <section class="panel notes-card">
        <div class="pill">How to use</div>
        <ul>
          <li>Reload the page to start with a new sample customer.</li>
          <li>Edit any field and click <strong>Score Customer</strong>.</li>
          <li>Open the dashboard to watch request counts, latency, and prediction mix update live.</li>
        </ul>
      </section>
    </aside>
  </div>

  <script>
    const categoricalChoices = {
      Gender: ["M", "F"],
      Education_Level: ["Graduate", "High School", "College", "Post-Graduate", "Doctorate", "Uneducated", "Unknown"],
      Marital_Status: ["Married", "Single", "Divorced", "Unknown"],
      Income_Category: ["Less than $40K", "$40K - $60K", "$60K - $80K", "$80K - $120K", "$120K +", "Unknown"],
      Card_Category: ["Blue", "Silver", "Gold", "Platinum"],
    };

    function pick(list) {
      return list[Math.floor(Math.random() * list.length)];
    }

    function randomInt(min, max) {
      return Math.floor(Math.random() * (max - min + 1)) + min;
    }

    function randomFloat(min, max, digits = 2) {
      return Number((Math.random() * (max - min) + min).toFixed(digits));
    }

    function buildRandomPayload() {
      const creditLimit = randomFloat(1500, 30000, 2);
      const revolvingBal = randomFloat(0, creditLimit * 0.85, 2);
      return {
        Customer_Age: randomInt(26, 72),
        Gender: pick(categoricalChoices.Gender),
        Dependent_count: randomInt(0, 5),
        Education_Level: pick(categoricalChoices.Education_Level),
        Marital_Status: pick(categoricalChoices.Marital_Status),
        Income_Category: pick(categoricalChoices.Income_Category),
        Card_Category: pick(categoricalChoices.Card_Category),
        Months_on_book: randomInt(12, 60),
        Total_Relationship_Count: randomInt(1, 6),
        Months_Inactive_12_mon: randomInt(0, 6),
        Contacts_Count_12_mon: randomInt(0, 6),
        Credit_Limit: creditLimit,
        Total_Revolving_Bal: revolvingBal,
        Avg_Open_To_Buy: Number((creditLimit - revolvingBal).toFixed(2)),
        Total_Amt_Chng_Q4_Q1: randomFloat(0.2, 2.2, 2),
        Total_Trans_Amt: randomFloat(500, 12000, 2),
        Total_Trans_Ct: randomInt(10, 120),
        Total_Ct_Chng_Q4_Q1: randomFloat(0.1, 2.5, 2),
        Avg_Utilization_Ratio: randomFloat(0.01, 0.99, 2),
      };
    }

    function populateForm(payload) {
      Object.entries(payload).forEach(([key, value]) => {
        document.getElementById(key).value = value;
      });
    }

    function readForm() {
      const form = document.getElementById("predict-form");
      const data = new FormData(form);
      return {
        Customer_Age: Number(data.get("Customer_Age")),
        Gender: data.get("Gender"),
        Dependent_count: Number(data.get("Dependent_count")),
        Education_Level: data.get("Education_Level"),
        Marital_Status: data.get("Marital_Status"),
        Income_Category: data.get("Income_Category"),
        Card_Category: data.get("Card_Category"),
        Months_on_book: Number(data.get("Months_on_book")),
        Total_Relationship_Count: Number(data.get("Total_Relationship_Count")),
        Months_Inactive_12_mon: Number(data.get("Months_Inactive_12_mon")),
        Contacts_Count_12_mon: Number(data.get("Contacts_Count_12_mon")),
        Credit_Limit: Number(data.get("Credit_Limit")),
        Total_Revolving_Bal: Number(data.get("Total_Revolving_Bal")),
        Avg_Open_To_Buy: Number(data.get("Avg_Open_To_Buy")),
        Total_Amt_Chng_Q4_Q1: Number(data.get("Total_Amt_Chng_Q4_Q1")),
        Total_Trans_Amt: Number(data.get("Total_Trans_Amt")),
        Total_Trans_Ct: Number(data.get("Total_Trans_Ct")),
        Total_Ct_Chng_Q4_Q1: Number(data.get("Total_Ct_Chng_Q4_Q1")),
        Avg_Utilization_Ratio: Number(data.get("Avg_Utilization_Ratio")),
      };
    }

    function renderResult(result) {
      const probability = Number(result.probability);
      const verdict = document.getElementById("verdict");
      document.getElementById("prediction-value").textContent = result.prediction;
      document.getElementById("probability-value").textContent = probability.toFixed(4);
      if (result.prediction === 1) {
        verdict.textContent = "Elevated churn risk";
        verdict.classList.add("bad");
      } else {
        verdict.textContent = "Low churn risk";
        verdict.classList.remove("bad");
      }
    }

    async function scoreCustomer(payload) {
      const status = document.getElementById("status");
      status.textContent = "Scoring customer through /predict...";
      const response = await fetch("/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Prediction failed.");
      }
      renderResult(data);
      status.textContent = "Prediction complete.";
    }

    document.getElementById("predict-form").addEventListener("submit", async (event) => {
      event.preventDefault();
      try {
        await scoreCustomer(readForm());
      } catch (error) {
        document.getElementById("status").textContent = error.message;
      }
    });

    function refreshDefaults() {
      populateForm(buildRandomPayload());
      document.getElementById("status").textContent = "Loaded a fresh sample profile.";
    }

    document.getElementById("randomize").addEventListener("click", refreshDefaults);
    document.getElementById("reset-defaults").addEventListener("click", refreshDefaults);

    refreshDefaults();
  </script>
</body>
</html>
"""


def dashboard_page_html() -> str:
    """Return the live online-serving metrics dashboard."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Serving Metrics Dashboard</title>
  <style>
    :root {
      --bg: #f8f4ea;
      --panel: rgba(255, 255, 255, 0.84);
      --ink: #16221f;
      --muted: #657570;
      --accent: #8b3d1f;
      --highlight: #d06c3c;
      --good: #226b57;
      --bad: #8f2d2d;
      --line: rgba(22, 34, 31, 0.1);
    }

    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Trebuchet MS", "Gill Sans", sans-serif;
      color: var(--ink);
      background:
        linear-gradient(180deg, rgba(208, 108, 60, 0.08), transparent 18%),
        linear-gradient(135deg, #f5efdf, #f1e8d2);
      min-height: 100vh;
    }

    .wrap {
      width: min(1200px, calc(100% - 28px));
      margin: 26px auto 34px;
    }

    .topbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      margin-bottom: 18px;
    }

    .topbar h1 {
      margin: 0;
      font-size: clamp(2rem, 4vw, 3.6rem);
      letter-spacing: -0.05em;
    }

    .topbar a {
      text-decoration: none;
      color: var(--ink);
      border: 1px solid var(--line);
      padding: 11px 16px;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.55);
    }

    .grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 16px;
    }

    .card {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 22px;
      padding: 20px;
      box-shadow: 0 16px 44px rgba(56, 60, 56, 0.08);
      backdrop-filter: blur(8px);
    }

    .kpi {
      font-size: 2.4rem;
      line-height: 1;
      letter-spacing: -0.05em;
      margin: 12px 0 6px;
    }

    .label {
      color: var(--muted);
      font-size: 0.88rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }

    .wide {
      grid-column: span 2;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 10px;
    }

    th, td {
      text-align: left;
      padding: 10px 0;
      border-bottom: 1px solid var(--line);
      font-size: 0.95rem;
    }

    .muted { color: var(--muted); }
    .ok { color: var(--good); }
    .bad { color: var(--bad); }

    @media (max-width: 980px) {
      .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }

    @media (max-width: 680px) {
      .grid { grid-template-columns: 1fr; }
      .wide { grid-column: span 1; }
      .topbar { flex-direction: column; align-items: flex-start; }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="topbar">
      <div>
        <h1>Serving Metrics Dashboard</h1>
        <div class="muted">Auto-refreshing online inference telemetry for the churn API.</div>
      </div>
      <a href="/">Back to Predictor</a>
    </div>

    <div class="grid">
      <section class="card"><div class="label">Total Requests</div><div id="total_requests" class="kpi">0</div><div class="muted">All /predict calls since app start</div></section>
      <section class="card"><div class="label">Success Rate</div><div id="success_rate" class="kpi">0%</div><div class="muted">Successful predictions / total requests</div></section>
      <section class="card"><div class="label">Average Latency</div><div id="avg_latency_ms" class="kpi">0 ms</div><div class="muted">Mean response time</div></section>
      <section class="card"><div class="label">P95 Latency</div><div id="p95_latency_ms" class="kpi">0 ms</div><div class="muted">95th percentile latency</div></section>

      <section class="card"><div class="label">Failed Requests</div><div id="failed_requests" class="kpi">0</div><div class="muted">Bad requests or model/API failures</div></section>
      <section class="card"><div class="label">Requests / Minute</div><div id="requests_per_minute" class="kpi">0</div><div class="muted">Observed request throughput</div></section>
      <section class="card"><div class="label">Average Probability</div><div id="avg_probability" class="kpi">0.0000</div><div class="muted">Average churn score of successful requests</div></section>
      <section class="card"><div class="label">Positive Prediction Rate</div><div id="positive_prediction_rate" class="kpi">0%</div><div class="muted">Share of requests predicted as churn</div></section>

      <section class="card wide">
        <div class="label">Recent Predictions</div>
        <table>
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Prediction</th>
              <th>Probability</th>
              <th>Latency</th>
            </tr>
          </thead>
          <tbody id="recent_predictions"></tbody>
        </table>
      </section>

      <section class="card wide">
        <div class="label">Last Error</div>
        <div id="last_error" class="kpi muted" style="font-size:1.2rem; line-height:1.4;">None</div>
        <div class="muted">Most recent non-successful /predict error captured by the service.</div>
      </section>
    </div>
  </div>

  <script>
    function formatPercent(value) {
      return `${(Number(value) * 100).toFixed(1)}%`;
    }

    function renderRows(rows) {
      const tbody = document.getElementById("recent_predictions");
      if (!rows.length) {
        tbody.innerHTML = '<tr><td colspan="4" class="muted">No predictions yet.</td></tr>';
        return;
      }

      tbody.innerHTML = rows.map((row) => `
        <tr>
          <td>${new Date(row.timestamp).toLocaleTimeString()}</td>
          <td class="${row.prediction === 1 ? "bad" : "ok"}">${row.prediction}</td>
          <td>${Number(row.probability).toFixed(4)}</td>
          <td>${Number(row.latency_ms).toFixed(2)} ms</td>
        </tr>
      `).join("");
    }

    async function refreshDashboard() {
      const response = await fetch("/metrics/summary");
      const data = await response.json();
      document.getElementById("total_requests").textContent = data.total_requests;
      document.getElementById("success_rate").textContent = formatPercent(data.success_rate);
      document.getElementById("avg_latency_ms").textContent = `${Number(data.avg_latency_ms).toFixed(2)} ms`;
      document.getElementById("p95_latency_ms").textContent = `${Number(data.p95_latency_ms).toFixed(2)} ms`;
      document.getElementById("failed_requests").textContent = data.failed_requests;
      document.getElementById("requests_per_minute").textContent = Number(data.requests_per_minute).toFixed(2);
      document.getElementById("avg_probability").textContent = Number(data.avg_probability).toFixed(4);
      document.getElementById("positive_prediction_rate").textContent = formatPercent(data.positive_prediction_rate);
      document.getElementById("last_error").textContent = data.last_error || "None";
      renderRows(data.recent_predictions);
    }

    refreshDashboard();
    setInterval(refreshDashboard, 3000);
  </script>
</body>
</html>
"""
