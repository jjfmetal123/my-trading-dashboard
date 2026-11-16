import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timezone

st.set_page_config(page_title="AI Market Intelligence — v1", page_icon="📈", layout="wide")

UNIVERSE = {
    "Broad market": ["SPY", "QQQ", "IWM", "DIA"],
    "Stocks": ["NVDA", "TSLA", "AMD", "MSFT", "AAPL", "AMZN", "META", "GOOGL", "AVGO", "PLTR"],
    "Gold & silver": ["GLD", "IAU", "SLV", "GDX"],
    "Oil & energy": ["USO", "BNO", "XLE", "XOP"],
    "Crypto": ["BTC-USD", "ETH-USD", "SOL-USD"],
    "Rates & dollar": ["TLT", "IEF", "UUP"],
}
ALL_TICKERS = list(dict.fromkeys(t for group in UNIVERSE.values() for t in group))

st.title("📈 AI Market Intelligence")
st.caption("Version 1.0 · Multi-market trend scanner · Research and paper-trading signals only")
st.warning("Research prototype, not financial advice. Signals are rule-based, not an AI prediction. Data comes from Yahoo Finance via yfinance and may be delayed, incomplete, or unavailable. No orders are placed.")

@st.cache_data(ttl=300, show_spinner=False)
def load_history(tickers, period="1y"):
    raw = yf.download(
        tickers=list(tickers), period=period, interval="1d",
        auto_adjust=True, group_by="ticker", progress=False, threads=True
    )
    out = {}
    if raw.empty:
        return out
    if isinstance(raw.columns, pd.MultiIndex):
        for t in tickers:
            if t in raw.columns.get_level_values(0):
                d = raw[t].copy()
                if "Close" in d and d["Close"].dropna().size:
                    out[t] = d.dropna(subset=["Close"])
    else:
        if len(tickers) == 1 and "Close" in raw:
            out[tickers[0]] = raw.dropna(subset=["Close"])
    return out

