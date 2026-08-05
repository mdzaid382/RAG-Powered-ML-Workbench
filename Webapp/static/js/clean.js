// ==========================================================
// Data Cleaning
// ==========================================================

const datasetPill = document.getElementById("datasetPill");
const datasetPillText = document.getElementById("datasetPillText");

const columnSelect = document.getElementById("columnSelect");

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
// Clean Dataset
// ==========================================================

cleanBtn.addEventListener(
    "click",
    runCleaning
);

cleanAgainBtn.addEventListener(
    "click",
    resetCleaning
);


async function runCleaning() {

    if (cleaning) return;

    hideError();

    setCleaning(true);

    const selectedColumns = Array.from(

        columnSelect.selectedOptions

    ).map(

        option => option.value

    );

    try {

        const response = await fetch(

            "/clean",

            {

                method: "POST",

                headers: {

                    "Content-Type": "application/json"

                },

                body: JSON.stringify({

                    columns_to_remove: selectedColumns

                })

            }

        );

        const data = await response.json();

        if (!response.ok) {

            throw new Error(

                data.detail ||

                "Failed to clean dataset."

            );

        }

        renderResults(

            data.report

        );

    }

    catch (error) {

        showError(

            error.message

        );

    }

    finally {

        setCleaning(false);

    }

}


// ==========================================================
// Button State
// ==========================================================

function setCleaning(isCleaning) {

    cleaning = isCleaning;

    cleanBtn.disabled = isCleaning;

    cleanBtnText.innerHTML = isCleaning

        ? `<span class="btn-spinner"></span> Cleaning...`

        : `Clean Dataset`;

}


// ==========================================================
// Error
// ==========================================================

function showError(message) {

    cleaningError.textContent = message;

    cleaningError.classList.remove("hidden");

}

function hideError() {

    cleaningError.classList.add("hidden");

    cleaningError.textContent = "";

}


// ==========================================================
// Render Results
// ==========================================================

function renderResults(report) {

    resultsSection.classList.remove("hidden");

    cleanAgainBtn.classList.remove("hidden");

    datasetPill.classList.remove("empty");

    datasetPillText.textContent =

        report.dataset_name;

    renderSummary(report);

    renderShape(report);

    renderMissingHandled(

        report.missing_values_handled || {}

    );

    renderConstantRemoved(

        report.constant_columns_removed || []

    );

    renderUserRemoved(

        report.user_removed_columns || []

    );

    renderDatatypeChanges(

        report.datatype_changes || {}

    );

    resultsSection.scrollIntoView({

        behavior: "smooth"

    });

}


// ==========================================================
// Summary
// ==========================================================

function renderSummary(report) {

    const missingHandled = Object.keys(

        report.missing_values_handled || {}

    ).length;

    const rowsDropped =

        report.rows_before -

        report.rows_after;

    const columnsDropped =

        report.columns_before -

        report.columns_after;

    const stats = [

        {

            label: "Duplicates Removed",

            value: report.duplicates_removed

        },

        {

            label: "Columns Filled",

            value: missingHandled

        },

        {

            label: "Rows Dropped",

            value: rowsDropped

        },

        {

            label: "Columns Dropped",

            value: columnsDropped

        }

    ];

    summaryGrid.innerHTML = stats.map(

        stat =>

        `

        <div class="stat-card">

            <div class="stat-label">

                ${stat.label}

            </div>

            <div class="stat-value">

                ${formatNumber(stat.value)}

            </div>

        </div>

        `

    ).join("");

}


// ==========================================================
// Shape
// ==========================================================

function renderShape(report) {

    shapeCompare.innerHTML = `

        <div class="shape-item">

            <strong>Rows</strong>

            ${formatNumber(report.rows_before)}

            →

            ${formatNumber(report.rows_after)}

        </div>

        <div class="shape-item">

            <strong>Columns</strong>

            ${formatNumber(report.columns_before)}

            →

            ${formatNumber(report.columns_after)}

        </div>

    `;

}


// ==========================================================
// Missing Values
// ==========================================================

function renderMissingHandled(values) {

    const entries = Object.entries(values);

    if (entries.length === 0) {

        missingHandledEmpty.classList.remove("hidden");

        missingHandledScroll.classList.add("hidden");

        missingHandledSubtitle.textContent = "";

        return;

    }

    missingHandledEmpty.classList.add("hidden");

    missingHandledScroll.classList.remove("hidden");

    missingHandledSubtitle.textContent =

        `${entries.length} columns`;

    missingHandledBody.innerHTML = entries.map(

        ([column, info]) =>

        `

        <tr>

            <td>${escapeHTML(column)}</td>

            <td>${info.count}</td>

            <td>${info.method}</td>

        </tr>

        `

    ).join("");

}


// ==========================================================
// Removed Columns
// ==========================================================

function renderConstantRemoved(columns) {

    constantRemoved.innerHTML =

        columns.length

            ? columns.join(", ")

            : "None";

}

function renderUserRemoved(columns) {

    userRemoved.innerHTML =

        columns.length

            ? columns.join(", ")

            : "None";

}


// ==========================================================
// Datatype Changes
// ==========================================================

function renderDatatypeChanges(changes) {

    const entries = Object.entries(changes);

    if (entries.length === 0) {

        datatypeEmpty.classList.remove("hidden");

        datatypeScroll.classList.add("hidden");

        datatypeSubtitle.textContent = "";

        return;

    }

    datatypeEmpty.classList.add("hidden");

    datatypeScroll.classList.remove("hidden");

    datatypeSubtitle.textContent =

        `${entries.length} converted`;

    datatypeBody.innerHTML = entries.map(

        ([column, change]) =>

        `

        <tr>

            <td>${escapeHTML(column)}</td>

            <td>${change.from}</td>

            <td>${change.to}</td>

        </tr>

        `

    ).join("");

}


// ==========================================================
// Reset
// ==========================================================

function resetCleaning() {

    resultsSection.classList.add("hidden");

    cleanAgainBtn.classList.add("hidden");

    hideError();

    datasetPill.classList.add("empty");

    datasetPillText.textContent =

        "Dataset Ready";

    Array.from(

        columnSelect.options

    ).forEach(

        option => option.selected = false

    );

}


// ==========================================================
// Helpers
// ==========================================================

function formatNumber(value) {

    return Number(value || 0).toLocaleString();

}

function escapeHTML(text) {

    const div = document.createElement("div");

    div.textContent = text;

    return div.innerHTML;

}