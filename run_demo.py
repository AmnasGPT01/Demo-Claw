"""Demo runner: load the factory, build the portfolio-analyst agent, run it.

Usage:
    python run_demo.py
"""
from __future__ import annotations

import json
from pathlib import Path

from factory import Builder, Registry, Runtime, Trace
from factory.tool_registry import ALL_TOOLS


def main() -> None:
    # 1) Load specs
    reg = Registry()
    n = reg.load_dir("agents")
    print(f"Loaded {n} agent spec(s): {reg.names()}")

    # 2) Build the agent
    spec = reg.get("portfolio-analyst")
    trace_path = Path("traces/portfolio_analyst.jsonl")
    trace = Trace(sink=trace_path)
    agent = Builder(ALL_TOOLS).build(spec, trace=trace)
    print(agent.describe())

    # 3) Run on a sample task
    task = {
        "ticker": "AAPL",
        "start": "2024-01-02",
        "end": "2024-12-31",
    }
    result = Runtime(agent).run(task)

    # 4) Print results
    print("\n--- Result ---")
    print(json.dumps(result.output, indent=2))
    print(f"\nSteps: {result.steps}")
    print(f"Trace written to: {trace_path}")


if __name__ == "__main__":
    main()
