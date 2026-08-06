// ==========================================================
// Dataset Analyzer
// ==========================================================

const uploadZone = document.getElementById("uploadZone");
const uploadZoneInner = document.getElementById("uploadZoneInner");
const fileInput = document.getElementById("fileInput");
const browseBtn = document.getElementById("browseBtn");
const uploadError = document.getElementById("uploadError");

const demoSection = document.getElementById("demoSection");
const demoCards = document.querySelectorAll(".demo-card");

const reportSection = document.getElementById("reportSection");
const filenamePill = document.getElementById("reportFilenamePill");
const reportFilename = document.getElementById("reportFilename");
const summaryGrid = document.getElementById("summaryGrid");

const columnTypesTotal = document.getElementById("columnTypesTotal");
const typeBar = document.getElementById("typeBar");
const typeLegend = document.getElementById("typeLegend");

const missingSubtitle = document.getElementById("missingSubtitle");
const missingEmpty = document.getElementById("missingEmpty");
const missingPanelScroll = document.getElementById("missingPanelScroll");
const missingTableBody = document.getElementById("missingTableBody");

const outliersValue = document.getElementById("outliersValue");
const constantValue = document.getElementById("constantValue");
const cardinalityValue = document.getElementById("cardinalityValue");

const correlationsEmpty = document.getElementById("correlationsEmpty");
const correlationsPanelScroll = document.getElementById("correlationsPanelScroll");
const correlationsTableBody = document.getElementById("correlationsTableBody");

const recommendationsList = document.getElementById("recommendationsList");

const resetBtn = document.getElementById("resetBtn");

const ACCEPTED_EXTENSIONS = [".csv"];
const UPLOAD_ICON_HTML = uploadZoneInner ? uploadZoneInner.innerHTML : "";

// Column-type legend colors, reused for the segmented bar and its legend dots
const TYPE_COLORS = {
    numeric: "#2563eb",
    categorical: "#06b6d4",
    datetime: "#8b5cf6",
    boolean: "#f59e0b"
};

const TYPE_LABELS = {
    numeric: "Numeric",
    categorical: "Categorical",
    datetime: "Datetime",
    boolean: "Boolean"
};

let uploading = false;

// ==========================================================
// Events
// ==========================================================

browseBtn.addEventListener("click", function (e) {
    e.stopPropagation();
    fileInput.click();
});

uploadZone.addEventListener("click", function () {
    if (!uploading) fileInput.click();
});

fileInput.addEventListener("change", function () {
    if (fileInput.files.length > 0) {
        handleFile(fileInput.files[0]);
    }
});

["dragenter", "dragover"].forEach(function (evt) {
    uploadZone.addEventListener(evt, function (e) {
        e.preventDefault();
        e.stopPropagation();
        if (!uploading) uploadZone.classList.add("dragover");
    });
});

["dragleave", "drop"].forEach(function (evt) {
    uploadZone.addEventListener(evt, function (e) {
        e.preventDefault();
        e.stopPropagation();
        uploadZone.classList.remove("dragover");
    });
});

uploadZone.addEventListener("drop", function (e) {
    if (uploading) return;
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
});

resetBtn.addEventListener("click", resetUpload);

demoCards.forEach(function (card) {
    card.addEventListener("click", function () {
        if (uploading) return;
        loadDemoDataset(card.dataset.demoId);
    });
});

// ==========================================================
// File handling
// ==========================================================

function handleFile(file) {

    const ext = "." + file.name.split(".").pop().toLowerCase();

    if (!ACCEPTED_EXTENSIONS.includes(ext)) {
        showError(`"${ext}" isn't a supported format. Upload a CSV file.`);
        return;
    }

    uploadFile(file);

}

async function uploadFile(file) {

    hideError();
    setUploading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {

        const response = await fetch("/upload", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error("Couldn't analyze this file. Check the format and try again.");
        }

        const data = await response.json();
        renderReport(data);

    }
    catch (error) {
        setUploading(false);
        showError(error.message);
    }

}

