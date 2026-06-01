"""Append-only trace log for agent runs.

Every tool call a runtime makes is recorded here. After a run,
the trace is the artifact you inspect to debug, evaluate, or audit.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


class Trace:
    def __init__(self, sink: str | Path | None = None) -> None:
        self.events: list[dict] = []
        self._sink = Path(sink) if sink else None
        if self._sink:
            self._sink.parent.mkdir(parents=True, exist_ok=True)

    def record(self, kind: str, **payload) -> None:
        evt = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "kind": kind,
            **payload,
        }
        self.events.append(evt)
        if self._sink:
            with self._sink.open("a") as f:
                f.write(json.dumps(evt) + "\n")

    def save(self) -> None:
        """No-op if events are already being appended to disk."""
        pass

    def to_dict(self) -> dict:
        return {"events": self.events}
