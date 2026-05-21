// ── Utility ───────────────────────────────────────────────────────
function fillExample(career, skills) {
    document.getElementById("careerInput").value = career;
    document.getElementById("skillsInput").value = skills;
    if (career && skills) analyze();
}

function showLoader() {
    document.getElementById("btn-text").classList.add("hidden");
    document.getElementById("btn-icon").classList.add("hidden");
    document.getElementById("btn-loader").classList.remove("hidden");
}

function hideLoader() {
    document.getElementById("btn-text").classList.remove("hidden");
    document.getElementById("btn-icon").classList.remove("hidden");
    document.getElementById("btn-loader").classList.add("hidden");
}

function formatNumber(n) {
    return n.toLocaleString("en-PK");
}

// ── Main Analyze ──────────────────────────────────────────────────
async function analyze() {
    const career = document.getElementById("careerInput").value.trim();
    const skills = document.getElementById("skillsInput").value.trim();

    if (!career || !skills) {
        alert("Please enter both a career goal and your current skills.");
        return;
    }

    showLoader();

    try {
        const response = await fetch("/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ career, skills })
        });
        const data = await response.json();
        hideLoader();
        renderResults(data);
    } catch (err) {
        hideLoader();
        showError("Something went wrong. Please try again.");
    }
}

// ── Render Results ────────────────────────────────────────────────
function renderResults(data) {
    const resultsSection = document.getElementById("results");
    resultsSection.classList.remove("hidden");

    setTimeout(() => {
        resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 100);

    if (data.error) {
        showError(data.error);
        hideReportElements();
        return;
    }

    document.getElementById("errorBox").classList.add("hidden");
    showReportElements();

    // Report Header
    document.getElementById("reportTitle").textContent = data.career;
    document.getElementById("reportBadge").textContent =
        data.match_pct >= 70 ? "Job Ready" :
        data.match_pct >= 40 ? "In Progress" : "Just Starting";

    // Metrics
    document.getElementById("matchScore").textContent = data.match_pct + "%";
    document.getElementById("gapScore").textContent   = data.gap_pct + "%";
    document.getElementById("avgSalary").textContent  = formatNumber(data.avg_salary);
    document.getElementById("totalJobs").textContent  = data.total_jobs;

    // Salary Range
    document.getElementById("salaryRange").innerHTML = `
        <div class="salary-box">
            <div class="salary-box-label">Minimum</div>
            <div class="salary-box-value green">${formatNumber(data.min_salary)}</div>
            <div class="metric-sub">PKR / month</div>
        </div>
        <div class="salary-box">
            <div class="salary-box-label">Average</div>
            <div class="salary-box-value blue">${formatNumber(data.avg_salary)}</div>
            <div class="metric-sub">PKR / month</div>
        </div>
        <div class="salary-box">
            <div class="salary-box-label">Maximum</div>
            <div class="salary-box-value white">${formatNumber(data.max_salary)}</div>
            <div class="metric-sub">PKR / month</div>
        </div>
    `;

    // City Demand
    const cityDiv  = document.getElementById("cityDemand");
    const maxCount = Math.max(...Object.values(data.locations));
    cityDiv.innerHTML = "";
    Object.entries(data.locations).forEach(([city, count]) => {
        const pct = Math.round((count / maxCount) * 100);
        cityDiv.innerHTML += `
            <div class="city-row">
                <div class="city-row-top">
                    <span class="city-name">${city}</span>
                    <span class="city-count">${count} jobs</span>
                </div>
                <div class="bar-bg">
                    <div class="bar-fill" style="width:${pct}%"></div>
                </div>
            </div>
        `;
    });

    // Matched Skills
    document.getElementById("matchedTags").innerHTML =
        data.matched.length > 0
        ? data.matched.map(s => `<span class="tag tag-green">${s}</span>`).join("")
        : `<span style="color:var(--sub);font-size:0.85rem;">No matching skills. Start with the learning path below.</span>`;

    // Missing Skills
    document.getElementById("missingTags").innerHTML =
        data.missing.length > 0
        ? data.missing.map(s => `<span class="tag tag-red">${s}</span>`).join("")
        : `<span style="color:var(--accent2);font-size:0.85rem;font-weight:600;">You have all required skills!</span>`;

    // Irrelevant Warning
    const warningPanel = document.getElementById("warningPanel");
    if (data.irrelevant && data.irrelevant.length > 0) {
        warningPanel.classList.remove("hidden");
        document.getElementById("warningText").textContent =
            `The following skills are not required for ${data.career}. Redirect your learning time toward missing skills.`;
        document.getElementById("irrelevantTags").innerHTML =
            data.irrelevant.map(s => `<span class="tag tag-yellow">${s}</span>`).join("");
    } else {
        warningPanel.classList.add("hidden");
    }

    // Low Demand Warning
    const lowDemandPanel = document.getElementById("lowDemandPanel");
    if (data.low_demand && data.low_demand.length > 0) {
        lowDemandPanel.classList.remove("hidden");
        document.getElementById("lowDemandText").textContent =
            `These skills exist in the ${data.career} market but have low demand. Good to know, but not a priority.`;
        document.getElementById("lowDemandTags").innerHTML =
            data.low_demand.map(s => `<span class="tag tag-blue">${s}</span>`).join("");
    } else {
        lowDemandPanel.classList.add("hidden");
    }

    // Learning Path
    const lpDiv     = document.getElementById("learningPath");
    const maxDemand = data.learning_path.length > 0
                      ? data.learning_path[0].demand_count : 1;

    document.getElementById("learningSubtitle").textContent =
        `Skills ranked by how many ${data.career} jobs require them. Learn in this exact order for maximum employability.`;

    lpDiv.innerHTML = "";

    if (data.learning_path.length === 0) {
        lpDiv.innerHTML = `<div style="color:var(--accent2);font-size:0.9rem;font-weight:600;padding:16px 0;">No missing skills — you are fully job ready!</div>`;
    } else {
        data.learning_path.forEach((item, index) => {
            const barWidth = Math.round((item.demand_count / maxDemand) * 100);
            lpDiv.innerHTML += `
                <div class="lp-item">
                    <div class="lp-left">
                        <div class="lp-rank">${index + 1}</div>
                        <div>
                            <div class="lp-skill">${item.skill}</div>
                            <div class="lp-bar-wrap">
                                <div class="lp-bar" style="width:${barWidth}%"></div>
                            </div>
                        </div>
                    </div>
                    <div class="lp-right">
                        <div class="lp-count">${item.demand_count}/${item.total_jobs} jobs</div>
                        <div class="lp-pct">${item.demand_pct}% demand</div>
                    </div>
                </div>
            `;
        });
    }
}

// ── Helpers ───────────────────────────────────────────────────────
function showError(msg) {
    document.getElementById("errorBox").classList.remove("hidden");
    document.getElementById("errorText").textContent = msg;
    hideReportElements();
}

function showReportElements() {
    ["reportHeader", "metricsGrid", "salaryCity",
     "skillsGrid", "learningPanel"].forEach(id => {
        document.getElementById(id).classList.remove("hidden");
    });
}

function hideReportElements() {
    ["reportHeader", "metricsGrid", "salaryCity", "skillsGrid",
     "learningPanel", "warningPanel", "lowDemandPanel"].forEach(id => {
        document.getElementById(id).classList.add("hidden");
    });
}

// ── Enter Key Support ─────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
    ["careerInput", "skillsInput"].forEach(id => {
        document.getElementById(id).addEventListener("keydown", e => {
            if (e.key === "Enter") analyze();
        });
    });
});