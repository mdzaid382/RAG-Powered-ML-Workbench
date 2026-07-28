from pathlib import Path
import json
import numpy as np
import pandas as pd

from Logger import logging


class DatasetAnalyzer:
    """
    Analyze a dataset and generate a JSON report.
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        dataset_name: str = "Dataset",
        report_dir: str = "reports",
    ):
        try:
            logging.info(
                f"Initializing DatasetAnalyzer for '{dataset_name}'."
            )

            self.df = dataframe
            self.dataset_name = dataset_name

            self.report_dir = Path(report_dir)
            self.report_dir.mkdir(parents=True, exist_ok=True)

            # Cache dataframe metadata
            self.rows = len(self.df)
            self.columns = len(self.df.columns)
            self.memory_usage = round(
                self.df.memory_usage(deep=True).sum() / (1024 ** 2), 2
            )

            # Cache column groups
            self.numeric_columns = self.df.select_dtypes(
                include=np.number
            ).columns

            self.categorical_columns = self.df.select_dtypes(
                include=["object", "category", "string"]
            ).columns

            self.datetime_columns = self.df.select_dtypes(
                include=["datetime", "datetimetz"]
            ).columns

            self.boolean_columns = self.df.select_dtypes(
                include="bool"
            ).columns

            logging.info(
                f"Dataset loaded successfully "
                f"({self.rows} rows, {self.columns} columns)."
            )

        except Exception:
            logging.exception(
                "Failed to initialize DatasetAnalyzer."
            )
            raise

    # ---------------------------------------------------
    # Basic Information
    # ---------------------------------------------------

    def get_rows(self):
        return self.rows

    def get_columns(self):
        return self.columns

    def get_memory_usage(self):
        return self.memory_usage

    # ---------------------------------------------------
    # Column Types
    # ---------------------------------------------------

    def get_column_types(self):

        return {
            "numeric": len(self.numeric_columns),
            "categorical": len(self.categorical_columns),
            "datetime": len(self.datetime_columns),
            "boolean": len(self.boolean_columns),
        }

    # ---------------------------------------------------
    # Missing Values
    # ---------------------------------------------------

    def get_missing_values(self):

        missing = self.df.isnull().sum()
        missing = missing[missing > 0]

        return missing.astype(int).to_dict()

    # ---------------------------------------------------
    # Duplicate Rows
    # ---------------------------------------------------

    def get_duplicates(self):

        return int(self.df.duplicated().sum())

    # ---------------------------------------------------
    # High Correlations
    # ---------------------------------------------------

    def get_high_correlations(self, threshold=0.90):

        if len(self.numeric_columns) == 0:
            return []

        numeric = self.df[self.numeric_columns]

        corr = numeric.corr()

        correlations = []

        columns = corr.columns

        for i in range(len(columns)):
            for j in range(i + 1, len(columns)):

                value = corr.iloc[i, j]

                if abs(value) >= threshold:

                    correlations.append(
                        {
                            "feature1": columns[i],
                            "feature2": columns[j],
                            "correlation": round(float(value), 2),
                        }
                    )

        return correlations

    # ---------------------------------------------------
    # Outlier Detection
    # ---------------------------------------------------

    def get_outliers(self):

        outliers = []

        for column in self.numeric_columns:

            q1 = self.df[column].quantile(0.25)
            q3 = self.df[column].quantile(0.75)

            iqr = q3 - q1

            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr

            count = (
                (
                    (self.df[column] < lower)
                    | (self.df[column] > upper)
                )
            ).sum()

            if count > 0:

                outliers.append(
                    {
                        "column": column,
                        "count": int(count),
                    }
                )

        return outliers

    # ---------------------------------------------------
    # Constant Columns
    # ---------------------------------------------------

    def get_constant_columns(self):

        constant_columns = []

        for column in self.df.columns:

            if self.df[column].nunique(dropna=False) == 1:
                constant_columns.append(column)

        return constant_columns

    # ---------------------------------------------------
    # High Cardinality
    # ---------------------------------------------------

    def get_high_cardinality_columns(self, threshold=0.50):

        high_cardinality = []

        for column in self.categorical_columns:

            ratio = self.df[column].nunique(dropna=True) / self.rows

            if ratio >= threshold:

                high_cardinality.append(column)

        return high_cardinality

    # ---------------------------------------------------
    # Recommendations
    # ---------------------------------------------------

    def get_recommendations(self):

        recommendations = []

        if self.get_missing_values():
            recommendations.append(
                "Handle missing values before model training."
            )

        if self.get_duplicates() > 0:
            recommendations.append(
                "Remove duplicate rows."
            )

        if self.get_high_correlations():
            recommendations.append(
                "Review highly correlated features."
            )

        if self.get_outliers():
            recommendations.append(
                "Investigate numeric outliers."
            )

        if self.get_constant_columns():
            recommendations.append(
                "Drop constant columns."
            )

        if self.get_high_cardinality_columns():
            recommendations.append(
                "Encode high-cardinality categorical columns."
            )

        return recommendations

    # ---------------------------------------------------
    # Generate Report
    # ---------------------------------------------------

    def generate_report(self):

        logging.info(
            f"Generating profiling report for "
            f"'{self.dataset_name}'."
        )

        try:

            report = {
                "dataset_name": self.dataset_name,
                "rows": self.get_rows(),
                "columns": self.get_columns(),
                "memory_usage_mb": self.get_memory_usage(),
                "column_types": self.get_column_types(),
                "missing_values": self.get_missing_values(),
                "duplicates": self.get_duplicates(),
                "high_correlations": self.get_high_correlations(),
                "outliers": self.get_outliers(),
                "constant_columns": self.get_constant_columns(),
                "high_cardinality_columns": self.get_high_cardinality_columns(),
                "recommendations": self.get_recommendations(),
            }

            report_path = (
                self.report_dir /
                f"{self.dataset_name}.json"
            )

            with open(
                report_path,
                "w",
                encoding="utf-8",
            ) as file:

                json.dump(
                    report,
                    file,
                    indent=4,
                    ensure_ascii=False,
                )

            logging.info(
                f"Profiling report saved successfully "
                f"to '{report_path}'."
            )

            return report

        except Exception:
            logging.exception(
                "Failed to generate profiling report."
            )
            raise


