# Market Intelligence Dashboard — Hosted Starter

A responsive Streamlit web dashboard designed to work in a desktop browser and on a phone. This starter scans a diversified list of stock, ETF, commodity-proxy, and crypto symbols using daily historical prices.

## Current capabilities
- Multi-market daily trend scan with configurable market groups.
- 5-day, 20-day, and 60-day returns; RSI(14); 20/50/200-day moving averages; 20-day annualized volatility.
- Transparent 0–100 rules-based trend score and ranked results.
- Price chart and an illustrative volatility reference.
- Mobile-friendly Streamlit layout; use your browser's Add to Home Screen option for quick phone access.

## Important limitations
- This is a research scanner, **not an autonomous AI trader** and not financial advice.
- The score is a transparent heuristic, not a prediction and not a buy/sell recommendation.
- Yahoo Finance via `yfinance` is a prototype data source. Data can be delayed, incomplete, rate-limited, or unavailable; check licensing and data entitlements before relying on it.
- Daily bars only. No intraday signals, persistent portfolio, backtesting, news analysis, broker connection, or order execution yet.
- No API keys, brokerage credentials, or personal financial information are needed by this starter.

## Deploy to Streamlit Community Cloud

### 1. Create a GitHub repository
1. Sign in to GitHub and create a new repository named `market-intelligence-dashboard`.
2. For a personal trading tool, choose **Private** if your account and deployment setup support private repositories. Do not put API keys, brokerage credentials, account numbers, or personal financial data in this repository.
3. Upload the contents of this folder to the repository root. Make sure `app.py`, `requirements.txt`, and `.streamlit/config.toml` are at the root / expected paths.

### 2. Deploy the app
1. Open <https://share.streamlit.io/> and sign in.
2. Connect/authorize your GitHub account when prompted.
3. Select **Create app**.
4. Choose the repository, branch (usually `main`), and main file path `app.py`.
5. Choose an app URL/subdomain if available, then select **Deploy**.
6. Wait for the build to finish. Streamlit will provide a `https://...streamlit.app` address.

Official instructions: <https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy>

### 3. Open it on both devices
- Windows 11: open the Streamlit URL in Edge or Chrome and bookmark it.
- Android: open the same URL in Chrome, tap the browser menu, and choose **Add to Home screen** (wording may vary). This creates an app-like shortcut; it remains a website.

## Run locally on Windows 11
1. Install Python 3.10 or newer from <https://www.python.org/downloads/>. During setup, enable **Add Python to PATH**.
2. Extract this ZIP to a folder, for example `C:\\Users\\YourName\\market_dashboard_hosted`.
3. Open that folder in File Explorer, click the address bar, type `cmd`, and press Enter.
4. Run:

```bat
py -m venv .venv
.venv\\Scripts\\activate
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

The local dashboard opens at <http://localhost:8501>.

## Next build stages
1. Add a persistent virtual $1,000 paper account, positions, cash ledger, and trade journal.
2. Add robust backtesting with fees, spreads, slippage, out-of-sample and walk-forward tests.
3. Add market-session-aware intraday data from a provider with documented licensing and latency.
4. Add alerts and a separate AI explanation layer grounded in retrieved data/news. AI commentary must not silently override strategy rules.
5. Add broker paper trading only after the strategy and risk limits are validated. Live execution stays disabled until separately and explicitly approved, with a kill switch and audit trail.
