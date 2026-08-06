// ==========================================================
// Model Training
// ==========================================================

const datasetPill = document.getElementById("datasetPill");
const datasetPillText = document.getElementById("datasetPillText");

const targetColumnSelect = document.getElementById("targetColumnSelect");
const problemTypeSelect = document.getElementById("problemTypeSelect");
const testSizeSlider = document.getElementById("testSizeSlider");
const testSizeValue = document.getElementById("testSizeValue");
const randomStateInput = document.getElementById("randomStateInput");

const modelChecklist = document.getElementById("modelChecklist");
const selectAllModelsBtn = document.getElementById("selectAllModelsBtn");
const clearAllModelsBtn = document.getElementById("clearAllModelsBtn");

const trainBtn = document.getElementById("trainBtn");
const trainBtnText = document.getElementById("trainBtnText");
const trainAgainBtn = document.getElementById("trainAgainBtn");
const trainingError = document.getElementById("trainingError");

const resultsSection = document.getElementById("resultsSection");
const summaryGrid = document.getElementById("summaryGrid");

const splitBar = document.getElementById("splitBar");
const splitLegend = document.getElementById("splitLegend");
const splitSubtitle = document.getElementById("splitSubtitle");

const modelsSubtitle = document.getElementById("modelsSubtitle");
const modelsTableHead = document.getElementById("modelsTableHead");
const modelsTableBody = document.getElementById("modelsTableBody");

// Mirrors Training/models.py ModelFactory exactly, so checkbox values
// always match a model the backend actually knows how to train.
const MODELS_BY_PROBLEM_TYPE = {
    classification: [
        "Logistic Regression",
        "Decision Tree",
        "Random Forest",
        "KNN",
        "SVM",
        "Naive Bayes",
        "XGBoost"
    ],
    regression: [
        "Linear Regression",
        "Ridge",
        "Lasso",
        "Decision Tree",
        "Random Forest",
        "KNN",
        "SVR",
        "XGBoost"
    ]
};

// Metric columns shown per problem type, in report-key order
const METRIC_COLUMNS = {
    classification: [
        { key: "accuracy", label: "Accuracy" },
        { key: "precision", label: "Precision" },
        { key: "recall", label: "Recall" },
        { key: "f1_score", label: "F1 score" }
    ],
    regression: [
        { key: "r2_score", label: "R\u00B2 score" },
        { key: "mae", label: "MAE" },
        { key: "mse", label: "MSE" },
        { key: "rmse", label: "RMSE" }
    ]
};

let training = false;

// ==========================================================
// Model checklist: rebuild when problem type changes
// ==========================================================

if (problemTypeSelect) {

    renderModelChecklist(problemTypeSelect.value);

    problemTypeSelect.addEventListener("change", function () {
        renderModelChecklist(problemTypeSelect.value);
    });

}

function renderModelChecklist(problemType) {

    const models = MODELS_BY_PROBLEM_TYPE[problemType] || [];

    modelChecklist.innerHTML = models.map(function (name) {
        return `
            <label class="model-check-item" data-model-name="${escapeHTML(name)}">
                <input type="checkbox" class="model-checkbox" value="${escapeHTML(name)}" checked>
                <span>${escapeHTML(name)}</span>
            </label>
        `;
    }).join("");

    modelChecklist.querySelectorAll(".model-check-item").forEach(syncCheckedClass);

}

modelChecklist.addEventListener("change", function (e) {
    if (e.target.classList.contains("model-checkbox")) {
        syncCheckedClass(e.target.closest(".model-check-item"));
    }
});

function syncCheckedClass(item) {
    const checkbox = item.querySelector(".model-checkbox");
    item.classList.toggle("checked", checkbox.checked);
}

if (selectAllModelsBtn) {

    selectAllModelsBtn.addEventListener("click", function () {
        modelChecklist.querySelectorAll(".model-checkbox").forEach(function (checkbox) {
            checkbox.checked = true;
        });
        modelChecklist.querySelectorAll(".model-check-item").forEach(syncCheckedClass);
    });

}

if (clearAllModelsBtn) {

    clearAllModelsBtn.addEventListener("click", function () {
        modelChecklist.querySelectorAll(".model-checkbox").forEach(function (checkbox) {
            checkbox.checked = false;
        });
        modelChecklist.querySelectorAll(".model-check-item").forEach(syncCheckedClass);
    });

}

function getSelectedModels() {

    return Array.from(
        modelChecklist.querySelectorAll(".model-checkbox:checked")
    ).map(function (checkbox) { return checkbox.value; });

}

// ==========================================================
// Test size slider
// ==========================================================

if (testSizeSlider) {

    testSizeSlider.addEventListener("input", function () {
        testSizeValue.textContent = Number(testSizeSlider.value).toFixed(2);
    });

}

// ==========================================================
// Train action
// ==========================================================

if (trainBtn) {
    trainBtn.addEventListener("click", runTraining);
}

if (trainAgainBtn) {
    trainAgainBtn.addEventListener("click", resetTraining);
}

