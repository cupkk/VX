from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ProjectConfig:
    profile: dict[str, Any]
    policy: dict[str, Any]
    topics: dict[str, Any]


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def load_project_config(root: Path) -> ProjectConfig:
    config_dir = root / "config"
    return ProjectConfig(
        profile=read_json(config_dir / "profile.json"),
        policy=read_json(config_dir / "policy.json"),
        topics=read_json(config_dir / "topics.json"),
    )
