from pathlib import Path
import shutil

import pandas as pd

from fastapi import FastAPI
from fastapi import UploadFile
from fastapi import File
from fastapi.requests import Request
from pydantic import BaseModel

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from DataProfiling.Profiling import DatasetAnalyzer
from RAG.chat import ChatService
from RAG.ingest import RAGIngestor
from RAG.vectorstore import VectorStoreManager


app = FastAPI()

chat_service = ChatService()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

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

@app.get("/")
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="dataset.html"
    )

@app.get("/assistant")
async def assistant(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="assistant.html"
    )


# ----------------------------------------------------
# Dataset Upload
# ----------------------------------------------------

@app.post("/upload")
async def upload_dataset(
    file: UploadFile = File(...)
):

    # -----------------------------
    # Clear Previous Project
    # -----------------------------

    # Reset vector store
    VectorStoreManager().reset()

    # Clear chat memory
    chat_service.memory.clear_all()

    # Delete old uploaded datasets
    for old_file in UPLOAD_DIR.glob("*"):
        old_file.unlink()

    # Delete old reports
    REPORT_DIR = Path("reports")
    REPORT_DIR.mkdir(exist_ok=True)

    for old_report in REPORT_DIR.glob("*.json"):
        old_report.unlink()

    # -----------------------------
    # Save New Dataset
    # -----------------------------

    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    df = pd.read_csv(file_path)

    analyzer = DatasetAnalyzer(
        dataframe=df,
        dataset_name=file_path.stem
    )

    report = analyzer.generate_report()

    # -----------------------------
    # Ingest Report
    # -----------------------------

    ingestor = RAGIngestor()

    ingestor.add_report(
        json_path=f"reports/{file_path.stem}.json",
        report_type="profiling"
    )

    return report


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