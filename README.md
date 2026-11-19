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


## Dashboard V3.30 remaining protective quantities
The Cloud Scanner's read-only broker protection table now displays the remaining stop and target share quantities after any partial exit fills, rather than showing original child-order quantities. This makes the displayed values directly comparable to the broker's current open position. Dashboard code remains observation-only.


## Dashboard V3.33 broker data quality

The Cloud Scanner's broker decision table now exposes parent-order fill-quantity validation separately from lifecycle status and protective-exit coverage. Explicitly invalid broker fill quantities are counted in a dedicated alert metric and displayed as `BROKER_DATA_INVALID`; missing quantity metadata remains `UNAVAILABLE` rather than being presented as valid. This is read-only diagnostics.


## Dashboard V3.32 broker replacement-chain visibility

The Alpaca broker audit table now displays replacement-chain classification and the ordered broker order IDs when the worker supplies that metadata. Incomplete, ambiguous, cyclic, and inconsistent broker links remain visible rather than being presented as a verified replacement chain.


## Dashboard V3.33 replacement-aware protection audit

The broker audit view now distinguishes the replacement-chain classification and order IDs from the exact broker order used for position-protection verification. This makes it clear when protection was assessed against the latest verified replacement rather than the original parent order.


## Dashboard V3.45 shadow research evidence readiness
The Cloud Scanner includes a read-only panel for the worker's latest unified research evidence snapshot. It shows research-supported shadow groups, groups not established, source observation counts, and per-group checks/reasons. The panel requires the worker migration `202611190002_research_evidence_readiness.sql` to be applied in Supabase. These diagnostics have no candidate-ranking, position-sizing, stop, execution-gate, or order authority.


## Dashboard V3.46 downside-tail research context
The unified shadow research evidence table now surfaces matched loss rate, worst-decile average return, fifth-percentile return, and worst observed return when supplied by the worker. An explainer distinguishes these close-to-close signal-horizon statistics from portfolio maximum drawdown, intraday adverse excursion, and realized broker losses. These fields are descriptive only and do not affect research readiness or trading decisions.


## Dashboard V3.47 matched cross-regime downside intelligence
The unified shadow research panel now displays pairwise downside-tail differences between market regimes, matched exactly on setup, score bucket, and horizon. It shows loss-rate, worst-decile, and fifth-percentile differences with per-regime sample counts and explicit descriptive-only interpretation. Missing or thin pairs remain not established. These comparisons are not causal and have no readiness, ranking, sizing, stop, gate, or order authority.


## Dashboard V3.48 volatility-transition outcome study
The unified shadow research panel now displays matched volatility-transition outcome comparisons against stable cohorts at the same current volatility, matched exactly on setup, score bucket, and horizon. It shows chronological training/holdout samples, mean-return differences, holdout cutoff, and explicit not-established reasons. The study is observational, not causal or predictive, and has no readiness, ranking, sizing, stop, gate, or order authority.


## Dashboard V3.50 post-volatility-transition response matrix

The unified shadow research panel now displays strategy response at exact session ages 1, 5, 10, and 20 after a point-in-time volatility transition, crossed with forward outcome horizons of 1, 5, 10, and 20 sessions. It shows matched transition/stable training and holdout sample counts, mean-return differences, holdout win rates and downside-tail context, the shared chronological cutoff, and fail-closed reasons. Transition age is distinct from the forward return horizon. The worker excludes recent post-transition observations through the longest checkpoint from the stable baseline. These observational comparisons are not causal or predictive and have no readiness, ranking, sizing, stop, gate, or order authority. The panel requires the corresponding Worker PR #5 code and the earlier worker evidence-persistence migration/snapshot pipeline.


## Volatility response uncertainty (V3.50)
- Displays the 95% weekly date-block bootstrap interval for each transition-versus-stable holdout mean-return difference, plus the number of weekly blocks and uncertainty status.
- Intervals are intentionally withheld when either cohort has fewer than eight distinct holdout weeks. The estimate is descriptive uncertainty context, not causal or predictive confidence.


## Dashboard V3.51 calendar-year volatility-response robustness
- The post-transition response matrix now summarizes supported calendar years and positive/negative year counts separately for training and holdout.
- A second table expands each calendar year, showing matched transition/stable sample counts, cohort mean returns, their difference, and whether the year meets the minimum of 10 observations per cohort.
- Training support is classified as multi-year, single-year, or insufficient. Holdout periods remain separate and cannot influence training classifications.
- These are descriptive observational diagnostics only; no candidate ranking, sizing, stops, execution gates, or order authority is changed.


## Dashboard V3.52 volatility classification sensitivity
- Adds a read-only table comparing the existing 20-session / 252-session / 25th-75th percentile volatility definition with six pre-specified alternatives.
- Displays unique signal-date coverage, regime-label agreement, transition-label agreement, and observed transition dates for each definition.
- These are point-in-time classification diagnostics only. No strategy returns are used to select thresholds, and no ranking, sizing, stops, gates, execution, or order authority changes.
- Requires Worker PR #8 sensitivity metadata and the existing research evidence snapshot pipeline.


### Version 3.53 — Full-history volatility sensitivity
- Adds read-only full-session LOW/NORMAL/HIGH occupancy and unknown-session coverage across the seven pre-specified volatility definitions.
- Displays transition counts and alternative-definition transition-date displacement versus the unchanged baseline.
- Diagnostics are descriptive, point-in-time, and have no ranking, sizing, stop, gate, or order authority.


### Version 3.54 — Holdout-boundary purge visibility
- Shows how many training observations are purged because their forward-return windows overlap the chronological holdout period.
- Keeps the 1/5/10/20-session transition-age and forward-horizon matrix descriptive and shadow-only.
