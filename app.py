"""Streamlit web UI for the portfolio-analyst agent.

Run with:
    streamlit run app.py

Opens a browser tab with a form: type a ticker, pick dates, click Analyze.
"""
from __future__ import annotations

from datetime import date

import streamlit as st

from factory import Builder, Registry, Runtime, Trace
from factory.tool_registry import ALL_TOOLS


# --- Page setup -------------------------------------------------------------
st.set_page_config(page_title="Portfolio Analyst", page_icon="📈", layout="wide")
st.title("📈 Portfolio Analyst")
st.caption("Agent factory demo · finance metrics from a price series")

# --- Sidebar: input form ---------------------------------------------------
with st.sidebar:
    st.header("Inputs")
    ticker = st.text_input("Ticker symbol", value="AAPL").upper().strip()
    start = st.date_input("Start date", value=date(2024, 1, 2))
    end = st.date_input("End date", value=date(2024, 12, 31))
    run = st.button("Analyze", type="primary", use_container_width=True)

# --- Load + build the agent (once, cached) ---------------------------------
@st.cache_resource
def build_agent():
    reg = Registry()
    reg.load_dir("agents")
    spec = reg.get("portfolio-analyst")
    return Builder(ALL_TOOLS).build(spec, trace=Trace())

agent = build_agent()

# --- Run on click ----------------------------------------------------------
if run:
    if start >= end:
        st.error("End date must be after start date.")
        st.stop()
    if not ticker:
        st.error("Please enter a ticker symbol.")
        st.stop()

    with st.spinner(f"Analyzing {ticker}..."):
        task = {
            "ticker": ticker,
            "start": start.isoformat(),
            "end": end.isoformat(),
        }
        result = Runtime(agent).run(task)

    out = result.output

    # --- Top metrics row --------------------------------------------------
    st.subheader(f"{ticker} · {start} → {end}")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("First price", f"${out['first_price']:,.2f}")
    last = out["last_price"]
    first = out["first_price"]
    pct = ((last / first) - 1) * 100
    col2.metric("Last price", f"${last:,.2f}", f"{pct:+.2f}%")
    col3.metric("Volatility (ann.)", f"{out['volatility_annualized']*100:.2f}%")
    col4.metric("Sharpe ratio", f"{out['sharpe_ratio']:.2f}")

    # --- Drawdown card ----------------------------------------------------
    mdd = out["max_drawdown"]
    st.subheader("Max drawdown")
    dc1, dc2, dc3 = st.columns(3)
    dc1.metric("Drawdown", f"{mdd['drawdown']*100:.2f}%")
    dc2.metric("Peak date", mdd["peak_date"])
    dc3.metric("Trough date", mdd["trough_date"])

    # --- Price chart ------------------------------------------------------
    st.subheader("Price series")
    # The trace has every tool call + result; pull the get_prices result.
    for evt in result.trace:
        if evt.get("kind") == "tool_result" and evt.get("tool") == "get_prices":
            prices = evt["result"]
            st.line_chart(prices, height=300)
            break

    # --- Raw output -------------------------------------------------------
    with st.expander("Raw output (JSON)"):
        st.json(out)

    st.caption(f"Completed in {result.steps} steps · trace in traces/")
else:
    st.info("👈 Enter a ticker and date range in the sidebar, then click **Analyze**.")
    st.markdown("""
    **What this does**

    Runs the `portfolio-analyst` agent: pulls a price series, computes returns,
    annualized volatility, Sharpe ratio, and max drawdown.

    **Try different tickers** — AAPL, TSLA, MSFT, NVDA, AMZN, GOOG, META, etc.
    Each generates a different deterministic series (synthetic data for the demo).
    """)
