"""Spec registry: load and look up agent YAML specs."""
from __future__ import annotations

from pathlib import Path

import yaml


class Registry:
    """In-memory registry of agent specs, keyed by name."""

    def __init__(self) -> None:
        self._specs: dict[str, dict] = {}

    def register(self, spec: dict) -> None:
        name = spec.get("name")
        if not name:
            raise ValueError("spec missing 'name'")
        self._specs[name] = spec

    def load_dir(self, path: str | Path) -> int:
        """Load every *.yaml in path. Returns count loaded."""
        count = 0
        for p in Path(path).glob("*.yaml"):
            self.register(load_spec(p))
            count += 1
        return count

    def get(self, name: str, version: str | None = None) -> dict:
        if name not in self._specs:
            raise KeyError(f"unknown agent: {name}")
        spec = self._specs[name]
        if version and spec.get("version") != version:
            raise KeyError(f"agent {name} has no version {version}")
        return spec

    def names(self) -> list[str]:
        return sorted(self._specs)


def load_spec(path: str | Path) -> dict:
    """Load a single spec file as a dict."""
    with open(path) as f:
        return yaml.safe_load(f)
