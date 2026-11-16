import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime

st.set_page_config(page_title="AI Market Intelligence", page_icon="📈", layout="wide")

UNIVERSE = {
    "Broad market": ["SPY", "QQQ", "IWM", "DIA"],
    "Stocks": ["NVDA", "TSLA", "AMD", "MSFT", "AAPL", "AMZN", "META", "GOOGL", "AVGO", "PLTR"],
    "Gold & silver": ["GLD", "IAU", "SLV", "GDX"],
    "Oil & energy": ["USO", "BNO", "XLE", "XOP"],
    "Crypto": ["BTC-USD", "ETH-USD", "SOL-USD"],
    "Rates & dollar": ["TLT", "IEF", "UUP"],
}

st.title("📈 AI Market Intelligence")
st.caption("Version 1.1 · Multi-market scanner · Paper trading only")
st.warning("Research and simulation only—not financial advice. Trend scores are rules-based screens, not predictions. Yahoo Finance data may be delayed, incomplete, or unavailable. This app does not place real orders.")

@st.cache_data(ttl=300, show_spinner=False)
def load_history(tickers, period="1y"):
    raw = yf.download(list(tickers), period=period, interval="1d", auto_adjust=True,
                      group_by="ticker", progress=False, threads=True)
    out = {}
    if raw.empty:
        return out
    if isinstance(raw.columns, pd.MultiIndex):
        for ticker in tickers:
            if ticker in raw.columns.get_level_values(0):
                frame = raw[ticker].copy()
                if "Close" in frame and frame["Close"].dropna().size:
                    out[ticker] = frame.dropna(subset=["Close"])
    elif len(tickers) == 1 and "Close" in raw:
        out[tickers[0]] = raw.dropna(subset=["Close"])
    return out

