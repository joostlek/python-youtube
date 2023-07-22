"""Tests for the YouTube Library."""
import json
from pathlib import Path
from typing import Any


def load_fixture(filename: str) -> str:
    """Load a fixture."""
    path = Path(__package__) / "fixtures" / filename
    return path.read_text(encoding="utf-8")


def construct_fixture(object_type: str, parts: list[str], object_number: int) -> Any:
    """Construct a fixture from different files."""
    base_path = Path(__package__) / "fixtures" / object_type
    base_json = json.loads((base_path / "base.json").read_text(encoding="utf-8"))

    object_json = base_path / str(object_number)
    base_object_json = json.loads(
        (object_json / "base.json").read_text(encoding="utf-8"),
    )
    for part in parts:
        part_json_path = object_json / f"{part}.json"
        part_json = json.loads(part_json_path.read_text(encoding="utf-8"))
        base_object_json[part] = part_json
    base_json["items"].append(base_object_json)
    return base_json
