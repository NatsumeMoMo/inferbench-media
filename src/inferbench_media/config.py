from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import yaml


def load_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}
    if not isinstance(payload, dict):
        raise ValueError(f"config must be a mapping: {path}")
    return payload


def copy_config(source: Path, result_dir: Path) -> Path:
    destination = result_dir / "config.yaml"
    shutil.copyfile(source, destination)
    return destination


def resolve_config_path(config_path: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (config_path.parent / path).resolve()


def get_iterations(config: dict[str, Any], iterations_override: int | None = None) -> int:
    if iterations_override is not None:
        iterations = iterations_override
    else:
        iterations = config.get("experiment", {}).get("iterations", 1)
    try:
        parsed = int(iterations)
    except (TypeError, ValueError) as exc:
        raise ValueError("experiment.iterations must be an integer") from exc
    if parsed < 1:
        raise ValueError("experiment.iterations must be >= 1")
    return parsed

