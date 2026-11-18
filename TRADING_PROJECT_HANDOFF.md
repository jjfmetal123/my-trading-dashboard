# Trading Project Handoff

**Last maintained:** 2026-11-18 (updated after V5.30 durable paper-order intent)  
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


**Dashboard V3.27:** Added a read-only “Alpaca paper-trading decisions” panel to the Cloud scanner tab. It reads the newest 100 rows from `paper_trade_decisions`, summarizes ready-not-submitted / broker-order / blocked counts, and displays quote feed/time, bid/ask/midpoint, spread, proposed shares, notional, estimated risk, current R:R, and broker order ID. It does not mutate either account. Latest app commit `3c4969698b06f294a9b2f3057460d7995a2efdf4`; Dashboard Python syntax CI passed (run `44394665548`). Streamlit Community Cloud deployment still needs visual confirmation.

**Deployment update:** Render deploy `dep-dbv0sdftrrvc73b7uts0` for worker README commit `b5f2537f55fb48c6f641457f2451d925985ab2ca` is live. Startup logs confirm V5.29 and paper-only safety mode; `ALPACA_PAPER_TRADING_ENABLED` is false. GitHub Actions tests and Python checks passed on `07c091f6f553d0bf8df4e0e4ffad9b30434b19f7` and `b5f2537f55fb48c6f641457f2451d925985ab2ca`. At first post-deploy cycle the worker still saw the previous scan (20:21 UTC) and blocked all 16 candidates as stale / no executable setup / insufficient signal score; a fresh scan was running. Recheck the latest saved scan and decision rows before assessing whether any setup is ready.

