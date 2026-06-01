"""Builder: turns a spec + tool registry into a runnable Agent."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from .trace import Trace


@dataclass
class Agent:
    """A materialized agent. Holds its spec, tools, and a trace recorder."""
    name: str
    version: str
    role: str
    tools: dict[str, Callable] = field(default_factory=dict)
    constraints: dict = field(default_factory=dict)
    trace: Trace | None = None

    def describe(self) -> str:
        return (
            f"Agent(name={self.name}, version={self.version}, "
            f"tools={sorted(self.tools)})"
        )


class Builder:
    """Resolves a spec into an Agent using a tool registry."""

    def __init__(self, tool_registry: dict[str, Callable]) -> None:
        self._tools = tool_registry

    def build(self, spec: dict, trace: Trace | None = None) -> Agent:
        # Resolve only the tools the spec asks for. Fail loud on missing.
        resolved: dict[str, Callable] = {}
        for tool_name in spec.get("tools", []):
            if tool_name not in self._tools:
                raise KeyError(
                    f"spec '{spec.get('name')}' requires tool '{tool_name}' "
                    f"which is not in the tool registry"
                )
            resolved[tool_name] = self._tools[tool_name]

        return Agent(
            name=spec["name"],
            version=spec.get("version", "0.0.0"),
            role=spec.get("role", "").strip(),
            tools=resolved,
            constraints=spec.get("constraints", {}),
            trace=trace or Trace(),
        )
