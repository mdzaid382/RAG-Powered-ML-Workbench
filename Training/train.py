from pathlib import Path
import json
import time
import joblib

import pandas as pd

from sklearn.model_selection import train_test_split

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    r2_score,
    mean_absolute_error,
    mean_squared_error
)

from Logger import logging

from Training.models import ModelFactory


class ModelTrainer:

    def __init__(
        self,
        dataset_path: str | Path,
        target_column: str,
        selected_models: list[str],
        problem_type: str,
        test_size: float = 0.2,
        random_state: int = 42,
        model_directory: str | Path = "trained_models"
    ):

        try:

            self.dataset_path = Path(dataset_path)

            self.df = pd.read_csv(self.dataset_path)

            self.target_column = target_column

            self.selected_models = selected_models

            self.problem_type = problem_type.lower()

            if self.problem_type not in ["classification", "regression"]:
            
                raise ValueError(
                    "Problem type must be either 'classification' or 'regression'."
                )

            self.test_size = test_size

            self.random_state = random_state

            self.model_directory = Path(model_directory)

            self.model_directory.mkdir(
                parents=True,
                exist_ok=True
            )

            self.report = {

                "dataset_name": self.dataset_path.stem,

                "target_column": target_column,

                "problem_type": "",

                "train_rows": 0,

                "test_rows": 0,

                "train_size": 1 - test_size,

                "test_size": test_size,

                "models": [],

                "best_model": "",

                "saved_models": []

            }

            logging.info(
                f"Loaded dataset '{self.dataset_path.name}'."
            )

        except Exception:

            logging.exception(
                "Failed to initialize ModelTrainer."
            )

            raise

    # --------------------------------------------------
    # Split Dataset
    # --------------------------------------------------

    def split_dataset(self):

        X = self.df.drop(
            columns=self.target_column
        )

        y = self.df[self.target_column]

        stratify = None

        if self.problem_type == "classification":

            stratify = y

        return train_test_split(

            X,

            y,

            test_size=self.test_size,

            random_state=self.random_state,

            stratify=stratify

        )

    # --------------------------------------------------
    # Train
    # --------------------------------------------------

    def train(self):

        try:

            logging.info(
                "Starting model training."
            )

            self.report["problem_type"] = self.problem_type

            X_train, X_test, y_train, y_test = self.split_dataset()

            self.report["train_rows"] = len(X_train)

            self.report["test_rows"] = len(X_test)

            if self.problem_type == "classification":

                available_models = ModelFactory.classification_models()

            else:

                available_models = ModelFactory.regression_models()

            best_score = float("-inf")

            for model_name in self.selected_models:

                if model_name not in available_models:

                    continue

                logging.info(
                    f"Training {model_name}"
                )

                model = available_models[model_name]

                start = time.time()

                model.fit(
                    X_train,
                    y_train
                )

                predictions = model.predict(
                    X_test
                )

                training_time = round(
                    time.time() - start,
                    3
                )

                if self.problem_type == "classification":

                    score = accuracy_score(
                        y_test,
                        predictions
                    )

                    metrics = {

                        "model": model_name,

                        "accuracy": round(score,4),

                        "precision": round(
                            precision_score(
                                y_test,
                                predictions,
                                average="weighted",
                                zero_division=0
                            ),
                            4
                        ),

                        "recall": round(
                            recall_score(
                                y_test,
                                predictions,
                                average="weighted",
                                zero_division=0
                            ),
                            4
                        ),

                        "f1_score": round(
                            f1_score(
                                y_test,
                                predictions,
                                average="weighted",
                                zero_division=0
                            ),
                            4
                        ),

                        "training_time": training_time

                    }

                else:

                    mse = mean_squared_error(
                        y_test,
                        predictions
                    )

                    rmse = mse ** 0.5

                    score = r2_score(
                        y_test,
                        predictions
                    )

                    metrics = {

                        "model": model_name,

                        "r2_score": round(score,4),

                        "mae": round(
                            mean_absolute_error(
                                y_test,
                                predictions
                            ),
                            4
                        ),

                        "mse": round(
                            mse,
                            4
                        ),

                        "rmse": round(
                            rmse,
                            4
                        ),

                        "training_time": training_time

                    }

                self.report["models"].append(
                    metrics
                )

                model_path = self.model_directory / (
                    model_name.replace(
                        " ",
                        "_"
                    ) + ".pkl"
                )

                joblib.dump(
                    model,
                    model_path
                )

                self.report["saved_models"].append(
                    str(model_path)
                )

                if score > best_score:

                    best_score = score

                    self.report["best_model"] = model_name

            logging.info(
                "Model training completed."
            )

            return self.report

        except Exception:

            logging.exception(
                "Training pipeline failed."
            )

            raise