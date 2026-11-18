# Trading Dashboard

A private, mobile-friendly Streamlit dashboard connected to a separate observation-only cloud worker and Supabase research store.

## Current capabilities

- Multi-market daily scanner covering equities, broad ETFs, metals, energy/commodity proxies, rates/currencies, and crypto.
- Rules-based trend, momentum, RSI, weekly confirmation, volatility, relative-strength, and ATR reference analysis.
- Cloud command center showing the latest scan, scan health, sector/asset proxy rotation, research shortlist, portfolio concentration, and historical setup diagnostics.
- Persistent virtual paper account with positions, cash, journal, realized/unrealized P&L, and daily snapshots stored in Supabase.
- Strategy validation lab tracking first-seen signal observations and forward outcomes.
- Read-only intraday monitoring of paper-position stop/target levels.
- Historical shared-capital portfolio replay with costs, chronological holdout, walk-forward folds, pooled setup attribution, and asset-class diagnostics.
- Separate crypto and non-crypto holdout portfolios, each using fresh independent starting capital, plus attribution from trades accepted in the combined portfolio.

## Research and safety boundaries

- The scanner, replay engine, and intraday monitor are research/simulation tools, not financial advice or evidence of a durable trading edge.
- The cloud worker is observation-only. Alpaca access is read-only; it does not submit orders or change broker positions.
- The dashboard's paper account is virtual and stored separately from Alpaca.
- Standalone asset-class returns are independent simulations with separate capital. Their returns are not additive to the combined portfolio.
- Combined-portfolio asset-class P&L is closed-trade attribution from trades accepted under shared cash and risk constraints.
- Walk-forward pooled P&L sums closed trades across test folds; it is not a compounded portfolio return.
- Historical universe data is not point-in-time and may contain survivorship bias. Yahoo Finance data can be delayed, incomplete, rate-limited, or revised.
- Do not place secrets, passwords, API keys, broker credentials, or personal financial information in source control.

## Deployment

The dashboard is designed for Streamlit Community Cloud. Set these values in Streamlit app Secrets:

```toml
APP_PASSWORD = "your-private-dashboard-password"
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_SECRET_KEY = "your-server-side-supabase-key"
```

Use a server-side Supabase key only in the Streamlit Secrets store. Never expose it in browser code or commit it to GitHub.

The cloud worker is deployed separately as a Render background worker. It writes scan reports and simulation results to the same Supabase project; the dashboard reads those reports.

## Run locally

```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# macOS / Linux:
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

The dashboard opens at http://localhost:8501.

## Validation

GitHub Actions compiles `app.py` on pushes and pull requests. The cloud worker has its own deterministic unit-test workflows; its results are separate from the dashboard's syntax check.


## Dashboard V3.28 broker lifecycle and risk guardrails
- Cloud scanner's Alpaca panel now displays the latest paper-account daily-loss guardrail: starting equity, daily P&L, daily loss percentage, halt/clear state, and trading date.
- Decision history now includes broker-confirmed lifecycle state, filled and remaining share quantities, and attached protective exit-leg states from the worker's nested read-only order snapshot.
- Broker lifecycle statuses are included in the broker-order count. Unknown broker states are not counted as confirmed broker orders.
- All additions are read-only. The dashboard continues to keep the Supabase virtual paper account separate from the Alpaca paper brokerage account.


## Dashboard V3.29 broker position protection audit
The Cloud Scanner's read-only Alpaca decision table now includes the broker-reported open position quantity, stop-exit quantity, target-exit quantity, and a protection audit status and reason code. The dashboard counts active protection exceptions for review while excluding closed positions and superseded entry orders. PROTECTED is shown only when both active bracket exits exactly match the actual open position quantity. This is a read-only audit; it does not modify broker orders or either paper account.
