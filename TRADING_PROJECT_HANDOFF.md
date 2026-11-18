# Trading Project Handoff

**Last maintained:** 2026-11-18 (updated after V5.27 / V3.25 data-quality batch)  
**Purpose:** Durable checkpoint for continuing the trading dashboard and observation-only cloud worker across ChatGPT conversations.

> **Resume phrase:** “Resume the trading project.”  
> On resume, read this file first, then inspect the live GitHub repositories and deployment state before changing code. Treat this document as a checkpoint, not a substitute for verifying current source.

## 1. Project repositories and deployment

| Component | Repository / service | Known state |
|---|---|---|
| Dashboard | [jjfmetal123/my-trading-dashboard](https://github.com/jjfmetal123/my-trading-dashboard) | Streamlit dashboard; README confirms capabilities and research/safety boundaries |
| Cloud worker | [jjfmetal123/trading-cloud-worker](https://github.com/jjfmetal123/trading-cloud-worker) | **V5.27** data-quality diagnostics; latest code/docs commits recorded below |
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

The worker is an observation-only scanner and paper-position monitor. V5.26 documentation includes:

- Read-only Supabase paper-position monitoring and optional read-only Alpaca paper-account checks.
- Daily multi-asset scanning and ranked scan reports.
- Validated OHLCV alignment and benchmark alignment.
- Descriptive event studies and isolated event-level paper-execution replay.
- Shared-cash portfolio replay with overlapping positions, cash/equity curve, aggregate stop risk, gross exposure, sector caps, partial fills, fees, drawdown, and mark-to-market history.
- Chronological training/holdout analysis, walk-forward checks, setup attribution, cost stress scenarios, and separate crypto/non-crypto analysis.
- Portfolio concentration and pairwise correlation diagnostics. Correlation pairs include the count of overlapping sessions supporting each estimate.

## 3. Non-negotiable safety rules

1. **The cloud worker is observation-only.**
2. Alpaca integration must remain pinned to the paper API host and use read-only GET requests only.
3. Never submit brokerage orders or mutate Alpaca positions, cash, or account state.
4. Never mutate the dashboard's Supabase virtual paper account unless the user explicitly asks for that specific change.
5. Keep simulation/replay ledgers isolated from the virtual paper account and from the brokerage account.
6. Never request, print, commit, or expose passwords, API keys, broker credentials, verification codes, or other secrets.
7. Preserve existing paper-account seed positions and cash. Do not reset or reseed an account as part of routine development.
8. Historical results are research estimates, not proof of a durable trading edge or a promise of future performance.
9. Keep realistic execution caveats visible: gaps, slippage, fees, liquidity, partial fills, intraday path, latency, and data quality can make realized losses larger than a daily-bar stop estimate.
10. Do not describe a strategy as ready for live trading without substantial validation and explicit user direction.

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

**Completed batch:** Worker V5.27 records per-symbol missing-data reasons and potentially stale daily-price warnings; dashboard V3.25 displays missing/stale counts and detail tables. Worker tests and Python checks passed on commits `22b7373` and `ee7ca2e`; dashboard syntax check passed on `796a9fe`. A fresh V5.27 scan logged 239/240 symbols (99.6%), zero stale prices, with UNI-USD the single missing symbol. Render deploy `dep-dbv0d3ju2v8c73fc0dng` was live; follow-up deploy `dep-dbv0dbv0n0ks73duvq1g` for the newest worker commit was still building at last check.

**Next task:** Verify the latest Render deploy is live and the new scan report is visible in the dashboard; then use the dashboard virtual paper account to evaluate and manually approve any simulated entries.

**Still open:** Diagnose the repeated `UNI-USD` data failure without silently reducing crypto coverage. Confirm the freshness thresholds against exchange holidays and provider behavior.

**Latest code changes:** Dashboard V3.25 latest commit `796a9fe9492ce647baf2d5aece1cf1fbc6a048ce`; worker V5.27 latest relevant code commit `22b737387e0efb5495659710f8d2f1fbd21b1f95` and latest docs commit `ee7ca2e8e9568a0a3f9740ed5cfdd4804db83b98`.

**Before further editing:** Refresh current repository heads and inspect actual source and deployment state.
