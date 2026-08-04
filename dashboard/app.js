// Dashboard logic: talks to the FastAPI backend at API_BASE.
const API_BASE = window.location.origin.includes("8080")
  ? "http://localhost:8000/api"   // dashboard served separately on :8080
  : "/api";                        // dashboard served by FastAPI itself at /dashboard

const healthBadge = document.getElementById("health-badge");
const runForm = document.getElementById("run-form");
const runBtn = document.getElementById("run-btn");
const resultCard = document.getElementById("result-card");
const runsTableBody = document.querySelector("#runs-table tbody");

const stages = {
  researcher: document.getElementById("stage-researcher"),
  writer: document.getElementById("stage-writer"),
  reviewer: document.getElementById("stage-reviewer"),
  coordinator: document.getElementById("stage-coordinator"),
};

async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`);
    const data = await res.json();
    if (data.ollama_reachable) {
      healthBadge.textContent = `● Online (${data.ollama_model})`;
      healthBadge.className = "badge badge-ok";
    } else {
      healthBadge.textContent = "● Ollama unreachable";
      healthBadge.className = "badge badge-bad";
    }
  } catch (e) {
    healthBadge.textContent = "● Backend unreachable";
    healthBadge.className = "badge badge-bad";
  }
}

function resetPipeline() {
  Object.values(stages).forEach((el) => el.classList.remove("active", "done"));
}

function animatePipeline() {
  const order = ["researcher", "writer", "reviewer", "coordinator"];
  let i = 0;
  resetPipeline();
  const interval = setInterval(() => {
    if (i > 0) stages[order[i - 1]].classList.replace("active", "done");
    if (i < order.length) {
      stages[order[i]].classList.add("active");
      i++;
    } else {
      clearInterval(interval);
    }
  }, 700);
  return interval;
}

runForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const topic = document.getElementById("topic").value.trim();
  const max_revisions = parseInt(document.getElementById("max_revisions").value, 10);
  if (!topic) return;

  runBtn.disabled = true;
  runBtn.textContent = "Running...";
  const pipelineTimer = animatePipeline();

  try {
    const res = await fetch(`${API_BASE}/workflow/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic, max_revisions }),
    });
    const data = await res.json();

    clearInterval(pipelineTimer);
    Object.values(stages).forEach((el) => el.classList.replace("active", "done"));

    resultCard.style.display = "block";
    document.getElementById("out-research").textContent = data.research_notes || "—";
    document.getElementById("out-draft").textContent = data.draft || "—";
    document.getElementById("out-feedback").textContent = data.review_feedback || "None (approved)";
    document.getElementById("out-final").textContent = data.final_output || "—";
    document.getElementById("out-meta").textContent =
      `Run ID: ${data.run_id} | Status: ${data.status} | Revisions: ${data.revision_count}`;

    loadRuns();
  } catch (err) {
    alert("Workflow run failed: " + err);
  } finally {
    runBtn.disabled = false;
    runBtn.textContent = "▶ Run Workflow";
  }
});

async function loadRuns() {
  try {
    const res = await fetch(`${API_BASE}/workflow`);
    const runs = await res.json();
    runsTableBody.innerHTML = "";
    runs.forEach((r) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `<td>${r.run_id}</td><td>${r.status}</td>`;
      runsTableBody.appendChild(tr);
    });
  } catch (e) {
    console.error("Failed to load runs", e);
  }
}

document.getElementById("refresh-runs").addEventListener("click", loadRuns);

document.getElementById("trigger-daily").addEventListener("click", async () => {
  const msg = document.getElementById("daily-msg");
  msg.textContent = "Triggering...";
  try {
    const res = await fetch(`${API_BASE}/automation/run-daily-now`, { method: "POST" });
    const data = await res.json();
    msg.textContent = data.message;
  } catch (e) {
    msg.textContent = "Failed to trigger daily task.";
  }
});

checkHealth();
loadRuns();
setInterval(checkHealth, 15000);
