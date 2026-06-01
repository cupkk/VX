from __future__ import annotations

from pathlib import Path
from typing import Any

SUPPORTED_EXTENSIONS = {".md", ".txt", ".json"}
IGNORED_PARTS = {"style-guides", "README.md"}
MAX_FILES = 20
MAX_CHARS_PER_FILE = 1200
MAX_COMBINED_CHARS = 5000


def _is_resource_file(path: Path, resource_dir: Path) -> bool:
    relative = path.relative_to(resource_dir)
    if any(part in IGNORED_PARTS for part in relative.parts):
        return False
    return path.suffix.lower() in SUPPORTED_EXTENSIONS


def _excerpt(text: str) -> str:
    cleaned_lines = [line.strip() for line in text.splitlines() if line.strip()]
    cleaned = "\n".join(cleaned_lines)
    return cleaned[:MAX_CHARS_PER_FILE]


def load_resource_context(root: Path) -> dict[str, Any]:
    resource_dir = root / "resource"
    if not resource_dir.exists():
        return {"root": "resource", "files": [], "combined_excerpt": ""}

    files: list[dict[str, Any]] = []
    for path in sorted(resource_dir.rglob("*")):
        if not path.is_file() or not _is_resource_file(path, resource_dir):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        excerpt = _excerpt(text)
        if not excerpt:
            continue
        files.append(
            {
                "path": path.relative_to(root).as_posix(),
                "chars": len(text),
                "excerpt": excerpt,
            }
        )
        if len(files) >= MAX_FILES:
            break

    combined = "\n\n".join(f"[{item['path']}]\n{item['excerpt']}" for item in files)
    return {
        "root": "resource",
        "files": files,
        "combined_excerpt": combined[:MAX_COMBINED_CHARS],
    }