def rsi(series, n=14):
    delta = series.diff()
    gain = delta.clip(lower=0).ewm(alpha=1/n, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1/n, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

def analyze(ticker, df):
    c = df["Close"].dropna()
    if len(c) < 60:
        return None
    sma20, sma50, sma200 = c.rolling(20).mean(), c.rolling(50).mean(), c.rolling(200).mean()
    ret5 = c.pct_change(5).iloc[-1] * 100
    ret20 = c.pct_change(20).iloc[-1] * 100
    ret60 = c.pct_change(60).iloc[-1] * 100
    rv20 = c.pct_change().rolling(20).std().iloc[-1] * np.sqrt(252) * 100
    last = c.iloc[-1]
    s20, s50 = sma20.iloc[-1], sma50.iloc[-1]
    s200 = sma200.iloc[-1] if pd.notna(sma200.iloc[-1]) else np.nan
    r = rsi(c).iloc[-1]
    score = 0
    score += 25 if last > s20 else 0
    score += 20 if s20 > s50 else 0
    score += 20 if pd.notna(s200) and last > s200 else 0
    score += 15 if ret20 > 0 else 0
    score += 10 if ret60 > 0 else 0
    score += 10 if 45 <= r <= 68 else (4 if 35 <= r < 45 or 68 < r <= 75 else 0)
    if score >= 75:
        trend = "Strong uptrend"
    elif score >= 55:
        trend = "Positive"
    elif score >= 35:
        trend = "Mixed"
    else:
        trend = "Weak"
    # Informational risk levels only; not orders.
    stop = last - 2 * (c.diff().abs().rolling(14).mean().iloc[-1])
    return {
        "Symbol": ticker, "Last": last, "Score": score, "Trend": trend,
        "1W %": ret5, "1M %": ret20, "3M %": ret60,
        "RSI": r, "20D Vol %": rv20, "SMA20": s20, "SMA50": s50,
        "SMA200": s200, "Illustrative risk level": stop
    }

with st.sidebar:
    st.header("Scanner settings")
    selected_groups = st.multiselect("Markets to scan", list(UNIVERSE), default=list(UNIVERSE))
    lookback = st.selectbox("History", ["6mo", "1y", "2y"], index=1)
    st.caption("Daily bars. Refreshes cached data every 5 minutes.")
    run = st.button("Run market scan", type="primary", use_container_width=True)
    st.divider()
    st.markdown("**Signal logic**")
    st.caption("Trend score uses price vs. 20/50/200-day averages, 1- and 3-month momentum, and RSI. It is a transparent screening heuristic, not a forecast.")

tickers = list(dict.fromkeys(t for g in selected_groups for t in UNIVERSE[g]))
if not tickers:
    st.info("Choose at least one market group in the sidebar.")
    st.stop()

if "scan_data" not in st.session_state:
    st.session_state.scan_data = None

if run or st.session_state.scan_data is None:
    with st.spinner("Downloading market history and calculating indicators..."):
        hist = load_history(tuple(tickers), lookback)
        rows = [analyze(t, d) for t, d in hist.items()]
        rows = [r for r in rows if r is not None]
        st.session_state.scan_data = pd.DataFrame(rows).sort_values("Score", ascending=False) if rows else pd.DataFrame()

data = st.session_state.scan_data
if data is None or data.empty:
    st.error("No usable market data returned. Check your internet connection, symbols, or try again later.")
    st.stop()

stamp = datetime.now().astimezone().strftime("%b %d, %Y %I:%M %p %Z")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Markets scanned", len(data))
c2.metric("Strong uptrends", int((data["Trend"] == "Strong uptrend").sum()))
c3.metric("Positive / strong", int(data["Trend"].isin(["Positive", "Strong uptrend"]).sum()))
c4.metric("Scan updated", stamp)

st.subheader("Strongest trends")
display = data[["Symbol", "Trend", "Score", "Last", "1W %", "1M %", "3M %", "RSI", "20D Vol %"]].copy()
st.dataframe(
    display.style.format({
        "Last": "${:,.2f}", "1W %": "{:+.1f}%", "1M %": "{:+.1f}%",
        "3M %": "{:+.1f}%", "RSI": "{:.0f}", "20D Vol %": "{:.1f}%"
    }).background_gradient(subset=["Score"], cmap="RdYlGn"),
    use_container_width=True, hide_index=True
)

left, right = st.columns([1.2, 1])
with left:
    st.subheader("Trend ranking")
    chart = data.set_index("Symbol")[["Score"]].sort_values("Score")
    st.bar_chart(chart)
with right:
    st.subheader("Selected asset")
    symbol = st.selectbox("Inspect symbol", data["Symbol"].tolist())
    row = data[data["Symbol"] == symbol].iloc[0]
    st.metric("Trend score", f'{int(row["Score"])}/100', row["Trend"])
    st.metric("Relative strength (RSI)", f'{row["RSI"]:.1f}')
    st.metric("Illustrative risk reference", f'${row["Illustrative risk level"]:.2f}')
    st.caption("The risk reference is a simple volatility-based research marker. It is not a recommended stop order.")

st.subheader("Price history")
hist_one = load_history((symbol,), lookback)
if symbol in hist_one:
    d = hist_one[symbol]
    st.line_chart(d["Close"].rename("Adjusted close"), use_container_width=True)
else:
    st.info("Price history unavailable for this symbol.")

st.subheader("How to interpret the screen")
st.markdown("""
- **75–100, Strong uptrend:** several trend and momentum conditions align; still can reverse sharply.
- **55–74, Positive:** more conditions are constructive than not.
- **35–54, Mixed:** signals conflict.
- **0–34, Weak:** trend conditions are mostly unfavorable.
- **RSI:** a momentum indicator, not a buy/sell instruction. High readings can persist in strong trends.
""")

st.subheader("Next build steps")
st.markdown("""
1. Add a persistent paper portfolio with entries, exits, cash, and trade journal.
2. Add walk-forward backtesting with fees, spread and slippage assumptions.
3. Add alerts when a defined setup appears.
4. Add a separate AI analyst that explains signals and news catalysts, without changing the rules.
5. Only after validation, connect a broker's paper-trading API. Live order execution remains disabled.
""")
st.caption("Prototype limitations: daily data only; no intraday execution; no fundamental/news analysis; no guarantee of data completeness; no broker connection.")
