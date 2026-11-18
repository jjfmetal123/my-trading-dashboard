# Trading Project Handoff

**Last maintained:** 2026-11-18 (updated after V5.28 paper-execution foundation)  
**Purpose:** Durable checkpoint for continuing the trading dashboard and observation-only cloud worker across ChatGPT conversations.

> **Resume phrase:** “Resume the trading project.”  
> On resume, read this file first, then inspect the live GitHub repositories and deployment state before changing code. Treat this document as a checkpoint, not a substitute for verifying current source.

## 1. Project repositories and deployment

| Component | Repository / service | Known state |
|---|---|---|
| Dashboard | [jjfmetal123/my-trading-dashboard](https://github.com/jjfmetal123/my-trading-dashboard) | Streamlit dashboard; README confirms capabilities and research/safety boundaries |
| Cloud worker | [jjfmetal123/trading-cloud-worker](https://github.com/jjfmetal123/trading-cloud-worker) | **V5.28** adds a separate, disabled-by-default Alpaca paper-order adapter; not yet connected to automatic signal routing |
| Render workspace | My Workspace — `tea-dbu9vo6tlv9c73bqbdh0` | User-confirmed workspace |
| Render worker service | `srv-dbua8frm8hqs73f895h0` | Worker V5.26 was confirmed deployed successfully in Render logs |
| Dashboard deployment | Streamlit Community Cloud (per dashboard README) | Current deployment status must be checked; do not assume latest commit is live |

### Known code checkpoints

- Worker V5.27 scan diagnostics: commit `eb6b72431dbbc4f70ac51197f39cdbd0a964b464` (per-symbol missing reasons, stale-price warnings).
- Worker zero-coverage handling / reason refinement: commit `22b737387e0efb5495659710f8d2f1fbd21b1f95`.
- Worker V5.27 documentation: commits `d76aa7811f415ddc30d01b930edd03be9bcbc2ce` and `ee7ca2e8e9568a0a3f9740ed5cfdd4804db83b98`.
- Worker V5.26 version bump: commit `7e8cdb23d733ff70956f3d47892b9bd2a59b81bc`.
- Worker correlation sample-size change: commit `14fc8a80bf9c04eb24d5dfaca2e7c6fc215bc5f1`.
- Worker V5.26 README update: commit `eeaa4442a0dbb235e523f5fe3d5aa76eddcbbd17`.
- Worker GitHub Actions checks previously passed:
  - Python checks run `44387005586` (completed, success).
  - Python tests run `44386961274` (completed, success).
- Dashboard portfolio-risk visibility update previously recorded at commit `2eb42cc2f677745ad065f7e0398fdfb009babbb7`.
- Dashboard correlation overlap display update previously recorded at commit `ca64ca1c5ab7850e9f25e840c62f19c64fa05455`.
- Dashboard V3.25 scan-quality UI: commit `2f4cd46f890b7f74565afcc12c4ccd600fb68ba2`.
- Dashboard V3.25 section/footer label alignment: commit `796a9fe9492ce647baf2d5aece1cf1fbc6a048ce`.
- Dashboard V3.26 expanded local paper-trade scanner universe with GILD, ICE, CME, and CL plus sector mappings: commit `e0ff4fd13a9083e8305f0a3a00b9aca6cf639fa5`.

**Important:** These are known checkpoints, not a claim that they are still the current branch heads. On every resume, fetch the latest default-branch commits for both repositories and reconcile this file with actual source and deploys.

## 2. What the system does

### Dashboard

The dashboard README describes a private, mobile-friendly Streamlit application connected to a separate observation-only worker and Supabase research store. Current documented capabilities include:

- Multi-market daily scanner for equities, ETFs, metals, energy/commodity proxies, rates/currencies, and crypto.
- Trend, momentum, RSI, weekly confirmation, volatility, relative-strength, and ATR reference analysis.
- Cloud command center for scan health, sector/asset rotation, research shortlist, portfolio concentration, and historical setup diagnostics.
- Persistent virtual paper account with positions, cash, journal, P&L, and daily snapshots in Supabase.
- Strategy validation using first-seen signal observations and forward outcomes.
- Read-only intraday monitoring of virtual paper-position stop/target levels.
- Shared-capital historical replay with costs, chronological holdout, walk-forward folds, setup attribution, and asset-class diagnostics.
- Separate crypto and non-crypto holdout portfolios with independent starting capital, plus attribution of combined-portfolio trades.

### Cloud worker

The worker is a scanner and paper-position monitor. Its scheduled loop is still observation-only. V5.28 adds a separate, disabled-by-default paper-order adapter but no automatic signal routing yet. V5.26 documentation includes:

- Read-only Supabase paper-position monitoring and optional read-only Alpaca paper-account checks.
- Daily multi-asset scanning and ranked scan reports.
- Validated OHLCV alignment and benchmark alignment.
- Descriptive event studies and isolated event-level paper-execution replay.
- Shared-cash portfolio replay with overlapping positions, cash/equity curve, aggregate stop risk, gross exposure, sector caps, partial fills, fees, drawdown, and mark-to-market history.
- Chronological training/holdout analysis, walk-forward checks, setup attribution, cost stress scenarios, and separate crypto/non-crypto analysis.
- Portfolio concentration and pairwise correlation diagnostics. Correlation pairs include the count of overlapping sessions supporting each estimate.

## 3. Non-negotiable safety rules

1. **Automated Alpaca paper trading is an approved project goal.** The user wants the bot to execute and manage simulated trades without manual approval once the paper-only execution system is fully built and tested.
2. **Live brokerage trading is prohibited.** Never submit live orders, never use the live Alpaca host, and never use live credentials for this worker.
3. Paper execution must use the hard-coded `https://paper-api.alpaca.markets` endpoint, with a separate explicit enable flag, paper-account identity verification, and fail-closed behavior. No configurable live endpoint or fallback.
4. The new V5.28 paper-order adapter is currently disabled and not wired into the worker loop. Do not enable it or add the environment flag to Render until signal triggers, sizing, buying-power checks, open-order/position reconciliation, partial fills, stop/target lifecycle, daily loss limits, idempotency, and comprehensive tests are complete.
5. Never request, print, commit, or expose passwords, API keys, broker credentials, verification codes, or other secrets.
6. Never mutate the dashboard's Supabase virtual paper account unless the user explicitly asks for that specific change.
7. Keep simulation/replay ledgers isolated from the virtual paper account and Alpaca paper brokerage account.
8. Preserve existing paper-account seed positions and cash. Do not reset or reseed an account as part of routine development.
9. Historical results are research estimates, not proof of a durable trading edge or a promise of future performance.
10. Keep realistic execution caveats visible: gaps, slippage, fees, liquidity, partial fills, intraday path, latency, and data quality can make realized losses larger than a daily-bar stop estimate.
11. Do not describe a strategy as ready for live trading; this project is paper-only.

### Account separation

- The dashboard virtual paper account is stored separately in Supabase. A Render read-only monitor log at 2026-11-18 20:12 UTC confirmed two open virtual positions, AAPL and MSFT; quantities and current account state must be read from Supabase before making assumptions.
- The Alpaca paper account is a different account. A prior worker log showed approximately $100,000 equity and zero positions in Alpaca; that is not the dashboard's virtual portfolio.
- The previously recorded dashboard virtual seed state included AAPL 0.9460 shares at $351.86, stop $341.2945, target $372.9910, and $667.14 cash from a $1,000 starting balance. Treat this only as a preservation reference; inspect live Supabase/dashboard state before making any assumptions or changes.

## 4. Key technical and research decisions to preserve

- Shared-capital portfolio replay is the relevant historical test when trades overlap; independent asset-class simulations use separate fresh capital and their returns must not be added together.
- Combined-portfolio asset-class P&L is attribution from trades accepted under shared cash/risk constraints.
- Walk-forward pooled P&L is a sum of closed trades across test folds, not a compounded portfolio return.
- Historical universe data is not point-in-time and may contain survivorship bias.
- Yahoo Finance data can be delayed, incomplete, rate-limited, revised, or unavailable.
- Do not silently shift a missing/invalid next-session entry to a later date.
- Do not use same-session exit proceeds to fund an opening entry that occurred earlier that session.
- Use prior-session volume for capacity assumptions, not the current session's final volume.
- If stop and target are both touched within an ambiguous bar, preserve conservative stop-priority handling.
- A daily-bar stop cannot guarantee a maximum loss during an intraday crash or gap.

## 5. Known issues and follow-up investigations

### A. Incomplete scan coverage / stale data visibility — next dashboard priority

A worker scan previously analyzed 239 of 240 requested symbols. V5.27 now makes missing symbols and stale prices explicit, so an incomplete scan cannot look complete. A fresh V5.27 scan on 2026-11-18 reported 239/240 (99.6%) coverage, latest price date 2026-11-18, zero stale symbols, and UNI-USD missing because Yahoo Finance returned no daily bars.

Next work:
- Inspect the current dashboard and worker data structures for requested, successful, missing, stale, and failed symbols.
- Surface requested count, successful count, missing count, coverage percentage, and stale-price warnings in the dashboard command center.
- Preserve per-symbol failure reasons and source timestamps where available.
- Ensure failed symbols are not silently treated as valid zero values or omitted without a warning.
- Add tests for partial coverage and stale data.
- Keep asset-class coverage visible; do not “fix” a failed symbol by silently dropping it from the universe.

### B. UNI-USD Yahoo Finance data failure

A Render worker log repeatedly reported: `UNI-USD: No data found, symbol may be delisted`.

Investigate whether this is a Yahoo ticker/provider issue, a temporary outage, or a symbol mapping problem. Test a supported alternative data path or mapping before changing the universe. Preserve crypto coverage and document any intentional replacement. Do not assume UNI is delisted based on that log alone.

### C. Deployment verification

- Verify the latest worker commit, Render deploy status, and startup logs.
- Verify the dashboard default-branch head and whether Streamlit Community Cloud has deployed it.
- Confirm the deployed versions match the intended source before calling a release complete.

## 6. User collaboration preferences

- The user likes an energetic, collaborative “keep rolling / go” workflow.
- Prefer substantial, cohesive batches of related improvements over tiny incremental edits and repeated small decision requests.
- When the user says “go,” “keep rolling,” or similar, inspect the latest artifact/source, implement the next sensible batch, run appropriate checks, and report the actual outcome.
- Do not stop to ask for decisions that can safely be made from established project goals and constraints.
- Be clear about what was changed, what was tested, what deployed, and what remains unverified.

## 7. Resume procedure for a new conversation

When the user says **“Resume the trading project”**:

1. Read this handoff.
2. Inspect both GitHub repositories' current default branch, latest commits, and relevant source files. Do not rely on old chat summaries alone.
3. Check the latest GitHub Actions status for the relevant commits.
4. Check Render worker service `srv-dbua8frm8hqs73f895h0` and latest deploy/logs. Check dashboard deployment separately.
5. Reconcile any differences between this file and live source/deploy state.
6. Continue with the next priority in Section 5, unless the user gives a different direction.
7. After every substantial batch, update this file with new versions, commit SHAs, checks, deployment state, decisions, known issues, and the next exact task.

## 8. Immediate next checkpoint

**V5.29 paper-decision engine built and connected (Nov 18, 2026):**
- Worker V5.29 adds a read-only Alpaca latest-quote client (`alpaca_market_data.py`) and deterministic pre-trade risk gate (`paper_trade_engine.py`).
- The worker loop reads the newest scanner watchlist, fetches fresh Alpaca IEX quotes, checks quote/scan age, spread, setup quality, signal score, entry proximity, stop/target validity, current reward-to-risk, positions, pending orders, buying power, daily loss, and aggregate open risk.
- Defaults: 0.5% equity risk per trade; 1.0% aggregate open risk; 10% max single-name notional; 50% max gross exposure; 2% daily loss stop; five concurrent positions; 60-second quote freshness; 0.20% max spread; 0.30% max entry chase; 1.8 minimum current reward-to-risk; whole shares only.
- Existing positions without a confirmed protective stop cause open risk to be treated as unknown and block new entries.
- Added `paper_trade_decisions` audit table with RLS/service-role-only access. Migration `paper_trade_decisions` was applied to Supabase project `khjkbqjsykinlbwhkwtf`; this table is separate from `paper_account`.
- Order gateway is connected behind `ALPACA_PAPER_TRADING_ENABLED=true`, with hard-coded paper endpoint, PA-account identity check, stable client order IDs, duplicate lookup, whole-share bracket orders, and normalized bracket price precision.
- **Execution flag remains unset/off.** Worker logs confirmed `auto_enabled=False`, 16 decisions were recorded on first cycle, and zero orders were submitted. At that moment, the saved scan was stale (9 blocked), 5 candidates had no executable setup, and 2 failed signal-score threshold. The first scan cycle began afterward; wait for a fresh scan and inspect its decision rows before assessing candidate readiness.
- Supabase dashboard virtual account was read only: cash $553, realized P&L -$5.21, with AAPL and MSFT positions. Do not mutate or reset it. Alpaca paper account is separate; recent read-only worker logs showed ACTIVE, $100,000 equity, $200,000 buying power, zero positions.
- V5.28 foundation deploy was live. V5.29 connected-decision code commit `58e5a89a78f20ec91d777c0ff2058c4b415a488b` was live briefly; later safety/log and price-precision commits are rolling through Render. Latest worker code commit `07c091f6f553d0bf8df4e0e4ffad9b30434b19f7`; latest README/handoff docs commit `b5f2537f55fb48c6f641457f2451d925985ab2ca`. Render deploy for docs commit was queued at last check. Verify latest deploy before calling V5.29 fully live.
- GitHub Actions tests/syntax jobs passed for commit `58e5a89a78f20ec91d777c0ff2058c4b415a488b`; jobs for later commits were still running at last check. Verify latest run result before release sign-off.

**Next tasks:**
1. Confirm latest Render V5.29 deploy is live and startup logs show version 5.29, paper-only switch off, and one-minute account snapshot refresh.
2. Let a fresh 15-minute scanner cycle complete. Query `paper_trade_decisions` for fresh scan rows; review whether any candidate reaches `READY_NOT_SUBMITTED` and why the rest are blocked.
3. Add integration tests around the worker's database-to-quote-to-decision persistence cycle, including stale scan, missing quote, market closed, and duplicate order scenarios.
4. Add full broker lifecycle reconciliation: order accepted/rejected, partial fills, attached bracket legs, cancelled/replaced exits, position sizing vs filled quantity, restart recovery, and daily loss circuit breaker persistence.
5. Add dashboard UI for decision history, quote timestamp/feed, block reasons, proposed quantity/risk, broker orders, fills, and exit status.
6. Keep `ALPACA_PAPER_TRADING_ENABLED` unset until end-to-end paper lifecycle tests pass and the user explicitly approves enabling automatic paper execution.
7. Confirm V3.26 dashboard deployment in Streamlit Community Cloud.
8. Continue investigating UNI-USD missing Yahoo daily bars without silently dropping it.


**Dashboard V3.27:** Added a read-only “Alpaca paper-trading decisions” panel to the Cloud scanner tab. It reads the newest 100 rows from `paper_trade_decisions`, summarizes ready-not-submitted / broker-order / blocked counts, and displays quote feed/time, bid/ask/midpoint, spread, proposed shares, notional, estimated risk, current R:R, and broker order ID. It does not mutate either account. Commit `7d962f42c26249d4ac20f8e341e98011ea94fff3`; Dashboard Python syntax CI passed (run `44394491902`). Streamlit Community Cloud deployment still needs visual confirmation.

**Deployment update:** Render deploy `dep-dbv0sdftrrvc73b7uts0` for worker README commit `b5f2537f55fb48c6f641457f2451d925985ab2ca` is live. Startup logs confirm V5.29 and paper-only safety mode; `ALPACA_PAPER_TRADING_ENABLED` is false. GitHub Actions tests and Python checks passed on `07c091f6f553d0bf8df4e0e4ffad9b30434b19f7` and `b5f2537f55fb48c6f641457f2451d925985ab2ca`. At first post-deploy cycle the worker still saw the previous scan (20:21 UTC) and blocked all 16 candidates as stale / no executable setup / insufficient signal score; a fresh scan was running. Recheck the latest saved scan and decision rows before assessing whether any setup is ready.

**Latest worker files/commits:** `alpaca_market_data.py` commit `3e0bc91171b26721a90a1dbffcf2b4433fccaeae`; `paper_trade_engine.py` commit `0c2776ed9555505864fe483028875cf0a176b346` (later open-risk enhancement `8b736f2cbf0459509c1da68e60ab38ebb98cc32c)); paper decision schema commit `f460dca5f4084990022a151f369838c607294942`; read-only snapshot expansion commit `283400c7f0d2a7bd77ec9b2a16e34705fb4b9739`; worker integration commit `58e5a89a78f20ec91d777c0ff2058c4b415a488b`; worker final label commit `07c091f6f553d0bf8df4e0e4ffad9b30434b19f7`; final adapter price-precision commit `e9f5d1d6f7c268296cd6b529b415e2e1fc127d65`; adapter precision test commit `5b101f160b4d00c4bde368118aa236c768c36a6a`; README V5.29 commit `b5f2537f55fb48c6f641457f2451d925985ab2ca`.

**Before further editing:** Refresh both repository heads, GitHub Actions, Render deploys/logs, and Supabase decision rows. Do not infer successful deployment from a queued build or successful syntax job alone.
