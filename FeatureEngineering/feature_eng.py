from pathlib import Path
import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype

from sklearn.preprocessing import (
    LabelEncoder,
    StandardScaler,
    MinMaxScaler
)

from Logger import logging


class FeatureEngineer:

    def __init__(
        self,
        dataset_path: str | Path,
        target_column: str,
        categorical_encoding: str = "none",
        scaling: str = "none",
        correlation_threshold: float = 0.90
    ):

        try:

            self.dataset_path = Path(dataset_path)

            self.df = pd.read_csv(self.dataset_path)

            self.target_column = target_column

            # Original numeric feature columns
            self.numeric_columns = self.df.select_dtypes(
                include="number"
            ).columns.tolist()
            
            if self.target_column in self.numeric_columns:
                self.numeric_columns.remove(self.target_column)


            self.categorical_encoding = categorical_encoding.lower()

            self.scaling = scaling.lower()

            self.correlation_threshold = correlation_threshold

            self.report = {

                "dataset_name": self.dataset_path.stem,

                "target_column": target_column,

                "categorical_encoding": categorical_encoding,

                "scaling": scaling,

                "correlation_threshold": correlation_threshold,

                "target_encoded": False,

                "encoded_columns": [],

                "scaled_columns": [],

                "correlated_columns_removed": [],

                "columns_before": self.df.shape[1],

                "columns_after": self.df.shape[1]

            }

            logging.info(
                f"Loaded dataset '{self.dataset_path.name}' for feature engineering."
            )

        except Exception:

            logging.exception(
                "Failed to load dataset."
            )

            raise

    # --------------------------------------------------
    # Encode Target
    # --------------------------------------------------
    
    
    def encode_target(self):
    
        try:
    
            if self.target_column not in self.df.columns:
                return
    
            if not is_numeric_dtype(self.df[self.target_column]):
    
                encoder = LabelEncoder()
    
                self.df[self.target_column] = encoder.fit_transform(
    
                    self.df[self.target_column].astype(str)
    
                )
    
                self.report["target_encoded"] = True
    
                logging.info(
                    "Target column label encoded."
                )
    
        except Exception:
    
            logging.exception(
                "Target encoding failed."
            )
    
            raise

    # --------------------------------------------------
    # Encode Features
    # --------------------------------------------------

    def encode_features(self):
   
       try:
   
           categorical_columns = [
   
               column
   
               for column in self.df.select_dtypes(
                   include=["object", "category", "bool"]
               ).columns
   
               if column != self.target_column
   
           ]
   
           if not categorical_columns:
               return
   
           if self.categorical_encoding == "label":
   
               for column in categorical_columns:
   
                   encoder = LabelEncoder()
   
                   self.df[column] = encoder.fit_transform(
                       self.df[column].astype(str)
                   )
   
           elif self.categorical_encoding == "onehot":
   
               self.df = pd.get_dummies(
   
                   self.df,
   
                   columns=categorical_columns,
   
                   drop_first=True,
   
                   dtype=int
   
               )
   
           self.report["encoded_columns"] = categorical_columns
   
           logging.info(
               "Categorical encoding completed."
           )
   
       except Exception:
   
           logging.exception(
               "Categorical encoding failed."
           )
   
           raise
    # --------------------------------------------------
    # Scaling
    # --------------------------------------------------

    def scale_features(self):
    
        try:
    
            if self.scaling == "none":
                return
    
            numeric_columns = [
    
                column
    
                for column in self.numeric_columns
    
                if column in self.df.columns
    
            ]
    
            if not numeric_columns:
                return
    
            if self.scaling == "standard":
    
                scaler = StandardScaler()
    
            elif self.scaling == "minmax":
    
                scaler = MinMaxScaler()
    
            else:
    
                return
    
            self.df[numeric_columns] = scaler.fit_transform(
    
                self.df[numeric_columns]
    
            )
    
            self.report["scaled_columns"] = numeric_columns
    
            logging.info(
                "Feature scaling completed."
            )
    
        except Exception:
    
            logging.exception(
                "Scaling failed."
            )
    
            raise

    # --------------------------------------------------
    # Remove Highly Correlated Features
    # --------------------------------------------------

    def remove_correlated_columns(self):

        try:

            correlation = self.df.corr(
                numeric_only=True
            ).abs()

            upper = correlation.where(

                np.triu(
                np.ones(correlation.shape),
                k=1
                ).astype(bool)

            )

            

            columns_to_drop = [

                column

                for column in upper.columns

                if any(

                    upper[column]
                    > self.correlation_threshold

                )

            ]

            if columns_to_drop:

                self.df.drop(

                    columns=columns_to_drop,

                    inplace=True

                )

            self.report[
                "correlated_columns_removed"
            ] = columns_to_drop

            logging.info(

                f"Removed {len(columns_to_drop)} correlated columns."

            )

        except Exception:

            logging.exception(
                "Correlation removal failed."
            )

            raise

    # --------------------------------------------------
    # Complete Pipeline
    # --------------------------------------------------

    def engineer(self):

        try:

            logging.info(
                "Starting feature engineering."
            )

            self.encode_target()

            self.encode_features()

            self.scale_features()

            self.remove_correlated_columns()

            self.report["columns_after"] = self.df.shape[1]

            logging.info(
                "Feature engineering completed."
            )

            return self.df, self.report

        except Exception:

            logging.exception(
                "Feature engineering pipeline failed."
            )

            raise