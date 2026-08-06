from pathlib import Path
import shutil
import json

import pandas as pd
from Logger import logging

from fastapi import FastAPI
from fastapi import UploadFile
from fastapi import File
from fastapi.requests import Request
from fastapi import HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel


from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from DataProfiling.Profiling import DatasetAnalyzer
from RAG.chat import ChatService
from RAG.ingest import RAGIngestor
from RAG.vectorstore import VectorStoreManager
from DataCleaning.clean import DataCleaner
from FeatureEngineering.feature_eng import FeatureEngineer
from Training.train import ModelTrainer


app = FastAPI()

app.state.current_dataset = None

chat_service = ChatService()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True)

CLEANED_DIR = Path("cleaned_datasets")
CLEANED_DIR.mkdir(exist_ok=True)

FEATURE_DIR = Path("feature_engineered_datasets")
FEATURE_DIR.mkdir(exist_ok=True)

TRAINED_MODEL_DIR = Path("trained_models")
TRAINED_MODEL_DIR.mkdir(exist_ok=True)

# Folder where the demo dataset CSVs actually live on disk.
# Add a file here for every entry in DEMO_DATASET_FILES below,
# e.g. Webapp/demo_datasets/titanic.csv
DEMO_DIR = Path("Webapp/demo_datasets")
DEMO_DIR.mkdir(exist_ok=True, parents=True)

templates = Jinja2Templates(
    directory="Webapp/templates"
)

app.mount(
    "/static",
    StaticFiles(directory="Webapp/static"),
    name="static"
)


# ----------------------------------------------------
# Pages
# ----------------------------------------------------

DEMO_DATASETS = [
    {
        "id": "titanic",
        "name": "Titanic Dataset",
        "description": "Passenger survival prediction"
    }
]

# Maps a demo id (from DEMO_DATASETS above) to the actual filename
# stored in DEMO_DIR. Keep this in sync with DEMO_DATASETS.
DEMO_DATASET_FILES = {
    "titanic": "titanic.csv"
}

@app.get("/")
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="dataset.html",
        context={
            "request": request,
            "demo_datasets": DEMO_DATASETS
        }
    )

@app.get("/assistant")
async def assistant(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="assistant.html"
    )


@app.get("/clean")
async def cleaning(request: Request):

    try:

        columns = []

        if app.state.current_dataset is not None:

            df = pd.read_csv(
                app.state.current_dataset,
                nrows=0
            )

            columns = df.columns.tolist()

        return templates.TemplateResponse(

            request=request,

            name="clean.html",

            context={

                "request": request,

                "columns": columns

            }

        )

    except Exception:

        logging.exception(
            "Failed to load cleaning page."
        )

        raise HTTPException(

            status_code=500,

            detail="Failed to load cleaning page."

        )

# ----------------------------------------------------
# Model Training Page
# ----------------------------------------------------

@app.get("/training")
async def training(request: Request):

    try:

        columns = []

        if app.state.current_dataset is not None:

            df = pd.read_csv(
                app.state.current_dataset,
                nrows=0
            )

            columns = df.columns.tolist()

        return templates.TemplateResponse(

            request=request,

            name="training.html",

            context={

                "request": request,

                "columns": columns

            }

        )

    except Exception:

        logging.exception(
            "Failed to load training page."
        )

        raise HTTPException(

            status_code=500,

            detail="Failed to load training page."

        )

# ----------------------------------------------------
# Feature Engineering Page
# ----------------------------------------------------

@app.get("/feature")
async def feature_engineering(request: Request):

    try:

        columns = []

        if app.state.current_dataset is not None:

            df = pd.read_csv(
                app.state.current_dataset,
                nrows=0
            )

            columns = df.columns.tolist()

        return templates.TemplateResponse(

            request=request,

            name="feature.html",

            context={

                "request": request,

                "columns": columns

            }

        )

    except Exception:

        logging.exception(
            "Failed to load feature engineering page."
        )

        raise HTTPException(

            status_code=500,

            detail="Failed to load feature engineering page."

        )


# ----------------------------------------------------
# Shared helpers: reset workspace + analyze/ingest
# ----------------------------------------------------

def _reset_workspace():
    """
    Clears out everything tied to the previously loaded dataset
    (vector store, chat memory, uploaded/derived files) so a fresh
    dataset - uploaded or demo - starts from a clean slate.
    """

    VectorStoreManager().reset()

    chat_service.memory.clear_all()

    app.state.current_dataset = None

    for old_file in UPLOAD_DIR.glob("*"):
        old_file.unlink()

    for old_report in REPORT_DIR.glob("*.json"):
        old_report.unlink()

    for old_file in CLEANED_DIR.glob("*"):
        old_file.unlink()

    for old_file in FEATURE_DIR.glob("*"):
        old_file.unlink()

    for old_file in TRAINED_MODEL_DIR.glob("*"):
        old_file.unlink()


