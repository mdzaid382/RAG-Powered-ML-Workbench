// ==========================================================
// Data Cleaning
// ==========================================================

const datasetPill = document.getElementById("datasetPill");
const datasetPillText = document.getElementById("datasetPillText");

const columnSearch = document.getElementById("columnSearch");
const selectAllBtn = document.getElementById("selectAllBtn");
const clearAllBtn = document.getElementById("clearAllBtn");
const columnChecklist = document.getElementById("columnChecklist");
const selectedCountLabel = document.getElementById("selectedCountLabel");

const cleanBtn = document.getElementById("cleanBtn");
const cleanBtnText = document.getElementById("cleanBtnText");
const cleanAgainBtn = document.getElementById("cleanAgainBtn");
const cleaningError = document.getElementById("cleaningError");

const resultsSection = document.getElementById("resultsSection");
const summaryGrid = document.getElementById("summaryGrid");
const shapeCompare = document.getElementById("shapeCompare");

const missingHandledSubtitle = document.getElementById("missingHandledSubtitle");
const missingHandledEmpty = document.getElementById("missingHandledEmpty");
const missingHandledScroll = document.getElementById("missingHandledScroll");
const missingHandledBody = document.getElementById("missingHandledBody");

const constantRemoved = document.getElementById("constantRemoved");
const userRemoved = document.getElementById("userRemoved");

const datatypeSubtitle = document.getElementById("datatypeSubtitle");
const datatypeEmpty = document.getElementById("datatypeEmpty");
const datatypeScroll = document.getElementById("datatypeScroll");
const datatypeBody = document.getElementById("datatypeBody");

let cleaning = false;

// ==========================================================
// Column checklist: search, select all, clear, live count
// ==========================================================

if (columnChecklist) {

    columnChecklist.addEventListener("change", updateSelectedCount);
    updateSelectedCount();

}

if (columnSearch) {

    columnSearch.addEventListener("input", function () {

        const query = columnSearch.value.trim().toLowerCase();

        columnChecklist.querySelectorAll(".column-check-item").forEach(function (item) {
            const name = item.getAttribute("data-column-name") || "";
            item.classList.toggle("column-hidden", query !== "" && !name.includes(query));
        });

    });

}

if (selectAllBtn) {

    selectAllBtn.addEventListener("click", function () {

        columnChecklist.querySelectorAll(".column-check-item:not(.column-hidden) .column-checkbox")
            .forEach(function (checkbox) { checkbox.checked = true; });

        updateSelectedCount();

    });

}

if (clearAllBtn) {

    clearAllBtn.addEventListener("click", function () {

        columnChecklist.querySelectorAll(".column-checkbox")
            .forEach(function (checkbox) { checkbox.checked = false; });

        updateSelectedCount();

    });

}

function getSelectedColumns() {

    return Array.from(
        columnChecklist.querySelectorAll(".column-checkbox:checked")
    ).map(function (checkbox) { return checkbox.value; });

}

function updateSelectedCount() {

    const count = getSelectedColumns().length;

    selectedCountLabel.textContent = count === 0
        ? "Optional — pick any columns to drop"
        : `${count} column${count === 1 ? "" : "s"} selected for removal`;

}

// ==========================================================
// Clean action
// ==========================================================

if (cleanBtn) {
    cleanBtn.addEventListener("click", runCleaning);
}

if (cleanAgainBtn) {
    cleanAgainBtn.addEventListener("click", resetCleaning);
}

async function runCleaning() {

    if (cleaning) return;

    hideError();
    setCleaning(true);

    try {

        const response = await fetch("/clean", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ columns_to_remove: getSelectedColumns() })
        });

        const data = await response.json().catch(function () { return {}; });

        if (!response.ok) {
            throw new Error(data.detail || "Failed to clean dataset.");
        }

        renderResults(data.report);

    }
    catch (error) {
        showError(error.message);
    }
    finally {
        setCleaning(false);
    }

}

function setCleaning(isCleaning) {

    cleaning = isCleaning;
    cleanBtn.disabled = isCleaning;

    cleanBtnText.innerHTML = isCleaning
        ? `<span class="btn-spinner"></span> Cleaning…`
        : "Clean dataset";

}

function showError(message) {
    cleaningError.textContent = message;
    cleaningError.classList.remove("hidden");
}

function hideError() {
    cleaningError.classList.add("hidden");
    cleaningError.textContent = "";
}

// ==========================================================
// Render results
// ==========================================================

function renderResults(report) {

    resultsSection.classList.remove("hidden");
    cleanAgainBtn.classList.remove("hidden");

    datasetPill.classList.remove("empty");
    datasetPillText.textContent = report.dataset_name || "Dataset cleaned";

    renderSummary(report);
    renderShape(report);
    renderMissingHandled(report.missing_values_handled || {});
    renderConstantRemoved(report.constant_columns_removed || []);
    renderUserRemoved(report.user_removed_columns || []);
    renderDatatypeChanges(report.datatype_changes || {});

    resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });

}

