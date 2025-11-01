from fastapi import FastAPI, Query, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from services.analyze import analyze_repo
from pydantic import BaseModel
import zipfile, tempfile, os, shutil
from services.analyze_file import analyze_single_file


class AnalyzePayload(BaseModel):
    repo: str

    def normalized(self) -> str:
        value = (self.repo or "").strip()
        if not value:
            raise ValueError("Repository reference is required.")
        return value

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/api/analyze")
def analyze(repo_path: str = Query(...)):
    try:
        return analyze_repo(repo_path)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@app.post("/api/analyze")
def analyze_from_body(payload: AnalyzePayload):
    try:
        return analyze_repo(payload.normalized())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

@app.post("/api/upload")
def upload_and_analyze(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".zip"):
        raise HTTPException(
            status_code=400, detail="Fisierul incarcat trebuie sa fie o arhiva .zip."
        )

    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, file.filename or "upload.zip")
    try:
        with open(zip_path, "wb") as f:
            f.write(file.file.read())
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)
        return analyze_repo(temp_dir)
    except zipfile.BadZipFile as exc:
        raise HTTPException(status_code=400, detail="Arhiva .zip este corupta.") from exc
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

@app.post("/api/analyze-file")
def analyze_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Numele fișierului este obligatoriu.")

    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, file.filename or "uploaded_file")
    
    try:

        with open(file_path, "wb") as f:
            f.write(file.file.read())
        

        return analyze_single_file(file_path)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Eroare la analiza fisierului: {str(exc)}") from exc
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
