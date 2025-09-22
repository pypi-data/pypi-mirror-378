"""Tech stack detection helpers (Python port)."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def detect_tech_stack(project_root: Path, config: Optional[Dict] = None) -> Dict[str, str]:
    project_root = Path(project_root)
    detected: Dict[str, str] = {}

    package_json = project_root / "package.json"
    if package_json.exists():
        import json

        try:
            data = json.loads(package_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}
        deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
        if any(key in deps for key in ("react", "next", "@types/react")):
            detected["frontend"] = "react"
            if "next" in deps:
                detected["framework"] = "nextjs"
        if any(key in deps for key in ("express", "fastify", "@nestjs/core")):
            detected["backend"] = "node"
            if "express" in deps:
                detected["framework"] = "express"
            elif "fastify" in deps:
                detected["framework"] = "fastify"
            elif "@nestjs/core" in deps:
                detected["framework"] = "nestjs"

    requirements = project_root / "requirements.txt"
    pyproject = project_root / "pyproject.toml"
    if requirements.exists() or pyproject.exists():
        detected.setdefault("backend", "python")
        req_text = _read_text(requirements)
        py_text = _read_text(pyproject)
        if "fastapi" in req_text or "fastapi" in py_text:
            detected.setdefault("framework", "fastapi")
        elif "django" in req_text or "django" in py_text:
            detected.setdefault("framework", "django")
        elif "flask" in req_text or "flask" in py_text:
            detected.setdefault("framework", "flask")

    if detected.get("frontend") and detected.get("backend"):
        detected["type"] = "full-stack"
    elif detected.get("frontend"):
        detected["type"] = "frontend"
    elif detected.get("backend"):
        detected["type"] = "backend"
    else:
        detected["type"] = "unknown"

    return detected