function renderSummary(report) {

    const missingHandledCount = Object.keys(report.missing_values_handled || {}).length;
    const rowsDropped = (report.rows_before || 0) - (report.rows_after || 0);
    const columnsDropped = (report.columns_before || 0) - (report.columns_after || 0);

    const stats = [
        { label: "Duplicates removed", value: formatNumber(report.duplicates_removed), warn: (report.duplicates_removed || 0) > 0 },
        { label: "Columns with fills", value: formatNumber(missingHandledCount), warn: missingHandledCount > 0 },
        { label: "Rows dropped", value: formatNumber(rowsDropped), warn: rowsDropped > 0 },
        { label: "Columns dropped", value: formatNumber(columnsDropped), warn: columnsDropped > 0 }
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

    const items = [
        { label: "Rows", before: report.rows_before, after: report.rows_after },
        { label: "Columns", before: report.columns_before, after: report.columns_after }
    ];

    shapeCompare.innerHTML = items.map(function (item) {

        const delta = (item.after || 0) - (item.before || 0);
        const deltaLabel = delta === 0 ? "No change" : `${delta > 0 ? "+" : ""}${delta}`;
        const deltaClass = delta === 0 ? "neutral" : "";

        return `
            <div class="shape-item">
                <div class="shape-label">${escapeHTML(item.label)}</div>
                <div class="shape-track">
                    <span class="shape-value">${formatNumber(item.before)}</span>
                    <span class="shape-arrow">&rarr;</span>
                    <span class="shape-value">${formatNumber(item.after)}</span>
                    <span class="shape-delta ${deltaClass}">${escapeHTML(deltaLabel)}</span>
                </div>
            </div>
        `;

    }).join("");

}

function renderMissingHandled(missingValuesHandled) {

    const entries = Object.entries(missingValuesHandled);

    if (entries.length === 0) {
        missingHandledSubtitle.textContent = "";
        missingHandledEmpty.classList.remove("hidden");
        missingHandledScroll.classList.add("hidden");
        return;
    }

    missingHandledEmpty.classList.add("hidden");
    missingHandledScroll.classList.remove("hidden");
    missingHandledSubtitle.textContent = `${entries.length} column${entries.length === 1 ? "" : "s"} filled`;

    entries.sort(function (a, b) { return b[1].count - a[1].count; });

    missingHandledBody.innerHTML = entries.map(function ([name, info]) {
        return `
            <tr>
                <td>${escapeHTML(name)}</td>
                <td>${formatNumber(info.count)}</td>
                <td><span class="dtype-badge">${escapeHTML(info.method)}</span></td>
            </tr>
        `;
    }).join("");

}

function renderConstantRemoved(columns) {

    constantRemoved.innerHTML = columns.length === 0
        ? `<span class="badge-empty">None removed</span>`
        : columns.map(function (name) {
            return `<span class="badge badge-danger">${escapeHTML(name)}</span>`;
        }).join("");

}

function renderUserRemoved(columns) {

    userRemoved.innerHTML = columns.length === 0
        ? `<span class="badge-empty">None selected</span>`
        : columns.map(function (name) {
            return `<span class="badge badge-info">${escapeHTML(name)}</span>`;
        }).join("");

}

function renderDatatypeChanges(datatypeChanges) {

    const entries = Object.entries(datatypeChanges);

    if (entries.length === 0) {
        datatypeSubtitle.textContent = "";
        datatypeEmpty.classList.remove("hidden");
        datatypeScroll.classList.add("hidden");
        return;
    }

    datatypeEmpty.classList.add("hidden");
    datatypeScroll.classList.remove("hidden");
    datatypeSubtitle.textContent = `${entries.length} column${entries.length === 1 ? "" : "s"} converted`;

    datatypeBody.innerHTML = entries.map(function ([name, change]) {
        return `
            <tr>
                <td>${escapeHTML(name)}</td>
                <td><span class="dtype-badge">${escapeHTML(change.from)}</span></td>
                <td><span class="dtype-badge">${escapeHTML(change.to)}</span></td>
            </tr>
        `;
    }).join("");

}

// ==========================================================
// Reset
// ==========================================================

function resetCleaning() {

    resultsSection.classList.add("hidden");
    cleanAgainBtn.classList.add("hidden");
    hideError();

    if (columnChecklist) {
        columnChecklist.querySelectorAll(".column-checkbox").forEach(function (checkbox) {
            checkbox.checked = false;
        });
    }

    if (columnSearch) columnSearch.value = "";
    updateSelectedCount();

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