// ==========================================================
// Demo dataset handling
// ==========================================================

async function loadDemoDataset(demoId) {

    hideError();
    setUploading(true);

    try {

        const response = await fetch(`/demo-datasets/${demoId}`, {
            method: "POST"
        });

        if (!response.ok) {
            throw new Error("Couldn't load that demo dataset. Try again.");
        }

        const data = await response.json();
        renderReport(data);

    }
    catch (error) {
        setUploading(false);
        showError(error.message);
    }

}

function setUploading(isUploading) {

    uploading = isUploading;

    if (isUploading) {
        uploadZone.classList.add("uploading");
        if (demoSection) demoSection.classList.add("hidden");
        uploadZoneInner.innerHTML = `
            <div class="spinner"></div>
            <h2>Analyzing your dataset…</h2>
            <p>Profiling columns, types, and missing values.</p>
        `;
    } else {
        uploadZone.classList.remove("uploading");
        uploadZoneInner.innerHTML = UPLOAD_ICON_HTML;
    }

}

function showError(message) {
    uploadError.textContent = message;
    uploadError.classList.remove("hidden");
    if (demoSection) demoSection.classList.remove("hidden");
}

function hideError() {
    uploadError.classList.add("hidden");
    uploadError.textContent = "";
}

// ==========================================================
// Render report
// ==========================================================

function renderReport(data) {

    uploadZone.classList.add("hidden");
    if (demoSection) demoSection.classList.add("hidden");
    reportSection.classList.remove("hidden");

    reportFilename.textContent = data.dataset_name || "Dataset";
    filenamePill.classList.remove("empty");

    renderSummary(data);
    renderColumnTypes(data.column_types || {});
    renderMissingValues(data.missing_values || {}, data.rows || 0);
    renderQualityChecks(data.outliers || [], data.constant_columns || [], data.high_cardinality_columns || []);
    renderCorrelations(data.high_correlations || []);
    renderRecommendations(data.recommendations || []);

}

function renderSummary(data) {

    const missingCells = Object.values(data.missing_values || {})
        .reduce(function (sum, n) { return sum + n; }, 0);

    const stats = [
        { label: "Rows", value: formatNumber(data.rows), warn: false },
        { label: "Columns", value: formatNumber(data.columns), warn: false },
        { label: "Missing cells", value: formatNumber(missingCells), warn: missingCells > 0 },
        { label: "Duplicate rows", value: formatNumber(data.duplicates), warn: (data.duplicates || 0) > 0 },
        { label: "Memory", value: `${data.memory_usage_mb ?? 0} MB`, warn: false }
    ];

    summaryGrid.innerHTML = stats.map(function (stat) {
        return `
            <div class="stat-card ${stat.warn ? "warn" : ""}">
                <div class="stat-label">${escapeHTML(stat.label)}</div>
                <div class="stat-value">${escapeHTML(stat.value)}</div>
            </div>
        `;
    }).join("");

}

function renderColumnTypes(columnTypes) {

    const total = Object.values(columnTypes).reduce(function (sum, n) { return sum + n; }, 0);
    columnTypesTotal.textContent = `${total} column${total === 1 ? "" : "s"} total`;

    const order = ["numeric", "categorical", "datetime", "boolean"];

    typeBar.innerHTML = order.map(function (key) {
        const count = columnTypes[key] || 0;
        if (count === 0 || total === 0) return "";
        const pct = (count / total * 100).toFixed(2);
        return `<div class="type-bar-segment" style="width:${pct}%; background:${TYPE_COLORS[key]}"></div>`;
    }).join("");

    typeLegend.innerHTML = order.map(function (key) {
        const count = columnTypes[key] || 0;
        return `
            <div class="type-legend-item">
                <span class="type-dot" style="background:${TYPE_COLORS[key]}"></span>
                <span>${TYPE_LABELS[key]}</span>
                <span class="type-count">${count}</span>
            </div>
        `;
    }).join("");

}

