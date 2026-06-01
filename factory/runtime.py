"""Runtime: executes an Agent on a task.

For v1, the "policy" that decides which tool to call next is hard-coded
in the run() method. Swapping in a real LLM-driven policy is a single
replacement of that method — the rest of the factory stays unchanged.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .builder import Agent


@dataclass
class RunResult:
    agent: str
    task: str
    output: dict = field(default_factory=dict)
    steps: int = 0
    trace: list[dict] = field(default_factory=list)


class Runtime:
    def __init__(self, agent: Agent) -> None:
        self.agent = agent
        self.max_steps = int(agent.constraints.get("max_steps", 10))
        self.trace = agent.trace

    def run(self, task: dict) -> RunResult:
        """Execute the agent on a task dict.

        v1 portfolio-analyst task shape:
          {"ticker": "AAPL", "start": "2024-01-02", "end": "2024-12-31"}
        """
        if self.trace:
            self.trace.record("run_start", task=task, agent=self.agent.name)

        # --- Hard-coded policy for v1 -------------------------------------
        # Replace this block with an LLM loop in v2.
        step = 0
        out: dict[str, Any] = {}

        def call(tool: str, **kwargs) -> Any:
            nonlocal step
            step += 1
            if step > self.max_steps:
                raise RuntimeError(f"max_steps ({self.max_steps}) exceeded")
            if self.trace:
                self.trace.record("tool_call", step=step, tool=tool, args=kwargs)
            result = self.agent.tools[tool](**kwargs)
            if self.trace:
                self.trace.record("tool_result", step=step, tool=tool, result=result)
            return result

        # 1) Pull prices
        prices = call(
            "get_prices",
            ticker=task["ticker"],
            start=task["start"],
            end=task["end"],
        )
        out["n_prices"] = len(prices)
        out["first_price"] = prices[sorted(prices)[0]]
        out["last_price"] = prices[sorted(prices)[-1]]

        # 2) Compute returns + metrics
        rets = call("compute_returns", prices=prices)
        out["n_returns"] = len(rets)

        vol = call("volatility", returns=rets)
        out["volatility_annualized"] = vol

        sharpe = call("sharpe_ratio", returns=rets, risk_free=0.0001)
        out["sharpe_ratio"] = sharpe

        mdd = call("max_drawdown", prices=prices)
        out["max_drawdown"] = mdd
        # -------------------------------------------------------------------

        if self.trace:
            self.trace.record("run_end", steps=step, output_keys=sorted(out))

        return RunResult(
            agent=self.agent.name,
            task=task,
            output=out,
            steps=step,
            trace=self.trace.events if self.trace else [],
        )
