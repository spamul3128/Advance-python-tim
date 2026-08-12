#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
IGNORED_DIRS = {".idea", ".git", "scripts", "__pycache__"}

PURPOSE_HINTS = {
    "10-Advanced-Python-Features": "Collection of focused Python examples that demonstrate advanced language features and patterns.",
    "3-Beginner-AI-Projects": "Starter AI project set intended for hands-on learning and progressive experimentation.",
    "Advanced-Langflow-Web-Agent": "Langflow-powered web agent for orchestrating browsing and LLM-driven task execution.",
    "AdvancedMCPServerWithAuth": "Full-stack Model Context Protocol server with authentication and client-facing frontend.",
    "Agentspan-Course": "Course workspace for building, testing, and evaluating AI agents in practical scenarios.",
    "AI-Image-Generator": "Image generation playground with scripts that demonstrate prompt-driven AI image workflows.",
    "AIBrandSearch": "Brand and product discovery app that combines search, ranking, and LLM-assisted insights.",
    "AmazonPriceCompetitorAnalysisLLM": "LLM-based competitor analysis workflow focused on Amazon pricing intelligence.",
    "API-For-Your-LLM": "API wrapper project for exposing LLM capabilities through simple HTTP endpoints.",
    "BattleBotsApp": "Backend and frontend application for managing and visualizing battle bot competitions.",
    "BuildAndDeployAIAgent": "Template project for creating, running, and deploying an AI agent workflow.",
    "DeepgramVoiceAgent": "Voice-enabled AI agent that integrates Deepgram and domain-specific helper functions.",
    "DevLaunchDiscordBot": "Discord bot that combines messaging automation, data storage, and LLM-powered features.",
    "Django-YouTube-Clone": "Django application implementing core YouTube-style content and interaction patterns.",
    "FastAPIPhotoVideoSharing": "FastAPI-based media sharing service for handling photo/video upload and retrieval flows.",
    "FastAPIProject": "FastAPI service project with modular app structure and database-backed endpoints.",
    "I-Learned-Python-With-These-Projects": "Learning project set that reinforces Python basics through small practical scripts.",
    "Inngest-RAG-App-Demo": "Demo of event-driven Retrieval-Augmented Generation with app and Streamlit interfaces.",
    "LangGraph-Tutorial": "Tutorial workspace for experimenting with graph-based agent orchestration patterns.",
    "Langchain-Transformers-Python": "Examples that combine LangChain abstractions with transformer model workflows.",
    "LocalAIAgentWithRAG": "Local-first AI agent that performs retrieval over project data before responding.",
    "OllamaTutorial": "Hands-on Ollama tutorial for local model requests and lightweight integration patterns.",
    "ProductionGradeRAGPythonApp": "Production-oriented RAG application scaffold with deployment-friendly structure.",
    "PythonAIAgentFromScratch": "From-scratch implementation path for understanding AI agent core components.",
    "PythonAIAgentin10Minutes": "Rapid-start AI agent example optimized for quick setup and first run.",
    "PythonAgentAI": "General AI agent project with runnable entrypoint and customizable behavior.",
    "PythonMCPServer": "Python implementation of an MCP-compatible server for tool/context integration.",
    "Scaleable-Web-AI-Agent": "Scalable web AI agent architecture with modular runtime components.",
    "Sorting-Algorithm-Visualizer": "Visualization and educational walkthroughs for common sorting algorithms.",
    "Streamlit-Intro-App": "Introductory Streamlit app for learning app layout, state, and interaction basics.",
}


def top_level_projects(root: Path) -> list[Path]:
    projects = []
    for child in sorted(root.iterdir(), key=lambda p: p.name.lower()):
        if not child.is_dir() or child.name in IGNORED_DIRS or child.name.startswith("."):
            continue
        projects.append(child)
    return projects


def detect_manifests(project: Path) -> list[str]:
    manifests = []
    for name in ("pyproject.toml", "requirements.txt", "package.json", "uv.lock"):
        if (project / name).exists():
            manifests.append(name)
    for scoped in ("backend/pyproject.toml", "frontend/package.json", "backend/requirements.txt"):
        if (project / scoped).exists():
            manifests.append(scoped)
    return manifests


def detect_entrypoints(project: Path) -> list[str]:
    candidates = [
        "main.py",
        "app.py",
        "frontend.py",
        "bot.py",
        "agent.py",
        "streamlit_app.py",
        "tutorial.py",
        "sample_request.py",
        "youtube/manage.py",
        "backend/main.py",
        "frontend/src/main.tsx",
    ]
    found = [c for c in candidates if (project / c).exists()]

    if not found:
        # Include first few scripts as fallback for script-heavy projects.
        py_files = sorted(
            p.relative_to(project).as_posix()
            for p in project.glob("*.py")
            if p.is_file()
        )
        found.extend(py_files[:3])

    return found


