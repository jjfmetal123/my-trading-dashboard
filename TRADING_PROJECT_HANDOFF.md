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


## V5.43 account-state observability and broker identity response validation (Nov 18, 2026)
- Added all three account restriction flags to the periodic read-only Alpaca snapshot log. Verified live log at 22:38:28 UTC reports `trading_blocked=false`, `account_blocked=false`, and `trade_suspended_by_user=false`.
- Existing client-order-ID hits now also require a valid UUID broker order ID and a non-empty lifecycle status before being accepted as already-existing. Malformed IDs or missing status block the idempotent path and never trigger another POST.
- Added tests for malformed UUID and missing lifecycle status. Final worker test/compile run `44413500064` SUCCESS on test commit `9fd39b75fbc9d6dcae018b72daba56a82a356e46`; full suite passed **186 tests**.
- V5.43 code/version commit `a1f5885d43f182b88a71a0f73075e01cea6521eb`; order ID/lifecycle validation commit `a3eb088bbf78b5a35d52bb0f87ebfdb56b82ccd9`; README commit `d9d8e2a6c5d31ee3e7b4aa4c5f4bf0ef3a9bb4fd`. Render deploy `dep-dbv2h39j7cmc73dfe5ig` is LIVE and startup confirms `WORKER_VERSION=5.43` at 22:38:26 UTC. Safety log confirms paper order submission remains disabled unless explicit opt-in is enabled.
- Fresh read-only Alpaca snapshot at 22:38:28 UTC: ACTIVE, $100,000 equity, $200,000 buying power, zero brokerage positions, and all three account restriction flags false. Market was closed; entry evaluation skipped. No brokerage orders submitted.


## V5.44 known lifecycle validation for existing-order idempotency (Nov 18, 2026)
- Tightened _validate_existing_order: an idempotency lookup hit must contain a string lifecycle status from Alpaca's recognized order-status set. Missing, numeric, empty, or unknown status values fail closed. Recognized working and terminal states are accepted as proof that the client ID already exists, preventing a duplicate POST without implying the order remains open/protective.
- Existing-order identity checks still require valid UUID, exact client order ID, symbol, side, type, order class, time-in-force, and exact quantity.
- Adapter code commit 4c7e8926ca0cc0a1edf2d8624669ab418e81ba74; regression test commit 98aaa33268c2af9ec5ca16b18d2d2580da5bb01c. Worker CI run 44413731557 SUCCESS (compile + full unit suite).
- Version bump commit 3fa574696ebda693729e7a1a6dae0e940f9867ac; README commit ad22c9f60d2d09d3368b0d6605265391ae46004e. Verify latest CI and Render startup before calling V5.44 live.
- Safety unchanged: Alpaca fixed paper host only, explicit PA account match, all account restrictions must be false, paper execution switch OFF, and no brokerage orders submitted.

- V5.44 final verification: worker test/compile run `44413860888` SUCCESS on README commit `ad22c9f60d2d09d3368b0d6605265391ae46004e`; full suite passed **187 tests**. README syntax run `44413893282` SUCCESS. Render deploy `dep-dbv2iq0qsg7c73e7r8m0` is LIVE; startup at 22:41:40 UTC confirms `WORKER_VERSION=5.44`. Latest read-only Alpaca snapshot at 22:41:43 UTC: ACTIVE, $100,000 equity, $200,000 buying power, zero brokerage positions, and all three account restrictions false. Paper-only safety mode remains active; order switch OFF and no brokerage orders submitted.