**Latest worker files/commits:** `alpaca_market_data.py` commit `3e0bc91171b26721a90a1dbffcf2b4433fccaeae`; `paper_trade_engine.py` commit `0c2776ed9555505864fe483028875cf0a176b346` (later open-risk enhancement `8b736f2cbf0459509c1da68e60ab38ebb98cc32c)); paper decision schema commit `f460dca5f4084990022a151f369838c607294942`; read-only snapshot expansion commit `283400c7f0d2a7bd77ec9b2a16e34705fb4b9739`; worker integration commit `58e5a89a78f20ec91d777c0ff2058c4b415a488b`; worker final label commit `07c091f6f553d0bf8df4e0e4ffad9b30434b19f7`; final adapter price-precision commit `e9f5d1d6f7c268296cd6b529b415e2e1fc127d65`; adapter precision test commit `5b101f160b4d00c4bde368118aa236c768c36a6a`; README V5.29 commit `b5f2537f55fb48c6f641457f2451d925985ab2ca`.

**Before further editing:** Refresh both repository heads, GitHub Actions, Render deploys/logs, and Supabase decision rows. Do not infer successful deployment from a queued build or successful syntax job alone.


## 9. V5.30 durable order-intent checkpoint (Nov 18, 2026)

- Worker V5.30 commit `5957714bd693f976cacec3dfa3f2a189e4a852f6` moves the Alpaca paper broker request behind a successful Supabase decision upsert.
- A qualifying order is first persisted as `ORDER_INTENT` with reason `ORDER_INTENT_PERSISTED_BEFORE_SUBMISSION`. If this write fails, the worker skips broker submission.
- After the broker response, the same `(scan_id,symbol)` row is updated to `ORDER_SUBMITTED`, `ORDER_ALREADY_EXISTS`, or `BLOCKED`. If the final database update fails after a broker response, the worker emits a CRITICAL log containing the stable client order ID so the broker state can be reconciled.
- The stable client order ID and Alpaca duplicate lookup provide a recovery path if the worker restarts after submission but before the final audit update. This is not a complete broker lifecycle manager; partial fills, bracket-leg state, cancellation/replacement, exit reconciliation, and durable circuit-breaker state remain unfinished.
- Added regression test `tests/test_worker_order_intent_ordering.py` to verify the intent upsert occurs before the broker submission call and final outcome persistence occurs after it. Test commit: `708ed7609a02d77530cb33d01094ed8c0a699b52`.
- Worker README V5.30 documents the new sequencing; README commit `3064602bf6e374d376d1b14b40dcfdf8bc9cf87c`.
- Worker source commit containing the intent-first sequencing: `86143c1aec06e1fe76e9770ab41d85fd09d44e86`.
- Worker source version bump to V5.30: `5957714bd693f976cacec3dfa3f2a189e4a852f6`.
- Python syntax CI passed on the initial intent-sequencing commit. Full Python test workflow completed successfully for that initial commit; the new ordering regression test and later V5.30/doc commits require their own latest-run verification.
- Render deployment for the first intent-sequencing commit was still `build_in_progress` at last check; later commits may supersede that deployment. Verify latest deploy status and startup log reports V5.30 before claiming release live.
- Alpaca paper execution remains disabled. No order was placed. A live worker log at 20:58–20:59 UTC on Nov 18 showed Alpaca paper ACTIVE with $100,000 equity, $200,000 buying power, and zero Alpaca positions; the worker continued to monitor the separate Supabase virtual AAPL/MSFT positions without mutating them.
- Fresh decision cycle near the close had zero ready entries. Several IEX quotes were exceptionally wide (e.g. LLY, MMM, TGT, ICE, CME); other candidates were rejected for setup or entry proximity. A later cycle showed some spreads normalize while entry proximity still failed. Do not loosen the 0.20% spread gate to force a trade. Investigate consolidated SIP quote availability versus IEX before the next session; keep fail-closed behavior if SIP entitlement is unavailable.
- The regular session ended at 21:00 UTC / 3:00 p.m. Central on this date. No need to force an order after the close.

**Next build priorities after V5.30:**
1. Verify latest GitHub Actions tests and Python syntax checks for the newest worker commit.
2. Verify Render latest deployment is live and startup reports V5.30 with `ALPACA_PAPER_TRADING_ENABLED=false`.
3. Investigate Alpaca SIP consolidated quote availability/entitlement versus IEX; keep the 0.20% spread and quote-freshness gates unchanged until verified.
4. Build broker lifecycle reconciliation for accepted/rejected/partial-filled orders, attached bracket legs, canceled/replaced exits, actual filled quantity versus positions, and restart recovery.
5. Add persisted daily loss breaker and session-level reconciliation.
6. Update dashboard decision UI to distinguish `ORDER_INTENT`, broker accepted/filled/partial, and exit-leg lifecycle states.
7. Keep execution OFF until full end-to-end paper lifecycle tests pass and the user explicitly approves enabling automatic paper trading.


## 10. V5.31 broker lifecycle audit reconciliation (Nov 18, 2026)

- V5.30 is confirmed live on Render; latest prior startup log reported V5.30 and paper-only safety mode.
- Added read-only recent-order snapshot (latest 100 broker orders) and normalized order lifecycle fields: accepted/pending, partial fills, filled, canceled, expired, rejected, replace/cancel pending, plus nested bracket legs and unresolved exit-leg states.
- Worker V5.31 now reconciles its own stable `scan-` client order IDs against `paper_trade_decisions` and updates audit rows with broker-confirmed lifecycle status and nested lifecycle snapshot. This does not call any Alpaca order-modification endpoint.
- Added `broker_lifecycle.py` and `tests/test_broker_lifecycle.py`; worker source commit currently `f2afce57991e5ec377d300da7a3f2c3b7b00e2da`, module commit `a257d7ae9563b83d71eb13bdf77b2f8760ff824b`, test commit `75ead5d3ee7a5d1c9dde6091bd6dbdb9665ed3c7`. README update pending.
- CI and Render deployment for V5.31 are pending. Verify both before claiming V5.31 live.
- Important: broker reconciliation is GET-only against Alpaca; audit updates affect only `paper_trade_decisions`. Supabase virtual `paper_account` remains untouched. `ALPACA_PAPER_TRADING_ENABLED` remains false/unset. Never enable until full lifecycle integration tests and explicit user approval.
- Next: add tests for audit-row reconciliation and missing/unknown client IDs; reconcile actual broker position quantity against filled entry quantity and protective exit legs; add persistent daily-loss circuit breaker without changing any live trading state.


## 11. V5.32 persistent daily-loss guardrail (Nov 18, 2026)

- Created `public.paper_execution_guardrails` through Supabase migration `create_paper_execution_guardrails`. It is keyed by Alpaca paper account and New York trading date and stores starting/current equity, daily P&L, daily loss percentage, halt flag/reason, and update timestamp.
- Verified the table exists, RLS is enabled, `service_role` has SELECT access, and `anon` / `authenticated` do not. Supabase security advisor shows an informational `rls_enabled_no_policy` finding, consistent with service-role-only tables; no public role privileges were granted.
- Worker V5.32 adds a persisted 2.0% default daily-loss circuit breaker (`ALPACA_MAX_DAILY_LOSS_PCT`). It latches for the remainder of the New York trading date once breached. Invalid baseline, unverified PA account, or database read/write failure blocks entries.
- Circuit breaker helper was moved into standalone `daily_loss_guardrail.py` so tests do not import the heavy worker runtime. Worker source commit `d82a3d20a2d2c5ec81ce834f3a7e4de88da78fab`; helper extraction commit `4f39eb9f0a6496ea2d7b267f8c05cb185810ff47`; worker integration commit `55d76e49cfbef753143e236680721757e59d8cee`; test isolation commit `408b057fad12507f620fb88f0df131e559833ffe`. Latest README V5.32 and SQL schema file are in the worker repository.
- Earlier CI failures were caused by the integration test importing `worker.py` (which requires yfinance, not installed in the lightweight unit-test job). That dependency was removed by moving persistence logic to the standalone helper. Latest CI for `408b057...` was queued/in progress at last check; verify before sign-off.
- Render has not yet been confirmed running V5.32. Latest verified Render startup still showed V5.31. A later Render deploy for the guardrail schema commit was queued/building; check latest deploy and startup logs before calling V5.32 live.
- Supabase query showed no guardrail rows yet, expected until a V5.32 worker version runs the persistence function. Do not manually seed test values into the production table.
- This table and code are exclusively for Alpaca paper account risk controls. The separate Supabase virtual `paper_account` and its AAPL/MSFT positions remain untouched.
- Historical validation caution: the recent shared-cash out-of-sample replay was negative under moderate costs (-2.1082%, profit factor 0.907); non-crypto moderate-cost P&L was -$2,888.68 / PF 0.887. Treat this as evidence that the strategy is not yet validated, not a profit claim. Keep paper execution disabled.

**Next exact tasks:** verify V5.32 CI and Render deployment; add tests around order audit reconciliation; reconcile broker-filled quantity and protective exit-leg quantity to actual Alpaca positions; ensure daily-loss guardrail is called before any candidate evaluation; add dashboard display for broker lifecycle and daily halt state. Do not enable paper orders until the full end-to-end lifecycle is proven and the user explicitly approves.


### V5.32 final verification correction
- Latest worker commit `9c10e45ae3fdd6f5ebec1aef369dfb4c3ce77ba3` fixes the escaped-newline syntax issue in the worker guardrail call.
- GitHub Actions on `9c10e45...`: Python tests run `44398837925` completed SUCCESS; Python checks run `44398837496` completed SUCCESS.
- Render deploy `dep-dbv18u1j7cmc73de61bg` for `9c10e45...` is LIVE. Startup and runtime logs show V5.32 running, Alpaca paper account ACTIVE, and the guardrail table being read/upserted successfully. A prior intermediate deployment briefly crashed due to the escaped-newline syntax error; the corrected commit is live and the worker has resumed.
- Verified live guardrail row for Alpaca paper account `PA34ODALY`, date `2026-11-18`: starting equity $100,000, current equity $100,000, daily P&L $0, daily loss 0%, halted=false. This is the Alpaca paper account only.
- V5.32 worker uses the standalone `daily_loss_guardrail.py` helper; integration tests no longer import worker runtime. Paper execution switch remains OFF.


## 12. Dashboard V3.28 broker lifecycle and guardrail visibility (Nov 18, 2026)
- Dashboard V3.28 adds a read-only Alpaca daily-loss guardrail panel to the Cloud Scanner tab: starting equity, daily P&L, daily loss percentage, halted/clear state, and trading date.
- Existing Alpaca decision audit table now fetches the decision JSON and displays normalized broker state, filled/remaining shares, and protective exit-leg states. Broker lifecycle statuses are included in the broker-order count; unknown statuses are excluded.
- Dashboard code commit `6798e37a4a98eeea7fce3ecbf80020b498663d2e`; README update follows. Need verify dashboard GitHub Actions and Streamlit Community Cloud deployment before calling it live.
- Dashboard panel is read-only. It does not touch the separate Supabase virtual `paper_account`, does not submit Alpaca orders, and does not enable the paper execution flag.


- Dashboard V3.28 syntax workflow run `44399244197` completed SUCCESS on handoff commit `8653ca1e6cedb88dda43b461bd37910d89419395`. The app code commit `6798e37a4a98eeea7fce3ecbf80020b498663d2e` and README commit `a64834b56e8f35323c9e74dfa7d27eddd07a842c` also passed syntax checks. Streamlit Community Cloud visual deployment is still unverified.


## 13. V5.33 broker position protection audit and Dashboard V3.29 (Nov 18, 2026)
- Added `broker_position_protection.py`, a pure audit helper. It links each actual Alpaca position to the newest matching worker-owned `scan-` entry order and checks its nested bracket stop/target legs.
- `PROTECTED` requires both exit legs to be active and each exit quantity to exactly match the broker-reported open position quantity. Missing stop/target, inactive legs, quantity mismatch, unavailable quantities, and positions without a matching worker entry are distinct non-success states. Unknown/unlinked positions are never assumed protected.
- Worker reconciliation now persists `decision.position_protection` in the matching `paper_trade_decisions` row and logs non-PROTECTED/unlinked states. This is read-only: it does not submit, cancel, replace, or close orders.
- Worker helper/test commits: `48ef82e6858d907f8fb1de62ae1d0b2c0608fa97`, `b7dfef20b27bc1e07ede870913482e6d94bf99dc`, `de6d8725c4b2569d481d5f96e3386168134cca04`, `2cfccd58ffba30a8b6af97317b206d1c9705b9d4`; worker integration commit `77af76bc332096bc898efd1a52bcf2e8fbcb6e66`.
- GitHub Actions for worker commit `77af76bc...`: Python tests run `44400154713` SUCCESS and Python checks run `44400154682` SUCCESS. Earlier helper and matching tests also passed (`44399954753`, `44399947528`, `44400112847`, `44400092435`).
- Dashboard V3.29 displays protection status, open shares, stop shares, target shares, and counts non-PROTECTED audit states. App commit `cada87d5063e9ab774a6cc158682586498675666`; README update follows.
- Worker README V5.33 documentation commit and dashboard README update are being recorded in this batch. Dashboard syntax CI and both Render/Streamlit deployments still require verification.
- The verified Alpaca paper account still has zero positions, so the new position-protection path is unit-tested but has not yet been observed against a real open paper position. Do not create a test position in the production paper account.
- `ALPACA_PAPER_TRADING_ENABLED` remains OFF. The daily-loss guardrail row remains at $100,000 starting/current equity, $0 P&L, 0% loss, not halted, for Alpaca paper account `PA34ODALY` on 2026-11-18. The separate Supabase virtual account remains untouched.
- Historical strategy holdout remains negative under moderate execution costs. Do not claim profitability or loosen entry filters to force trades.

**Next exact tasks:** verify latest Render deployment and logs for worker integration commit `77af76bc...`; verify Dashboard V3.29 syntax CI and Streamlit deployment; inspect protection audit after naturally occurring paper positions (without placing test orders); add an explicit fail-closed new-entry gate for any known unprotected Alpaca position before considering execution enablement; then add restart/partial-fill integration tests. Keep paper execution OFF pending full lifecycle validation and explicit user approval.


### V5.33 fail-closed existing-position entry gate (Nov 18, 2026)
- Added `evaluate_new_entry_protection_gate(snapshot)` to the pure broker protection module. An empty broker position list passes; every existing position must link to the newest worker-owned entry order and have active stop and target legs whose quantities exactly match the broker position.
- Any unlinked/manual position, missing or inactive exit leg, unknown quantity, or quantity mismatch blocks the entire new-entry cycle before candidate evaluation. This intentionally favors safety over availability. No order repair/cancel/replace/close action is performed.
- Helper commit `4c3dd4070e13277793da82dfefc0c8c341dc0c2b`; tests commit `0848c412383d90c9ee369099d94a1a606818ec9f`; worker integration commit `e50711a7b5facc5d384e2a547d9d44a5144aa22e`.
- GitHub Actions on `e50711a...`: Python tests run `44400571045` SUCCESS; Python checks run `44400571038` SUCCESS. The gate's pure tests also passed on `0848c412...`.
- Render deployment for `e50711a...` was still BUILD_IN_PROGRESS at the time this handoff entry was written. The previous V5.33 version-label commit `6a8b453...` is LIVE and Render logs confirm `WORKER_VERSION=5.33`. Verify the newest deployment and startup logs before claiming the entry gate is deployed.
- Dashboard V3.29 syntax CI passed on commit `91777feae5169329244465d3a5a86903409abfb9` (run `44400446548`). Streamlit Community Cloud visual deployment remains unverified.
- Automatic Alpaca paper order submission remains OFF. No real-money endpoints are supported. The Alpaca paper account had no open positions at the last verified snapshot; the protection audit has therefore been unit-tested but not exercised against an actual open broker position.


### V5.33 deployment verification and runtime state (Nov 18, 2026)
- Worker integration commit `e50711a7b5facc5d384e2a547d9d44a5144aa22e` is LIVE on Render deploy `dep-dbv1ddf0n0ks73e01ep0` (finished 2026-11-18 21:22:02 UTC). Startup logs confirm `WORKER_VERSION=5.33` and the paper-only safety mode. The new fail-closed existing-position protection gate is included in this live commit.
- GitHub Actions for `e50711a...`: tests run `44400571045` SUCCESS; syntax checks run `44400571038` SUCCESS. The earlier helper, position-matching, and entry-gate test runs also passed.
- Live Alpaca read-only snapshot after deploy: account ACTIVE, equity $100,000, buying power $200,000, zero Alpaca positions. The daily-loss guardrail table was successfully read and upserted. No broker order was submitted.
- The separate Supabase virtual paper account still has AAPL and MSFT positions; the worker's virtual-account monitor read them but received stale after-hours one-minute bars and correctly skipped exit evaluation. These are not Alpaca positions and were not modified.
- Dashboard V3.29 code and version commit `91777feae5169329244465d3a5a86903409abfb9` passed GitHub Actions run `44400446548`. Dashboard README commit `f7b4fdb...` and handoff updates passed CI. Streamlit Community Cloud visual deployment remains unverified.
- Worker README documents the new entry gate at commit `2eb186e23f6033ab130558bfeb4d38a3b0abfed3`; its Render docs-only deployment was still building at last check. The code commit `e50711a...` itself is already confirmed live.
- Keep `ALPACA_PAPER_TRADING_ENABLED` OFF. Do not create production test positions. The new protection evaluator has unit coverage but no live open Alpaca position against which to exercise it yet.


### V5.33 broker audit persistence regression coverage (Nov 18, 2026)
- Extracted the worker's database reconciliation routine into `broker_audit.py` so it can be tested without importing the full worker runtime. The worker now calls this helper using its existing read-only Alpaca snapshot.
- Added mocked Supabase-client tests for stable client-ID recovery, lifecycle/protection persistence, non-worker order filtering, missing audit rows, and idempotent repeated snapshots.
- Added stale-state cleanup: closed positions become `NO_OPEN_POSITION`; older entry orders whose symbol's current position belongs to a newer worker entry become `NOT_CURRENT_POSITION_ENTRY`. Dashboard alert counts exclude these two informational states while still flagging actual protection exceptions.
- Worker commits: broker audit extraction `fc58081098f5fbe41e20461151ac88095f6f60de`; audit regression tests `22873974a21d7dafc2a37715c7e2cab3e1055ff5`; worker integration `928b6ec2772f7967c35eb019db023129b719be16`; stale-state cleanup `6e36ed35d958247713dde43532e2c0f4a36e6984`; stale-state tests `9e534ffeb9aeece4f8b7a637d134246bbbd2adb7`.
- GitHub Actions on worker commit `928b6ec2...`: Python tests run `44400925407` SUCCESS and Python checks run `44400925387` SUCCESS. Stale-state tests on `9e534ffe...`: Python tests run `44401025903` SUCCESS and Python checks run `44401025719` SUCCESS.
- Dashboard commit `f4058cd78272d56809ec2dc65abf98b58f2fecb9` passed syntax CI run `44401049642`.
- Render deployment for commit `928b6ec2...` was update-in-progress at the last check; the previous V5.33 commit `e50711a...` is live. The latest stale-state test commit `9e534ffe...` was queued for deployment. Verify the newest deployment and startup logs before calling this sub-batch live.


### V5.33 exit-state classification and short-quantity hardening (Nov 18, 2026)
- Tightened the protection evaluator's active-state allowlist. Only accepted, pending-acceptance, partially-filled, cancel-pending, and replace-pending legs count as active. `DONE_FOR_DAY`, `STOPPED`, `SUSPENDED`, and `CALCULATED` now fail closed as inactive.
- A regression test initially caught that the intended allowlist edit had not been committed; the actual source was corrected in commit `b725bf7cd5fcb8ed5f30e88ff712d6c2e17fc479`. CI tests and syntax checks both passed (runs `44401423964`, `44401423969`).
- Position quantities are now compared by absolute share count so a broker-reported negative short quantity can match buy-to-cover exits. Helper commit `d177f43922f38e07e0aa57f57df8908608308ce7`; regression test commit `dcd2dd10d1113b5381836923a2e93343633b1cef`. CI tests run `44401570040` and syntax run `44401569987` both completed SUCCESS.
- Render deploy for the active-state correction `b725bf7...` is LIVE. Deploy for the signed-quantity commit `dcd2dd10...` was BUILD_IN_PROGRESS at the last check; verify it before calling the final edge-case update deployed.


### V5.33 partial-fill and restart-recovery test coverage (Nov 18, 2026)
- Added protection test for a partially filled entry where the actual open position and both active exit legs equal the filled quantity, not the original requested quantity. Test commit `4f43d36e20599878e075981c1a77adf520a19634`; both Python test/syntax runs passed (`44401768514`, `44401768443`).
- Enhanced the fake Supabase test client to apply updates, then verified first-pass persistence of `BROKER_PARTIALLY_FILLED` and matching exit coverage, followed by a second identical snapshot that performs no duplicate update. This exercises idempotent restart recovery using the stable client order ID.
- Audit test commit `d69fc711d0c83e301ac0d894a146bcf012259022`; Python tests run `44401817127` SUCCESS and syntax run `44401817098` SUCCESS.
- Worker code commit `dcd2dd10...` (signed short quantity normalization) is LIVE on Render. The subsequent audit test commit changes tests only; worker README documentation deployment is pending. The actual Alpaca paper account remains at zero positions, so the broker protection path is not yet observed on a naturally occurring open position.


### Dashboard V3.29 protection reason detail
- The Cloud Scanner decision table now shows the exact broker position protection reason alongside status, open shares, stop shares, and target shares.
- App commit `c0aedd152c80c2709a5c125206cb3b4fdaced909` passed syntax CI run `44402000809`. Streamlit Community Cloud visual deployment remains unverified.


## 14. V5.34 partial-exit and lifecycle hardening / Dashboard V3.30 (Nov 18, 2026)
- Found and fixed a lifecycle classification gap: `CANCEL_PENDING` and `REPLACE_PENDING` no longer count as confirmed protective coverage. Only accepted, pending-acceptance, and partially-filled child exits count as active.
- Exit protection now compares each child's remaining quantity (`qty - filled_qty`) with actual open broker position shares. A partially filled stop is considered protective only if its remaining shares still match the current position and the target's remaining shares also match.
- Multiple active stop or target legs of the same role are treated as ambiguous and fail closed. Unknown exit quantities remain UNKNOWN; zero remaining quantity is inactive.
- Entry gate now rejects incomplete/malformed snapshots, malformed position rows, and reported `position_count` mismatches rather than assuming missing data means zero positions.
- Worker helper commit `63473dc531106b74e50486ab0bfb77a18ff09c31`; tests commit `289e9d13052db9d4a2fd1697b8fc746d06043ea7` initially exposed a classification expectation mismatch. The helper was corrected in `bfa590467f31c9fcc980b99c34bf35ac176c4738`. Snapshot count validation commit `18a8ecb129ce52ea239a7389c33ab7b094289059`; position count regression tests commit `9f38aadfe53f1997e12f73f8257cb692f5f23343`.
- CI for final pre-version helper commits: Python tests `44402839158` SUCCESS; Python checks `44402838809` SUCCESS. Snapshot-count validation tests/syntax `44402908221`, `44402907586` SUCCESS. Latest full tests and checks on `9f38aadf...` passed (`44402932120`, `44402931935`).
- Worker version bump commit `53e95450682bcfc2a98736b2d7c9ecef0a86a1c0`; worker README commit `ee590a4f8a4e7e0eb59d6dfb6c31c15ac77b2808`. Render deployment for these commits must be verified before calling V5.34 live.
- Dashboard V3.30 code commit `dcd80769dfa57b3f43ff6c65c8ccefe5255f4f2a` displays remaining stop/target shares rather than original quantities; its syntax CI run `44402974481` is still in progress at handoff time. Dashboard README update follows.
- The verified Alpaca paper account has zero open positions; no test orders were created. This audit is unit-tested but hasn't yet been observed on an actual open broker position. Paper execution switch remains OFF; no live brokerage endpoints are supported.
- Continue next with real read-only order snapshot fixtures for Alpaca bracket child lifecycle transitions, plus worker fail-closed integration tests for snapshot fetch failure and stale snapshot age. Confirm Render and Streamlit deployment states before announcing releases.


## 15. V5.35 fresh Alpaca snapshot guard (Nov 18, 2026)
- Added `is_snapshot_fresh` to the read-only Alpaca client. Every successful account/positions/orders/clock snapshot now carries an aware UTC `snapshot_fetched_at` timestamp.
- Before any candidate evaluation, `run_paper_execution_cycle` requires a valid timestamp within 120 seconds by default (`ALPACA_MAX_SNAPSHOT_AGE_SECONDS` configurable, minimum 30 seconds). Missing, malformed, naive, future, or stale snapshots block entries. This is an additional guard on top of the existing fetch-error cache clear, paper-account identity, daily loss, and position-protection gates.
- Snapshot timestamp commit `d0b7f3667d7c5f4dc487ec3e59f8ab29e36ddbb3`; freshness regression tests commit `cc8a7879f59086df6124e64621fc41e7273bd831`; worker entry-cycle integration commit `11048a91466e17ec02293bee9fb14b63a9581437`.
- CI on worker integration `11048a91...`: Python tests run `44403344358` SUCCESS; syntax checks run `44403343712` still running at time of note. Freshness tests run `44403314225` SUCCESS and `44403314021` SUCCESS.
- Worker version bump commit `d04b056aba57a20913763883845321fac14eff58`; worker README update `5460ab817a608a4c0a3d3dbed29d7872ff177a33`. Render deploy of the version bump and docs must be checked before calling V5.35 live.
- V5.34 code is confirmed LIVE on Render deploy `dep-dbv1k7oqsg7c73e6trk0`, commit `ee590a4f...`; both worker tests and syntax checks passed. Dashboard V3.30 code commit `dcd80769...` and README/handoff updates passed CI (runs `44402974481`, `44403099691`, `44403123803`).
- Dashboard Streamlit visual deployment remains unverified. Alpaca paper account remains empty; no test orders placed. Paper order switch stays OFF.


### V5.35 final verification (Nov 18, 2026)
- Worker tests run `44403474230` and syntax checks run `44403474180` both SUCCESS on version bump commit `d04b056a...`; README tests/checks `44403490968` and `44403490491` both SUCCESS on `5460ab81...`.
- Render deploy `dep-dbv1ldftrrvc73b8oqr0` for commit `5460ab81...` is LIVE. Startup logs confirm `WORKER_VERSION=5.35` at 21:38:55 UTC. Immediately afterward, the live worker completed a fresh read-only Alpaca snapshot (ACTIVE paper account, $100,000 equity, $200,000 buying power, zero positions) and logged the expected market-closed no-entry result.
- Dashboard V3.30 code, README, and handoff CI all SUCCESS: `44402974481`, `44403099691`, `44403123803`. Streamlit Community Cloud visual rendering still not independently verified.
- Current safety: paper order switch remains OFF; no orders submitted; Alpaca paper account remains empty. No real-money endpoint is supported.


## 16. V5.36 Alpaca bracket child normalization (Nov 18, 2026)
- Identified a critical audit-path defect: `normalize_order_lifecycle` retained child lifecycle and quantity fields but dropped child `side`, `type`, `stop_price`, and `limit_price`. The downstream protection checker requires those fields to identify stop/limit exit legs. A real nested bracket could therefore be incorrectly classified as missing protection.
- Fixed normalization to preserve child side/type, stop/limit/trailing prices, group role, and replacement metadata. Malformed non-list nested `legs` are treated as absent rather than trusted.
- Added raw Alpaca nested-bracket regression fixtures, including a partial stop fill with an OCO sibling reduced to the remaining position quantity, and malformed leg-shape coverage.
- Code commit `8de3b68cd3a5b778f3cda12a3ab2970241ef49cd`; regression tests commit `2cc213c084795fce1fc95a1764ac9fade7dfccb7`. CI: Python tests `44404369054` SUCCESS; Python syntax checks `44404369086` SUCCESS. The earlier code-only commit also passed tests `44404354388` and syntax `44404354304`.
- Worker version bump commit `2c09705763d214326a9ef3bc1fe6244e47faa1ee`; README documentation commit `58f0c6e0558636cd0ec5888fdb3a5217340cc866`. Render deployment must be verified before calling V5.36 live.
- The live Alpaca paper account previously verified empty; no test orders have been submitted. Paper execution remains OFF. Real-money trading is not supported.

- V5.36 final verification: Render deploy `dep-dbv1od48775c73ec20g0` is LIVE on commit `58f0c6e0558636cd0ec5888fdb3a5217340cc866`. Startup log confirms `WORKER_VERSION=5.36` at 21:45:43 UTC. The new instance completed a read-only Alpaca snapshot at 21:45:45 UTC: ACTIVE paper account, $100,000 equity, $200,000 buying power, zero Alpaca positions; market-closed gate correctly skipped entries. No brokerage orders were submitted.
- Final worker CI on README commit: tests `44404576962` SUCCESS and syntax checks `44404576894` SUCCESS. Worker version bump commit tests/checks `44404548851` and `44404548850` SUCCESS. Dashboard handoff syntax CI `44404612619` SUCCESS.
- Supabase virtual paper account still separately reports its AAPL/MSFT virtual positions; this is not the Alpaca brokerage account and was not modified. Dashboard Streamlit visual deployment remains unverified.


## 17. V5.37 broker snapshot completeness gate (Nov 18, 2026)
- Continued lifecycle/recovery hardening after V5.36. Found that `evaluate_new_entry_protection_gate` accepted a snapshot with no `position_count`, because it only compared the count when the field happened to be present. This weakened the snapshot completeness contract.
- Changed the gate to require an actual integer (not bool, float, or numeric string) whose value exactly equals the `positions` array length. Missing, malformed, or mismatched count metadata now fails closed as `POSITION_COUNT_MISSING_OR_MISMATCH`. A truly empty account is allowed through this check only with an explicit integer `position_count: 0`.
- Added regression tests for missing, string, boolean, float, and mismatched counts. Preserved the malformed-position-row regression test.
- Code commit `0905de4ea68964f7403973e2fb2a26c3024ed16f`; test commits `8e3f68ab51bcabe101c3857bf0117bd8ab2b8fa1` and `c28ab6705a10107823f0cb4797747cb8e89e734b`. The first test run `44407101652` caught a fixture omission (the malformed-position fixture needed an explicit count); corrected it. Full deterministic worker suite on `c28ab670...` passed: run `44407205659` SUCCESS.
- Version bump to V5.37 commit `344176a54bb8b8de45dbea160da6ac4d2fabe719`; README commit `c747489fe35c24ba4c1ba60931d60a1accfd4a0f`. CI and Render deployment for these final commits must be verified before calling V5.37 live.
- Alpaca feed investigation: official docs confirm the Basic plan's real-time equities feed is IEX only; full-market SIP access is included with Algo Trader Plus (currently documented at $99/month). Paper-only accounts are IEX-only. SIP access requires the appropriate subscription and data endpoint/feed; do not assume that enabling a feed parameter grants entitlement. Keep the current 20 bps spread gate and IEX source fail-closed; do not upgrade or alter feed behavior without explicit user approval. References: https://docs.alpaca.markets/us/docs/about-market-data-api and https://docs.alpaca.markets/us/docs/market-data-faq.
- Safety unchanged: `ALPACA_PAPER_TRADING_ENABLED` remains OFF; no paper or live orders submitted; live brokerage endpoints remain unsupported. Alpaca brokerage paper account is separate from the Supabase virtual account. Dashboard visual deployment remains unverified.

- V5.37 final verification: Render deploy `dep-dbv204nbhbds73f21600` is LIVE on README commit `c747489fe35c24ba4c1ba60931d60a1accfd4a0f`. Startup log at 22:02:15 UTC confirms `WORKER_VERSION=5.37`. The new instance completed a read-only Alpaca paper snapshot at 22:02:17 UTC: ACTIVE, $100,000 equity, $200,000 buying power, zero brokerage positions. Market was closed and entry evaluation correctly skipped. Safety log confirms order submission remains disabled unless the explicit paper flag is enabled.
- Final V5.37 worker CI: tests run `44407353460` SUCCESS and deterministic checks run `44407351019` SUCCESS on README commit `c747489f...`; version bump CI runs `44407336733` and `44407335905` SUCCESS. Dashboard handoff syntax CI run `44407404073` SUCCESS on handoff commit `de653196c5917d89fa71623e402ce835bf3cb635`.


## 18. V5.38 broker-native protective stop risk accounting (Nov 18, 2026)
- Found a conservative compatibility gap in `estimate_existing_open_risk`: it relied on optional `group_role=stop_loss` metadata, while raw Alpaca nested bracket legs are reliably described by broker-native fields such as `type=stop`, `side`, `qty`, `filled_qty`, and `stop_price`. Without a group_role label, existing-position risk could be reported unknown and block otherwise valid new entries.
- Updated risk estimation to infer stop legs from native fields when role metadata is absent. Requires the correct closing side (sell for long, buy for short), a working state when state is supplied, exactly one matching stop per symbol, positive stop price on the protective side of average entry, and sufficient remaining quantity. Partial fills subtract filled quantity before comparing remaining coverage. Unknown, inactive, wrong-side, duplicate, or undersized coverage remains fail-closed.
- Added tests for native Alpaca nested legs without group_role, partial stop fills, wrong-side/inactive/duplicate stop legs, and short-side stop direction. Updated the existing fixture to include realistic side and lifecycle data.
- Code commit `ccfd7115a547974968e035cf5df4ce84581453ab`; tests commit `f2e1e209bdd3b6a8be6d90dd5bd5b04740acfa9e`. Worker CI run `44409838288` SUCCESS (dependency install, compile, and full unit suite).
- Version bump V5.38 commit `81d2da1fb90da4bb7801de8794125e79a70c776c`; README commit `465b298ea077b5beb56adb1ff9a5eb6ecd6e1c27`. Verify final CI and Render deployment before calling V5.38 live.
- Safety unchanged: paper execution switch remains OFF; no paper or live orders submitted. Keep the separate Supabase virtual account untouched.


### V5.38 follow-on hardening and final verification
- Added an additional lifecycle fail-closed guard in `estimate_existing_open_risk`: a candidate protective stop must have an explicit recognized active state (`new`, `accepted`, `pending_new`, or `partially_filled`); missing/unknown/cancel-pending/replace-pending/terminal states do not count. Stop quantity and filled quantity must both be finite and valid; negative fills, fills greater than total quantity, missing fills, and nonpositive order quantity are rejected rather than inflating remaining protection.
- Position side must be explicitly `long` or `short`; risk estimation no longer assumes long when side metadata is missing. Added regression tests for missing lifecycle, cancel/replace pending, invalid fill values, and missing position side.
- Added nested raw Alpaca bracket integration tests confirming parent/child order IDs and client IDs survive normalization, and that a nested cancel-pending stop blocks the new-entry protection gate. Existing OCO partial-exit and child lifecycle tests now include the required position entry basis.
- V5.38 also strengthens broker bracket audit validation: both stop and target prices must be present, positive, and on the protective/profit side of the actual average entry basis for long and short positions. Missing entry basis or malformed exit prices remain UNKNOWN/blocked; wrong-side levels are INVALID_EXIT_PRICE. This is audit-only and does not modify orders.
- The test suite initially exposed fixture gaps after entry-basis validation (synthetic positions missing average entry) and one short-stop fixture missing explicit filled quantity. Fixtures were corrected; no safety rule was weakened. Final full worker tests run `44410152609` SUCCESS and syntax run `44410152361` SUCCESS on commit `c14e1e207c78317654964305aa75b8a9155a2e91`.
- Latest Render deployment for commit `c14e1e207c78317654964305aa75b8a9155a2e91` is `dep-dbv27n153drc73e30100`; deployment/runtime verification is pending at time of this note. Do not mark V5.38 LIVE until the deployment reports live and startup logs confirm version 5.38.
- Safety unchanged: `ALPACA_PAPER_TRADING_ENABLED` remains OFF; no broker orders have been submitted; live brokerage endpoints remain unsupported; Supabase virtual positions remain separate and untouched.


## 19. V5.39 protective bracket price validation (Nov 18, 2026)
- Continued broker lifecycle safety review and found the bracket protection inspector checked active state and remaining share coverage but did not verify that the stop and target prices were protective relative to the actual position's average entry basis.
- The inspector now requires a positive broker-reported average entry price and positive stop/target prices. Long positions require stop < average entry < target; short positions require target < average entry < stop. Missing/invalid price basis returns UNKNOWN; wrongly oriented prices return INVALID_EXIT_PRICE. The new status is not treated as protected by the entry gate.
- Added tests for long stop above entry, long target below entry, short stop below entry, and missing average-entry basis. Existing valid long/short and partial-fill protection fixtures now include realistic entry basis.
- V5.38 also added broker-native nested stop-risk recognition without optional group_role, with correct closing side, lifecycle, remaining quantity, unique stop, and long/short direction checks. A CI failure exposed that one short-stop test fixture omitted filled_qty; the implementation correctly failed closed, and the fixture was corrected to explicitly model Alpaca's zero-fill state.
- Final complete worker tests and compile checks passed on commit `c14e1e207c78317654964305aa75b8a9155a2e91`: runs `44410152361` and `44410152609` SUCCESS. Earlier intermediate test runs failed on incomplete fixtures and were corrected; do not treat those intermediate commits as release verification.
- V5.39 version commit `22d24f8727f1ead67f2e6d00d30adb3ac8ab49fa`; README commit `3762d4fa6bfee706c774113ff59cd58019dc0595`. Final CI and Render deployment for V5.39 must be verified before calling it live.
- Safety unchanged: paper execution switch remains OFF; no paper/live orders submitted. Keep the Supabase virtual account separate and untouched. No risk thresholds were relaxed.


- Final V5.38 hardening/verification: protection checks now also require valid stop/target prices relative to the actual position average entry (long: stop < entry < target; short: target < entry < stop). Open-risk estimation requires explicit confirmed active lifecycle and valid explicit filled quantity; missing/negative/overfilled quantities, pending-cancel/replace, wrong-side, duplicate, or undersized stops fail closed. Fixtures were corrected to include real entry basis and explicit stop fill quantities after CI exposed omissions.
- Final worker test and syntax workflows passed on `c14e1e207c78317654964305aa75b8a9155a2e91`: test run `44410152609` SUCCESS; syntax run `44410152361` SUCCESS. Render deploy `dep-dbv27n153drc73e30100` is LIVE on that commit; startup log at 22:17:50 UTC confirms `WORKER_VERSION=5.38` and the safety-mode warning. Runtime logs also show the Supabase virtual paper account still monitors its existing AAPL/MSFT positions; Alpaca brokerage paper account remains a separate account. No broker orders were submitted.
- The scanner returned 239/240 symbols; UNI-USD had no daily bars from Yahoo Finance. This is an isolated provider data gap, not a worker startup failure; coverage was 99.6%. Keep this visible as partial scan coverage rather than treating the missing symbol as a valid no-signal.
- Dashboard handoff CI for the previous handoff passed; the additional V5.38 runtime/test details in this append require the new dashboard syntax run to finish.

- V5.39 final verification: worker test and compile workflows passed on code/version commit `22d24f8727f1ead67f2e6d00d30adb3ac8ab49fa` (runs `44410291168` and `44410291166`) and the final README commit `541419268f5b6d1266b3d583708a41c23539c82d` passed full tests/compile (run `44410343137`). Render deploy `dep-dbv28cajnfac739htdpg` is LIVE on the V5.39 version commit. Startup log at 22:19:06 UTC confirms `WORKER_VERSION=5.39`; runtime safety log confirms order submission remains disabled unless the explicit paper flag is enabled. A follow-on README-only commit `54141926...` is also being deployed; it does not change worker code. Dashboard handoff CI run `44410380164` SUCCESS.


### V5.39 additional fail-closed exit-fill checks
- Tightened `inspect_bracket_protection` as well as the open-risk estimator: stop and target children require explicit finite `filled_qty` values between zero and total quantity. Missing, NaN, negative, or overfilled quantities no longer default to full remaining coverage. The broker position must explicitly state `long` or `short`; direct audit inspection no longer silently assumes long.
- Added regression tests for missing/invalid child fill quantities and missing position side. Updated broker-audit fixtures to represent explicit broker fill quantities.
- The first CI attempt exposed three audit fixtures that lacked child `filled_qty`; fixtures were corrected without weakening validation. Final worker full-suite run `44410426880` SUCCESS and syntax run `44410426868` SUCCESS on commit `e40b8e8cabfc0103408dfa76b77d53f90a16e862`.
- Render deployment for `e40b8e8...` is queued/in progress; do not mark this latest V5.39 code live until Render confirms it.

- Additional worker-cycle regression coverage: added `tests/test_worker_execution_snapshot_gate.py` with four execution-cycle checks: missing snapshot skips without database access; stale snapshot skips before daily guardrail/database access; missing position_count blocks before market scan; and a complete fresh empty-account snapshot reaches the market-closed gate without querying candidates. Optional yfinance/Supabase/OpenAI imports are stubbed only for these isolated unit tests; no network or broker action occurs.
- Full deterministic suite now passes **170 tests** plus compile checks on test commit `065dba24ebd41bf733353888506216ea7544033a`, CI run `44410732448` SUCCESS. V5.39 code remains live from Render deploy `dep-dbv28l7trrvc73b9c4e0` (commit `825771e4...`), which includes the corrected V5.39 docstring. The latest test-only commit's Render build is still in progress at the time of this note; no runtime code changed in that test commit.


### V5.39 snapshot-cycle integration tests
- Added worker-level tests around `run_paper_execution_cycle`: missing snapshot returns without DB access; stale snapshot exits before daily-loss persistence; missing `position_count` blocks before candidate/market-scan work; a complete fresh empty snapshot reaches the expected market-closed gate without touching the DB.
- The first attempt correctly surfaced that the minimal CI environment does not install optional provider SDKs. Added import-only stubs for yfinance, Supabase, and OpenAI in the test module; no network clients are invoked by these tests.
- Final worker test run `44410732448` SUCCESS and syntax run `44410732398` SUCCESS on commit `065dba24ebd41bf733353888506216ea7544033a`.
- This final commit adds tests/stubs only; the V5.39 runtime code was already live on Render commit `825771e4bb85a33a14a44b0360f934fd0f2b1d13` (deploy `dep-dbv28l7trrvc73b9c4e0`). The follow-on test-only commit `065dba24...` has a Render build in progress and does not alter worker runtime behavior.


- Final V5.39 deployment verification: Render deploy `dep-dbv29ksel2ts73b8784g` is LIVE on test/stub commit `065dba24ebd41bf733353888506216ea7544033a`. Startup at 22:22:15 UTC confirms `WORKER_VERSION=5.39`; safety log explicitly confirms order submission remains disabled unless the explicit paper flag is enabled. The new instance continues to monitor only the separate Supabase virtual AAPL/MSFT positions; Alpaca paper read-only snapshot verification was completed on the preceding V5.39 runtime deployment. No brokerage orders were submitted.
- Dashboard handoff syntax workflow for the current note is run `44410892055`; verify its completion before treating the handoff CI as green.


### V5.39 expanded worker preflight matrix (Nov 18, 2026)
- Expanded integration-level run_paper_execution_cycle tests with three additional cases: non-PA/unverified account identity blocks before the daily guardrail, trading_blocked=true blocks before the guardrail, and an existing unprotected position blocks before market-scan access.
- Combined with the earlier four cases (missing snapshot, stale snapshot, missing position count, and complete fresh empty snapshot), the worker-level preflight matrix now covers seven critical gate paths.
- Full unit suite and compile checks passed on commit 33e1927ed3430fd9e9df8c4393c8d94a66a14b0a: test run 44410890180 SUCCESS; syntax run 44410890066 SUCCESS. Dashboard handoff syntax run 44410892055 SUCCESS before this additional note.
- README update commit f10a2fb0c2c97bf4ff0f76e1f3df1dc83dde4f51 documents the added preflight tests. The V5.39 worker code is already live; subsequent test/documentation-only commits do not change the execution engine. Keep paper execution OFF.


- Additional audit-integrity guard: `reconcile_broker_order_audit` now compares the normalized broker order symbol with the matched Supabase audit-row symbol before writing lifecycle/protection data. Missing or mismatched symbols are skipped and logged, preventing a client-ID collision or malformed row from applying broker state to the wrong instrument. Code commit `a3ebbbe493bb0d6d508d8805dc5f519ddb124a8e`; regression test commit `40184b0cb17df2ccfec9f54c8494e9c813ea1af7`. Full worker suite: **175 tests passed**, compile passed, CI run `44411100239` SUCCESS.


## V5.40 exact paper-account identity binding (Nov 18, 2026)
- Found a safety gap in the paper order gateway: it verified that the broker account had a PA prefix, but did not prove it was the exact paper account used to size the candidate. A credential/account switch between the read-only sizing snapshot and the order request could have routed the bracket into a different paper account.
- Changed submit_paper_bracket_order to require expected_account_number from the fresh snapshot. The gateway validates that expected identity is a PA account, verifies the live paper account is active/unblocked, and compares the actual account number exactly before even looking up the client_order_id or sending a POST. Missing or mismatched expected identity blocks without any broker order lookup/submission.
- Worker now passes snapshot.account_number into the order gateway. Added tests for mismatched PA account, missing expected account, and successful same-account path. Updated the AST intent-order test to recognize the multiline gateway call.
- Adapter commit f2cd33211aa66565456e8e558e8a15d72207f53e; worker commit 309759c8b217a678d7822f7b546bca00ea7777ad; test commit 9f38ea61a34ac21de7203cc526a2ef5b656d51c8; follow-up test matcher commit 2e7424a070d8bee7e1957c493db03f16a251ca5d.
- Full worker suite and compile checks passed on final test commit: run 44411371913 SUCCESS; syntax run 44411371909 SUCCESS. V5.40 version commit 65ae79e08061d823ad4748b3131a8e5b0e692c97; README commit 8223897b14095884c9098fbaa99d864b6e0f2143. Verify final CI and Render startup before calling V5.40 live.
- Safety remains unchanged: ALPACA_PAPER_TRADING_ENABLED stays OFF; no paper or live orders are submitted by this work. This guard makes the already paper-only path more specific; it does not authorize execution.


### V5.40 idempotency lookup fail-closed guard
- Found a duplicate-order edge case: the idempotency lookup previously treated any response without an `id` as evidence that no order existed. A successful but malformed response could therefore have allowed a duplicate POST.
- Added a private explicit `_ORDER_NOT_FOUND` sentinel returned only for the broker's 404 on the exact client-order lookup route. A new POST is permitted only for that sentinel. A JSON `null`, empty object, malformed payload, or response without an order ID now raises a safe execution error and blocks submission.
- Regression tests cover malformed object and JSON-null lookup responses, while confirming the explicit not-found path remains the only path to a new POST. Adapter code commit `f60cbd16d667b8ee1aaa0136a00c86f73271ad6a`; test commit `067de347802c61a7b4f4c483c0fec11791fe03f8`. Full worker suite run `44411559931` SUCCESS; syntax run `44411559740` SUCCESS.
- README records the V5.40 idempotency guard in commit `4cd3140ffd77878b9017e13457167970b66ce27a`. The Render deploy for the final code/test commit `067de347...` is in progress; verify it before marking the newest V5.40 revision live.
- V5.40 safety state unchanged: `ALPACA_PAPER_TRADING_ENABLED` remains OFF, no orders have been submitted, and no live brokerage endpoints exist in the adapter.

- V5.40 final verification: worker test run `44411559931` and syntax/compile run `44411559740` both SUCCESS on final idempotency-test commit `067de347802c61a7b4f4c483c0fec11791fe03f8`; the full suite passed **179 tests**. Render deploy `dep-dbv2bonbhbds73f2cmrg` is LIVE on that commit. Startup at 22:27:06 UTC confirms `WORKER_VERSION=5.40`; safety-mode log confirms order submission remains disabled unless explicit opt-in is enabled. Fresh read-only Alpaca paper snapshot at 22:27:08 UTC showed ACTIVE, $100,000 equity, $200,000 buying power, and zero brokerage positions. The market-closed entry gate correctly skipped evaluation. No brokerage orders were submitted.
- V5.40 idempotency lookup now uses a dedicated sentinel for the broker's explicit 404/not-found response. Only that exact condition permits a POST. A successful response containing JSON null, an empty object, or an object without an order ID blocks submission. Regression tests cover malformed/null lookup, duplicate existing order, and explicit not-found path.
- Latest dashboard handoff syntax CI for this update must be checked after commit. V5.40 runtime is live; paper execution remains OFF.


- V5.40 runtime verification: Render deploy `dep-dbv2bonbhbds73f2cmrg` is LIVE on final code/test commit `067de347802c61a7b4f4c483c0fec11791fe03f8`. Startup at 22:27:06 UTC confirms `WORKER_VERSION=5.40`; safety log confirms order submission remains disabled unless `ALPACA_PAPER_TRADING_ENABLED=true`. Fresh read-only Alpaca paper snapshot at 22:27:08 UTC: ACTIVE, $100,000 equity, $200,000 buying power, zero brokerage positions. Market closed and entry evaluation skipped. Supabase virtual account remains separate and monitors its existing AAPL/MSFT positions. No brokerage orders submitted.


- Final V5.40 documentation/runtime confirmation: README commit `4cd3140ffd77878b9017e13457167970b66ce27a` is LIVE on Render deploy `dep-dbv2cd2vcj2c73c0d710`; startup at 22:27:48 UTC again confirms `WORKER_VERSION=5.40` and the paper-only safety warning. Dashboard handoff syntax CI run `44411795957` SUCCESS on commit `1a62ca407d7a8a0acb2d1daa7ee2175c379b8ed4`.


## V5.41 complete Alpaca account restriction gates (Nov 18, 2026)
- Hardened account eligibility in both the read-only snapshot and order gateway. Three broker flags must now be explicitly boolean false: trading_blocked, account_blocked, and trade_suspended_by_user. Missing, null, string-encoded, or true values fail closed before daily-loss guardrail/candidate evaluation and before any client-order lookup or POST.
- Alpaca snapshot normalization now preserves account_blocked and trade_suspended_by_user in addition to trading_blocked. Worker preflight checks all three; order gateway independently re-verifies all three on the fixed paper host and still requires exact expected PA account identity from the sizing snapshot.
- Added tests covering missing/unknown states for each restriction flag, worker preflight, adapter gateway, and snapshot normalization. The final fixture update was necessary because successful paper-account mocks must explicitly model all three false flags.
- Code commits: preserve flags 5a447b5f2d..., require all flags clear d11232f100..., worker gate f27f651c51...; final tests commit 71ff28c7c29207a8648ec481568cb81e13bce875. Full test suite and compile checks passed: run 44412195398 SUCCESS; syntax run 44412195255 SUCCESS.
- Version bump V5.41 commit e4211cb56376648901b155deca253982c59a7a31; README commit 4a46f958eba6a01b408ff6cd5d0496e258b50482. Verify final CI and Render startup before calling V5.41 live.
- Safety unchanged: ALPACA_PAPER_TRADING_ENABLED remains OFF. No paper or live orders submitted.

- V5.41 final verification: worker tests/compile passed on account-flag test commit 71ff28c7c29207a8648ec481568cb81e13bce875 (run 44412195398 SUCCESS); version bump CI runs 44412352097 and 44412351850 SUCCESS; README CI runs 44412374163 and 44412373910 SUCCESS. Render deploy dep-dbv2ed3u2v8c73fe3h00 is LIVE on README commit 4a46f958eba6a01b408ff6cd5d0496e258b50482. Startup at 22:32:37 UTC confirms WORKER_VERSION=5.41 and safety mode. Fresh Alpaca paper read-only snapshot at 22:32:39 UTC: ACTIVE, $100,000 equity, $200,000 buying power, zero brokerage positions. Supabase virtual AAPL/MSFT holdings remain separate and unchanged. Dashboard handoff CI run 44412414579 SUCCESS.


## V5.42 idempotent existing-order identity validation (Nov 18, 2026)
- Hardened the successful client_order_id lookup path. An existing-order hit is now accepted as idempotent only if it contains a valid broker order ID and exactly matches the requested client_order_id, symbol, side, order type, order class, time-in-force, and quantity. A malformed response or a client-ID collision with a different order fails closed; it never triggers a second POST and is not mislabeled as the requested order.
- Added regression tests for collisions in symbol, quantity, side, type, order_class, time_in_force, and client_order_id; preserved tests for malformed/null lookup responses and a legitimate matching existing order.
- Code commit 587b9690d633f31eedb2a5e0c6f9c79c6be5287f; tests commit 05070d338d39731e22cc723af38ff03ece8d470d. Full worker suite and compile checks passed: run 44412777496 SUCCESS; syntax run 44412777457 SUCCESS.
- Version bump V5.42 commit 233d58d8a56df822a6ff8ea0006bdc1260d6f3e6; README commit 5d515d6c2f0ff56171926c6c4ee8b8bb08d8d2c9. Verify final CI and Render startup before calling V5.42 live.
- Safety unchanged: order gateway remains fixed to Alpaca paper host, exact PA account identity required, all account restriction flags must be explicitly false, malformed idempotency lookup blocks, and ALPACA_PAPER_TRADING_ENABLED remains OFF.

- V5.42 final verification: worker test and compile run `44413001652` SUCCESS on README commit `5d515d6c2f0ff56171926c6c4ee8b8bb08d8d2c9`; full suite passed **184 tests**. Render deploy `dep-dbv2g70qsg7c73e7oqk0` is LIVE on the V5.42 code/version commit `233d58d8a56df822a6ff8ea0006bdc1260d6f3e6`. Startup at 22:35:58 UTC confirms `WORKER_VERSION=5.42` and the paper-only safety warning. `ALPACA_PAPER_TRADING_ENABLED` remains OFF; no brokerage orders submitted. The follow-on README-only deploy may still be queued; it does not alter worker code.


## V5.43 account restriction observability (Nov 18, 2026)
- Added explicit startup/preflight observability for Alpaca paper-account restriction flags so each eligibility check records the three broker states: `trading_blocked`, `account_blocked`, and `trade_suspended_by_user`. These remain required explicit booleans set to false; missing, unknown, malformed, or true values fail closed.
- The order gateway independently checks the same restrictions before order lookup or submission; this is observability and defense-in-depth, not an execution enablement.
- V5.43 code/version commit `a1f5885d43f1`; README/docs commit `d9d8e2a6c5d31ee3e7b4aa4c5f4bf0ef3a9bb4fd`. Worker test + compile run `44413290275` SUCCESS. Full suite passed; no regression in the account, order-identity, lifecycle, or risk-gate checks.
- Render deploy for docs commit `d9d8e2a6...` is building as of 22:37 UTC; previous V5.42 deployment remains the last confirmed LIVE version until V5.43 startup is verified.
- Latest Render scan logs from the existing worker show 239/240 daily symbols analyzed (99.6% coverage); UNI-USD was the one Yahoo Finance no-data symbol. The scanner reported 41 BUY CANDIDATE labels, but these are research observations only—not execution approvals or trades. Data coverage remains visibly PARTIAL rather than silently treating missing data as complete.
- Safety remains unchanged: `ALPACA_PAPER_TRADING_ENABLED` OFF, no brokerage orders submitted, no live endpoints, and Supabase virtual holdings remain separate.

- V5.43 final verification: worker test/compile run `44413290275` SUCCESS; Render deploy `dep-dbv2h39j7cmc73dfe5ig` LIVE. Runtime startup at 22:38:26 UTC confirms `WORKER_VERSION=5.43`; read-only Alpaca paper snapshot at 22:38:28 UTC shows ACTIVE, $100,000 equity, $200,000 buying power, zero brokerage positions, and all three account restriction flags explicitly false. Safety log confirms order submission remains disabled unless the explicit paper switch is enabled. Dashboard handoff syntax CI run `44413444705` SUCCESS on this update.