def rsi(series, n=14):
    delta = series.diff()
    gain = delta.clip(lower=0).ewm(alpha=1/n, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1/n, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

def analyze(ticker, frame):
    close = frame["Close"].dropna()
    if len(close) < 60:
        return None
    sma20, sma50, sma200 = close.rolling(20).mean(), close.rolling(50).mean(), close.rolling(200).mean()
    ret5 = close.pct_change(5).iloc[-1] * 100
    ret20 = close.pct_change(20).iloc[-1] * 100
    ret60 = close.pct_change(60).iloc[-1] * 100
    vol20 = close.pct_change().rolling(20).std().iloc[-1] * np.sqrt(252) * 100
    last, s20, s50 = close.iloc[-1], sma20.iloc[-1], sma50.iloc[-1]
    s200 = sma200.iloc[-1] if pd.notna(sma200.iloc[-1]) else np.nan
    r = rsi(close).iloc[-1]
    score = (25 if last > s20 else 0) + (20 if s20 > s50 else 0)
    score += (20 if pd.notna(s200) and last > s200 else 0)
    score += (15 if ret20 > 0 else 0) + (10 if ret60 > 0 else 0)
    score += 10 if 45 <= r <= 68 else (4 if 35 <= r < 45 or 68 < r <= 75 else 0)
    trend = "Strong uptrend" if score >= 75 else "Positive" if score >= 55 else "Mixed" if score >= 35 else "Weak"
    avg_abs_move = close.diff().abs().rolling(14).mean().iloc[-1]
    price_date = close.index[-1]
    if hasattr(price_date, "strftime"):
        price_date_label = price_date.strftime("%b %d, %Y")
    else:
        price_date_label = str(price_date)
    return {"Symbol": ticker, "Last": float(last), "Price date": price_date_label,
            "Score": int(score), "Trend": trend,
            "1W %": ret5, "1M %": ret20, "3M %": ret60, "RSI": r,
            "20D Vol %": vol20, "SMA20": s20, "SMA50": s50, "SMA200": s200,
            "Illustrative risk level": last - 2 * avg_abs_move}

# Paper account: session-only prototype. A persistent database is a later setup step.
if "paper_cash" not in st.session_state:
    st.session_state.paper_cash = 1000.00
if "paper_positions" not in st.session_state:
    st.session_state.paper_positions = {}
if "paper_journal" not in st.session_state:
    st.session_state.paper_journal = []
if "realized_pnl" not in st.session_state:
    st.session_state.realized_pnl = 0.00

with st.sidebar:
    st.header("Scanner settings")
    selected_groups = st.multiselect("Markets to scan", list(UNIVERSE), default=list(UNIVERSE))
    lookback = st.selectbox("History", ["6mo", "1y", "2y"], index=1)
    st.caption("Daily price bars. Cached for five minutes.")
    run_scan = st.button("Run market scan", type="primary", use_container_width=True)
    st.divider()
    st.caption("Trend score combines moving averages, momentum, and RSI. It is a screening heuristic, not a forecast.")

tickers = list(dict.fromkeys(t for group in selected_groups for t in UNIVERSE[group]))
if not tickers:
    st.info("Choose at least one market group in the sidebar.")
    st.stop()

if "scan_data" not in st.session_state:
    st.session_state.scan_data = None
if run_scan or st.session_state.scan_data is None:
    with st.spinner("Downloading market history and calculating indicators..."):
        history = load_history(tuple(tickers), lookback)
        rows = [analyze(t, frame) for t, frame in history.items()]
        rows = [row for row in rows if row is not None]
        st.session_state.scan_data = pd.DataFrame(rows).sort_values("Score", ascending=False) if rows else pd.DataFrame()

data = st.session_state.scan_data
if data is None or data.empty:
    st.error("No usable market data returned. Try again later or select different markets.")
    st.stop()

stamp = datetime.now().astimezone().strftime("%b %d, %Y %I:%M %p %Z")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Markets scanned", len(data))
c2.metric("Strong uptrends", int((data["Trend"] == "Strong uptrend").sum()))
c3.metric("Positive / strong", int(data["Trend"].isin(["Positive", "Strong uptrend"]).sum()))
c4.metric("Scan updated", stamp)

scanner_tab, paper_tab = st.tabs(["📊 Market scanner", "💵 $1,000 paper account"])
with scanner_tab:
    st.subheader("Strongest trends")
    display = data[["Symbol", "Trend", "Score", "Last", "Price date", "1W %", "1M %", "3M %", "RSI", "20D Vol %"]].copy()
    st.dataframe(display.style.format({"Last": "${:,.2f}", "1W %": "{:+.1f}%", "1M %": "{:+.1f}%", "3M %": "{:+.1f}%", "RSI": "{:.0f}", "20D Vol %": "{:.1f}%"}).background_gradient(subset=["Score"], cmap="RdYlGn"), use_container_width=True, hide_index=True)
    left, right = st.columns([1.2, 1])
    with left:
        st.subheader("Trend ranking")
        st.bar_chart(data.set_index("Symbol")[["Score"]].sort_values("Score"))
    with right:
        st.subheader("Selected asset")
        symbol = st.selectbox("Inspect symbol", data["Symbol"].tolist())
        row = data[data["Symbol"] == symbol].iloc[0]
        st.metric("Trend score", f'{int(row["Score"])}/100', row["Trend"])
        st.metric("Relative strength (RSI)", f'{row["RSI"]:.1f}')
        st.metric("Illustrative risk reference", f'${row["Illustrative risk level"]:.2f}')
        st.caption("This reference is informational only; it is not an order or recommended stop.")
    st.subheader("Price history")
    one = load_history((symbol,), lookback)
    if symbol in one:
        st.line_chart(one[symbol]["Close"].rename("Adjusted close"), use_container_width=True)
    st.caption("Strong uptrend means several technical conditions align. It does not mean an asset is automatically a good buy.")

with paper_tab:
    st.subheader("Virtual account")
    st.info("Simulation only. Prices are the latest available DAILY bars from Yahoo Finance—not live or executable quotes. The price date shown below is the date of the market data, not the time this page refreshed. This prototype is session-only and may reset if the app restarts or your session expires; do not use it as a permanent trade record.")
    prices = dict(zip(data["Symbol"], data["Last"]))
    positions = st.session_state.paper_positions
    market_value = sum(pos["quantity"] * prices.get(sym, pos["average_price"]) for sym, pos in positions.items())
    equity = st.session_state.paper_cash + market_value
    a, b, c, d = st.columns(4)
    a.metric("Cash available", f'${st.session_state.paper_cash:,.2f}')
    b.metric("Position value", f"${market_value:,.2f}")
    c.metric("Account value", f"${equity:,.2f}", f"${equity-1000:+,.2f} vs. start")
    d.metric("Realized P/L", f'${st.session_state.realized_pnl:+,.2f}')
    st.markdown("#### Approve a simulated trade")
    with st.form("paper_trade_form"):
        action = st.selectbox("Action", ["Buy", "Sell"])
        trade_symbol = st.selectbox("Asset", data["Symbol"].tolist())
        trade_qty = st.number_input("Quantity (fractional shares/units allowed)", min_value=0.001, value=1.0, step=0.1, format="%.3f")
        estimated_price = float(prices[trade_symbol])
        price_date = str(data.loc[data["Symbol"] == trade_symbol, "Price date"].iloc[0])
        st.caption(f"Daily-bar reference price: ${estimated_price:,.4f} per unit · estimated order value: ${estimated_price*trade_qty:,.2f}")
        st.caption(f"Market data date: {price_date} · This is not a live quote.")
        acknowledge_price = st.checkbox("I understand this simulated trade uses a historical daily price, not a live quote.")
        confirmed = st.form_submit_button(f"Approve simulated {action.lower()}", type="primary")
    if confirmed and not acknowledge_price:
        st.error("Please acknowledge that this is a historical daily price before recording the simulated trade.")
    if confirmed and acknowledge_price:
        price = float(prices[trade_symbol])
        cost = price * float(trade_qty)
        current = st.session_state.paper_positions.get(trade_symbol, {"quantity": 0.0, "average_price": 0.0})
        if action == "Buy":
            if cost > st.session_state.paper_cash + 1e-8:
                st.error("Not enough virtual cash for this purchase.")
            else:
                new_qty = current["quantity"] + float(trade_qty)
                new_avg = ((current["quantity"] * current["average_price"]) + cost) / new_qty
                st.session_state.paper_positions[trade_symbol] = {"quantity": new_qty, "average_price": new_avg}
                st.session_state.paper_cash -= cost
                st.session_state.paper_journal.insert(0, {"Time": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z"), "Action": "BUY", "Symbol": trade_symbol, "Quantity": float(trade_qty), "Reference price": price, "Value": cost, "Realized P/L": 0.0})
                st.success(f"Simulated buy recorded: {trade_qty:g} {trade_symbol} at ${price:,.4f}.")
        else:
            if float(trade_qty) > current["quantity"] + 1e-8:
                st.error("You cannot sell more units than you hold in the virtual account.")
            elif current["quantity"] <= 0:
                st.error("There is no position in this asset to sell.")
            else:
                pnl = (price - current["average_price"]) * float(trade_qty)
                remaining = current["quantity"] - float(trade_qty)
                if remaining <= 1e-8:
                    st.session_state.paper_positions.pop(trade_symbol, None)
                else:
                    st.session_state.paper_positions[trade_symbol] = {"quantity": remaining, "average_price": current["average_price"]}
                st.session_state.paper_cash += cost
                st.session_state.realized_pnl += pnl
                st.session_state.paper_journal.insert(0, {"Time": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z"), "Action": "SELL", "Symbol": trade_symbol, "Quantity": float(trade_qty), "Reference price": price, "Value": cost, "Realized P/L": pnl})
                st.success(f"Simulated sale recorded. Realized P/L: ${pnl:+,.2f} before costs.")
    st.markdown("#### Open positions")
    if st.session_state.paper_positions:
        position_rows = []
        for sym, pos in st.session_state.paper_positions.items():
            mark = prices.get(sym, pos["average_price"])
            value = pos["quantity"] * mark
            unrealized = (mark - pos["average_price"]) * pos["quantity"]
            position_rows.append({"Symbol": sym, "Quantity": pos["quantity"], "Average cost": pos["average_price"], "Reference price": mark, "Market value": value, "Unrealized P/L": unrealized})
        st.dataframe(pd.DataFrame(position_rows).style.format({"Quantity": "{:.4f}", "Average cost": "${:,.4f}", "Reference price": "${:,.4f}", "Market value": "${:,.2f}", "Unrealized P/L": "${:+,.2f}"}), use_container_width=True, hide_index=True)
    else:
        st.caption("No virtual positions yet. Your full $1,000 is in cash.")
    st.markdown("#### Trade journal")
    if st.session_state.paper_journal:
        st.dataframe(pd.DataFrame(st.session_state.paper_journal), use_container_width=True, hide_index=True)
    else:
        st.caption("Approved simulated trades will appear here.")
    if st.button("Reset virtual account to $1,000", help="Clears all simulated positions and journal entries."):
        st.session_state.paper_cash = 1000.00
        st.session_state.paper_positions = {}
        st.session_state.paper_journal = []
        st.session_state.realized_pnl = 0.00
        st.rerun()

st.caption("Prototype limitations: daily data only; no intraday feed, persistent database, backtesting, news/AI analysis, broker connection, or real order execution. Simulated trades exclude commissions, spread, slippage, and taxes.")
