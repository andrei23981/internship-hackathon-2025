import subprocess, json
from .ollama_client import ask_ai

def analyze_repo(repo_path):
    pylint = subprocess.run(["pylint", repo_path, "--output-format=json"], capture_output=True, text=True)
    bandit = subprocess.run(["bandit", "-r", repo_path, "-f", "json"], capture_output=True, text=True)
    
    lint_issues = json.loads(pylint.stdout or "[]")
    security_issues = json.loads(bandit.stdout or "{}").get("results", [])
    findings = lint_issues[:5] + security_issues[:5]

    ai_summary = ask_ai(findings)
    return {"score": 100 - len(findings), "summary": ai_summary, "issues": findings}