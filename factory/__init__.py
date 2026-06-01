"""Agent factory: turns declarative specs into runnable, traceable agents.

Pieces:
- registry:  versions and looks up agent specs by name
- trace:     append-only record of every tool call, for observability
- builder:   materializes a spec + tool registry into a runnable Agent
- runtime:   executes an Agent on a task, enforcing constraints
"""
from .registry import Registry, load_spec
from .trace import Trace
from .builder import Builder, Agent
from .runtime import Runtime, RunResult

__all__ = [
    "Registry",
    "load_spec",
    "Trace",
    "Builder",
    "Agent",
    "Runtime",
    "RunResult",
]