async function runTraining() {

    if (training) return;

    if (!targetColumnSelect.value) {
        showError("Please select a target column.");
        return;
    }

    const selectedModels = getSelectedModels();

    if (selectedModels.length === 0) {
        showError("Please select at least one model to train.");
        return;
    }

    hideError();
    setTraining(true);

    try {

        const response = await fetch("/training", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                target_column: targetColumnSelect.value,
                problem_type: problemTypeSelect.value,
                selected_models: selectedModels,
                test_size: parseFloat(testSizeSlider.value),
                random_state: parseInt(randomStateInput.value, 10) || 0
            })
        });

        const data = await response.json().catch(function () { return {}; });

        if (!response.ok) {
            throw new Error(data.detail || "Failed to train models.");
        }

        renderResults(data.report);

    }
    catch (error) {
        showError(error.message);
    }
    finally {
        setTraining(false);
    }

}

function setTraining(isTraining) {

    training = isTraining;
    trainBtn.disabled = isTraining;

    trainBtnText.innerHTML = isTraining
        ? `<span class="btn-spinner"></span> Training…`
        : "Train models";

}

function showError(message) {
    trainingError.textContent = message;
    trainingError.classList.remove("hidden");
}

function hideError() {
    trainingError.classList.add("hidden");
    trainingError.textContent = "";
}

// ==========================================================
// Render results
// ==========================================================

function renderResults(report) {

    resultsSection.classList.remove("hidden");
    trainAgainBtn.classList.remove("hidden");

    datasetPill.classList.remove("empty");
    datasetPillText.textContent = report.dataset_name || "Training complete";

    renderSummary(report);
    renderSplit(report);
    renderModelsTable(report);

    resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });

}

function renderSummary(report) {

    const stats = [
        { label: "Best model", value: report.best_model || "—" },
        { label: "Models trained", value: formatNumber((report.models || []).length) },
        { label: "Train rows", value: formatNumber(report.train_rows) },
        { label: "Test rows", value: formatNumber(report.test_rows) }
    ];

    summaryGrid.innerHTML = stats.map(function (stat) {
        return `
            <div class="stat-card ok">
                <div class="stat-label">${escapeHTML(stat.label)}</div>
                <div class="stat-value">${escapeHTML(String(stat.value))}</div>
            </div>
        `;
    }).join("");

}

function renderSplit(report) {

    const trainPct = (report.train_size || 0) * 100;
    const testPct = (report.test_size || 0) * 100;

    splitSubtitle.textContent = `${trainPct.toFixed(0)}% train · ${testPct.toFixed(0)}% test`;

    splitBar.innerHTML = `
        <div class="split-segment train" style="width:${trainPct}%"></div>
        <div class="split-segment test" style="width:${testPct}%"></div>
    `;

    splitLegend.innerHTML = `
        <div class="split-legend-item">
            <span class="split-dot train"></span>
            <span>Train</span>
            <span class="split-count">${formatNumber(report.train_rows)} rows</span>
        </div>
        <div class="split-legend-item">
            <span class="split-dot test"></span>
            <span>Test</span>
            <span class="split-count">${formatNumber(report.test_rows)} rows</span>
        </div>
    `;

}

function renderModelsTable(report) {

    const models = report.models || [];
    const problemType = report.problem_type === "regression" ? "regression" : "classification";
    const metricColumns = METRIC_COLUMNS[problemType];

    modelsSubtitle.textContent = `${models.length} model${models.length === 1 ? "" : "s"} · ${problemType}`;

    modelsTableHead.innerHTML = `
        <tr>
            <th>Model</th>
            ${metricColumns.map(function (col) { return `<th>${escapeHTML(col.label)}</th>`; }).join("")}
            <th>Training time</th>
            <th>Download</th>
        </tr>
    `;

    // Higher is better for accuracy/f1/r2, so sort rows accordingly per problem type
    const sortKey = problemType === "regression" ? "r2_score" : "accuracy";
    const sortedModels = models.slice().sort(function (a, b) {
        return (b[sortKey] || 0) - (a[sortKey] || 0);
    });

    modelsTableBody.innerHTML = sortedModels.map(function (model) {

        const isBest = model.model === report.best_model;
        const fileName = model.model.replace(/ /g, "_");

        const metricCells = metricColumns.map(function (col) {
            return `<td class="metric-cell">${formatMetric(model[col.key])}</td>`;
        }).join("");

        return `
            <tr class="${isBest ? "best-model-row" : ""}">
                <td>
                    <div class="model-name-cell">
                        ${escapeHTML(model.model)}
                        ${isBest ? `<span class="best-badge">Best</span>` : ""}
                    </div>
                </td>
                ${metricCells}
                <td class="metric-cell">${formatMetric(model.training_time)}s</td>
                <td>
                    <a class="download-btn" href="/download-model/${encodeURIComponent(fileName)}" download>
                        ⬇ .pkl
                    </a>
                </td>
            </tr>
        `;

    }).join("");

}

// ==========================================================
// Reset
// ==========================================================

function resetTraining() {

    resultsSection.classList.add("hidden");
    trainAgainBtn.classList.add("hidden");
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

function formatMetric(n) {
    if (n === null || n === undefined) return "—";
    return Number(n).toString();
}

function escapeHTML(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}