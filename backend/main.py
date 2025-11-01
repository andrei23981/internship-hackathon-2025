from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from services.analyze import analyze_repo

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/api/analyze")
def analyze(repo_path: str = Query(...)):
    return analyze_repo(repo_path)