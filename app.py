import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime

st.set_page_config(page_title="AI Market Intelligence", page_icon="📈", layout="wide")

# Simple app-level password gate. The password is stored in Streamlit Secrets,
# never in the GitHub source code. This protects the app UI, not the database
# from a determined attacker; database permissions will be configured separately.
import hmac

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

app_password = st.secrets.get("APP_PASSWORD", "")
if not app_password:
    st.error("App access is not configured yet. Add APP_PASSWORD in Streamlit Settings → Secrets.")
    st.stop()

if not st.session_state.authenticated:
    st.title("🔒 AI Market Intelligence")
    st.subheader("Private dashboard login")
    with st.form("login_form"):
        entered_password = st.text_input("Dashboard password", type="password")
        submitted = st.form_submit_button("Log in", type="primary")
    if submitted:
        if hmac.compare_digest(entered_password, str(app_password)):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("That password didn't match. Please try again.")
    st.stop()

with st.sidebar:
    if st.button("Log out", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

UNIVERSE = {
    "Broad market": ["SPY", "QQQ", "IWM", "DIA"],
    "Stocks": ["NVDA", "TSLA", "AMD", "MSFT", "AAPL", "AMZN", "META", "GOOGL", "AVGO", "PLTR"],
    "Gold & silver": ["GLD", "IAU", "SLV", "GDX"],
    "Oil & energy": ["USO", "BNO", "XLE", "XOP"],
    "Crypto": ["BTC-USD", "ETH-USD", "SOL-USD"],
    "Rates & dollar": ["TLT", "IEF", "UUP"],
}

st.title("📈 AI Market Intelligence")
st.caption("Version 1.6 · Password-protected · Risk sizing + simulated exit rules · Paper trading only")
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
    # Simple transparent screening labels, not AI predictions or guaranteed trade recommendations.
    if score >= 75 and 0 < ret20 <= 15 and 45 <= r <= 68:
        signal = "BUY CANDIDATE"
        signal_reason = "Strong trend, positive 1-month momentum, and RSI in the screening range"
    elif score >= 55 and ret20 > 0 and r < 72:
        signal = "WATCH"
        signal_reason = "Positive trend; wait for stronger confirmation"
    elif r > 72:
        signal = "EXTENDED"
        signal_reason = "RSI is elevated; avoid chasing a sharp move"
    else:
        signal = "NO SETUP"
        signal_reason = "Current trend/momentum rules are not aligned"
    avg_abs_move = close.diff().abs().rolling(14).mean().iloc[-1]
    price_date = close.index[-1]
    if hasattr(price_date, "strftime"):
        price_date_label = price_date.strftime("%b %d, %Y")
    else:
        price_date_label = str(price_date)
    return {"Symbol": ticker, "Last": float(last), "Price date": price_date_label,
            "Score": int(score), "Trend": trend, "Signal": signal, "Signal reason": signal_reason,
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
    display = data[["Symbol", "Signal", "Trend", "Score", "Last", "Price date", "1W %", "1M %", "3M %", "RSI", "20D Vol %"]].copy()
    st.dataframe(display.style.format({"Last": "${:,.2f}", "1W %": "{:+.1f}%", "1M %": "{:+.1f}%", "3M %": "{:+.1f}%", "RSI": "{:.0f}", "20D Vol %": "{:.1f}%"}).background_gradient(subset=["Score"], cmap="RdYlGn"), use_container_width=True, hide_index=True)
    candidates = data[data["Signal"] == "BUY CANDIDATE"]
    st.subheader("Rule-based trade candidates")
    st.caption("These are screening candidates only—not AI recommendations. The rules require a strong trend, positive 1-month return, and RSI between 45 and 68. Always review the chart and risk before paper trading.")
    if not candidates.empty:
        st.dataframe(candidates[["Symbol", "Score", "Last", "Price date", "1M %", "RSI", "Signal reason"]].style.format({"Last": "${:,.2f}", "1M %": "{:+.1f}%", "RSI": "{:.1f}"}), use_container_width=True, hide_index=True)
    else:
        st.info("No assets currently meet the candidate rules. That's okay—no trade is better than forcing one.")
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
    # Simulated exit monitoring uses the latest available DAILY close only.
    # It is not intraday monitoring and does not guarantee execution at the stop/target.
    triggered_exits = []
    for sym, pos in list(st.session_state.paper_positions.items()):
        mark = float(prices.get(sym, pos["average_price"]))
        stop_level = pos.get("stop_price")
        target_level = pos.get("target_price")
        exit_reason = None
        if stop_level is not None and mark <= float(stop_level):
            exit_reason = "STOP RULE (daily close)"
        elif target_level is not None and mark >= float(target_level):
            exit_reason = "TARGET RULE (daily close)"
        if exit_reason:
            qty = float(pos["quantity"])
            proceeds = qty * mark
            pnl = (mark - float(pos["average_price"])) * qty
            st.session_state.paper_cash += proceeds
            st.session_state.realized_pnl += pnl
            st.session_state.paper_journal.insert(0, {
                "Time": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z"),
                "Action": "AUTO " + exit_reason, "Symbol": sym, "Quantity": qty,
                "Reference price": mark, "Value": proceeds, "Realized P/L": pnl
            })
            st.session_state.paper_positions.pop(sym, None)
            triggered_exits.append(f"{sym}: {exit_reason} at daily reference price ${mark:,.2f}")
    if triggered_exits:
        st.warning("Simulated exit rule triggered: " + " · ".join(triggered_exits) +
                   ". This is recorded at the available daily reference price, not the exact stop/target price.")
    positions = st.session_state.paper_positions
    market_value = sum(pos["quantity"] * prices.get(sym, pos["average_price"]) for sym, pos in positions.items())
    equity = st.session_state.paper_cash + market_value
    a, b, c, d = st.columns(4)
    a.metric("Cash available", f'${st.session_state.paper_cash:,.2f}')
    b.metric("Position value", f"${market_value:,.2f}")
    c.metric("Account value", f"${equity:,.2f}", f"${equity-1000:+,.2f} vs. start")
    d.metric("Realized P/L", f'${st.session_state.realized_pnl:+,.2f}')
    st.markdown("#### Risk planner and simulated trade")
    candidate_symbols = data.loc[data["Signal"] == "BUY CANDIDATE", "Symbol"].tolist()
    default_symbol = candidate_symbols[0] if candidate_symbols else data.iloc[0]["Symbol"]
    default_index = data["Symbol"].tolist().index(default_symbol)
    st.caption("The asset selector starts with the highest-ranked scanner candidate when one exists. A buy plan uses the illustrative stop reference and a 2-to-1 reward/risk target. Simulated exit rules are checked only when the app reruns with a new daily price.")
    action = st.selectbox("Action", ["Buy", "Sell"])
    trade_symbol = st.selectbox("Asset", data["Symbol"].tolist(), index=default_index)
    selected_signal = data.loc[data["Symbol"] == trade_symbol].iloc[0]
    estimated_price = float(prices[trade_symbol])
    price_date = str(selected_signal["Price date"])
    stop_reference = float(selected_signal["Illustrative risk level"])
    risk_pct = st.select_slider("Maximum planned account risk per buy", options=[0.5, 1.0, 1.5, 2.0], value=1.0, format_func=lambda x: f"{x:.1f}%")
    risk_budget = max(0.0, equity * risk_pct / 100.0)
    risk_per_unit = estimated_price - stop_reference
    target_reference = estimated_price + (2.0 * risk_per_unit) if risk_per_unit > 0 else estimated_price
    cash_limited_qty = st.session_state.paper_cash / estimated_price if estimated_price > 0 else 0.0
    if risk_per_unit > 0:
        risk_limited_qty = risk_budget / risk_per_unit
        suggested_qty = min(risk_limited_qty, cash_limited_qty)
        planned_loss = suggested_qty * risk_per_unit
    else:
        suggested_qty = 0.0
        planned_loss = 0.0
    st.caption(f"Scanner status: {selected_signal['Signal']} — {selected_signal['Signal reason']}")
    r1, r2, r3, r4, r5 = st.columns(5)
    r1.metric("Daily reference price", f"${estimated_price:,.2f}")
    r2.metric("Illustrative stop reference", f"${stop_reference:,.2f}")
    r3.metric("2R profit target", f"${target_reference:,.2f}")
    r4.metric("Risk budget", f"${risk_budget:,.2f}")
    r5.metric("Estimated position size", f"{suggested_qty:.3f}")
    if risk_per_unit > 0:
        st.caption(f"Estimated risk per unit: ${risk_per_unit:,.2f} · Planned loss at suggested size: ${planned_loss:,.2f} · Cash available: ${st.session_state.paper_cash:,.2f}")
    else:
        st.error("The calculated stop reference is not below the current price. The risk planner cannot size a long buy for this asset.")
    st.warning("Simulation limitation: the stop and 2R target are stored as rules and checked only when the app reruns using a new DAILY close. They are not live orders, are not monitored intraday, and exits are recorded at the available daily reference price—not necessarily the stop/target price. Gaps can cause larger losses.")
    with st.form("paper_trade_form"):
        default_qty = max(0.001, round(suggested_qty, 3)) if action == "Buy" else max(0.001, round(min(st.session_state.paper_positions.get(trade_symbol, {}).get("quantity", 0.001), 1.0), 3))
        trade_qty = st.number_input("Quantity (fractional shares/units allowed)", min_value=0.001, value=float(default_qty), step=0.1, format="%.3f")
        st.caption(f"Estimated order value: ${estimated_price*trade_qty:,.2f} · Market data date: {price_date} · Not a live quote.")
        acknowledge_price = st.checkbox("I understand this simulated trade uses a historical daily price, not a live quote.")
        confirmed = st.form_submit_button(f"Approve simulated {action.lower()}", type="primary")
    if confirmed and not acknowledge_price:
        st.error("Please acknowledge that this is a historical daily price before recording the simulated trade.")
    if confirmed and acknowledge_price:
        price = float(prices[trade_symbol])
        cost = price * float(trade_qty)
        current = st.session_state.paper_positions.get(trade_symbol, {"quantity": 0.0, "average_price": 0.0})
        if action == "Buy":
            if risk_per_unit <= 0:
                st.error("Buy blocked: no valid illustrative stop reference is available for this asset.")
            elif trade_symbol in st.session_state.paper_positions:
                st.error("Adding to an existing position is disabled in this prototype. Close the existing position first.")
            elif float(trade_qty) > suggested_qty + 1e-6:
                st.error(f"Buy blocked: quantity exceeds the risk-sized limit of {suggested_qty:.3f}. Reduce quantity or choose another asset.")
            elif cost > st.session_state.paper_cash + 1e-8:
                st.error("Not enough virtual cash for this purchase.")
            else:
                st.session_state.paper_positions[trade_symbol] = {
                    "quantity": float(trade_qty),
                    "average_price": price,
                    "stop_price": float(stop_reference),
                    "target_price": float(target_reference)
                }
                st.session_state.paper_cash -= cost
                st.session_state.paper_journal.insert(0, {"Time": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z"), "Action": "BUY", "Symbol": trade_symbol, "Quantity": float(trade_qty), "Reference price": price, "Value": cost, "Realized P/L": 0.0})
                st.success(f"Simulated buy recorded: {trade_qty:g} {trade_symbol} at ${price:,.4f}. Stop rule ${stop_reference:,.2f}; 2R target ${target_reference:,.2f}.")
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
            position_rows.append({"Symbol": sym, "Quantity": pos["quantity"], "Average cost": pos["average_price"], "Daily reference": mark, "Stop rule": pos.get("stop_price"), "2R target": pos.get("target_price"), "Market value": value, "Unrealized P/L": unrealized})
        st.dataframe(pd.DataFrame(position_rows).style.format({"Quantity": "{:.4f}", "Average cost": "${:,.4f}", "Daily reference": "${:,.4f}", "Stop rule": "${:,.4f}", "2R target": "${:,.4f}", "Market value": "${:,.2f}", "Unrealized P/L": "${:+,.2f}"}), use_container_width=True, hide_index=True)
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