function renderMissingValues(missingValues, totalRows) {

    const entries = Object.entries(missingValues);

    if (entries.length === 0) {
        missingSubtitle.textContent = "";
        missingEmpty.classList.remove("hidden");
        missingPanelScroll.classList.add("hidden");
        return;
    }

    missingEmpty.classList.add("hidden");
    missingPanelScroll.classList.remove("hidden");
    missingSubtitle.textContent = `${entries.length} column${entries.length === 1 ? "" : "s"} affected`;

    // Worst-first ordering makes the table read as a priority list
    entries.sort(function (a, b) { return b[1] - a[1]; });

    missingTableBody.innerHTML = entries.map(function ([name, count]) {

        const pct = totalRows > 0 ? (count / totalRows * 100) : 0;
        const barClass = pct >= 30 ? "high" : "";

        return `
            <tr>
                <td>${escapeHTML(name)}</td>
                <td>${formatNumber(count)}</td>
                <td>
                    <div class="missing-cell">
                        <div class="missing-bar-track">
                            <div class="missing-bar-fill ${barClass}" style="width:${Math.min(pct, 100)}%"></div>
                        </div>
                        <span class="missing-pct">${pct.toFixed(1)}%</span>
                    </div>
                </td>
            </tr>
        `;

    }).join("");

}

function renderQualityChecks(outliers, constantColumns, highCardinalityColumns) {

    outliersValue.innerHTML = outliers.length === 0
        ? `<span class="check-clear">None detected</span>`
        : outliers.map(function (o) {
            return `<span class="badge badge-warn">${escapeHTML(o.column)} · ${formatNumber(o.count)}</span>`;
        }).join("");

    constantValue.innerHTML = constantColumns.length === 0
        ? `<span class="check-clear">None found</span>`
        : constantColumns.map(function (name) {
            return `<span class="badge badge-warn">${escapeHTML(name)}</span>`;
        }).join("");

    cardinalityValue.innerHTML = highCardinalityColumns.length === 0
        ? `<span class="check-clear">None found</span>`
        : highCardinalityColumns.map(function (name) {
            return `<span class="badge badge-warn">${escapeHTML(name)}</span>`;
        }).join("");

}

function renderCorrelations(correlations) {

    if (correlations.length === 0) {
        correlationsEmpty.classList.remove("hidden");
        correlationsPanelScroll.classList.add("hidden");
        return;
    }

    correlationsEmpty.classList.add("hidden");
    correlationsPanelScroll.classList.remove("hidden");

    correlationsTableBody.innerHTML = correlations.map(function (pair) {
        return `
            <tr>
                <td>${escapeHTML(pair.feature1)}</td>
                <td>${escapeHTML(pair.feature2)}</td>
                <td><span class="dtype-badge">${pair.correlation}</span></td>
            </tr>
        `;
    }).join("");

}

function renderRecommendations(recommendations) {

    if (recommendations.length === 0) {
        recommendationsList.innerHTML = `
            <li class="recommendation-item clear">
                <span class="rec-icon">✓</span>
                <span>Dataset looks clean — no action items right now.</span>
            </li>
        `;
        return;
    }

    recommendationsList.innerHTML = recommendations.map(function (text) {
        return `
            <li class="recommendation-item">
                <span class="rec-icon">→</span>
                <span>${escapeHTML(text)}</span>
            </li>
        `;
    }).join("");

}

// ==========================================================
// Reset
// ==========================================================

function resetUpload() {

    reportSection.classList.add("hidden");
    uploadZone.classList.remove("hidden");
    if (demoSection) demoSection.classList.remove("hidden");
    setUploading(false);
    hideError();
    fileInput.value = "";

    filenamePill.classList.add("empty");
    reportFilename.textContent = "No dataset loaded";

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