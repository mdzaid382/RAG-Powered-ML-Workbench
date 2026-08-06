// ==========================================================
// Feature Engineering
// ==========================================================

const datasetPill = document.getElementById("datasetPill");
const datasetPillText = document.getElementById("datasetPillText");

const targetColumnSelect = document.getElementById("targetColumnSelect");
const encodingSelect = document.getElementById("encodingSelect");
const scalingSelect = document.getElementById("scalingSelect");
const correlationSlider = document.getElementById("correlationSlider");
const correlationValue = document.getElementById("correlationValue");

const runBtn = document.getElementById("runBtn");
const runBtnText = document.getElementById("runBtnText");
const runAgainBtn = document.getElementById("runAgainBtn");
const featureError = document.getElementById("featureError");

const resultsSection = document.getElementById("resultsSection");
const summaryGrid = document.getElementById("summaryGrid");
const shapeCompare = document.getElementById("shapeCompare");
const settingsUsed = document.getElementById("settingsUsed");

const encodedColumns = document.getElementById("encodedColumns");
const scaledColumns = document.getElementById("scaledColumns");
const correlatedRemoved = document.getElementById("correlatedRemoved");
const correlatedSubtitle = document.getElementById("correlatedSubtitle");

let running = false;

// ==========================================================
// Slider live value
// ==========================================================

if (correlationSlider) {

    correlationSlider.addEventListener("input", function () {
        correlationValue.textContent = Number(correlationSlider.value).toFixed(2);
    });

}

// ==========================================================
// Run action
// ==========================================================

if (runBtn) {
    runBtn.addEventListener("click", runFeatureEngineering);
}

if (runAgainBtn) {
    runAgainBtn.addEventListener("click", resetFeature);
}

async function runFeatureEngineering() {

    if (running) return;

    if (!targetColumnSelect.value) {
        showError("Please select a target column.");
        return;
    }

    hideError();
    setRunning(true);

    try {

        const response = await fetch("/feature", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                target_column: targetColumnSelect.value,
                categorical_encoding: encodingSelect.value,
                scaling: scalingSelect.value,
                correlation_threshold: parseFloat(correlationSlider.value)
            })
        });

        const data = await response.json().catch(function () { return {}; });

        if (!response.ok) {
            throw new Error(data.detail || "Failed to perform feature engineering.");
        }

        renderResults(data.report);

    }
    catch (error) {
        showError(error.message);
    }
    finally {
        setRunning(false);
    }

}

function setRunning(isRunning) {

    running = isRunning;
    runBtn.disabled = isRunning;

    runBtnText.innerHTML = isRunning
        ? `<span class="btn-spinner"></span> Running…`
        : "Run feature engineering";

}

function showError(message) {
    featureError.textContent = message;
    featureError.classList.remove("hidden");
}

function hideError() {
    featureError.classList.add("hidden");
    featureError.textContent = "";
}

// ==========================================================
// Render results
// ==========================================================

function renderResults(report) {

    resultsSection.classList.remove("hidden");
    runAgainBtn.classList.remove("hidden");

    datasetPill.classList.remove("empty");
    datasetPillText.textContent = report.dataset_name || "Feature engineering complete";

    renderSummary(report);
    renderShape(report);
    renderSettingsUsed(report);
    renderBadgeGroup(encodedColumns, report.encoded_columns || [], "badge-info", "No columns encoded");
    renderBadgeGroup(scaledColumns, report.scaled_columns || [], "badge-accent", "No columns scaled");

    const correlatedList = report.correlated_columns_removed || [];
    correlatedSubtitle.textContent = correlatedList.length > 0
        ? `${correlatedList.length} column${correlatedList.length === 1 ? "" : "s"} above threshold`
        : `No columns above threshold`;
    renderBadgeGroup(correlatedRemoved, correlatedList, "badge-danger", "None removed");

    resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });

}

function renderSummary(report) {

    const stats = [
        { label: "Target encoded", value: report.target_encoded ? "Yes" : "No", warn: false },
        { label: "Encoded columns", value: formatNumber((report.encoded_columns || []).length), warn: false },
        { label: "Scaled columns", value: formatNumber((report.scaled_columns || []).length), warn: false },
        { label: "Correlated dropped", value: formatNumber((report.correlated_columns_removed || []).length), warn: (report.correlated_columns_removed || []).length > 0 }
    ];

    summaryGrid.innerHTML = stats.map(function (stat) {
        return `
            <div class="stat-card ${stat.warn ? "warn" : "ok"}">
                <div class="stat-label">${escapeHTML(stat.label)}</div>
                <div class="stat-value">${escapeHTML(stat.value)}</div>
            </div>
        `;
    }).join("");

}

function renderShape(report) {

    const delta = (report.columns_after || 0) - (report.columns_before || 0);
    const deltaLabel = delta === 0 ? "No change" : `${delta > 0 ? "+" : ""}${delta}`;
    const deltaClass = delta === 0 ? "neutral" : "";

    shapeCompare.innerHTML = `
        <div class="shape-item">
            <div class="shape-label">Columns</div>
            <div class="shape-track">
                <span class="shape-value">${formatNumber(report.columns_before)}</span>
                <span class="shape-arrow">&rarr;</span>
                <span class="shape-value">${formatNumber(report.columns_after)}</span>
                <span class="shape-delta ${deltaClass}">${escapeHTML(deltaLabel)}</span>
            </div>
        </div>
    `;

}

function renderSettingsUsed(report) {

    const settings = [
        { key: "Target", val: report.target_column },
        { key: "Encoding", val: report.categorical_encoding },
        { key: "Scaling", val: report.scaling },
        { key: "Correlation threshold", val: report.correlation_threshold }
    ];

    settingsUsed.innerHTML = settings.map(function (setting) {
        return `
            <div class="setting-pill">
                <span class="setting-key">${escapeHTML(setting.key)}</span>
                <span class="setting-val">${escapeHTML(String(setting.val))}</span>
            </div>
        `;
    }).join("");

}

function renderBadgeGroup(container, items, badgeClass, emptyLabel) {

    container.innerHTML = items.length === 0
        ? `<span class="badge-empty">${escapeHTML(emptyLabel)}</span>`
        : items.map(function (name) {
            return `<span class="badge ${badgeClass}">${escapeHTML(name)}</span>`;
        }).join("");

}

// ==========================================================
// Reset
// ==========================================================

function resetFeature() {

    resultsSection.classList.add("hidden");
    runAgainBtn.classList.add("hidden");
    hideError();

    datasetPill.classList.add("empty");
    datasetPillText.textContent = "No dataset loaded";

}

// ==========================================================
// Helpers
// ==========================================================

function formatNumber(n) {
    if (n === null || n === undefined) return "0";
    return Number(n).toLocaleString();
}

function escapeHTML(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}