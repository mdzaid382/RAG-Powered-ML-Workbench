import pandas as pd
from pathlib import Path
from Logger import logging




class DataCleaner:

    def __init__(
        self,
        dataset_path: str | Path,
        columns_to_remove: list[str] | None = None
    ):

        try:

            self.dataset_path = Path(dataset_path)

            self.df = pd.read_csv(self.dataset_path)

            self.columns_to_remove = columns_to_remove or []

            self.report = {

                "dataset_name": self.dataset_path.stem,

                "duplicates_removed": 0,

                "missing_values_handled": {},

                "constant_columns_removed": [],

                "user_removed_columns": [],

                "datatype_changes": {},

                "rows_before": len(self.df),

                "rows_after": len(self.df),

                "columns_before": self.df.shape[1],

                "columns_after": self.df.shape[1]

            }

            logging.info(
                f"Loaded dataset '{self.dataset_path.name}' for cleaning."
            )

        except Exception:

            logging.exception(
                "Failed to load dataset."
            )

            raise
    # ---------------------------------------------------
    # Remove Duplicate Rows
    # ---------------------------------------------------

    def remove_duplicates(self):

        try:

            before = len(self.df)

            self.df.drop_duplicates(inplace=True)

            after = len(self.df)

            self.report["duplicates_removed"] = before - after

            logging.info(
                f"Removed {before-after} duplicate rows."
            )

        except Exception:

            logging.exception(
                "Duplicate removal failed."
            )

            raise

    # ---------------------------------------------------
    # Handle Missing Values
    # ---------------------------------------------------

    def handle_missing_values(self):

        try:

            numeric_columns = self.df.select_dtypes(
                include="number"
            ).columns

            categorical_columns = self.df.select_dtypes(
                exclude="number"
            ).columns

            for column in numeric_columns:

                missing = self.df[column].isna().sum()

                if missing > 0:

                    median = self.df[column].median()

                    self.df[column].fillna(
                        median,
                        inplace=True
                    )

                    self.report["missing_values_handled"][column] = {

                        "count": int(missing),

                        "method": "median"

                    }

            for column in categorical_columns:

                missing = self.df[column].isna().sum()

                if missing > 0:

                    mode = self.df[column].mode()

                    if not mode.empty:

                        value = mode.iloc[0]

                    else:

                        value = "Unknown"

                    self.df[column].fillna(
                        value,
                        inplace=True
                    )

                    self.report["missing_values_handled"][column] = {

                        "count": int(missing),

                        "method": "mode"

                    }

            logging.info(
                "Missing values handled."
            )

        except Exception:

            logging.exception(
                "Missing value handling failed."
            )

            raise

    # ---------------------------------------------------
    # Remove Constant Columns
    # ---------------------------------------------------

    def remove_constant_columns(self):

        try:

            constant_columns = [

                column

                for column in self.df.columns

                if self.df[column].nunique() <= 1

            ]

            if constant_columns:

                self.df.drop(
                    columns=constant_columns,
                    inplace=True
                )

            self.report["constant_columns_removed"] = constant_columns

            logging.info(
                f"Removed {len(constant_columns)} constant columns."
            )

        except Exception:

            logging.exception(
                "Constant column removal failed."
            )

            raise


    # ---------------------------------------------------
    # Remove User Selected Columns
    # ---------------------------------------------------
    
    def remove_columns(self):
    
        try:
    
            existing_columns = [
    
                column
    
                for column in self.columns_to_remove
    
                if column in self.df.columns
    
            ]
    
            if existing_columns:
    
                self.df.drop(
                    columns=existing_columns,
                    inplace=True
                )
    
            self.report["user_removed_columns"] = existing_columns
    
            logging.info(
                f"Removed {len(existing_columns)} user selected column(s)."
            )
    
        except Exception:
    
            logging.exception(
                "Failed to remove selected columns."
            )
    
            raise

    # ---------------------------------------------------
    # Convert Data Types
    # ---------------------------------------------------

    def fix_datatypes(self):
    
        try:
    
            for column in self.df.columns:
    
                original_dtype = str(self.df[column].dtype)
    
                try:
                    converted = pd.to_numeric(self.df[column])
                except (ValueError, TypeError):
                    continue
    
                new_dtype = str(converted.dtype)
    
                if original_dtype != new_dtype:
    
                    self.df[column] = converted
    
                    self.report["datatype_changes"][column] = {
                        "from": original_dtype,
                        "to": new_dtype
                    }
    
            logging.info("Data type conversion completed.")
    
        except Exception:
    
            logging.exception("Data type conversion failed.")
            raise

    # ---------------------------------------------------
    # Run Complete Cleaning
    # ---------------------------------------------------

    def clean(self):

        try:

            logging.info(
                "Starting data cleaning."
            )

            self.remove_duplicates()
            self.handle_missing_values()
            self.remove_constant_columns()
            self.remove_columns()
            self.fix_datatypes()

            self.report["rows_after"] = len(self.df)
            self.report["columns_after"] = self.df.shape[1]

            logging.info(
                "Data cleaning completed successfully."
            )

            return self.df, self.report

        except Exception:

            logging.exception(
                "Cleaning pipeline failed."
            )

            raise