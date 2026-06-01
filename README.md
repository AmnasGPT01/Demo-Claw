# Demo-Claw

An experimental **agent factory** for building finance AI agents. You describe an agent in a YAML spec; the factory turns it into a runnable, traceable worker.

## What's in here

- **`agents/`** — declarative agent specs (YAML)
- **`tools/`** — pure-function tools the agents can call (deterministic finance math for v1)
- **`factory/`** — the factory itself: registry, builder, runtime, trace
- **`run_demo.py`** — terminal end-to-end demo
- **`app.py`** — Streamlit web UI (form-based, no commands)
- **`traces/`** — append-only audit logs (created on first run)

## Quick start

### Option A — Web UI (recommended for non-developers)

```bash
pip install -r requirements.txt
streamlit run app.py
```

Opens a browser tab. Type a ticker, pick dates, click **Analyze**. You get metrics and a price chart.

### Option B — Terminal

```bash
pip install -r requirements.txt
python run_demo.py
```

Prints the same analysis to the terminal. Writes a trace to `traces/portfolio_analyst.jsonl`.

## How it works

```
YAML spec  →  Registry loads it
          →  Builder wires up the right tools
          →  Runtime executes the agent on a task
          →  Trace records every step
```

### v1 agent: `portfolio-analyst`

Given a ticker and date range, it:

1. Fetches daily prices
2. Computes daily returns
3. Annualized volatility
4. Sharpe ratio (default 2.5% risk-free)
5. Max drawdown with peak/trough dates

### Adding a new agent

Write a new YAML spec in `agents/`, list the tools it needs (add them to `tools/` first), done. No changes to the factory.

```yaml
name: my-new-agent
version: 0.1.0
role: What this agent does
tools:
  - some_tool
constraints:
  max_steps: 10
```

The builder will refuse to build the spec if any required tool is missing — fail loud, not silent.

## Project layout

```
Demo-Claw/
├── agents/
│   └── portfolio_analyst.yaml    # agent spec
├── tools/
│   ├── __init__.py
│   ├── __main__.py               # `python -m tools` lists registered tools
│   └── finance.py                # finance math (get_prices, returns, volatility, sharpe, drawdown)
├── factory/
│   ├── __init__.py
│   ├── registry.py               # load + look up specs
│   ├── builder.py                # spec + tools → Agent
│   ├── runtime.py                # Agent + task → result
│   ├── trace.py                  # append-only audit log
│   └── tool_registry.py          # catalog of available tools
├── run_demo.py                   # terminal entry point
├── app.py                        # streamlit web UI
├── requirements.txt
└── README.md
```

## v1 design notes

- **No LLM calls yet.** The runtime has a hard-coded policy (which tool to call in which order) so the factory mechanics are testable without API keys. Swapping in an LLM-driven policy is a single-method replacement in `factory/runtime.py`.
- **Deterministic data.** `get_prices` generates a reproducible synthetic series so demos are stable. Swap in a real data source (Yahoo, Alpha Vantage) when ready.
- **Strict tool resolution.** The builder fails if the spec asks for a tool that isn't registered — better to break the build than to silently drop a capability.
- **Traces are first-class.** Every tool call is logged with timestamp, args, and result. Inspect `traces/*.jsonl` to debug or evaluate.

## Roadmap

- LLM-driven tool selection (replace hard-coded policy in `runtime.py`)
- Real price data source
- Eval harness (run the agent against a benchmark set, compare outputs)
- Memory layer (cross-run state)
- Multi-agent orchestration (supervisor + specialists)
