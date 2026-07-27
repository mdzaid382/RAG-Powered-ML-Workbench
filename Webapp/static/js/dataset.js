// -----------------------------
// Dataset Analyzer
// -----------------------------

const uploadBtn = document.getElementById("uploadBtn");

uploadBtn.addEventListener("click", uploadDataset);


// -----------------------------
// Upload Dataset
// -----------------------------

async function uploadDataset() {

    const fileInput = document.getElementById("csvFile");

    if (fileInput.files.length === 0) {

        alert("Please select a CSV file.");

        return;
    }

    const formData = new FormData();

    formData.append("file", fileInput.files[0]);

    try {

        uploadBtn.disabled = true;
        uploadBtn.innerText = "Analyzing...";

        const response = await fetch("/upload", {

            method: "POST",

            body: formData

        });

        if (!response.ok) {
            throw new Error("Failed to analyze dataset.");
        }

        const report = await response.json();

        updateSummary(report);

        updateColumnTypes(report.column_types);

        updateMissingValues(report.missing_values);

        updateCorrelations(report.high_correlations);

        updateOutliers(report.outliers);

        updateRecommendations(report.recommendations);

    }

    catch (error) {

        alert(error.message);

    }

    finally {

        uploadBtn.disabled = false;

        uploadBtn.innerText = "Analyze Dataset";

    }

}


// -----------------------------
// Summary Cards
// -----------------------------

function updateSummary(report) {

    document.getElementById("rows").textContent =
        report.rows;

    document.getElementById("columns").textContent =
        report.columns;

    document.getElementById("memory").textContent =
        report.memory_usage_mb + " MB";

}


// -----------------------------
// Column Types
// -----------------------------

function updateColumnTypes(columnTypes) {

    const table = document.getElementById("columnTypesTable");

    table.innerHTML = "";

    table.innerHTML += `
        <tr>
            <th>Type</th>
            <th>Count</th>
        </tr>
    `;

    for (const key in columnTypes) {

        table.innerHTML += `
            <tr>
                <td>${key}</td>
                <td>${columnTypes[key]}</td>
            </tr>
        `;
    }

}


// -----------------------------
// Missing Values
// -----------------------------

function updateMissingValues(missingValues) {

    const table = document.getElementById("missingTable");

    table.innerHTML = "";

    table.innerHTML += `
        <tr>
            <th>Column</th>
            <th>Missing Values</th>
        </tr>
    `;

    if (Object.keys(missingValues).length === 0) {

        table.innerHTML += `
            <tr>
                <td colspan="2">No Missing Values</td>
            </tr>
        `;

        return;
    }

    for (const key in missingValues) {

        table.innerHTML += `
            <tr>
                <td>${key}</td>
                <td>${missingValues[key]}</td>
            </tr>
        `;
    }

}


// -----------------------------
// High Correlations
// -----------------------------

function updateCorrelations(correlations) {

    const table = document.getElementById("correlationTable");

    table.innerHTML = "";

    table.innerHTML += `
        <tr>
            <th>Feature 1</th>
            <th>Feature 2</th>
            <th>Correlation</th>
        </tr>
    `;

    if (correlations.length === 0) {

        table.innerHTML += `
            <tr>
                <td colspan="3">No High Correlations</td>
            </tr>
        `;

        return;
    }

    correlations.forEach(item => {

        table.innerHTML += `
            <tr>
                <td>${item.feature1}</td>
                <td>${item.feature2}</td>
                <td>${item.correlation}</td>
            </tr>
        `;

    });

}


// -----------------------------
// Outliers
// -----------------------------

function updateOutliers(outliers) {

    const table = document.getElementById("outlierTable");

    table.innerHTML = "";

    table.innerHTML += `
        <tr>
            <th>Column</th>
            <th>Outliers</th>
        </tr>
    `;

    if (outliers.length === 0) {

        table.innerHTML += `
            <tr>
                <td colspan="2">No Outliers</td>
            </tr>
        `;

        return;
    }

    outliers.forEach(item => {

        table.innerHTML += `
            <tr>
                <td>${item.column}</td>
                <td>${item.count}</td>
            </tr>
        `;

    });

}


// -----------------------------
// Recommendations
// -----------------------------

function updateRecommendations(recommendations) {

    const list = document.getElementById("recommendationList");

    list.innerHTML = "";

    if (recommendations.length === 0) {

        list.innerHTML = "<li>No recommendations.</li>";

        return;
    }

    recommendations.forEach(item => {

        list.innerHTML += `
            <li>${item}</li>
        `;

    });

}