def _profile_and_ingest(file_path: Path) -> dict:
    """
    Runs profiling on the dataset at file_path, sets it as the
    current dataset, and ingests the profiling report into the
    RAG vector store. Used by both the upload and demo-dataset flows.
    """

    app.state.current_dataset = file_path

    logging.info(
        f"Dataset set at {file_path}"
    )

    df = pd.read_csv(file_path)

    analyzer = DatasetAnalyzer(

        dataframe=df,

        dataset_name=file_path.stem

    )

    report = analyzer.generate_report()

    RAGIngestor().add_report(

        json_path=f"reports/{file_path.stem}.json",

        report_type="profiling"

    )

    logging.info(
        "Dataset profiling completed."
    )

    return report


# ----------------------------------------------------
# Dataset Upload
# ----------------------------------------------------

@app.post("/upload")
async def upload_dataset(
    file: UploadFile = File(...)
):

    try:

        logging.info("Uploading new dataset.")

        # -----------------------------
        # Reset previous project
        # -----------------------------

        _reset_workspace()

        # -----------------------------
        # Save dataset
        # -----------------------------

        file_path = UPLOAD_DIR / file.filename

        with open(file_path, "wb") as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

        logging.info(
            f"Dataset saved at {file_path}"
        )

        # -----------------------------
        # Analyze + ingest
        # -----------------------------

        report = _profile_and_ingest(file_path)

        return report

    except Exception:

        logging.exception(
            "Dataset upload failed."
        )

        raise HTTPException(

            status_code=500,

            detail="Failed to upload dataset."

        )


# ----------------------------------------------------
# Demo Dataset
# ----------------------------------------------------

@app.post("/demo-datasets/{demo_id}")
async def load_demo_dataset(
    demo_id: str
):

    try:

        logging.info(
            f"Loading demo dataset '{demo_id}'."
        )

        demo_filename = DEMO_DATASET_FILES.get(demo_id)

        if demo_filename is None:

            raise HTTPException(

                status_code=404,

                detail="Unknown demo dataset."

            )

        source_path = DEMO_DIR / demo_filename

        if not source_path.exists():

            logging.error(
                f"Demo dataset file missing at {source_path}"
            )

            raise HTTPException(

                status_code=404,

                detail="Demo dataset file is not available."

            )

        # -----------------------------
        # Reset previous project
        # -----------------------------

        _reset_workspace()

        # -----------------------------
        # Copy demo dataset into the
        # uploads dir so it's treated
        # exactly like a user upload
        # -----------------------------

        file_path = UPLOAD_DIR / demo_filename

        shutil.copyfile(
            source_path,
            file_path
        )

        logging.info(
            f"Demo dataset copied to {file_path}"
        )

        # -----------------------------
        # Analyze + ingest
        # -----------------------------

        report = _profile_and_ingest(file_path)

        return report

    except HTTPException:

        raise

    except Exception:

        logging.exception(
            "Demo dataset loading failed."
        )

        raise HTTPException(

            status_code=500,

            detail="Failed to load demo dataset."

        )


# ----------------------------------------------------
# Dataset Cleaning
# ----------------------------------------------------
class CleaningRequest(BaseModel):

    columns_to_remove: list[str] = []

@app.post("/clean")
async def clean_dataset(
    body: CleaningRequest
):

    try:

        logging.info(
            "Starting dataset cleaning."
        )

        if app.state.current_dataset is None:

            raise HTTPException(

                status_code=400,

                detail="Please upload a dataset first."

            )

        cleaner = DataCleaner(

            dataset_path=app.state.current_dataset,

            columns_to_remove=body.columns_to_remove

        )

        cleaned_dataframe, report = cleaner.clean()

        # ----------------------------------
        # Save cleaned dataset
        # ----------------------------------

        cleaned_path = CLEANED_DIR / Path(
            app.state.current_dataset
        ).name

        cleaned_dataframe.to_csv(
            cleaned_path,
            index=False
        )

        app.state.current_dataset = cleaned_path

        logging.info(
            f"Cleaned dataset saved at {cleaned_path}"
        )

        # ----------------------------------
        # Save cleaning report
        # ----------------------------------

        cleaning_report_path = REPORT_DIR / (
            f"{cleaned_path.stem}_cleaning.json"
        )

        with open(
            cleaning_report_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                report,
                file,
                indent=4
            )

        logging.info(
            f"Cleaning report saved at {cleaning_report_path}"
        )

        # ----------------------------------
        # Add cleaning report to RAG
        # ----------------------------------

        RAGIngestor().add_report(

            json_path=str(cleaning_report_path),

            report_type="cleaning"

        )

        logging.info(
            "Cleaning report added to vector store."
        )

        return {

            "success": True,
            "message": "Dataset cleaned successfully.",
            "report": report

        }

    except HTTPException:

        raise

    except Exception:

        logging.exception(
            "Dataset cleaning failed."
        )

        raise HTTPException(

            status_code=500,

            detail="Failed to clean dataset."

        )


# ----------------------------------------------------
# Feature Engineering
# ----------------------------------------------------

