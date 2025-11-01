import json
import os
import shutil
import subprocess
import tempfile
from contextlib import contextmanager
from typing import Iterator
from urllib.parse import urlparse

from .ollama_client import ask_ai


def _looks_like_remote_repo(source: str) -> bool:
    parsed = urlparse(source)
    if parsed.scheme in {"http", "https", "ssh", "git"}:
        return True
    return source.startswith("git@")


@contextmanager
def _prepare_repository(source: str) -> Iterator[str]:
    if not source:
        raise ValueError("Repository reference is empty.")

    source = source.strip()
    temp_dir = None
    repo_path = source

    if _looks_like_remote_repo(source):
        temp_dir = tempfile.mkdtemp(prefix="codementor-clone-")
        repo_path = os.path.join(temp_dir, "repo")
        clone = subprocess.run(
            ["git", "clone", "--depth", "1", source, repo_path],
            capture_output=True,
            text=True,
            check=False,
        )
        if clone.returncode != 0:
            shutil.rmtree(temp_dir, ignore_errors=True)
            detail = clone.stderr.strip() or clone.stdout.strip() or "Clone failed"
            raise RuntimeError(f"Nu s-a putut clona repository-ul: {detail}")
    elif not os.path.exists(source):
        raise ValueError("Calea catre repository nu exista pe server.")

    try:
        yield repo_path
    finally:
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)


def _safe_run(command: list[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command, capture_output=True, text=True, check=False
        )
    except FileNotFoundError as exc:
        tool = command[0]
        raise RuntimeError(
            f"Unealta {tool} nu este disponibila pe serverul de analiza."
        ) from exc


def analyze_repo(source: str):
    with _prepare_repository(source) as repo_path:
        pylint = _safe_run(["pylint", repo_path, "--output-format=json"])
        bandit = _safe_run(["bandit", "-r", repo_path, "-f", "json"])

        lint_issues = json.loads(pylint.stdout or "[]")
        security_raw = json.loads(bandit.stdout or "{}")
        security_issues = security_raw.get("results", [])

        findings = lint_issues[:5] + security_issues[:5]
        ai_summary = ask_ai(findings)
        score = max(0, 100 - len(findings))

        return {"score": score, "summary": ai_summary, "issues": findings}