## V5.45 nested existing-bracket identity and exit protection verification (Nov 18, 2026)
- Hardened the idempotency path beyond parent-order matching. After a valid client-order-ID hit, the gateway performs a second read-only GET by the same broker order ID with nested=true, revalidates the returned parent, and requires the nested response to preserve that exact parent ID.
- The nested parent must include exactly two attached child legs: stop-loss and take-profit. Each child must match the expected symbol, closing side, order type, whole-share quantity, and exact normalized protective price. Missing, malformed, duplicate, wrong-symbol, wrong-side, wrong-price, wrong-quantity, or parent-ID-mismatched legs fail closed; no second POST is sent.
- Alpaca documents nested=true on GET /v2/orders/{order_id} to roll child orders under the parent legs array (official API docs: https://docs.alpaca.markets/us/reference/getorderbyorderid-1). The client-order-ID lookup remains the first read; the nested GET is used only to verify the exact bracket returned by that lookup.
- Adapter commits: 545f3af373ed (nested leg verification), 9f6b87d25af0 (syntax correction), 74af6d1a8d18 (bind nested response to original parent ID), d1638194351e (validate child symbol). Test commits: d5871a157613, 69c3d15f8e80, 8e77c12b9550. Worker CI run 44414376412 SUCCESS on the final nested child-symbol test commit; parent-ID test run 44414301182 SUCCESS.
- V5.45 version commit a0cc755ee12dcdb2eb2ab9cd7e165eab9f27988a; README commit a8e4393aaadc3a61eb30a7e0753b1e959b8449c2. Latest CI and Render startup still need final confirmation before marking V5.45 runtime live.
- Safety unchanged: paper execution switch OFF, fixed Alpaca paper host only, exact PA account match, explicit unblocked account flags, no live endpoints, and no orders submitted.

- V5.45 final runtime verification: latest worker version commit `181405be91bd` and README commit `82e289b89a91`; worker CI runs `44414488862` and `44414501474` SUCCESS. Render deploy `dep-dbv2ki0qsg7c73e7soa0` LIVE on `82e289b89a91`. Startup at 22:45:48 UTC confirms `WORKER_VERSION=5.45`; fresh Alpaca paper read-only snapshot at 22:45:50 UTC confirms ACTIVE, $100,000 equity, $200,000 buying power, zero broker positions, and all three restriction flags false. Safety mode still reports order submission disabled unless explicitly enabled. Dashboard handoff syntax CI run `44414534868` SUCCESS. The Supabase virtual paper account's separate AAPL/MSFT positions were read-only monitored; their stale intraday bars were explicitly skipped, with no exit evaluation on stale data.

- V5.45 final verification: test/compile run `44414376412` SUCCESS on nested child-symbol test commit `8e77c12b9550451cc57ac4630c146314b52e32fc`; full suite passed **189 tests**. Version commit `181405be91bd07c0c7ebea9eea0ea7c72b4827c9` and README commit `82e289b89a9135a53de547fdcfffebb00c235454` passed CI. Render deploy `dep-dbv2ki0qsg7c73e7soa0` is LIVE; startup at 22:45:48 UTC confirms `WORKER_VERSION=5.45` and paper-only safety mode. No brokerage orders submitted; order switch remains OFF.

## 2026-11-20 live continuation checkpoint

**Verified current repositories and deployment state (do not rely on the older V5.45 checkpoint above):**

### Dashboard
- Repository: `jjfmetal123/my-trading-dashboard`
- Current `main` head after the handoff update: `4a68771107159113d3f35b4d9c732653800ef767` (feature commit `5efe7fb14ba5b6a37db005b305a17f2df92431ee`, followed by the handoff checkpoint).
- Dashboard PR #8 (resilience/responsive layout), PR #14 (unique diagnostics-module import), PR #16 (restore missing read-only data loaders), and PR #17 (dedicated read-only Alpaca Paper Trading tab) are merged.
- Current `app.py` imports `dashboard_validation_diagnostics`; that exact module exists in `main`. Dashboard CI for current main commit passed (compile-and-test).
- Streamlit Community Cloud runtime still requires user-side visual confirmation; GitHub CI does not prove the hosted app has refreshed.

### Cloud worker
- Repository: `jjfmetal123/trading-cloud-worker`
- Current `main` commit: `438910d1e3fc9979d721178bb90a624992e593ce`.
- Worker runtime version: **V5.95** (confirmed by Render startup log at 2026-11-20 19:57:49 UTC). The worker source constant is V5.95; its module docstring and README heading still say V5.93 and need a documentation consistency pass.
- Render service: `srv-dbua8frm8hqs73f895h0`, workspace `tea-dbu9vo6tlv9c73bqbdh0`.
- Latest deploy for current main commit is LIVE: `dep-dc0abrntfofc73a4n7b0`.
- PR #24 corrected Alpaca bracket-stop lifecycle handling: raw `held` is normalized to `HELD` and counts as active only for the conditional stop-loss leg, never for a held take-profit leg.
- PR #25 merged as `7a3c42189fc0ed4113d747adfa06a0a0120717d6` and deployed. It adds explicit paper-execution switch logs, per-position protection audits, and per-cycle decision/reason summaries; no execution policy changed.
- PR #26 merged as `83b6648514606434c319be2df1b82f66573f5654` and deployed. Adds shadow-only annualized-volatility bands, ATR context, stop-risk-per-share, and theoretical whole-share capacity against strategy capital.
- PR #27 merged as `438910d1e3fc9979d721178bb90a624992e593ce` and deployed. Preserves Alpaca quote exchange/condition/tape metadata and marks locked quotes as diagnostic CAUTION; it does not change execution quote acceptance.
- CI passed on the PR #25, #26, and #27 heads.

### Current paper-account observation and safety
- Render logs at 2026-11-20 19:57 UTC report the Alpaca paper account ACTIVE with equity approximately **$4,998** and one open symbol, **ORLY**.
- Execution-cycle logs report `auto_enabled=True`; automatic execution is currently enabled for the paper account. Keep this setting unchanged unless the user explicitly directs otherwise.
- The worker is paper-only. The order adapter is hard-pinned to Alpaca's paper endpoint; live brokerage endpoints are prohibited.
- The current strategy allocation is **$5,000**, with the fixed **$50 daily-loss stop** from PR #23. The worker source also keeps ICE excluded from new-entry candidates while its separate exit/reconciliation issue is unresolved; this is not an instruction to close or modify the existing ICE position. Do not reset, reseed, or alter the broker account or the separate retired Supabase virtual-account archive.
- Recent cycles evaluated 35 candidates (15 long / 20 short) and submitted zero new orders because no candidate passed all gates. This is not a stopped worker; the scanner and paper decision cycle continue.
- The previous ORLY protection warnings were caused by the `held` stop-leg normalization gap addressed in PR #24. Confirm a fresh post-deploy `BROKER POSITION PROTECTION AUDIT` before claiming ORLY is protected; do not cancel, replace, or modify any broker order as part of verification.

### Open engineering work
- PR #28 (`Add shadow-only near-miss diagnostics`) remains a draft and is **not merged or deployed**. It adds distance-to-trigger margins and 1/5/10-minute shadow outcome observations.
- Review identified a concurrency hazard: the shadow collector read and replaced the entire `paper_trade_decisions.decision` JSONB value, potentially overwriting a simultaneous broker lifecycle update.
- A compare-and-set guard has now been added to PR #28: the update must match both row ID and the original `updated_at`. If broker reconciliation has advanced the row, the shadow write becomes a no-op and can be retried on a later pass. Regression tests were added for the successful write, concurrent broker update, and missing row version. Latest PR head: `acf4861e6a4f8b6a59ebfb77a031ca81fe8e478a`; fresh CI has not appeared yet (zero check runs/statuses), so verify the workflow trigger and run tests before merge.
- PR #28 must remain unmerged until the latest CI is green and the persistence guard is reviewed.
- The volatility-transition research chain remains open in stacked PRs #4–#9. It targets post-transition sessions 1, 5, 10, and 20, matched against stable-volatility observations, with chronological holdout and uncertainty checks. Preserve its shadow/research-only authority boundary and inspect branch ancestry before merging any stacked PR.
- PR #16 (449-symbol universe expansion) remains open; do not merge without a separate data-coverage/runtime review.
- Next exact actions: (1) verify the latest V5.93 startup and post-PR #24 ORLY protection audit; (2) verify the post-PR #25 execution-cycle summary and current switch state; (3) confirm PR #28 CAS tests pass and keep it draft until safe; (4) continue the 1/5/10/20-session volatility-transition study; (5) visually confirm the Streamlit dashboard deployment.

**Non-negotiable:** paper-only execution, no live endpoint/credentials, no broker/account reset, no mutation of the archived Supabase virtual account, and no enabling/disabling of automatic paper execution without explicit user direction.


## 2026-11-20 continuation update — PR #28 CAS verification pass

- Re-verified dashboard main at 6870ccd50d26cd8f0f37ba4aa909e6180fa52b22; Dashboard Python checks run 44807206389 SUCCESS. Dashboard open PRs: #1–#7 (volatility-transition/evidence research stack). PRs #8, #14, #16, and #17 are merged. Current main branch contains the dedicated read-only Alpaca Paper Trading tab and restored data loaders. Streamlit Community Cloud visual/runtime confirmation remains unavailable from this session; do not claim deployment verified.
- Re-verified worker main at 919f5a8f73869943c3de5772e13f30cda85fca31; Python tests run 44807365245 SUCCESS and Python checks run 44807365307 SUCCESS. Open worker PRs: #1–#9, #16, #17, and #28.
- Render worker service srv-dbua8frm8hqs73f895h0 is not suspended. Deploy dep-dc0adlm7bikc73fnlov0 for 919f5a8 is LIVE; startup at 2026-11-20 20:02:02 UTC confirms V5.95. Read-only Alpaca snapshots after deploy show ACTIVE, equity about $4,998, and ORLY as the one open broker symbol. The last observed execution cycle before the deploy (19:56:29 UTC) evaluated 35 candidates, had zero ready, zero newly submitted, and logged auto_enabled=True. After the V5.95 deploy, scanning, paper-account read-only snapshots, and simulation replay are visible; no post-deploy execution-cycle line was found in the inspected log window. Recheck the next cycle before claiming current-cycle execution state.
- PR #28 feat/near-miss-shadow-diagnostics-20261120 is open, non-draft, and not mergeable at present. It is 19 commits ahead / 4 behind worker main; merge base is b01c6c5bfb1f492379e3ff21edd3c70e8020ac6c. Do not merge until the branch is reconciled with main, mergeability is restored, and current-head CI passes.
- PR #28 head was advanced with a persistence correctness improvement: persist_shadow_outcome_update now requests the updated row ID and returns success only when the compare-and-set actually updated a row. The regression fake now returns selected rows and the concurrent-broker-update test asserts the stale shadow write returns false while preserving broker state. Commits: 407bd595d1a0c245f171436dba237eb4933e9ac4 and 401f0519b5d39887f3a504b333022f91bef8e59b.
- CI caveat: current PR #28 head 401f0519b5d39887f3a504b333022f91bef8e59b has zero GitHub check-runs and no workflow runs. Earlier PR head f41f588d9cadc9cd3e226ee9424f492ff8fa3cc3 passed Python tests/checks (runs 44806014128, 44806013979); several earlier intermediate revisions failed. The latest head is unvalidated; do not merge or deploy it. Worker main CI remains green.
- Safety: no live endpoint or credentials; no account reset or Supabase archive mutation. Preserve the current paper-only configuration. Do not change the existing paper execution enablement without explicit direction. Recent pre-deploy cycle submitted zero orders.
- Next exact actions: (1) reconcile PR #28's four-commit divergence from main without losing its shadow-only isolation; (2) get fresh CI on the reconciled head and review test output; (3) only then decide whether to merge/deploy; (4) confirm the next V5.95 execution-cycle and ORLY protection audit; (5) continue dashboard Streamlit visual verification. The shadow collector must never affect ranking, risk gates, sizing, protective orders, or broker execution.


## 2026-11-20 continuation update — PR #28 reconciled and CI green

- Worker PR #28 (`Add shadow-only near-miss diagnostics`) is reconciled with current worker main `919f5a8f73869943c3de5772e13f30cda85fca31`; merge base is now current main and compare reports 21 commits ahead / 0 behind. GitHub reports mergeable. Latest PR head `9adb45d51f8017b307f1da4cc8f8ff2b173ba530`.
- Reconciliation retained main's newer README/V5.95, Alpaca quote feed/provenance, shadow volatility diagnostics, and current risk policy while carrying PR #28's near-miss and outcome collection changes. Added tests for long/short trigger distance, threshold margins, and unknown/missing data. Added README documentation.
- CI on latest PR head is GREEN: Python checks run `44808524770` SUCCESS; Python tests run `44808524824` SUCCESS; full unittest suite passed **456 tests**. An earlier run failed because a test fixture used signal score 80 below the configured 90 threshold; corrected the fixture to 100 without weakening policy, then reran successfully.
- PR #28 remains unmerged and undeployed. Render worker service has `autoDeploy=yes` on main, so merging would automatically deploy the new collector. Keep it open until a separate explicit merge/deployment decision; no worker runtime behavior changed this session.
- Latest Render checks after V5.95 deploy show Alpaca paper account ACTIVE, equity approximately `$4,997.64`, one open symbol `ORLY`; only read-only snapshots appeared in the latest inspected window. Do not claim a new execution cycle or ORLY protection audit unless fresh matching logs are found.
- The next major research priority remains the stacked volatility-transition response chain: worker PRs #5–#9 and dashboard PRs #3–#7. It already targets exact post-transition session ages 1, 5, 10, and 20; comparisons are matched on setup, score bucket, trend regime, current volatility regime, and forward horizon, with stable controls, de-overlap, chronological 70/30 holdout, purge of overlapping training windows, block-bootstrap uncertainty, calendar-year robustness, classification sensitivity, and full-history occupancy/date-shift analysis. All remain research-only with `authority=NONE`; inspect data coverage and branch ancestry before merging any stacked PR.
- Safety remains unchanged: paper-only endpoints; current paper execution enablement unchanged; no live endpoints/credentials; no broker/account reset; no mutation of the retired Supabase virtual-account archive; no changes to stops, sizing, ranking, or execution policy.


## 2026-11-20 continuation update — independent paper-execution scheduler PR #29

- Runtime log review after V5.95 deploy: Render confirms worker process alive, continuous intelligence engines running, broker snapshot poller refreshing Alpaca paper account about once per minute, and account ACTIVE with equity around `$4,997.69` and ORLY as the only open broker symbol. The last inspected window (20:00–20:10 UTC) contained no `PAPER EXECUTION CYCLE START/SUMMARY` and no `BROKER POSITION PROTECTION AUDIT` after the 20:01:56 UTC deploy. Do not claim new execution-cycle or ORLY protection confirmation from this window.
- Root cause identified in `worker.py`: `main()` calls synchronous `run_market_scan()` before its inline paper execution cycle; `run_market_scan()` then runs three historical replay/backtest jobs after persisting the fresh scan. This can block the main thread and starve paper decision cycles even though the broker snapshot poller and intelligence threads remain alive.
- Opened draft worker PR #29 `Run paper execution cycles independently of market scans`: `https://github.com/jjfmetal123/trading-cloud-worker/pull/29`. It registers `run_paper_execution_cycle` as its own `ContinuousEngineSupervisor` engine with a separate Supabase client, obtains the latest thread-safe broker snapshot from `BrokerSnapshotPoller`, removes the inline cycle from the scan loop, and stops the execution supervisor before the snapshot poller on shutdown. No entry/exit logic, risk settings, protective-order logic, or paper switch changed.
- PR #29 latest head `5cd66278f3e919770dace96449e70bb28ff03cd6`; Python tests run `44809460096` SUCCESS (**448 tests passed**), Python checks run `44809460018` SUCCESS. Regression tests verify scheduler wiring and that the independent execution supervisor starts before market scans. PR remains draft and undeployed.
- PR #28 near-miss/outcome diagnostics remains open, reconciled with current main, mergeable, and CI green: latest head `9adb45d51f8017b307f1da4cc8f8ff2b173ba530`; tests run `44808524824` SUCCESS (**456 tests**), checks run `44808524770` SUCCESS. It remains unmerged and undeployed.
- Render service auto-deploys commits to main (`autoDeploy=yes`). Keep PR #28 and PR #29 unmerged unless an explicit merge/deployment decision is made; merging either into main would trigger production deployment. Continue to preserve paper-only execution and current switch configuration.
- Next verification: recheck V5.95 logs for execution-cycle and ORLY protection audit entries; after a separately authorized PR #29 deployment, verify execution cycles resume independently during long scans. Continue the 1/5/10/20-session volatility transition research chain in the stacked worker PRs #5–#9 and dashboard PRs #3–#7; do not merge stacked branches without ancestry reconciliation and CI.


## 2026-11-20 continuation update — volatility study session-calendar integrity

- Reviewed worker volatility-transition study PRs #5–#9 and dashboard chain #3–#7. The worker study explicitly evaluates post-transition ages 1/5/10/20 sessions against forward horizons 1/5/10/20, matched by setup, score bucket, trend regime, current volatility regime, transition type, and horizon. It also applies 20-session de-overlap, chronological 70/30 holdout with forward-window purge, weekly-block bootstrap intervals, and calendar-year robustness. All research outputs retain `authority=NONE` and `decision_authority=NONE`.
- Found and fixed an important session-index integrity issue in worker PR #9: the previous `market_session_index` was a zero-based ordinal from a rolling two-year SPY download. As the rolling window advanced, persisted indices from different scans could shift relative to one another, corrupting exact 20-session cooldown and holdout-purge calculations.
- Worker PR #9 now fetches SPY separately with `period=max` to create a stable inception-to-date session calendar while keeping the other universe symbols on bounded two-year batches. It marks the index stable only when the full-history fetch succeeds; on fallback to a rolling two-year SPY window, the index is omitted and downstream analysis uses date-based weekday fallback instead of mixing incompatible ordinals.
- Full-history sensitivity payload now reports SPY history start/end dates, provider period, and stable-index provenance. Worker PR #9 latest head `b80049c9bb0ef5e790db9feaf29b318fd0b1ddf4`; CI run `44809904896` SUCCESS, **479 tests passed**. PR #9 remains stacked/draft and not mergeable against its current base; do not merge in isolation.
- Dashboard PR #7 now surfaces SPY history coverage and whether the stable indexed session calendar was verified; if not, it labels the date-based fallback. Latest head `ff6910deb1be12b8cc7f0eee85a6371d1bd58c69`; dashboard CI run `44810026476` SUCCESS, **12 tests passed**. PR #7 remains stacked/draft on dashboard PR #6; do not merge in isolation.
- PR #28 near-miss/outcome diagnostics remains open, reconciled, mergeable, and green (456 tests); PR #29 independent paper-execution scheduler remains open/draft, mergeable, and green (448 tests). Neither is merged or deployed because Render auto-deploys main.
- Production runtime remains V5.95 on worker main. Render logs confirm continuous intelligence and the Alpaca paper snapshot poller are alive; account remains ACTIVE, equity approximately `$4,997.69`, ORLY is the only observed open symbol. No `PAPER EXECUTION CYCLE` or `BROKER POSITION PROTECTION AUDIT` was found in the inspected post-deploy window. PR #29 addresses the synchronous scan/replay starvation path but must remain undeployed until a separate explicit deployment decision.
- Safety: no live brokerage access, no broker/account reset, no archived Supabase virtual-account mutation, no paper switch changes, no changes to trading rules or protective orders. Continue to preserve research-only authority boundaries.



## 2026-11-20 continuation update — paper execution scheduler hardening and live ORLY audit

- Consolidated the execution scheduler work into worker PR #29: `https://github.com/jjfmetal123/trading-cloud-worker/pull/29`. The PR remains **draft, open, unmerged, and undeployed**. Latest head: `f490d448ba0821387041efd9b3207a418feca090`.
- PR #29 now moves paper decision cycles into a dedicated `ContinuousEngineSupervisor` thread so synchronous market scans and historical replay work cannot starve execution checks. The execution engine has its own Supabase client and consumes the latest thread-safe broker snapshot; inline execution was removed from the scan loop.
- Hardened the shared supervisor in the same PR: validates unique engine names and positive integer intervals before starting; makes start/stop lifecycle thread-safe; prevents silent restart after shutdown; records attempt/success timestamps, duration, consecutive failures, and thread liveness; reconnects the database client after failed runs; and reports shutdown timeouts with one shared deadline instead of falsely logging a clean stop.
- CI on consolidated PR #29 head is GREEN: Python tests run `44811180007` SUCCESS (**453 tests passed**); Python checks run `44811179981` SUCCESS (compile and deterministic strategy checks). The initial hardening run `44811027151` exposed two test failures; both were corrected, then the full suite passed. No trading thresholds, risk rules, or safety gates were weakened.
- A temporary stacked PR #30 was used for the hardening work and then consolidated into PR #29's feature branch; it is closed. This was a feature-branch consolidation only, **not a merge to main and not a production deployment**.
- Fresh Render log review at 2026-11-20 20:24 UTC confirms production is still V5.95 on main commit `919f5a8f73869943c3de5772e13f30cda85fca31`; latest Render deploy `dep-dc0adlm7bikc73fnlov0` is LIVE. Worker is actively running paper execution cycles about every 1–2 minutes. The paper execution switch is ENABLED, paper-only; do not change it without explicit direction.
- Four recent cycles (20:19, 20:20, 20:22, 20:24 UTC) each evaluated 35 candidates (15 long / 20 short), had zero missing quotes, zero ready candidates, and zero newly submitted orders. The leading blockers were high-volatility classification (11 candidates), entry extension / short entry extension, wide spreads/invalid quotes, and non-executable or invalid setups. This is a functioning decision cycle, not evidence of a stopped bot.
- Fresh post-deploy broker protection audits at 20:19, 20:20, 20:22, and 20:24 UTC show ORLY **PROTECTED**: quantity 2 matched both active exit legs; stop at 91.09 is in HELD state and target at 100.23 is ACCEPTED. Older warnings from a prior Render instance (16:59–17:24 UTC) showed EXIT_LEG_INACTIVE; the newer instance's audits are green. Do not alter the existing position or its orders as part of this verification.
- PR #28 near-miss/outcome diagnostics remains open and unmerged, latest head `9adb45d51f8017b307f1da4cc8f8ff2b173ba530`, with tests run `44808524824` SUCCESS (**456 tests**) and checks run `44808524770` SUCCESS. Its collector remains shadow-only and has compare-and-set protection against concurrent broker lifecycle updates.
- The volatility-transition research chain remains stacked: worker PRs #5–#9 and dashboard PRs #3–#7. Worker PR #9 latest head `b80049c9bb0ef5e790db9feaf29b318fd0b1ddf4` passed `44809904896` (**479 tests**); dashboard PR #7 latest head `ff6910deb1be12b8cc7f0eee85a6371d1bd58c69` passed `44810026476` (**12 tests**). Do not merge stacked PRs in isolation.
- Render auto-deploys worker main. Keep PR #28 and PR #29 unmerged until explicitly authorized; any merge to main triggers deployment. Paper-only endpoints, account state, current paper switch, risk rules, stops, and protective orders remain unchanged.
- Next work: inspect the PR #28 collector's minute-bar timestamp semantics and ensure horizon excursion windows cannot include post-horizon bars; then continue the 1/5/10/20-session volatility study and dashboard integration. Keep all research/diagnostics non-authoritative until separately validated.



## 2026-11-20 continuation update — one-minute outcome horizon integrity

- Continued PR #28 shadow near-miss/outcome diagnostics. Found a time-alignment issue in the outcome collector: Yahoo one-minute OHLC timestamps label the bar open, while the previous collector treated a bar opening exactly at the horizon as if its OHLC excursion occurred inside that horizon. This could leak post-horizon high/low values into MFE/MAE and stop/target-touch observations.
- Corrected `shadow_outcome_tracker.py`: one-minute bar interval is explicit; MFE/MAE and barrier-touch calculations now include only completed bars fully contained within the observation horizon. The point return uses the first completed bar close at/after the horizon, records `bar_close_at` and `observation_lag_seconds`, and respects the grace window based on close time. OHLC touches remain diagnostic observations, never fills.
- Added boundary regression coverage, including a deliberately extreme bar that opens at the 1-minute horizon; it must not contaminate the 1-minute excursion or barrier-touch result. Updated long/short fixtures to use minute-bar open timestamps correctly.
- PR #28 latest head: `dca506ec1a1c9c1d186ee39a12fbd174c6248b8f`; GitHub reports mergeable. CI GREEN: Python tests run `44811501691` SUCCESS (**457 tests passed**); Python checks run `44811501643` SUCCESS. Earlier intermediate runs failed on test placement/fixture assumptions; those were corrected and the final head passed without weakening validation.
- PR #28 remains open, unmerged, and undeployed. Its authority remains shadow-only; compare-and-set persistence continues to protect concurrent broker lifecycle updates.
- PR #29 independent paper-execution scheduler + supervisor hardening remains draft/open/unmerged/undeployed at head `f490d448ba0821387041efd9b3207a418feca090`; tests run `44811180007` SUCCESS (**453 tests**) and checks run `44811179981` SUCCESS.
- Production runtime remains V5.95 on main commit `919f5a8f73869943c3de5772e13f30cda85fca31`; at 20:24 UTC, paper execution cycles were running every 1–2 minutes with switch ENABLED in paper-only mode, evaluating 35 candidates and submitting zero new orders because none passed the current gates. Fresh ORLY protection audits showed the 2-share position PROTECTED with stop HELD at 91.09 and target ACCEPTED at 100.23.
- Keep PR #28 and PR #29 unmerged until separately authorized; Render auto-deploys main. Do not change the paper switch, account, position, exit orders, or risk policy as part of this work.



## 2026-11-20 continuation — shadow outcome completeness and volatility calendar provenance

- PR #28 shadow outcome collector latest head: `a032382ba18e4e38fa674f6a1677ce829733bbd1`, open/unmerged/undeployed. Python tests run `44812465513` SUCCESS (**459 tests passed**); Python checks run `44812468966` SUCCESS.
- Extended outcome integrity beyond horizon boundary alignment: path-dependent MFE/MAE and stop/target OHLC touches are now withheld unless the expected one-minute bar sequence is complete and every bar has a valid OHLC range (finite high/low, high >= low, low <= close <= high). Point close returns remain separately observable when the horizon bar is available. New fields report expected/missing excursion bars, invalid OHLC bars, and coverage completeness. This avoids turning missing or malformed candles into false claims about favorable/adverse path or barrier touches.
- PR #28's 459-test suite includes regression coverage for post-horizon candle leakage, missing minute bars, and malformed OHLC ranges. Shadow-only authority and compare-and-set broker lifecycle protection remain unchanged.
- PR #9 volatility full-history research latest head: `8ff9cc682f46d8a2291d69348ce9c7dbb5ad374d`, draft/stacked/unmerged. Python tests run `44812314706` SUCCESS (**481 tests passed**).
- Found and corrected a subtle session-calendar provenance issue: old persisted records may have rolling two-year market-session ordinals while new rows use inception-to-date SPY ordinals. Both are integers but are not necessarily comparable. Timeline rows now carry `market_session_calendar_id` (`SPY_FULL_HISTORY_V1:<calendar-origin>`) only when the stable full-history SPY calendar is verified. Worker refreshes existing signal metadata with the current index and provenance.
- Volatility response cooldown and holdout purge now use ordinal differences only when both records share the same non-empty calendar ID. Mixed/legacy provenance falls back to date-based business-day gaps. Added regression tests proving incompatible ordinals cannot bypass de-overlap.
- PR #9 remains stacked on the preceding volatility research chain. Do not merge it independently. Dashboard PR #7 remains stacked on its dashboard chain; no production changes made.
- PR #29 independent paper-execution scheduler remains draft/open/unmerged/undeployed at head `f490d448ba0821387041efd9b3207a418feca090`; Python tests run `44811180007` SUCCESS (**453 tests**) and checks run `44811179981` SUCCESS.
- Production remains deployed from worker main commit `919f5a8f73869943c3de5772e13f30cda85fca31` (V5.95); no PR changes have been merged or deployed. Keep the paper-only switch, broker account, existing positions/orders, risk gates, and protective-order handling unchanged.
- Next: continue end-to-end validation of the volatility timeline's session-age labels and event-study purge/holdout behavior against real persisted rows, and verify that the dashboard clearly distinguishes stable full-history provenance from waiting/fallback states. Keep research non-authoritative.



## 2026-11-20 latest live verification — 20:32 UTC

- Render still reports the production worker on the previously deployed V5.95 main commit `919f5a8f73869943c3de5772e13f30cda85fca31`; all research/engineering PRs remain unmerged and no new deployment was triggered.
- Fresh production execution starts and summaries continued at 20:26, 20:28, 20:30, and 20:32 UTC. Each used `submission_switch=ENABLED`, `paper_only=true`, and a present broker snapshot. The 20:32 summary evaluated 35 candidates (15 long / 20 short), zero missing quotes, zero ready candidates, zero newly submitted orders; blockers included wide spreads, high-volatility classification, entry extension, and setup validity. This confirms the current production execution loop remains alive; it does not mean the independent scheduler PR #29 is deployed.
- Fresh 20:32:48 UTC broker protection audit reports ORLY position **PROTECTED**: 2 shares, active stop at 91.09 in HELD state and target at 100.23 ACCEPTED, quantities matched.
- Latest PR #28 collector head `a032382ba18e4e38fa674f6a1677ce829733bbd1` passes 459 tests and Python checks; latest PR #9 volatility calendar provenance head `8ff9cc682f46d8a2291d69348ce9c7dbb5ad374d` passes 481 tests. PR #29 scheduler head `f490d448ba0821387041efd9b3207a418feca090` remains green at 453 tests plus Python checks.


## 2026-11-20 continuation — production scheduler starvation re-confirmed and PR safety audit

- Rechecked Render directly. Worker service `srv-dbua8frm8hqs73f895h0` is active, unsuspended, configured to auto-deploy commits to `main`, and still points to the V5.95 main deployment `919f5a8f73869943c3de5772e13f30cda85fca31` (`dep-dc0adlm7bikc73fnlov0`, LIVE). No PR branch is deployed.
- Fresh logs show paper execution cycles at 20:30:47 and 20:32:48 UTC, each in paper-only mode with submission switch ENABLED; both evaluated 35 candidates and submitted zero orders. ORLY's two-share position remained PROTECTED in both audits: stop 91.09 HELD and target 100.23 ACCEPTED with matching quantities.
- Crucial scheduler finding: the later log window contains active intelligence/learning/quote engines at 20:43–20:49 UTC, but no later `PAPER EXECUTION CYCLE` or protection audit after 20:32 UTC. The worker process is alive, but the current main-thread execution cycle is not keeping pace while synchronous scan/replay and other work run. This independently reinforces the root cause addressed by worker PR #29; it does not mean the bot or Render process is dead.
- PR #29 remains draft/open/unmerged/undeployed at `f490d448ba0821387041efd9b3207a418feca090`. Its dedicated paper-execution supervisor starts independently of the blocking scan loop and owns a separate Supabase client. The scheduler must remain unmerged until review and explicit deployment approval because Render auto-deploys main.
- PR #28 remains open/unmerged/undeployed at `a032382ba18e4e38fa674f6a1677ce829733bbd1`; latest recorded CI is 459 tests + Python checks. Code review confirms the minute-bar path metrics are withheld when coverage or OHLC validation is incomplete, and CAS persistence protects concurrent broker lifecycle updates. Additional review item: stress-test collector fairness/backlog behavior when more than 500 recent decision rows are pending; the current query selects only the newest 500 rows, so repeated updates could starve older pending rows under sustained high volume. Do not treat this as fixed until tested and addressed.
- PR #9 remains stacked/draft/unmerged at `8ff9cc682f46d8a2291d69348ce9c7dbb5ad374d`; latest recorded CI is 481 tests. PR #7 remains stacked/draft on the dashboard side. Neither should be merged independently.
- No changes were made to production, Render configuration, paper switch, brokerage account, existing ORLY position/orders, strategy gates, sizing, stops, or live credentials. Paper-only boundary remains intact.
- Next major engineering batch: (1) validate PR #29 under simulated slow scans, DB failures, stale snapshots, and shutdown races; (2) fix/test PR #28 collector fairness and retry semantics; (3) finish PR #9 persisted-row calendar-provenance and holdout-purge end-to-end tests; (4) re-run complete CI on final heads; (5) update this handoff. Do not merge/deploy without explicit approval.


## 2026-11-20 continuation — PR #28 collector backlog fairness

- Code review identified a starvation mode in the shadow-outcome collector: selecting the newest 500 decision rows on each five-minute pass, while refreshing `updated_at` for pending rows, could repeatedly select the same newest batch and leave older pending rows unprocessed.
- Worker PR #28 was updated at commit `da04e08afba5bf3731a2e25347058c50237d86e6`: the collector now excludes rows whose `near_miss_future_outcomes_status` is already `MATURED` and selects the oldest pending rows first. Successful CAS updates advance their timestamps, moving those rows behind untouched backlog rows on the next pass.
- PR #28 description records the fairness change and explicitly distinguishes previous green CI (459 tests at `a032382ba18e4e38fa674f6a1677ce829733bbd1`) from the new head. No CI run for the new head was visible at the time of this update; rerun/verify the full suite before treating this change as validated.
- PR #28 remains open/unmerged/undeployed. No production deployment, paper switch, strategy policy, order handling, or broker account changes.


## 2026-11-20 latest verification — PR #28 fairness hardening CI green

- Worker PR #28 current head `da04e08afba5bf3731a2e25347058c50237d86e6` passed fresh CI after the collector fairness change: Python tests run `44814918456` SUCCESS (**459 tests passed**); Python checks run `44814918444` SUCCESS (compile + deterministic strategy checks).
- GitHub currently reports PR #28 open, unmerged, and mergeable. Its description now records the current-head CI results. It remains undeployed; Render auto-deploys only main.
- Collector fairness query change is covered by a green full suite, although the tests do not yet include a high-volume multi-batch starvation simulation. Add that targeted stress/regression test in a later hardening pass before relying on fairness under sustained backlog.
- No production or broker state was modified.


## 2026-11-20 massive reliability batch — legacy collector inclusion + supervisor lifecycle stress tests

### PR #28 collector query correction
- A second-order review found that a plain PostgREST `neq(MATURED)` predicate can exclude SQL NULL values. That would risk excluding legacy JSON rows that have no maturity-status key yet — precisely the rows that must be collected.
- Replaced the filter with an explicit OR predicate: JSON maturity status IS NULL OR status != MATURED. Old/legacy rows are now included while matured rows are excluded; oldest-first ordering remains.
- Added a worker integration-level query-builder test asserting the OR-null predicate, oldest-first ordering, and 500-row batch limit.
- Latest PR #28 head: `0f849bef27a0fc476e7ae148f3ffbfff41948a73`. CI: Python tests run `44815394877` SUCCESS (**460 tests passed**); Python checks run `44815395112` SUCCESS.
- PR #28 remains open/unmerged/undeployed.

### PR #29 supervisor reliability coverage
- Added deterministic lifecycle tests for idempotent start, refusal to restart after terminal shutdown, shared shutdown deadline / stuck-thread reporting, and DB-client recreation after engine failure.
- Latest PR #29 head: `b00bd15dfc9777f883fb33699f47aa6e08f337ed`. CI: Python tests run `44815440341` SUCCESS (**456 tests passed**); Python checks run `44815440413` SUCCESS.
- PR #29 remains draft/open/unmerged/undeployed.

### Research/production boundaries
- PR #9 remains stacked and draft. Its calendar-ID checks and date fallback are preserved; no merge attempted.
- Production worker remains V5.95 on main. Render auto-deploys main only. No deployment, no broker writes, no position/order modifications, no risk/policy changes.
- Next review: test that the JSON-path OR predicate is accepted by the actual Supabase/PostgREST endpoint in a safe read-only diagnostic (not a write); stress-test collector backlog with more than 500 mixed legacy/pending/matured rows; add mixed-calendar holdout-purge regression; then re-run complete CI.


## 2026-11-20 massive batch — collector eligibility and execution isolation

### PR #28 — Shadow outcome collector queue eligibility
- Re-reviewed the collector after the NULL-safe maturity predicate and found another starvation source: ordinary paper decision rows without a near-miss price reference could consume all 500 query slots before Python-side filtering.
- Added a PostgREST `NOT IS NULL` predicate on `decision->>near_miss_price_reference`, limiting the batch to actual shadow-outcome observations before maturity filtering and oldest-first ordering.
- Regression test now asserts: near-miss reference non-null filter, NULL-safe future-status OR condition, oldest-first `updated_at`, and 500-row cap.
- Latest head `84a18fca482d1f3aa6a90f402048efce1b1c29c6`: Python tests `44816502673` SUCCESS (**460 tests passed**); Python checks `44816502616` SUCCESS.
- PR #28 remains open, unmerged, and undeployed.

### PR #29 — Direct scan/execution isolation stress test
- Added an integration-level test that deliberately blocks a simulated market scan on a separate thread while the independent paper-execution supervisor runs its cycle.
- Initial CI caught two test harness issues (missing `threading` import and unmocked Supabase client factory); both were corrected. Final CI is green.
- Latest head `7c0fa479dd52c3760cf1f384e63fcb22393ad562`: Python tests `44816771601` SUCCESS (**457 tests passed**); Python checks `44816773612` SUCCESS.
- PR #29 remains draft, open, unmerged, and undeployed. The test validates the supervisor isolation model; it does not prove production has received the fix.

### PR #9 — Volatility transition research
- Added a mixed-market-calendar holdout-purge regression test. When cutoff rows contain incompatible calendar IDs, the study must fall back to conservative date-based business-session purging rather than comparing incompatible session ordinals.
- New head: `2163f59c3aafb37f41ec681471c195232a9a453f`. No new CI workflow run is currently reported for this head; earlier recorded successful CI on the prior head does not validate this added test. Treat as pending verification.
- PR #9 remains stacked/draft/unmerged.

### Production and data verification
- Supabase read-only sample of `paper_trade_decisions` updated in the last 30 minutes: 69 rows; 69 had no `near_miss_future_outcomes_status`; 0 had near-miss price references. This supports keeping the collector's legacy/null handling and query eligibility precise; it does not demonstrate collection is active because PR #28 is not deployed.
- Render service remains active, auto-deploys `main`, and latest live deployment is V5.95 commit `919f5a8f73869943c3de5772e13f30cda85fca31`.
- No production deployment, broker mutation, position/order changes, risk/entry/exit policy changes, or account setting changes.
- Next: verify the exact PostgREST JSON-path filter on the live Data API via a read-only request if a safe query route is available; build a deterministic >500-row multi-pass backlog simulation; validate PR #9's new test in CI; then run full CI on final heads. Explicit approval remains required before merge/deploy.


### Production heartbeat spot-check — 2026-11-20 20:52–20:57 UTC
- Render logs show paper execution summaries continuing at 20:52:01, 20:53:06, 20:55:07, and 20:57:08 UTC.
- Submission switch remained ENABLED and `newly_submitted=0` on those cycles; 34 candidates were evaluated per cycle, with quote-missing count 0. Most common blockers remained high-volatility class, spread/quote quality, extension from entry trigger, and setup eligibility.
- This confirms the production paper-decision loop was still producing cycles in that interval; it does not imply trades were filled or that PR #29 has been deployed.


## 2026-11-20 massive improvement — shadow collector outage/backlog recovery

### Worker PR #31 — prevent pending observations from aging out
- A deeper queue audit found a starvation/data-loss edge in PR #28: the collector selected rows with `updated_at >= now - 30 minutes`. Since each successful compare-and-set collection pass advances `updated_at`, this age filter could hide older pending observations after an outage or long backlog, preventing them from ever being finalized.
- Removed the 30-minute `updated_at` cutoff. The queue remains restricted to actual near-miss rows, excludes matured rows with NULL-safe status logic, orders oldest-first, and keeps the 500-row cap.
- Stale pending records can now drain as explicit `DATA_UNAVAILABLE` outcomes when one-minute provider history is no longer retained, rather than silently aging out of the queue.
- Added a regression assertion that the collector does not apply an `updated_at` age cutoff.
- PR #31: https://github.com/jjfmetal123/trading-cloud-worker/pull/31
- Head: `6e665e877ba976f4fe1ea563fab54d1dfffb4d86`. CI workflow runs were not yet visible when checked; validation is pending. This is stacked on PR #28 and is not merged or deployed.
- PR #28 remains open/unmerged; PR #29 remains draft/unmerged; PR #9 remains draft/unmerged and its mixed-calendar test still needs a fresh CI run.

### Safety and production status
- This change is shadow-collector queue eligibility only. It does not change ranking, candidate gates, entry/exit logic, sizing, stops/targets, broker API calls, protective orders, account settings, or the paper switch.
- No merges, deployments, broker mutations, or production writes were performed.
- Production remains on main / V5.95 until explicit approval to merge and deploy. Keep Alpaca paper-only.
- Next hardening target: build a deterministic multi-pass simulation with >500 mixed rows, including ordinary decisions, legacy NULL statuses, pending observations, matured observations, old backlog, CAS conflicts, and transient query/bar/write failures; prove eventual queue drainage and per-row failure isolation. Also verify the exact PostgREST JSON-path filters safely and validate PR #9's latest head in CI.


## 2026-11-20 massive short-side observability batch — Worker PR #32

### Production finding
- Read-only Render log review showed the bearish short watchlist was populated: the 19:58 UTC log listed 20 candidates, and the 20:19 UTC paper execution cycle evaluated 20 shorts plus 15 longs.
- That cycle had 0 quote misses, 0 ready candidates, and 0 newly submitted orders. Combined blockers included 11 HIGH_VOLATILITY_CLASS, 5 SHORT_ENTRY_TOO_EXTENDED across the cycle, 2 INVALID_SHORT_SETUP_LEVELS, plus long-side and shared quote/spread blockers. Later cycles through 20:59 UTC continued to show 0 ready / 0 submitted.
- Important interpretation: the short scanner is not absent. It is producing candidates; the entry gates are rejecting/waiting on them. The combined summary does not make short-only blockers obvious enough.

### PR #32 — side-specific paper execution diagnostics
- Added a deterministic summary helper grouping execution outcomes by long, short, and unknown side, each with evaluated count, status counts, and reason counts.
- Paper execution cycle log now emits `side_breakdown` while retaining the existing combined status/reason summary for backward compatibility.
- Added two tests for side separation, deterministic counts, unknown-side handling, and malformed rows.
- PR: https://github.com/jjfmetal123/trading-cloud-worker/pull/32
- Branch: `feat/short-side-diagnostics-20261120`
- Head: `2c17975a805a4758d50f2ff774556d8b1e1c6767`; 3 files changed, 53 additions / 2 deletions. Draft/open/unmerged/undeployed. CI was not yet visible when checked; do not treat as validated until green.
- This is observability only. No short-entry thresholds, volatility treatment, setup logic, sizing, stops/targets, order submission, paper switch, or account settings changed.

### Next short-side research
- Use the new per-side reason report to isolate short rejection rates.
- Investigate the 0.30% short entry extension constraint and the SMA20-based pullback trigger under fast downside moves; separately evaluate breakdown and breakdown-retest hypotheses in historical/shadow research before any execution-policy changes.
- Audit why some short candidates have invalid geometry when current bid has moved through the precomputed target. Do not relax geometry checks or volatility blocks just to increase trade count.

### Production safety
- Render production remains main / V5.95; PR #32 is not deployed. No merges, broker writes, paper orders, account mutations, or policy changes were made.

- Follow-up CI verification: PR #32 head `2c17975a805a4758d50f2ff774556d8b1e1c6767` passed Python tests run `44819614648` and Python checks run `44819614626`; both completed SUCCESS. PR remains draft/open/unmerged/undeployed.


## 2026-11-20 massive short-strategy research batch — Worker PR #33

### PR #33 — shadow-only breakdown and breakdown-retest classifiers
- Added a standalone pure-Python classifier consuming chronological completed daily OHLCV bars. It labels the latest bar as `SHORT_BREAKDOWN_SHADOW`, `SHORT_BREAKDOWN_RETEST_SHADOW`, `NO_SHADOW_SETUP`, or `NOT_CLASSIFIED`.
- Breakdown requires a close below the preceding rolling support, ATR-normalized penetration, relative-volume confirmation, and a close in the lower 40% of the daily range.
- Retest requires a prior confirmed breakdown within a bounded window, a return to the broken support zone, a close back below that level, and a bearish rejection candle.
- Support/ATR/volume references are calculated only from bars preceding the bar under evaluation. Invalid/incomplete OHLCV fails closed. All outputs explicitly set `executable: false`.
- Six deterministic tests cover breakdown confirmation, volume rejection, retest rejection, support reclaim rejection, invalid/insufficient bars, and temporal behavior.
- PR: https://github.com/jjfmetal123/trading-cloud-worker/pull/33
- Branch: `research/short-breakdown-setups-20261120`; head `b9e307ea2f8c04214d6e14cac49e184b9ba87837`.
- PR #33 is draft/open/unmerged/undeployed and stacked on PR #32's diagnostics branch (`feat/short-side-diagnostics-20261120`) so its diff contains only the two new research files. CI not yet visible at last check; validation pending.

### Research boundary and next steps
- This classifier is not wired into the production worker, scanner, short candidate builder, short evaluator, or order path. It does not produce paper trades and no historical performance claims have been made.
- Current short-engine candidate payloads contain daily indicators but not the complete daily OHLCV history required for rigorous breakdown/retest replay. Next step is a separate historical-data adapter/replay that builds features chronologically, prevents look-ahead, and compares the baseline pullback against the two shadow setups across selloff, normal, and rising/choppy regimes.
- Do not loosen the high-volatility block, 0.30% chase limit, reward/risk, geometry, sizing, or other execution gates to increase trade count.

### Safety
- No changes to production main, no merges/deployments, no broker writes/orders, no account mutations, and no risk/entry/exit policy changes. Production remains V5.95 / main. PR #32 remains draft/open/unmerged/undeployed; its CI passed (Python tests `44819614648`, Python checks `44819614626`).

- Follow-up CI verification: PR #33 head `b9e307ea2f8c04214d6e14cac49e184b9ba87837` passed Python tests run `44820031670` and Python checks run `44820031921`; both completed SUCCESS. PR remains draft/open/unmerged/undeployed.


## 2026-11-20 massive short-strategy replay batch — Worker PR #34

### PR #34 — chronological historical replay for shadow short setups
- Added `short_strategy_replay.py`, a pure research harness that consumes injected per-symbol daily OHLCV histories and optionally aligned benchmark bars. It uses the PR #33 breakdown/retest classifier on each completed historical prefix; it never classifies a bar using future bars.
- Entry convention is explicitly the NEXT session open after the signal close. It measures short-side close returns, favorable/adverse price excursions (MFE/MAE), and 1/5/10/20-session horizons when the full horizon exists.
- Added round-trip cost sensitivity at 0, 10, and 25 bps. Optional benchmark regime labels use only trailing 20-session benchmark returns: sell-off <= -5%, rising >= +5%, otherwise range/chop.
- Overlapping events are retained and flagged by symbol rather than silently treated as independent. Small samples are labeled `LOW_SAMPLE_DO_NOT_INFER`. Every event is `executable: false`.
- Four deterministic tests cover fail-closed malformed input, next-session-open timing and short-return math, future-bar invariance of prior signal/entry, and monotonic cost sensitivity.
- PR: https://github.com/jjfmetal123/trading-cloud-worker/pull/34
- Branch: `research/short-historical-replay-20261120`; head `e0bae855c19c1f3ef30070df3f94038c478c9072`. Draft/open/unmerged/undeployed; stacked on PR #33 so the incremental diff contains only the replay module and tests.
- CI at handoff update: Python tests run `44822106190` was IN_PROGRESS. No successful result is claimed yet; check this exact head again before calling it validated.

### Interpretation limits / next research step
- This is a historical event-study harness, not a portfolio backtest and not proof of profitability. It does not model broker fills, stop/target execution, same-day barrier ordering, borrow availability/fees, dividends, corporate actions, or full market impact. MFE/MAE are excursions, not fills.
- No real historical replay result is claimed yet; no provider dataset was downloaded or run through the harness in this batch. The next step is a reproducible data adapter and actual symbol/benchmark history replay, with date coverage and data-quality reporting, followed by independent/non-overlapping sample analysis and a holdout period.
- No production imports, worker behavior, scanner, order path, risk gates, entry/exit rules, sizing, stops/targets, paper switch, account state, or broker calls were changed.

### Production safety
- Production remains V5.95 / main, paper-only. PR #34 is draft/open/unmerged/undeployed. No deployment, broker mutation, account mutation, order submission, or risk-policy change occurred. Explicit approval remains required before any merge or deployment.

- Follow-up CI verification: PR #34 Python tests run `44822106190` (run #937) completed SUCCESS, including module compilation and unit tests. No PR-triggered Python checks workflow appeared in the run list at the final check, so checks are not claimed green. PR remains draft/open/unmerged/undeployed.


## 2026-11-20 massive historical-data infrastructure batch — Worker PR #35

### PR #35 — reproducible adjusted daily OHLCV acquisition
- Added `short_history_data.py`, a standalone, injectable Yahoo Finance daily-history adapter using the repository's existing `yfinance` dependency. It is not imported by the production worker or any execution path.
- Requests adjusted daily OHLCV in bounded batches; normalizes single/multi-ticker responses; sorts and deduplicates dates; uses the shared completed-session cutoff to exclude today's incomplete candle; validates positive, internally consistent OHLC and positive volume; and reports per-symbol status, first/last date, valid session count, rejected rows, provider failures, and retrieval metadata.
- Provider exceptions are isolated by batch. Ambiguous multi-symbol flat-column responses fail closed instead of assigning one symbol's bars to another.
- Corrected PR #34 benchmark regime and benchmark-return matching to use trading-date joins, not matching array indexes. Added regression coverage for symbol/benchmark histories with different session indexes.
- Added five adapter tests plus the benchmark date-alignment test (six tests in this PR's incremental work).
- PR: https://github.com/jjfmetal123/trading-cloud-worker/pull/35
- Branch: `research/short-history-data-adapter-20261120`; head `9b625ac24c9687ea60130bfb7204f0a4c34f1519`. Draft/open/unmerged/undeployed; stacked on PR #34. CI workflow was not yet visible at the first check; validation pending.
- PR #34 Python tests remain green on head `e0bae855c19c1f3ef30070df3f94038c478c9072` (run `44822106190`, SUCCESS). Its separate checks workflow was not confirmed.

### Data quality and research limitations
- This adds the reproducible acquisition path but no real market history was downloaded or replayed in this batch. Do not report strategy returns until an explicit research run records the symbol universe, provider, adjustment mode, date coverage, rejected rows, and replay output.
- Yahoo adjusted history is provider-specific; `auto_adjust=true` is recorded in metadata. The adapter does not independently reconstruct dividends/splits, certify survivorship-bias-free universe history, model borrow/fees, or make the study an executable backtest.
- The replay remains descriptive, shadow-only, and `executable: false`.

### Safety
- No production worker imports, scanner changes, broker calls, paper/live orders, Supabase writes, account mutations, risk/entry/exit changes, or deployments. Production remains V5.95 / main / Alpaca paper-only. No merge or deployment was attempted.


- PR #35 CI follow-up: initial Python tests run `44833821898` failed because the CI test environment does not install yfinance and the new research module imported it eagerly. Fixed by making the provider import lazy; deterministic tests continue to inject a mock provider. Corrected head `9d98de3a2e355ea097ba3e7b44d19199c9aa0bb0`; a fresh workflow run was not yet visible at the final check. Treat PR #35 validation as pending, not green.


- PR #35 validation follow-up: after the lazy-import correction, Python tests run `44833904597` (head `9d98de3a2e355ea097ba3e7b44d19199c9aa0bb0`) compiled successfully but failed two new test fixtures because a pandas DatetimeIndex was used in boolean context. Corrected the fixture to test `dates is None` explicitly. Latest head: `3a191a0a856a2b75edd0e26db8f88e7294fa3ad0`; fresh CI run was not yet visible. PR #35 remains unvalidated until that run completes.

- Final PR #35 validation: corrected head `3a191a0a856a2b75edd0e26db8f88e7294fa3ad0` passed Python tests run `44833996119` (run #940). Module compilation and complete unit-test step succeeded. The earlier two failures and their corrections are retained above for auditability. PR remains draft/open/unmerged/undeployed.


## 2026-11-20 massive short-study orchestration batch — Worker PR #36

### PR #36 — reproducible historical study runner and report
- Added `run_short_strategy_study.py`, a CLI orchestration layer over PR #35's injectable adjusted-daily data adapter and PR #34's shadow replay.
- Accepts an explicit fixed symbol universe, benchmark, period and minimum sample threshold; fetches universe plus benchmark; records retrieval metadata, exact requested/usable/unavailable symbols, per-symbol date coverage, rejected rows, benchmark availability, and a UTC run timestamp.
- Emits machine-readable JSON and a Markdown report with data coverage and per-setup / regime / horizon metrics (sample count, average/median gross return, win rate, MFE/MAE, cost sensitivity and interpretation flags).
- Important methodological correction: the production BEARISH PULLBACK baseline is explicitly marked NOT_RUN. The production candidate builder uses scanner fields and its execution gate depends on intraday quote freshness/spread, trigger/chase, volatility, sizing and account-risk state. A daily-OHLCV approximation would not faithfully reproduce it, so no fake baseline comparison was added.
- Added deterministic mocked-provider tests for study orchestration, invalid-universe fail-closed behavior, and report coverage/limitations.
- PR: https://github.com/jjfmetal123/trading-cloud-worker/pull/36
- Branch: `research/short-study-runner-20261120`; head `5c42439f5680a1e05e583b9460a6f92354ddf082`. Draft/open/unmerged/undeployed; stacked on PR #35.
- CI workflow runs were not returned for this PR head at the final check. Validation is pending; do not claim tests passed until a PR-triggered run or equivalent full test evidence is available.
- No actual Yahoo Finance download or empirical replay was run in this batch. The runner is built, but there are no strategy-performance conclusions yet.

### Safety and limitations
- Research-only, shadow-only, all replay events non-executable. No production imports, worker loop changes, broker calls, paper/live orders, Supabase writes, account changes, risk/entry/exit policy changes, or deployment.
- Default universe is a small convenience set, not survivorship-bias-free and not evidence of broad-market performance. A later study should use a documented point-in-time universe or clearly retain this limitation.
- Existing fixed-universe and Yahoo-provider limitations remain visible in the generated report. No portfolio-level fills, intraday stop/target sequencing, borrow/locate costs, market impact or independent observations are assumed.
- Production remains main / V5.95 and paper-only. PRs #32–#36 remain separate open research/diagnostic branches; no merge or deployment was attempted.

### Next research milestone
- Validate PR #36 on CI, then run the runner against an explicitly selected historical universe and benchmark where the environment permits provider access. Save and inspect the exact coverage manifest and raw replay output before interpreting results.
- Build a faithful baseline only if the production daily scanner feature calculations and candidate thresholds can be reconstructed exactly from chronological OHLCV; keep quote/execution gates as a separately labeled execution feasibility layer.

- PR #36 CI follow-up: head `5c42439f5680a1e05e583b9460a6f92354ddf082` passed Python tests run `44835034920` (run #941). Module compilation and the full unit-test step succeeded; no separate Python checks workflow is claimed. PR remains draft/open/unmerged/undeployed.


## 2026-11-20 massive research-validation batch — Worker PR #37

### PR #37 — chronological holdout purge and independent-event diagnostics
- Added realized `exit_date_{horizon}s` to each shadow replay event, enabling validation to reason about the actual end date of each forward-return window rather than guessing from calendar days.
- Added `short_study_validation.py`:
  - Chronological event-level split based on unique signal dates.
  - Per-horizon purge removes training events whose measured forward window reaches or crosses the first holdout signal date.
  - Per-horizon, per-symbol non-overlap diagnostic retains the earliest entry and only accepts another after the prior event's measured horizon end.
  - Reports train/test sample sizes, purged counts, holdout gross return/win-rate summaries, and independent sample counts; insufficient history fails closed.
- Integrated the validation output into the study JSON and Markdown report. Added tests for horizon-boundary purging, non-overlap selection, insufficient dates, invalid parameters, and runner integration.
- PR: https://github.com/jjfmetal123/trading-cloud-worker/pull/37
- Branch: `research/short-study-validation-20261120`; head `17bd2fafc3cd08bbcb67786b9309a73971f070f9`. Draft/open/unmerged/undeployed, stacked on PR #36.
- CI workflow run was not yet visible at the final check. Validation is pending; do not claim tests passed until a fresh PR-triggered test run completes.
- No live Yahoo data download or empirical strategy replay was performed. This is validation infrastructure, not a performance result.

### Methodology and safety boundaries
- Holdout is event-level, chronological, and horizon-purged; it is not a portfolio simulation and does not model capital allocation, concurrent exposure, borrow, slippage, intraday barriers, stop/target fills, or market impact.
- The non-overlap sample is a diagnostic selection (earliest event per symbol, then wait until the previous event's horizon end), not a deployable trade schedule.
- No tuning on holdout, no baseline proxy, no claims of edge/profitability.
- All research events remain non-executable. No production imports, worker loop changes, broker calls, paper/live orders, Supabase writes, account mutations, entry/exit/risk-policy changes, or deployment.
- Production remains V5.95 / main, paper-only. PR #37 is draft/open/unmerged/undeployed.

### Next exact step
- Verify PR #37 CI on the exact head above. Fix any failures and re-run.
- Then validate all stacked research PRs (#35–#37) from the top branch, run the runner with a real provider only if external access is available, archive exact JSON/Markdown outputs and coverage, and review the results before making any strategy conclusions.
- Keep the production bearish-pullback comparator marked NOT_RUN until its daily scanner calculations can be faithfully reconstructed; do not invent a baseline.


- PR #37 CI failure/correction audit: first run `44838284967` compiled all modules but failed one new test because its fixture had only four unique signal dates; the validator correctly returned `INSUFFICIENT_DATES`, while the test incorrectly expected a completed result. Expanded the fixture to five unique dates (corrective head `367f2410978e1b4c877afaa0f130dc0ee22631bd`). Fresh CI for the corrective head was not yet visible at handoff update; status remains pending, not green.

- Second PR #37 CI audit: run `44838359811` reached unit tests and failed only the non-overlap fixture's expected count (actual 4, expected 3); the implementation retained valid independent events across separate symbols. Corrected the assertion to 4 in head `bac9f20ab64a592baa2fa029c642281e2a419786`. Fresh CI not yet visible; keep PR #37 validation pending.

- Final PR #37 validation: corrective head `bac9f20ab64a592baa2fa029c642281e2a419786` passed Python tests run `44838455237` (run #944). Module compilation and the full unit-test step passed. The two earlier failures and exact fixture corrections remain documented above. No separate Python checks workflow is claimed. PR #37 remains draft/open/unmerged/undeployed.


## 2026-11-20 massive research execution-enablement batch — Worker PR #38

### PR #38 — manually triggered real-history study workflow
- Added `.github/workflows/manual-short-strategy-study.yml` on branch `research/short-study-manual-run-20261120`.
- Workflow is `workflow_dispatch` only. It has explicit inputs for comma-separated symbol universe, benchmark, provider period, and minimum event count. No schedule, push trigger, or automatic recurring data fetch was added.
- Installs only research dependencies (pandas, NumPy, yfinance), runs the existing `run_short_strategy_study.py`, and archives the generated JSON and Markdown report for 30 days.
- Requires no Alpaca credentials, does not commit downloaded data, and does not call broker or Supabase services. The workflow is intended to run on the selected research branch after it is available for manual dispatch.
- Default universe remains the existing small convenience set (AAPL, MSFT, NVDA, AMZN, META, GOOGL, TSLA, AMD) against SPY. It is not survivorship-bias-free; results must not be generalized to the whole market.
- Production bearish-pullback baseline remains NOT_RUN; shadow signals remain non-executable.
- PR: https://github.com/jjfmetal123/trading-cloud-worker/pull/38
- Branch: `research/short-study-manual-run-20261120`; head `6f556e47988e4c1e0bdda209387f843e4848a6f4`; base is PR #37 branch `research/short-study-validation-20261120` at `bac9f20ab64a592baa2fa029c642281e2a419786`.
- PR #38 is draft/open/unmerged/undeployed. Its workflow file was read back and verified. No PR-triggered CI run was returned at the time of handoff update; do not claim workflow execution or empirical results.
- PR #37 parent validation remains Python tests run `44838455237` SUCCESS on head `bac9f20ab64a592baa2fa029c642281e2a419786`.

### Exact next action
- Review PR #38 workflow checks and, when the branch/workflow is manually dispatchable, run a real 5-year history study with a documented fixed universe and archive the JSON/Markdown artifacts. Inspect symbol coverage, rejected rows, event counts, holdout purge, overlap diagnostics, cost sensitivity, and low-sample warnings before interpreting any returns.
- Do not merge PR #38 or any stacked research PR without explicit user approval. Do not merge any worker changes to main because Render auto-deploys worker main.
- Production remains V5.95 / main / Alpaca paper-only. No paper trading, live trading, account, Supabase, risk-policy, or production deployment changes were made in this batch.


## 2026-11-20 MOON resume verification — live state and PR #38 CI

### Verified repository heads
- Dashboard default branch `main`: `7b9fdfa11bd5484d5eef12acdeec948ddc7195e0` (handoff documentation update for PR #38).
- Worker default branch `main`: `919f5a8f73869943c3de5772e13f30cda85fca31` (README/worker documentation alignment, V5.95).
- Both repositories were found and readable. Dashboard repository is public; worker repository is private.
- No branch was merged and no production deployment was triggered by this verification.

### Worker research stack
- PR #38: `research/short-study-manual-run-20261120`, head `6f556e47988e4c1e0bdda209387f843e4848a6f4`, base PR #37 at `bac9f20ab64a592baa2fa029c642281e2a419786`. Draft/open/unmerged/undeployed.
- PR #38 Python tests run `44842813238` completed SUCCESS. The workflow itself has not been dispatched and no real historical-data results are claimed.
- PR #37 Python tests run `44838455237` completed SUCCESS on head `bac9f20ab64a592baa2fa029c642281e2a419786`.
- PRs #35–#38 remain stacked and open. The manual workflow file is not on default branch `main`; it cannot yet be dispatched through the normal GitHub Actions UI until the workflow reaches the default branch. Do not merge any part of the stack without explicit user approval.
- Workflow file `.github/workflows/manual-short-strategy-study.yml` was read back from PR #38. It uses `workflow_dispatch` only, installs research dependencies, runs the shadow-only historical study, and archives JSON/Markdown artifacts for 30 days. No Alpaca credentials, broker requests, Supabase writes, or production imports are involved.

### Render production verification
- Worker service `srv-dbua8frm8hqs73f895h0` is configured for `main`, auto-deploy enabled, and is not suspended.
- Latest Render deployment: `dep-dc0adlm7bikc73fnlov0`, status LIVE, deployed commit `919f5a8f73869943c3de5772e13f30cda85fca31`.
- Runtime startup logs report `WORKER_VERSION=5.95`.
- Read-only logs around 2026-11-21 00:39 UTC show Alpaca paper account status ACTIVE and reported equity $4,996.44, with one ORLY position of 2 shares.
- The position-protection audit reported ORLY `PROTECTED`: stop leg active at $91.09, target leg active at $100.23, and both exit quantities match the 2-share position.
- The paper execution loop logs `submission_switch=ENABLED` and `paper_only=true`. The market-closed guard prevented new entry evaluation at the observed cycle. This is a material discrepancy from older handoff entries that recorded the execution switch OFF; do not change the switch or infer who changed it. Reconcile account identity/settings read-only before any future account-sensitive work.
- The current guardrail query uses an Alpaca account identity different from the older Nov 18 handoff snapshot. Do not assume the old $100,000 / zero-position account snapshot still describes the current account. No account, order, position, or guardrail data was mutated during this verification.
- Render deploy configuration confirms pushes to worker `main` auto-deploy. Never merge worker PRs without explicit approval.

### Dashboard and deployment caveat
- Dashboard main head is `7b9fdfa11bd5484d5eef12acdeec948ddc7195e0`; dashboard PRs #1–#7 are open and concern research panels.
- Streamlit Community Cloud visual deployment remains unverified. Do not claim dashboard deployment from GitHub commit status alone.

### Exact next actions
1. Reconcile the current Alpaca paper account identity and the observed enabled paper-submission switch using read-only evidence; do not alter settings, orders, positions, or guardrails.
2. Review the full dependency chain for worker PRs #34–#38 and prepare an ordered approval plan. Do not merge.
3. After the user explicitly approves the required merge sequence and the workflow is on default branch, manually dispatch the 5-year historical short study with a documented universe; inspect coverage, rejected rows, event counts, purged holdout, non-overlap diagnostics, and cost sensitivity before interpreting results.
4. Keep the production bearish-pullback comparator marked `NOT_RUN`; do not invent a daily-OHLCV proxy.
5. Continue paper-only operation. No live endpoints, live credentials, diagnostic orders, risk/entry/exit policy changes, or production deployments are authorized by a general “keep going” request.

### Verification boundary
- This session performed read-only GitHub, Render service/deploy/log, and CI inspection, plus a documentation-only branch/PR update.
- No strategy performance result was generated. No historical provider fetch was run. No order was submitted during this verification. No merge or deployment was performed.