class FeatureEngineeringRequest(BaseModel):

    target_column: str
    categorical_encoding: str = "none"
    scaling: str = "none"
    correlation_threshold: float = 0.90

@app.post("/feature")
async def feature_engineering(

    body: FeatureEngineeringRequest

):

    try:

        logging.info(
            "Starting feature engineering."
        )

        if app.state.current_dataset is None:

            raise HTTPException(

                status_code=400,

                detail="Please upload a dataset first."

            )

        engineer = FeatureEngineer(

            dataset_path=app.state.current_dataset,

            target_column=body.target_column,

            categorical_encoding=body.categorical_encoding,

            scaling=body.scaling,

            correlation_threshold=body.correlation_threshold

        )

        engineered_dataframe, report = engineer.engineer()

        # ----------------------------------
        # Save dataset
        # ----------------------------------

        feature_path = FEATURE_DIR / Path(

            app.state.current_dataset

        ).name

        engineered_dataframe.to_csv(

            feature_path,

            index=False

        )

        app.state.current_dataset = feature_path

        logging.info(

            f"Feature engineered dataset saved at {feature_path}"

        )

        # ----------------------------------
        # Save report
        # ----------------------------------

        feature_report_path = REPORT_DIR / (

            f"{feature_path.stem}_feature.json"

        )

        with open(

            feature_report_path,

            "w",

            encoding="utf-8"

        ) as file:

            json.dump(

                report,

                file,

                indent=4

            )

        logging.info(

            f"Feature engineering report saved at {feature_report_path}"

        )

        # ----------------------------------
        # Add report to RAG
        # ----------------------------------

        RAGIngestor().add_report(

            json_path=str(feature_report_path),

            report_type="feature_engineering"

        )

        logging.info(

            "Feature engineering report added to vector store."

        )

        return {

            "success": True,

            "message": "Feature engineering completed successfully.",

            "report": report

        }

    except HTTPException:

        raise

    except Exception:

        logging.exception(

            "Feature engineering failed."

        )

        raise HTTPException(

            status_code=500,

            detail="Failed to perform feature engineering."

        )


# ----------------------------------------------------
# Training
# ----------------------------------------------------

class TrainingRequest(BaseModel):

    target_column: str
    problem_type: str
    selected_models: list[str]
    test_size: float = 0.2
    random_state: int = 42

@app.post("/training")
async def train_models(

    body: TrainingRequest

):

    try:

        logging.info(
            "Starting model training."
        )

        if app.state.current_dataset is None:

            raise HTTPException(

                status_code=400,

                detail="Please upload a dataset first."

            )

        trainer = ModelTrainer(

            dataset_path=app.state.current_dataset,

            target_column=body.target_column,

            selected_models=body.selected_models,

            problem_type=body.problem_type,

            test_size=body.test_size,

            random_state=body.random_state

        )

        report = trainer.train()

        # ----------------------------------------
        # Save Report
        # ----------------------------------------

        report_path = REPORT_DIR / (

            f"{Path(app.state.current_dataset).stem}_training.json"

        )

        with open(

            report_path,

            "w",

            encoding="utf-8"

        ) as file:

            json.dump(

                report,

                file,

                indent=4

            )

        logging.info(
            f"Training report saved at {report_path}"
        )

        # ----------------------------------------
        # Add Report To RAG
        # ----------------------------------------

        RAGIngestor().add_report(

            json_path=str(report_path),

            report_type="training"

        )

        logging.info(
            "Training report added to vector store."
        )

        return {

            "success": True,

            "message": "Models trained successfully.",

            "report": report

        }

    except HTTPException:

        raise

    except Exception:

        logging.exception(
            "Model training failed."
        )

        raise HTTPException(

            status_code=500,

            detail="Failed to train models."

        )


# ----------------------------------------------------
# Download Trained Model
# ----------------------------------------------------

@app.get("/download-model/{model_name}")
async def download_model(

    model_name: str

):

    try:

        model_path = TRAINED_MODEL_DIR / (

            model_name + ".pkl"

        )

        if not model_path.exists():

            raise HTTPException(

                status_code=404,

                detail="Model not found."

            )

        return FileResponse(

            path=model_path,

            filename=model_path.name,

            media_type="application/octet-stream"

        )

    except HTTPException:

        raise

    except Exception:

        logging.exception(
            "Failed to download model."
        )

        raise HTTPException(

            status_code=500,

            detail="Failed to download model."

        )

# ----------------------------------------------------
# AI Assistant
# ----------------------------------------------------

class ChatRequest(BaseModel):

    session_id: str

    question: str


@app.post("/chat/new-session")
async def new_session():

    session_id = chat_service.new_session()

    return {

        "session_id": session_id

    }


@app.post("/chat/ask")
async def ask_question(
    request: ChatRequest
):

    return chat_service.ask(

        session_id=request.session_id,

        question=request.question

    )


@app.delete("/chat/{session_id}")
async def clear_session(
    session_id: str
):

    chat_service.clear_session(
        session_id
    )

    return {

        "message": "Session cleared successfully."

    }