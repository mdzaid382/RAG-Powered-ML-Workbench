from pathlib import Path
import shutil

import pandas as pd

from fastapi import FastAPI
from fastapi import UploadFile
from fastapi import File
from fastapi.requests import Request

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from DataProfiling.Profiling import DatasetAnalyzer


app = FastAPI()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

templates = Jinja2Templates(directory="Webapp/templates")

app.mount(
    "/static",
    StaticFiles(directory="Webapp/static"),
    name="static"
)

@app.get("/")
async def home(request: Request):

    return templates.TemplateResponse(
        "dataset.html",
        {
            "request": request
        }
    )


@app.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):

    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    df = pd.read_csv(file_path)

    analyzer = DatasetAnalyzer(
        dataframe=df,
        dataset_name=file_path.stem
    )

    report = analyzer.generate_report()

    return report