def infer_run_hint(project: Path, manifests: list[str], entrypoints: list[str]) -> list[str]:
    lines: list[str] = []
    if "pyproject.toml" in manifests:
        lines.append("uv sync")
        if entrypoints:
            lines.append(f"uv run python {entrypoints[0]}")
    elif "requirements.txt" in manifests:
        lines.append("python -m venv .venv")
        lines.append("source .venv/bin/activate")
        lines.append("pip install -r requirements.txt")
        if entrypoints:
            lines.append(f"python {entrypoints[0]}")
    elif "frontend/package.json" in manifests or "package.json" in manifests:
        lines.append("npm install")
        lines.append("npm run dev")
    elif entrypoints:
        lines.append(f"python {entrypoints[0]}")
    else:
        lines.append("# Add a run command once an executable entrypoint is confirmed")
    return lines


def list_key_items(project: Path) -> list[str]:
    items = []
    for child in sorted(project.iterdir(), key=lambda p: p.name.lower()):
        if child.name.startswith("."):
            continue
        if child.is_dir():
            items.append(f"{child.name}/")
        else:
            items.append(child.name)
    return items[:16]


def make_readme(project: Path, purpose: str, manifests: list[str], entrypoints: list[str], items: list[str]) -> str:
    manifest_text = ", ".join(f"`{m}`" for m in manifests) if manifests else "None detected"
    entry_text = ", ".join(f"`{e}`" for e in entrypoints) if entrypoints else "No explicit entrypoint detected"

    run_lines = "\n".join(f"{cmd}" for cmd in infer_run_hint(project, manifests, entrypoints))
    layout_lines = "\n".join(f"- `{item}`" for item in items) if items else "- (No files detected)"

    return f"""# {project.name}

## Overview
{purpose}

## Project Snapshot
- **Language/Stack**: Primarily Python (plus any frontend stack if present)
- **Dependency Files**: {manifest_text}
- **Likely Entrypoints**: {entry_text}

## Folder Layout (Top Level)
{layout_lines}

## Setup
Use the command path that matches this project structure.

```bash
{run_lines}
```

## Logic Walkthrough
1. **Initialize environment** from dependency manifests and configuration files.
2. **Run the primary entrypoint** to start the app, API, bot, or script workflow.
3. **Core modules handle domain logic** (for example: agents, retrieval, web operations, or UI routing).
4. **Outputs are returned** as console results, API responses, generated artifacts, or frontend updates.

## Code Reading Guide
- Start with the main entry file listed above to understand control flow.
- Review helper modules and domain-specific folders (for example `app/`, `src/`, `agents/`, `backend/`, `frontend/`).
- Check config/dependency files to understand runtime and package expectations.

## Notes
This README was generated to provide a reliable starting point and can be refined with project-specific behavior, APIs, and deployment details.
"""


def _pdf_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def write_simple_pdf(path: Path, title: str, lines: Iterable[str]) -> None:
    safe_lines = [line[:105] for line in lines]
    text_cmds = ["BT", "/F1 11 Tf", "50 790 Td", "14 TL"]
    text_cmds.append(f"({_pdf_escape(title)}) Tj")
    text_cmds.append("T*")
    for line in safe_lines:
        text_cmds.append(f"({_pdf_escape(line)}) Tj")
        text_cmds.append("T*")
    text_cmds.append("ET")
    stream = "\n".join(text_cmds).encode("latin-1", errors="replace")

    objs: list[bytes] = []
    objs.append(b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n")
    objs.append(b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n")
    objs.append(
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >> endobj\n"
    )
    objs.append(f"4 0 obj << /Length {len(stream)} >> stream\n".encode("latin-1") + stream + b"\nendstream endobj\n")
    objs.append(b"5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n")

    out = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for obj in objs:
        offsets.append(len(out))
        out.extend(obj)

    xref_offset = len(out)
    out.extend(f"xref\n0 {len(offsets)}\n".encode("latin-1"))
    out.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        out.extend(f"{offset:010d} 00000 n \n".encode("latin-1"))

    out.extend(
        f"trailer << /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("latin-1")
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(out)


def generate_docs() -> None:
    projects = top_level_projects(ROOT)

    for project in projects:
        purpose = PURPOSE_HINTS.get(
            project.name,
            "Project documentation generated from discovered files and structure.",
        )
        manifests = detect_manifests(project)
        entrypoints = detect_entrypoints(project)
        items = list_key_items(project)

        readme = make_readme(project, purpose, manifests, entrypoints, items)
        (project / "README.md").write_text(readme, encoding="utf-8")

        pdf_lines = [
            f"Project: {project.name}",
            "",
            "Overview:",
            purpose,
            "",
            "Entrypoints:",
            ", ".join(entrypoints) if entrypoints else "No explicit entrypoint detected",
            "",
            "Dependency files:",
            ", ".join(manifests) if manifests else "None detected",
            "",
            "Reading order:",
            "1) Start with entrypoint file",
            "2) Inspect app/src/agents/backend/frontend modules",
            "3) Review config and dependency manifests",
            "4) Run project and trace output flow",
        ]
        write_simple_pdf(project / "docs" / "logic-and-reading.pdf", f"{project.name} Logic Guide", pdf_lines)

    print(f"Generated README.md and docs/logic-and-reading.pdf for {len(projects)} projects.")


if __name__ == "__main__":
    generate_docs()

