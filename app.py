import streamlit as st
import pandas as pd
import numpy as np
import json
import yfinance as yf
from datetime import datetime, date

st.set_page_config(page_title="AI Market Intelligence", page_icon="📈", layout="wide")

# Simple app-level password gate. The password is stored in Streamlit Secrets,
# never in the GitHub source code. This protects the app UI, not the database
# from a determined attacker; database permissions will be configured separately.
import hmac
from supabase import create_client

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
    "Broad market": ["SPY", "QQQ", "IWM", "DIA", "VTI", "VOO", "RSP"],
    "Stocks": ["NVDA", "TSLA", "AMD", "MSFT", "AAPL", "AMZN", "META", "GOOGL", "AVGO", "PLTR", "NFLX", "COST", "LLY", "JPM", "ORCL", "CRM", "MU", "COIN", "HOOD", "SOFI"],
    "Gold & silver": ["GLD", "IAU", "SLV", "GDX", "GDXJ", "SGOL"],
    "Oil & energy": ["USO", "BNO", "XLE", "XOP", "OXY", "XOM", "CVX", "UNG", "URA"],
    "Crypto": ["BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD", "DOGE-USD", "ADA-USD", "LTC-USD", "LINK-USD", "AVAX-USD", "BCH-USD"],
    "Rates & dollar": ["TLT", "IEF", "SHY", "UUP", "FXE", "FXY"],
}

SECTOR_ETF = {
    "NVDA": "SMH", "AMD": "SMH", "AVGO": "SMH", "MU": "SMH",
    "AAPL": "XLK", "MSFT": "XLK", "ORCL": "XLK", "CRM": "XLK",
    "TSLA": "XLY", "AMZN": "XLY", "COST": "XLP", "LLY": "XLV",
    "JPM": "XLF", "COIN": "XLF", "HOOD": "XLF", "SOFI": "XLF",
    "META": "XLC", "GOOGL": "XLC", "NFLX": "XLC",
    "XOM": "XLE", "CVX": "XLE", "OXY": "XLE",
}

ASSET_CLASS = {
    **{t: "Broad market ETF" for t in UNIVERSE["Broad market"]},
    **{t: "Stock" for t in UNIVERSE["Stocks"]},
    **{t: "Precious metals ETF" for t in UNIVERSE["Gold & silver"]},
    **{t: "Energy / commodity proxy" for t in UNIVERSE["Oil & energy"]},
    **{t: "Cryptocurrency" for t in UNIVERSE["Crypto"]},
    **{t: "Rates / currency ETF" for t in UNIVERSE["Rates & dollar"]},
}

st.title("📈 AI Market Intelligence")
st.caption("Version 3.14 · Sector-aware cloud ranking · Automatic cloud AI review · Auto-refreshing cloud scanner · Intraday paper-exit monitor · Immediate portfolio refresh after trades · Clickable prioritized watchlist · AI-assisted trade analyst · Trade planning & invalidation · Expanded multi-market scanner · Account history · Supabase-saved paper account")
st.warning("Research and simulation only—not financial advice. Scanner scores are rules-based. The optional AI analyst provides a second opinion, not a prediction or guarantee. Yahoo Finance data may be delayed, incomplete, or unavailable. This app does not place real orders.")

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


@st.cache_data(ttl=20, show_spinner=False)
def load_intraday_bars(tickers):
    """Fetch recent one-minute Yahoo Finance bars for currently held symbols.

    This is a frequently refreshed data feed, not a guaranteed real-time quote
    or a broker execution feed. Yahoo can delay, omit, or revise intraday bars.
    """
    tickers = tuple(dict.fromkeys(str(t).upper() for t in tickers if t))
    if not tickers:
        return {}
    raw = yf.download(
        list(tickers), period="1d", interval="1m", auto_adjust=True,
        group_by="ticker", progress=False, threads=True, prepost=False
    )
    out = {}
    if raw is None or raw.empty:
        return out
    if isinstance(raw.columns, pd.MultiIndex):
        outer = set(raw.columns.get_level_values(0))
        inner = set(raw.columns.get_level_values(1))
        for ticker in tickers:
            if ticker in outer:
                frame = raw[ticker].copy()
            elif ticker in inner:
                frame = raw.xs(ticker, axis=1, level=1).copy()
            else:
                continue
            needed = [c for c in ("Open", "High", "Low", "Close", "Volume") if c in frame.columns]
            if "Close" in needed:
                out[ticker] = frame[needed].dropna(subset=["Close"])
    elif len(tickers) == 1 and "Close" in raw.columns:
        needed = [c for c in ("Open", "High", "Low", "Close", "Volume") if c in raw.columns]
        out[tickers[0]] = raw[needed].dropna(subset=["Close"])
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
    # Latest daily-bar volume compared with the prior 20 completed bars.
    # This is a rough participation check, not proof of buying or selling pressure.
    volume_ratio = np.nan
    if "Volume" in frame.columns:
        volume = pd.to_numeric(frame["Volume"], errors="coerce").dropna()
        if len(volume) >= 21:
            prior_avg_volume = float(volume.iloc[-21:-1].mean())
            if prior_avg_volume > 0:
                volume_ratio = float(volume.iloc[-1] / prior_avg_volume)
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
    atr14 = None
    recent_high20 = None
    recent_low20 = None
    if all(col in frame.columns for col in ["High", "Low", "Close"]):
        prev_close = frame["Close"].shift(1)
        true_range = pd.concat([
            frame["High"] - frame["Low"],
            (frame["High"] - prev_close).abs(),
            (frame["Low"] - prev_close).abs()
        ], axis=1).max(axis=1)
        if true_range.tail(14).notna().any():
            atr14 = float(true_range.tail(14).mean())
        if frame["High"].tail(20).notna().any():
            recent_high20 = float(frame["High"].tail(20).max())
        if frame["Low"].tail(20).notna().any():
            recent_low20 = float(frame["Low"].tail(20).min())
    # Weekly confirmation is calculated from the same daily source bars.
    # It is a slower trend check, not a separate live or intraday feed.
    weekly = close.resample("W-FRI").last().dropna()
    if len(weekly) >= 20:
        weekly_fast = weekly.rolling(10).mean().iloc[-1]
        weekly_slow = weekly.rolling(20).mean().iloc[-1]
        weekly_trend = "Bullish" if weekly.iloc[-1] > weekly_fast > weekly_slow else ("Bearish" if weekly.iloc[-1] < weekly_fast < weekly_slow else "Mixed")
    else:
        weekly_trend = "Insufficient history"
    risk_level = "High" if (pd.notna(vol20) and vol20 >= 55) else ("Moderate" if pd.notna(vol20) and vol20 >= 30 else "Lower")
    price_date = close.index[-1]
    if hasattr(price_date, "strftime"):
        price_date_label = price_date.strftime("%b %d, %Y")
    else:
        price_date_label = str(price_date)
    return {"Symbol": ticker, "Asset class": ASSET_CLASS.get(ticker, "Other"), "Last": float(last), "Price date": price_date_label,
            "Score": int(score), "Trend": trend, "Weekly trend": weekly_trend, "Risk level": risk_level,
            "Signal": signal, "Signal reason": signal_reason,
            "1W %": ret5, "1M %": ret20, "3M %": ret60, "RSI": r,
            "20D Vol %": vol20, "Latest volume / prior 20D avg": volume_ratio,
            "SMA20": s20, "SMA50": s50, "SMA200": s200,
            "ATR14": atr14, "Recent high 20D": recent_high20, "Recent low 20D": recent_low20,
            "Pullback low": (s20 - 0.25 * atr14) if atr14 is not None and pd.notna(s20) else np.nan,
            "Pullback high": (s20 + 0.25 * atr14) if atr14 is not None and pd.notna(s20) else np.nan,
            "Pullback stop": (s20 - 0.75 * atr14) if atr14 is not None and pd.notna(s20) else np.nan,
            "Breakout trigger": (recent_high20 + 0.10 * atr14) if atr14 is not None and recent_high20 is not None else np.nan,
            "Breakout stop": (recent_high20 + 0.10 * atr14 - atr14) if atr14 is not None and recent_high20 is not None else np.nan,
            "Illustrative risk level": last - 2 * avg_abs_move}

# Persistent paper account stored in Supabase. The secret key is used only
# server-side in Streamlit; it is never sent to the browser.
ACCOUNT_ID = "primary-paper-account"

@st.cache_resource(show_spinner=False)
def get_supabase_client():
    url = st.secrets.get("SUPABASE_URL", "")
    secret_key = st.secrets.get("SUPABASE_SECRET_KEY", "")
    if not url or not secret_key:
        raise RuntimeError("Missing SUPABASE_URL or SUPABASE_SECRET_KEY in Streamlit Secrets.")
    return create_client(str(url), str(secret_key))

def account_payload():
    return {
        "account_id": ACCOUNT_ID,
        "cash": round(float(st.session_state.paper_cash), 2),
        "realized_pnl": round(float(st.session_state.realized_pnl), 2),
        "positions": st.session_state.paper_positions,
        "journal": st.session_state.paper_journal,
        "updated_at": datetime.now().astimezone().isoformat(),
    }

def save_account():
    db.table("paper_account").upsert(account_payload(), on_conflict="account_id").execute()


def save_daily_snapshot(prices):
    """Upsert one end-of-day-style snapshot per app-server calendar date.

    Repeated app runs on the same date update that date's row instead of
    creating duplicate daily observations. This is not a scheduled process.
    """
    positions = st.session_state.paper_positions
    position_value = sum(
        float(pos.get("quantity", 0.0)) * float(prices.get(sym, pos.get("average_price", 0.0)))
        for sym, pos in positions.items()
    )
    unrealized = sum(
        (float(prices.get(sym, pos.get("average_price", 0.0))) - float(pos.get("average_price", 0.0)))
        * float(pos.get("quantity", 0.0))
        for sym, pos in positions.items()
    )
    cash = float(st.session_state.paper_cash)
    equity = cash + position_value
    snapshot_date = date.today().isoformat()
    payload = {
        "account_id": ACCOUNT_ID,
        "snapshot_date": snapshot_date,
        "cash": round(cash, 2),
        "position_value": round(position_value, 2),
        "equity": round(equity, 2),
        "realized_pnl": round(float(st.session_state.realized_pnl), 2),
        "unrealized_pnl": round(unrealized, 2),
        "positions": positions,
        "updated_at": datetime.now().astimezone().isoformat(),
    }
    db.table("paper_account_snapshots").upsert(
        payload, on_conflict="account_id,snapshot_date"
    ).execute()
    return payload


def load_snapshot_history():
    result = (db.table("paper_account_snapshots").select("snapshot_date,equity,cash,position_value,realized_pnl,unrealized_pnl")
              .eq("account_id", ACCOUNT_ID).order("snapshot_date").execute())
    return result.data or []


@st.cache_data(ttl=60, show_spinner=False)
def load_latest_cloud_scan():
    """Read the latest observation-only market scan saved by the cloud worker."""
    client = get_supabase_client()
    result = (
        client.table("market_scan_runs")
        .select("id,scanned_at,symbol_count,signal_counts,ranked_results,watchlist,data_source,scan_type,ai_review,ai_reviewed_at,ai_model")
        .order("scanned_at", desc=True)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None

try:
    db = get_supabase_client()
    if not st.session_state.get("paper_db_loaded", False):
        result = db.table("paper_account").select("*").eq("account_id", ACCOUNT_ID).limit(1).execute()
        if result.data:
            saved = result.data[0]
            st.session_state.paper_cash = float(saved["cash"])
            st.session_state.realized_pnl = float(saved["realized_pnl"])
            st.session_state.paper_positions = saved.get("positions") or {}
            st.session_state.paper_journal = saved.get("journal") or []
        else:
            # One-time migration of the user's confirmed first AAPL paper trade.
            # Original $1,000 less 0.9460 x $351.86 = $667.14044 cash.
            st.session_state.paper_cash = 667.14
            st.session_state.realized_pnl = 0.00
            st.session_state.paper_positions = {
                "AAPL": {
                    "quantity": 0.9460,
                    "average_price": 351.86,
                    "stop_price": 341.2945,
                    "target_price": 372.9910,
                }
            }
            st.session_state.paper_journal = [{
                "Time": "2026-11-16 20:34 UTC",
                "Action": "BUY",
                "Symbol": "AAPL",
                "Quantity": 0.9460,
                "Reference price": 351.86,
                "Value": 332.85956,
                "Realized P/L": 0.0,
            }]
            save_account()
        st.session_state.paper_db_loaded = True
except Exception as exc:
    st.error("The dashboard could not load its saved paper account from Supabase. Your account has not been reset. Check the Supabase connection settings and database permissions.")
    st.exception(exc)
    st.stop()

st.sidebar.success("Paper account connected · changes save automatically")

with st.sidebar:
    st.header("Scanner settings")
    selected_groups = st.multiselect("Markets to scan", list(UNIVERSE), default=list(UNIVERSE))
    lookback = st.selectbox("History", ["6mo", "1y", "2y"], index=1)
    st.caption("Daily price bars. Cached for five minutes.")
    run_scan = st.button("Run market scan", type="primary", use_container_width=True)
    st.divider()
    st.caption("Trend score combines moving averages, momentum, and RSI. Weekly trend adds a slower confirmation view. These are screening heuristics, not forecasts.")

tickers = list(dict.fromkeys(t for group in selected_groups for t in UNIVERSE[group]))
if not tickers:
    st.info("Choose at least one market group in the sidebar.")
    st.stop()

if st.session_state.get("scan_schema_version") != "3.1":
    st.session_state.scan_data = None
    st.session_state.scan_schema_version = "3.1"
if "scan_data" not in st.session_state:
    st.session_state.scan_data = None
if run_scan or st.session_state.scan_data is None:
    with st.spinner("Downloading market history and calculating indicators..."):
        # Always retrieve broad-market and mapped sector benchmarks alongside
        # the selected universe, but only display the assets the user selected.
        context_tickers = ["SPY", "QQQ"] + sorted(set(SECTOR_ETF.values()))
        fetch_tickers = tuple(dict.fromkeys(tickers + context_tickers))
        history = load_history(fetch_tickers, lookback)
        rows = [analyze(t, history[t]) for t in tickers if t in history]
        rows = [row for row in rows if row is not None]
        result_df = pd.DataFrame(rows)
        if not result_df.empty:
            def trailing_return(frame, days=20):
                if frame is None or "Close" not in frame or len(frame["Close"].dropna()) <= days:
                    return np.nan
                close_series = frame["Close"].dropna()
                return float((close_series.iloc[-1] / close_series.iloc[-days-1] - 1) * 100)
            spy_ret = trailing_return(history.get("SPY"))
            qqq_ret = trailing_return(history.get("QQQ"))
            result_df["SPY 1M %"] = spy_ret
            result_df["QQQ 1M %"] = qqq_ret
            result_df["Relative vs SPY 1M (pp)"] = result_df["1M %"] - spy_ret if pd.notna(spy_ret) else np.nan
            result_df["Sector ETF"] = result_df["Symbol"].map(SECTOR_ETF).fillna("—")
            sector_returns = {etf: trailing_return(history.get(etf)) for etf in set(SECTOR_ETF.values())}
            result_df["Sector ETF 1M %"] = result_df["Sector ETF"].map(sector_returns)
            result_df["Relative vs sector 1M (pp)"] = result_df["1M %"] - result_df["Sector ETF 1M %"]
        st.session_state.scan_data = result_df.sort_values("Score", ascending=False) if not result_df.empty else pd.DataFrame()

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


def build_closed_trade_metrics(journal):
    """Summarize realized SELL/automatic-exit journal rows; BUY rows are not closed trades."""
    closed = []
    for item in journal:
        action = str(item.get("Action", "")).upper()
        if action == "SELL" or action.startswith("AUTO "):
            try:
                pnl = float(item.get("Realized P/L", 0.0) or 0.0)
                closed.append({
                    "Symbol": item.get("Symbol", "—"),
                    "Action": item.get("Action", "—"),
                    "Time": item.get("Time", "—"),
                    "Quantity": float(item.get("Quantity", 0.0) or 0.0),
                    "Realized P/L": pnl,
                })
            except (TypeError, ValueError):
                continue
    return closed

def safe_pct(numerator, denominator):
    return (numerator / denominator * 100.0) if denominator else 0.0

scanner_tab, paper_tab, analytics_tab, cloud_tab = st.tabs(["📊 Market scanner", "💵 $1,000 paper account", "📈 Performance", "☁️ Cloud scanner"])

with cloud_tab:
    @st.fragment(run_every="60s")
    def render_cloud_scanner():
        st.subheader("☁️ Cloud market scanner")
        st.caption(
            "Latest rules-based scan produced by the Render background worker and saved in Supabase. "
            "Uses Yahoo Finance daily bars; this is a screening report, not an AI verdict or trade instruction."
        )
        refresh_cloud = st.button("Refresh cloud results", key="refresh_cloud_results")
        if refresh_cloud:
            load_latest_cloud_scan.clear()
        try:
            cloud_scan = load_latest_cloud_scan()
        except Exception as exc:
            cloud_scan = None
            st.error("Could not retrieve the cloud scan report from Supabase.")
            st.caption(f"Technical detail: {exc}")

        if cloud_scan:
            scanned_at = cloud_scan.get("scanned_at")
            try:
                scanned_label = pd.to_datetime(scanned_at, utc=True).astimezone().strftime("%b %d, %Y %I:%M:%S %p %Z")
            except Exception:
                scanned_label = str(scanned_at or "Unavailable")
            counts = cloud_scan.get("signal_counts") or {}
            ranked = cloud_scan.get("ranked_results") or []
            watchlist = cloud_scan.get("watchlist") or []

            c1, c2, c3 = st.columns(3)
            c1.metric("Symbols analyzed", int(cloud_scan.get("symbol_count") or 0))
            c2.metric("Ranked results stored", len(ranked))
            c3.metric("Watchlist entries stored", len(watchlist))
            st.write(f"**Last cloud scan:** {scanned_label}")
            st.caption(
                f"Source: {cloud_scan.get('data_source', 'Not specified')} · "
                f"Scan type: {cloud_scan.get('scan_type', 'Not specified')}"
            )

            st.markdown("#### Signal counts")
            if counts:
                count_cols = st.columns(min(len(counts), 4))
                for idx, (signal_name, signal_count) in enumerate(sorted(counts.items())):
                    count_cols[idx % len(count_cols)].metric(str(signal_name), int(signal_count))
            else:
                st.info("This scan did not include signal counts.")

            st.markdown("#### Top-ranked cloud scan results")
            if ranked:
                ranked_df = pd.DataFrame(ranked)
                display_columns = [
                    col for col in [
                        "symbol", "asset_class", "score", "adjusted_score", "signal_score", "sector_group", "sector_rotation_state", "sector_adjustment", "relative_1m_vs_spy_pp", "relative_1m_vs_sector_pp", "trend_points", "momentum_points", "rsi_points", "weekly_points", "volatility_penalty", "signal", "trend",
                        "weekly_trend", "risk", "last", "price_date",
                        "return_1w_pct", "return_1m_pct", "return_3m_pct",
                        "rsi", "annualized_volatility_pct", "reason"
                    ] if col in ranked_df.columns
                ]
                ranked_df = ranked_df[display_columns].rename(columns={
                    "symbol": "Symbol", "asset_class": "Asset class", "score": "Technical score",
                    "adjusted_score": "Refined rank score", "signal_score": "Mechanical signal score", "sector_group": "Sector group",
                    "sector_rotation_state": "Sector state", "sector_adjustment": "Sector adjustment",
                    "relative_1m_vs_spy_pp": "1M vs SPY (pp)", "relative_1m_vs_sector_pp": "1M vs sector ETF (pp)",
                    "volatility_penalty": "Volatility penalty", "trend_points": "Trend points",
                    "momentum_points": "Momentum points", "rsi_points": "RSI points", "weekly_points": "Weekly points",
                    "signal": "Signal", "trend": "Daily trend", "weekly_trend": "Weekly trend",
                    "risk": "Risk", "last": "Last daily price", "price_date": "Price date",
                    "return_1w_pct": "1W %", "return_1m_pct": "1M %",
                    "return_3m_pct": "3M %", "rsi": "RSI",
                    "annualized_volatility_pct": "Annualized volatility %",
                    "reason": "Screen rationale"
                })
                formatters = {
                    "Last daily price": "${:,.2f}", "1W %": "{:+.2f}%",
                    "1M %": "{:+.2f}%", "3M %": "{:+.2f}%",
                    "RSI": "{:.1f}", "Annualized volatility %": "{:.1f}%"
                }
                st.dataframe(ranked_df.style.format(
                    {k: v for k, v in formatters.items() if k in ranked_df.columns}
                ), use_container_width=True, hide_index=True)
            else:
                st.info("The latest scan did not store ranked results.")

            st.markdown("#### Cloud watchlist")
            if watchlist:
                watch_df = pd.DataFrame(watchlist)
                watch_columns = [
                    col for col in [
                        "symbol", "score", "adjusted_score", "signal_score", "sector_group", "sector_rotation_state", "relative_1m_vs_spy_pp", "relative_1m_vs_sector_pp", "signal", "weekly_trend", "return_1m_pct", "rsi", "risk"
                    ] if col in watch_df.columns
                ]
                watch_df = watch_df[watch_columns].rename(columns={
                    "symbol": "Symbol", "score": "Technical score", "adjusted_score": "Refined rank score", "signal_score": "Mechanical signal score",
                    "sector_group": "Sector group", "sector_rotation_state": "Sector state",
                    "relative_1m_vs_spy_pp": "1M vs SPY (pp)", "relative_1m_vs_sector_pp": "1M vs sector ETF (pp)", "signal": "Signal",
                    "return_1m_pct": "1M %", "rsi": "RSI", "risk": "Risk"
                })
                st.dataframe(watch_df.style.format({
                    k: v for k, v in {"1M %": "{:+.2f}%", "RSI": "{:.1f}"}.items()
                    if k in watch_df.columns
                }), use_container_width=True, hide_index=True)
            else:
                st.caption("No BUY CANDIDATE or WATCH assets were stored in the cloud watchlist.")
            # Sector/asset-group rotation is stored alongside the AI review. It is
            # computed from ETF/asset proxy price performance, not actual fund flows.
            ai_review_for_rotation = cloud_scan.get("ai_review") or {}
            rotation_rows = ai_review_for_rotation.get("sector_rotation") or []
            if rotation_rows:
                st.divider()
                st.markdown("### 🔄 Sector & asset-group rotation")
                st.caption("Ranked from 1W/1M/3M daily-bar returns and relative performance versus SPY. These are ETF/asset price proxies, not measured fund flows.")
                rotation_df = pd.DataFrame(rotation_rows)
                rotation_cols = [c for c in ["group", "proxy", "rotation_state", "return_1w_pct", "return_1m_pct", "return_3m_pct", "relative_1m_vs_spy_pp", "relative_3m_vs_spy_pp", "momentum_score"] if c in rotation_df.columns]
                rotation_df = rotation_df[rotation_cols].rename(columns={
                    "group": "Group", "proxy": "Proxy", "rotation_state": "Relative state",
                    "return_1w_pct": "1W %", "return_1m_pct": "1M %", "return_3m_pct": "3M %",
                    "relative_1m_vs_spy_pp": "1M vs SPY (pp)", "relative_3m_vs_spy_pp": "3M vs SPY (pp)",
                    "momentum_score": "Momentum score"
                })
                st.dataframe(rotation_df.style.format({c: "{:+.2f}" for c in ["1W %", "1M %", "3M %", "1M vs SPY (pp)", "3M vs SPY (pp)", "Momentum score"] if c in rotation_df.columns}), use_container_width=True, hide_index=True)

            st.divider()
            st.markdown("### 🤖 Automatic AI second-stage review")
            ai_review = cloud_scan.get("ai_review")
            if ai_review and isinstance(ai_review, dict):
                ai_report = ai_review.get("report") or {}
                ai_model_label = cloud_scan.get("ai_model") or ai_review.get("model") or "Model not recorded"
                reviewed_at = cloud_scan.get("ai_reviewed_at") or ai_review.get("created_at")
                try:
                    reviewed_label = pd.to_datetime(reviewed_at, utc=True).astimezone().strftime("%b %d, %Y %I:%M:%S %p %Z")
                except Exception:
                    reviewed_label = str(reviewed_at or "Unavailable")
                a1, a2 = st.columns(2)
                a1.metric("AI review status", "Completed")
                a2.metric("Candidates reviewed", min(12, len(ranked)))
                st.caption(f"Model: {ai_model_label} · Reviewed: {reviewed_label}")
                market_read = ai_report.get("market_read")
                if market_read:
                    st.markdown("#### Market read")
                    st.write(market_read)
                ai_ranked = ai_report.get("ranked_candidates") or []
                if ai_ranked:
                    st.markdown("#### AI-ranked research candidates")
                    for candidate in ai_ranked:
                        symbol_name = str(candidate.get("symbol", "Unknown"))
                        rank_value = candidate.get("rank", "—")
                        stance = str(candidate.get("stance", "Unspecified")).replace("_", " ")
                        with st.expander(f"#{rank_value} · {symbol_name} · {stance}"):
                            if candidate.get("rationale"):
                                st.write(candidate["rationale"])
                            if candidate.get("sector_group"):
                                st.caption(
                                    f"Sector context: {candidate.get('sector_group')} · "
                                    f"{candidate.get('sector_rotation_state', 'Not mapped')} · "
                                    f"ranking adjustment {candidate.get('sector_adjustment', 0):+} points"
                                )
                            bullish = candidate.get("bullish_factors") or []
                            bearish = candidate.get("bearish_factors") or []
                            left, right = st.columns(2)
                            with left:
                                st.markdown("**Bullish factors**")
                                if bullish:
                                    for item in bullish:
                                        st.markdown(f"- {item}")
                                else:
                                    st.caption("None specified")
                            with right:
                                st.markdown("**Bearish factors**")
                                if bearish:
                                    for item in bearish:
                                        st.markdown(f"- {item}")
                                else:
                                    st.caption("None specified")
                            if candidate.get("what_would_improve"):
                                st.markdown("**What would improve the setup:** " + str(candidate["what_would_improve"]))
                            if candidate.get("key_risk"):
                                st.markdown("**Key risk:** " + str(candidate["key_risk"]))
                top_three = ai_report.get("top_three_for_individual_review") or []
                if top_three:
                    st.markdown("**Top three for individual review:** " + " · ".join(str(x) for x in top_three))
                cautions = ai_report.get("important_cautions") or []
                limitations = ai_report.get("data_limitations") or []
                if cautions:
                    st.markdown("#### Important cautions")
                    for item in cautions:
                        st.markdown(f"- {item}")
                if limitations:
                    st.markdown("#### Data limitations noted by AI")
                    for item in limitations:
                        st.markdown(f"- {item}")
            else:
                st.info("The latest scan is saved, but its AI review is not available yet. The worker may still be reviewing it, or the AI request may have failed. The next scheduled scan will try again.")

            st.caption("V3.14 refined ranking uses continuous trend, momentum, RSI, weekly alignment, relative strength versus SPY and the mapped sector ETF, plus a volatility penalty. A bounded sector-rotation overlay is then applied. The separate mechanical signal score and BUY CANDIDATE/WATCH labels remain unchanged; unmapped assets receive no sector adjustment.")
            st.warning(
                "The scanner uses Yahoo Finance daily bars. The AI is a second opinion based only on the supplied scan facts; it does not verify live quotes, news, filings, fundamentals, or intraday conditions. Rankings are research prioritization, not buy/sell signals or instructions to trade. The cloud worker is observation-only."
            )
        else:
            st.info(
                "No cloud scan report is available yet. Confirm the Render worker is running and has saved "
                "a report to Supabase, then use Refresh cloud results."
            )

    render_cloud_scanner()

with scanner_tab:
    st.subheader("Market scanner")
    st.caption("Select a row to open its analysis immediately below the scanner. On desktop, click anywhere in the row; on mobile, tap the row.")
    display = data[["Symbol", "Asset class", "Signal", "Trend", "Weekly trend", "Risk level", "Score", "Last", "Price date", "1W %", "1M %", "3M %", "RSI", "20D Vol %"]].copy()
    selection_event = st.dataframe(
        display.style.format({"Last": "${:,.2f}", "1W %": "{:+.1f}%", "1M %": "{:+.1f}%", "3M %": "{:+.1f}%", "RSI": "{:.0f}", "20D Vol %": "{:.1f}%"}).background_gradient(subset=["Score"], cmap="RdYlGn"),
        use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row", key="scanner_table"
    )
    selected_rows = selection_event.selection.rows if selection_event and hasattr(selection_event, "selection") else []
    # A watchlist selection takes precedence over any previously selected scanner row.
    if st.session_state.pop("watchlist_override", False):
        pass
    elif selected_rows:
        selected_symbol = str(display.iloc[selected_rows[0]]["Symbol"])
        st.session_state["inspected_symbol"] = selected_symbol
    if st.session_state.get("inspected_symbol") not in data["Symbol"].tolist():
        st.session_state["inspected_symbol"] = str(data.iloc[0]["Symbol"])


    symbol = st.session_state["inspected_symbol"]
    row = data[data["Symbol"] == symbol].iloc[0]
    last = float(row["Last"])
    stop = float(row["Illustrative risk level"])
    per_unit_risk = max(last - stop, 0.01)
    target_1r, target_2r, target_3r = last + per_unit_risk, last + 2 * per_unit_risk, last + 3 * per_unit_risk
    risk_budget = 1000.0 * 0.01
    suggested_qty = risk_budget / per_unit_risk

    st.divider()
    st.subheader(f"🔎 {symbol} — individual asset analysis")
    st.caption("Your selected asset analysis appears here, immediately after the main scanner.")
    st.caption(f"{row['Asset class']} · Price date: {row['Price date']} · {row['Signal reason']}")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Last daily price", f"${last:,.2f}")
    m2.metric("Scanner score", f"{int(row['Score'])}/100", str(row["Trend"]))
    m3.metric("RSI", f"{float(row['RSI']):.1f}")
    m4.metric("Risk classification", str(row["Risk level"]), f"{float(row['20D Vol %']):.1f}% annualized volatility")

    st.markdown("**Trend and momentum**")
    t1, t2, t3 = st.columns(3)
    t1.metric("1-week return", f"{float(row['1W %']):+.1f}%")
    t2.metric("1-month return", f"{float(row['1M %']):+.1f}%")
    t3.metric("3-month return", f"{float(row['3M %']):+.1f}%")
    st.markdown("**Volume and market context**")
    st.caption("Benchmark returns are shown separately so you can compare the broad S&P 500 market (SPY) with the Nasdaq-100 (QQQ).")
    volume_ratio = row.get("Latest volume / prior 20D avg", np.nan)
    b1, b2, b3 = st.columns(3)
    if pd.notna(volume_ratio):
        b1.metric("Latest bar volume / prior 20D average", f"{float(volume_ratio):.2f}×")
        if float(volume_ratio) >= 1.5:
            st.info("Latest daily bar volume is at least 1.5× the prior 20-bar average. This indicates elevated activity, not whether buyers or sellers dominated.")
        elif float(volume_ratio) <= 0.7:
            st.warning("Latest daily-bar volume is below 70% of the prior 20-bar average; participation appears lighter.")
        else:
            st.caption("Latest daily-bar volume is near its prior 20-bar average. Volume alone does not confirm an entry.")
    else:
        b1.metric("Latest bar volume / prior 20D average", "Unavailable")
    b2.metric("SPY 1-month return", f"{float(row['SPY 1M %']):+.1f}%" if pd.notna(row.get("SPY 1M %")) else "Unavailable")
    b3.metric("QQQ 1-month return", f"{float(row['QQQ 1M %']):+.1f}%" if pd.notna(row.get("QQQ 1M %")) else "Unavailable")

    r1, r2, r3 = st.columns(3)
    r1.metric("Relative vs SPY", f"{float(row['Relative vs SPY 1M (pp)']):+.1f} pp" if pd.notna(row.get("Relative vs SPY 1M (pp)")) else "Unavailable")
    r2.metric("Relative vs QQQ", f"{float(row['1M %'] - row['QQQ 1M %']):+.1f} pp" if pd.notna(row.get("QQQ 1M %")) else "Unavailable")
    sector_name = str(row.get("Sector ETF", "—"))
    r3.metric(f"Relative vs {sector_name}", f"{float(row['Relative vs sector 1M (pp)']):+.1f} pp" if pd.notna(row.get("Relative vs sector 1M (pp)")) else "Unavailable")
    st.caption("Volume compares the latest available daily bar with the previous 20 bars; if today's bar is still forming, its volume ratio is provisional. SPY, QQQ and sector comparisons use the same daily-price source and trailing 20-session returns. Relative strength is the asset's return minus the benchmark return. Sector mappings are approximate group proxies, not formal classifications.")

    st.markdown("**Illustrative risk / reward plan**")
    st.caption("Reference levels only, calculated from the latest daily close and the scanner's 2 × average absolute daily move. They are not live quotes, guaranteed fills, or broker stop orders.")
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Reference entry", f"${last:,.2f}")
    r2.metric("Illustrative stop", f"${stop:,.2f}")
    r3.metric("2R target", f"${target_2r:,.2f}")
    r4.metric("3R target", f"${target_3r:,.2f}")
    st.write(f"At a hypothetical 1% risk budget on a $1,000 account ($10), the arithmetic position size would be about **{suggested_qty:.4f} units** before considering whole-share limits, fees, slippage, liquidity, or portfolio exposure. This is educational sizing, not an instruction to trade.")
    left, right = st.columns([1.2, 1])
    with left:
        st.markdown("**Recent daily price history**")
        one = load_history((symbol,), lookback)
        if symbol in one:
            st.line_chart(one[symbol]["Close"].rename("Adjusted close"), use_container_width=True)
    with right:
        st.markdown("**Why the scanner classified it this way**")
        st.write(f"- Signal: **{row['Signal']}**")
        st.write(f"- Daily trend: **{row['Trend']}**")
        st.write(f"- Weekly trend: **{row['Weekly trend']}**")
        st.write(f"- Signal rationale: {row['Signal reason']}")
        if float(row["RSI"]) > 68:
            st.warning("RSI is elevated; chasing the move may carry additional risk.")
        elif float(row["RSI"]) < 45:
            st.warning("RSI is below the scanner's preferred momentum range.")
        else:
            st.info("RSI is within the scanner's preferred 45–68 screening range.")
    # Trade-quality assessment: separate trend strength from whether price is
    # reasonably placed for a new entry. All thresholds are transparent heuristics.
    sma20 = float(row["SMA20"]) if pd.notna(row["SMA20"]) else float("nan")
    distance_sma20 = ((last / sma20) - 1.0) * 100.0 if pd.notna(sma20) and sma20 > 0 else float("nan")
    account_equity_for_plan = float(st.session_state.paper_cash) + sum(
        float(pos.get("quantity", 0.0)) * float(data.loc[data["Symbol"] == sym, "Last"].iloc[0]
        if sym in data["Symbol"].values else pos.get("average_price", 0.0))
        for sym, pos in st.session_state.paper_positions.items()
    )
    risk_budget_for_plan = account_equity_for_plan * 0.01
    cash_for_plan = float(st.session_state.paper_cash)
    risk_qty = risk_budget_for_plan / per_unit_risk if per_unit_risk > 0 else 0.0
    cash_qty = cash_for_plan / last if last > 0 else 0.0
    plan_qty = min(risk_qty, cash_qty)
    planned_dollar_risk = plan_qty * per_unit_risk
    if row["Signal"] != "BUY CANDIDATE":
        entry_assessment = "WAIT — scanner rules are not currently at BUY CANDIDATE."
        entry_color = "warning"
    elif pd.isna(distance_sma20):
        entry_assessment = "WAIT — not enough moving-average context to assess entry placement."
        entry_color = "warning"
    elif distance_sma20 > 3.0:
        entry_assessment = "WAIT FOR PULLBACK — price is more than 3% above its 20-day average."
        entry_color = "warning"
    elif distance_sma20 < -1.0:
        entry_assessment = "AVOID FOR NOW — price is below its 20-day average; trend needs to recover."
        entry_color = "error"
    else:
        entry_assessment = "POTENTIAL ENTRY AREA — price is near its 20-day average and passes the scanner screen; confirm manually."
        entry_color = "success"

    st.markdown("**Trade decision & entry quality**")
    if entry_color == "success":
        st.success(entry_assessment)
    elif entry_color == "error":
        st.error(entry_assessment)
    else:
        st.warning(entry_assessment)
    q1, q2, q3 = st.columns(3)
    q1.metric("Price vs. 20-day average", f"{distance_sma20:+.1f}%" if pd.notna(distance_sma20) else "—")
    q2.metric("Illustrative risk budget (1%)", f"${risk_budget_for_plan:,.2f}")
    q3.metric("Risk-sized quantity", f"{plan_qty:.4f} units")
    st.caption(f"At the reference price, cash available limits this plan to {cash_qty:.4f} units. Risk sizing limits it to {risk_qty:.4f}; the smaller amount is shown. Estimated loss at the stop: ${planned_dollar_risk:,.2f}, before fees, spread, slippage, gaps, or execution differences.")

    st.markdown("**What would invalidate this setup?**")
    st.write(
        f"- A daily close below the illustrative stop reference (${stop:,.2f}) invalidates the planned risk/reward setup. "
        + (f"A close below the 20-day average (${sma20:,.2f}) is an additional trend warning." if pd.notna(sma20) else "A 20-day average is unavailable, so use the stop reference only as a rough warning level.")
    )
    st.write("- A change to a negative 1-month return, a weak weekly trend, or RSI outside the scanner's preferred range should trigger a fresh review—not an automatic buy.")
    st.caption("These are educational decision rules, not AI predictions or guaranteed trade recommendations. Position sizing is hypothetical and does not check correlation, sector concentration, liquidity, or all existing portfolio exposures.")


    st.markdown("### Setup status monitor")
    st.caption("Status is calculated from the latest available daily bars and mechanical watch levels. It is a monitoring aid—not an automatic entry signal.")
    status_ohlc = one[symbol].tail(30) if symbol in one else pd.DataFrame()
    status_atr = None
    status_high20 = None
    if not status_ohlc.empty and all(col in status_ohlc for col in ["High", "Low", "Close"]):
        status_prev_close = status_ohlc["Close"].shift(1)
        status_true_range = pd.concat([
            status_ohlc["High"] - status_ohlc["Low"],
            (status_ohlc["High"] - status_prev_close).abs(),
            (status_ohlc["Low"] - status_prev_close).abs()
        ], axis=1).max(axis=1)
        if status_true_range.tail(14).notna().any():
            status_atr = float(status_true_range.tail(14).mean())
        status_high20 = float(status_ohlc["High"].tail(20).max())

    status_pullback_low = status_pullback_high = status_pullback_stop = None
    status_breakout_trigger = status_breakout_stop = None
    if pd.notna(sma20) and status_atr is not None and status_atr > 0:
        status_pullback_low = float(sma20 - 0.25 * status_atr)
        status_pullback_high = float(sma20 + 0.25 * status_atr)
        status_pullback_stop = float(status_pullback_low - 0.50 * status_atr)
    if status_high20 is not None and status_atr is not None and status_atr > 0:
        status_breakout_trigger = float(status_high20 + 0.10 * status_atr)
        status_breakout_stop = float(status_breakout_trigger - status_atr)

    def describe_pullback_status(low, high, stop_level):
        if low is None or high is None or stop_level is None:
            return ("DATA UNAVAILABLE", "Required daily price history is missing.", "off")
        if last <= stop_level:
            return ("INVALIDATED — REVIEW", f"Latest daily reference (${last:,.2f}) is at or below the pullback stop reference (${stop_level:,.2f}). Reassess this pullback scenario.", "error")
        if low <= last <= high:
            return ("IN WATCH RANGE — CONFIRMATION NEEDED", f"Price is inside the pullback watch range ${low:,.2f}–${high:,.2f}. Wait for stabilization and a supportive daily-bar pattern; touching the range alone is not confirmation.", "warning")
        if last > high:
            return ("WAITING", f"Price is above the pullback watch range. Do not chase; monitor for a pullback into ${low:,.2f}–${high:,.2f}.", "warning")
        return ("WAITING — TREND REVIEW", f"Price is below the pullback watch range but above its stop reference (${stop_level:,.2f}). Review trend conditions; do not assume the range is support.", "warning")

    def describe_breakout_status(trigger, stop_level):
        if trigger is None or stop_level is None:
            return ("DATA UNAVAILABLE", "Breakout reference could not be calculated from the available daily bars.", "off")
        if last <= stop_level:
            return ("INVALIDATED — REVIEW", f"Latest daily reference (${last:,.2f}) is at or below the breakout scenario's stop reference (${stop_level:,.2f}). Reassess the breakout scenario.", "error")
        if last >= trigger:
            return ("BREAKOUT THRESHOLD REACHED — VERIFY", f"Latest daily reference (${last:,.2f}) is at/above the breakout trigger (${trigger:,.2f}). Verify an actual daily close above the trigger and supporting volume before treating it as a potential setup.", "warning")
        distance_pct = (trigger / last - 1.0) * 100.0 if last > 0 else None
        return ("WAITING — BREAKOUT NOT TRIGGERED", f"Price is below the breakout trigger (${trigger:,.2f}) by {distance_pct:.1f}%. Monitor for a daily close above the trigger; the pullback range is a separate scenario.", "warning")

    pullback_status = describe_pullback_status(status_pullback_low, status_pullback_high, status_pullback_stop)
    breakout_status = describe_breakout_status(status_breakout_trigger, status_breakout_stop)
    status_col1, status_col2 = st.columns(2)
    with status_col1:
        st.markdown("**Pullback setup**")
        if pullback_status[2] == "error":
            st.error(pullback_status[0])
        elif pullback_status[2] == "warning":
            st.warning(pullback_status[0])
        else:
            st.info(pullback_status[0])
        st.write(pullback_status[1])
        if status_pullback_low is not None:
            st.caption(f"Watch ${status_pullback_low:,.2f}–${status_pullback_high:,.2f} · stop reference ${status_pullback_stop:,.2f}")
    with status_col2:
        st.markdown("**Breakout setup**")
        if breakout_status[2] == "error":
            st.error(breakout_status[0])
        elif breakout_status[2] == "warning":
            st.warning(breakout_status[0])
        else:
            st.info(breakout_status[0])
        st.write(breakout_status[1])
        if status_breakout_trigger is not None:
            st.caption(f"Trigger ${status_breakout_trigger:,.2f} · stop reference ${status_breakout_stop:,.2f}")
    st.caption("This version deliberately does not display ENTRY CONFIRMED: the app does not yet validate volume or candle-pattern confirmation. A price touching a watch level is not enough to confirm a trade.")

    st.markdown("### AI trade analyst")
    st.caption("AI second opinion with calculated pullback and breakout watch prices, scenario-specific stops, targets, and sizing. It can disagree with the rules-based scanner. It does not execute trades, and it only sees the daily market data and indicators shown here—not live quotes, news, filings, or your full portfolio context.")
    ai_api_key = st.secrets.get("OPENAI_API_KEY", "")
    if not ai_api_key:
        st.info("To enable the AI analyst, add OPENAI_API_KEY to Streamlit Community Cloud → App → Settings → Secrets. Keep the key there only; never put it in GitHub or share it in chat.")
        st.caption("An OpenAI API key and API billing are separate from a ChatGPT subscription. The analyst is optional; the rules-based scanner continues to work without it.")
    else:
        if st.button(f"Ask AI to analyze {symbol}", type="primary", key="ask_ai_analyst"):
            try:
                from openai import OpenAI
                client = OpenAI(api_key=str(ai_api_key))
                # Add recent daily OHLC context so the analyst can distinguish
                # a pullback from a breakout. These remain historical daily bars.
                recent_ohlc = one[symbol].tail(30) if symbol in one else pd.DataFrame()
                recent_high_20 = float(recent_ohlc["High"].tail(20).max()) if not recent_ohlc.empty and "High" in recent_ohlc else None
                recent_low_20 = float(recent_ohlc["Low"].tail(20).min()) if not recent_ohlc.empty and "Low" in recent_ohlc else None
                atr14 = None
                if not recent_ohlc.empty and all(col in recent_ohlc for col in ["High", "Low", "Close"]):
                    prev_close = recent_ohlc["Close"].shift(1)
                    true_range = pd.concat([
                        recent_ohlc["High"] - recent_ohlc["Low"],
                        (recent_ohlc["High"] - prev_close).abs(),
                        (recent_ohlc["Low"] - prev_close).abs()
                    ], axis=1).max(axis=1)
                    if true_range.tail(14).notna().any():
                        atr14 = round(float(true_range.tail(14).mean()), 4)
                # Deterministic watch levels: these are calculated from the
                # supplied historical daily bars, not invented by the AI.
                pullback_low = pullback_high = breakout_trigger = None
                pullback_stop = breakout_stop = None
                pullback_qty = breakout_qty = None
                pullback_risk_dollars = breakout_risk_dollars = None
                if sma20 > 0 and atr14 is not None and atr14 > 0:
                    # A narrow watch zone around the 20-day average.
                    pullback_low = round(float(sma20 - 0.25 * atr14), 4)
                    pullback_high = round(float(sma20 + 0.25 * atr14), 4)
                    # Stop below the watch zone by half an ATR.
                    pullback_stop = round(float(pullback_low - 0.50 * atr14), 4)
                if recent_high_20 is not None and atr14 is not None and atr14 > 0:
                    # Require a small buffer above the prior 20-day high.
                    breakout_trigger = round(float(recent_high_20 + 0.10 * atr14), 4)
                    breakout_stop = round(float(breakout_trigger - 1.00 * atr14), 4)

                def size_for_entry(entry_price, stop_price):
                    if entry_price is None or stop_price is None or entry_price <= stop_price:
                        return {"quantity": None, "risk_dollars": None, "risk_per_unit": None}
                    risk_per_unit = entry_price - stop_price
                    qty_by_risk = risk_budget_for_plan / risk_per_unit if risk_per_unit > 0 else 0.0
                    qty_by_cash = cash_for_plan / entry_price if entry_price > 0 else 0.0
                    qty = max(0.0, min(qty_by_risk, qty_by_cash))
                    return {
                        "quantity": round(qty, 6),
                        "risk_dollars": round(qty * risk_per_unit, 2),
                        "risk_per_unit": round(risk_per_unit, 4),
                    }

                pullback_mid = round((pullback_low + pullback_high) / 2, 4) if pullback_low is not None else None
                pullback_sizing = size_for_entry(pullback_mid, pullback_stop)
                breakout_sizing = size_for_entry(breakout_trigger, breakout_stop)

                facts = {
                    "symbol": symbol,
                    "asset_class": str(row["Asset class"]),
                    "price": round(last, 4),
                    "price_date": str(row["Price date"]),
                    "scanner_signal": str(row["Signal"]),
                    "scanner_score": int(row["Score"]),
                    "signal_reason": str(row["Signal reason"]),
                    "daily_trend": str(row["Trend"]),
                    "weekly_trend": str(row["Weekly trend"]),
                    "risk_classification": str(row["Risk level"]),
                    "one_week_return_pct": round(float(row["1W %"]), 3),
                    "one_month_return_pct": round(float(row["1M %"]), 3),
                    "three_month_return_pct": round(float(row["3M %"]), 3),
                    "rsi": round(float(row["RSI"]), 2),
                    "20_day_volatility_pct": round(float(row["20D Vol %"]), 2),
                    "latest_daily_bar_volume_vs_prior_20_bar_average": round(float(row["Latest volume / prior 20D avg"]), 3) if pd.notna(row.get("Latest volume / prior 20D avg")) else None,
                    "spy_1_month_return_pct": round(float(row["SPY 1M %"]), 3) if pd.notna(row.get("SPY 1M %")) else None,
                    "qqq_1_month_return_pct": round(float(row["QQQ 1M %"]), 3) if pd.notna(row.get("QQQ 1M %")) else None,
                    "relative_strength_vs_spy_percentage_points": round(float(row["Relative vs SPY 1M (pp)"]), 3) if pd.notna(row.get("Relative vs SPY 1M (pp)")) else None,
                    "relative_strength_vs_qqq_percentage_points": round(float(row["1M %"] - row["QQQ 1M %"]), 3) if pd.notna(row.get("QQQ 1M %")) else None,
                    "sector_etf_proxy": str(row.get("Sector ETF", "—")),
                    "sector_etf_1_month_return_pct": round(float(row["Sector ETF 1M %"]), 3) if pd.notna(row.get("Sector ETF 1M %")) else None,
                    "relative_strength_vs_sector_percentage_points": round(float(row["Relative vs sector 1M (pp)"]), 3) if pd.notna(row.get("Relative vs sector 1M (pp)")) else None,
                    "20_day_average": round(sma20, 4) if pd.notna(sma20) else None,
                    "20_day_high_from_daily_bars": round(recent_high_20, 4) if recent_high_20 is not None else None,
                    "20_day_low_from_daily_bars": round(recent_low_20, 4) if recent_low_20 is not None else None,
                    "14_day_average_true_range": atr14,
                    "price_vs_20_day_average_pct": round(distance_sma20, 3) if pd.notna(distance_sma20) else None,
                    "calculated_watch_levels": {
                        "pullback_watch_range_low": pullback_low,
                        "pullback_watch_range_high": pullback_high,
                        "pullback_midpoint_for_sizing_only": pullback_mid,
                        "pullback_stop_reference": pullback_stop,
                        "pullback_position_size_units": pullback_sizing["quantity"],
                        "pullback_estimated_loss_at_stop": pullback_sizing["risk_dollars"],
                        "breakout_trigger_price": breakout_trigger,
                        "breakout_stop_reference": breakout_stop,
                        "breakout_position_size_units": breakout_sizing["quantity"],
                        "breakout_estimated_loss_at_stop": breakout_sizing["risk_dollars"],
                        "calculation_note": "Pullback watch zone = 20-day average +/- 0.25 ATR; pullback stop = watch-zone low - 0.50 ATR; breakout trigger = prior 20-day high + 0.10 ATR; breakout stop = trigger - 1.00 ATR. These are mechanical watch references, not validated support/resistance or trade signals."
                    },
                    "reference_entry": round(last, 4),
                    "illustrative_stop": round(stop, 4),
                    "illustrative_1R_target": round(target_1r, 4),
                    "illustrative_2R_target": round(target_2r, 4),
                    "illustrative_3R_target": round(target_3r, 4),
                    "account_equity_estimate": round(account_equity_for_plan, 2),
                    "cash_available": round(cash_for_plan, 2),
                    "hypothetical_risk_budget_1pct": round(risk_budget_for_plan, 2),
                    "risk_and_cash_limited_quantity": round(plan_qty, 6),
                    "estimated_loss_at_reference_stop": round(planned_dollar_risk, 2),
                    "rule_based_entry_assessment": entry_assessment,
                }
                system_prompt = (
                    "You are a cautious market research assistant producing a price-specific paper-trade plan. "
                    "Use only the supplied facts. Do not invent news, fundamentals, quotes, catalysts, or probabilities. "
                    "The supplied prices come from historical daily bars and may be delayed. "
                    "Do not recommend or execute a real trade; this is paper-study analysis only. "
                    "You MUST use the numeric calculated_watch_levels supplied in the facts when available. "
                    "Do not replace those levels with vague phrases. If a level is null, say it is unavailable. "
                    "Return these sections in this exact order: "
                    "1. VERDICT: BUY CANDIDATE / WAIT / AVOID (paper-study only). "
                    "2. WHY. 3. BULLISH EVIDENCE. 4. BEARISH RISKS. "
                    "5. VOLUME AND MARKET CONTEXT: report the supplied latest-bar volume ratio, SPY and QQQ 1-month returns, and relative-strength percentage points versus each benchmark when available. Relative strength is asset 1-month return minus benchmark 1-month return. If the supplied relative-strength value is positive, the asset OUTPERFORMED that benchmark; if negative, it UNDERPERFORMED. Never contradict the supplied arithmetic. Also report sector-relative strength when available. Treat volume as provisional if the latest daily bar may still be forming; elevated volume does not reveal direction by itself. Do not invent missing context. "
                    "6. PRICE LEVELS TO WATCH: state the exact pullback range low and high, its midpoint, "
                    "the exact breakout trigger, and the current daily reference price. Clearly label these as watch levels, "
                    "not instructions to buy. If neither scenario is defensible, say NO VALID ENTRY RIGHT NOW, "
                    "but still report any calculated watch levels as conditional levels to monitor. "
                    "7. ENTRY CONFIRMATION: explain observable daily-bar conditions needed before considering either setup; "
                    "do not claim confirmation has already occurred unless the supplied facts prove it. "
                    "8. STOP / INVALIDATION: give the exact calculated stop for each scenario when available, "
                    "and explain that a daily close below the stop would invalidate that scenario. "
                    "9. PROFIT TARGETS: calculate 1R, 2R, and 3R separately for the pullback and breakout scenarios "
                    "using each scenario's own entry midpoint/trigger and stop. Show the arithmetic levels to 2 decimals. "
                    "10. POSITION SIZE: report the supplied risk-limited and cash-limited quantity for each scenario, "
                    "and estimated dollar loss at the stop. Never exceed the supplied 1% equity risk budget or available cash. "
                    "11. WHAT WOULD INVALIDATE THE IDEA. 12. WHAT DATA IS MISSING. "
                    "The calculated pullback and breakout levels are mechanical formulas based on SMA20, recent 20-day high, "
                    "and ATR; they are watch references only, not confirmed support/resistance. "
                    "If price is extended, reward/risk is poor, or confirmation is absent, the verdict should remain WAIT. "
                    "Never tell the user to chase price. Do not imply a specific entry is currently active just because "
                    "a watch range or trigger has been calculated. Be concise, use exact dollar figures, and explicitly "
                    "distinguish a watch price from a confirmed entry."
                )
                with st.spinner("AI is reviewing the selected asset's supplied market data..."):
                    response = client.chat.completions.create(
                        model="gpt-4.1-mini",
                        temperature=0.2,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": "Independently assess this asset using only these supplied facts:\n" + json.dumps(facts, indent=2)},
                        ],
                    )
                st.session_state["ai_analysis_" + symbol] = response.choices[0].message.content or "The AI returned an empty response."
                st.session_state["ai_analysis_date_" + symbol] = datetime.now().strftime("%Y-%m-%d %H:%M")
            except Exception as exc:
                st.error(f"AI analysis could not be completed: {exc}")
        saved_ai = st.session_state.get("ai_analysis_" + symbol)
        if saved_ai:
            st.markdown(f"**AI second opinion for {symbol}** · {st.session_state.get('ai_analysis_date_' + symbol, '')}")
            st.markdown(saved_ai)
            st.caption("AI output can be wrong or incomplete. It is not a verified signal, financial advice, or an instruction to trade. Review the underlying data yourself.")

    candidates = data[data["Signal"] == "BUY CANDIDATE"]
    st.subheader("Rule-based trade candidates")
    st.caption("These are screening candidates only—not AI recommendations. The rules require a strong daily trend, positive 1-month return, and RSI between 45 and 68. Always review risk before paper trading.")
    if not candidates.empty:
        st.dataframe(candidates[["Symbol", "Asset class", "Score", "Trend", "Weekly trend", "Risk level", "Last", "Price date", "1M %", "RSI", "Signal reason"]].style.format({"Last": "${:,.2f}", "1M %": "{:+.1f}%", "RSI": "{:.1f}"}), use_container_width=True, hide_index=True)
    else:
        st.info("No assets currently meet the candidate rules. That's okay—no trade is better than forcing one.")

    st.subheader("Market-wide entry watchlist")
    st.caption("Ranks scanned assets by proximity to mechanically calculated pullback and breakout watch levels. This is a daily-data watchlist—not an entry signal or a guarantee that a level will hold.")
    watch_rows = []
    for _, item in data.iterrows():
        px = float(item["Last"])
        atr = item.get("ATR14")
        p_low, p_high, p_stop = item.get("Pullback low"), item.get("Pullback high"), item.get("Pullback stop")
        b_trigger, b_stop = item.get("Breakout trigger"), item.get("Breakout stop")
        if pd.isna(atr) or float(atr) <= 0 or pd.isna(p_low) or pd.isna(b_trigger):
            continue
        atr = float(atr)
        # Report the most actionable current state, with separate pullback and breakout columns.
        if px <= float(p_stop):
            pullback_state = "INVALIDATED"
        elif float(p_low) <= px <= float(p_high):
            pullback_state = "IN WATCH RANGE"
        elif px > float(p_high):
            gap = (px - float(p_high)) / atr
            pullback_state = "NEAR PULLBACK" if gap <= 1.0 else "WAITING"
        else:
            pullback_state = "TREND REVIEW"
        if px <= float(b_stop):
            breakout_state = "INVALIDATED"
        elif px >= float(b_trigger):
            breakout_state = "TRIGGER REACHED — VERIFY CLOSE"
        else:
            gap = (float(b_trigger) - px) / atr
            breakout_state = "NEAR BREAKOUT" if gap <= 1.0 else "WAITING"
        distances = []
        if pullback_state == "IN WATCH RANGE":
            distances.append(0.0)
        elif pullback_state == "NEAR PULLBACK":
            distances.append(max(0.0, (px - float(p_high)) / atr))
        if breakout_state == "TRIGGER REACHED — VERIFY CLOSE":
            distances.append(0.0)
        elif breakout_state == "NEAR BREAKOUT":
            distances.append(max(0.0, (float(b_trigger) - px) / atr))
        proximity = min(distances) if distances else 99.0
        if proximity < 99.0 or "INVALIDATED" in (pullback_state, breakout_state):
            watch_rows.append({
                "Symbol": item["Symbol"], "Last": px, "Signal": item["Signal"],
                "Pullback status": pullback_state, "Pullback range": f"${float(p_low):,.2f}–${float(p_high):,.2f}",
                "Breakout status": breakout_state, "Breakout trigger": float(b_trigger),
                "Nearest setup (ATR)": proximity, "Score": int(item["Score"])
            })
    if watch_rows:
        watch_df = pd.DataFrame(watch_rows)

        def watch_priority(item):
            signal = str(item["Signal"]).upper()
            pullback = str(item["Pullback status"]).upper()
            breakout = str(item["Breakout status"]).upper()
            approaching = any(token in (pullback + " " + breakout) for token in (
                "IN WATCH RANGE", "NEAR PULLBACK", "NEAR BREAKOUT", "TRIGGER REACHED"
            ))
            # First: BUY CANDIDATEs already near a valid watch level.
            if signal == "BUY CANDIDATE" and approaching:
                return 0
            # Next: other BUY CANDIDATEs, even if their setup is not close yet.
            if signal == "BUY CANDIDATE":
                return 1
            # Then: WATCH assets that are approaching a price level.
            if signal == "WATCH" and approaching:
                return 2
            # Other WATCH assets, then all remaining/no-setup assets.
            if signal == "WATCH":
                return 3
            return 4

        watch_df["Priority"] = watch_df.apply(watch_priority, axis=1)
        watch_df = watch_df.sort_values(
            ["Priority", "Nearest setup (ATR)", "Score"],
            ascending=[True, True, False]
        )
        watch_df["Priority"] = watch_df["Priority"].map({
            0: "TOP: candidate near entry",
            1: "Candidate — monitor",
            2: "Watch — near price level",
            3: "Watch — monitor",
            4: "Lower priority — review"
        })
        visible_watch_df = watch_df.drop(columns=["Nearest setup (ATR)", "Score"])

        def watch_status_color(value):
            value = str(value).upper()
            if "IN WATCH RANGE" in value or "TRIGGER REACHED" in value:
                return "background-color: #d9f2df; color: #14532d; font-weight: 600"
            if "NEAR PULLBACK" in value or "NEAR BREAKOUT" in value:
                return "background-color: #fff1c2; color: #854d0e; font-weight: 600"
            if "INVALIDATED" in value:
                return "background-color: #f8d7da; color: #842029; font-weight: 600"
            if "TREND REVIEW" in value:
                return "background-color: #e5e7eb; color: #374151"
            return "color: inherit"

        st.caption("Sorted by priority: BUY CANDIDATEs near an entry level first, then other BUY CANDIDATEs, then WATCH assets, and finally lower-priority/no-setup assets. Within each group, the closest watch level appears first.")
        styled_watch_df = (
            visible_watch_df.style
            .format({"Last": "${:,.2f}", "Breakout trigger": "${:,.2f}"})
            .map(watch_status_color, subset=["Pullback status", "Breakout status"])
        )
        watch_selection = st.dataframe(
            styled_watch_df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            key="market_watchlist_table"
        )
        watch_selected_rows = (
            watch_selection.selection.rows
            if watch_selection and hasattr(watch_selection, "selection")
            else []
        )
        if watch_selected_rows:
            chosen_symbol = str(visible_watch_df.iloc[watch_selected_rows[0]]["Symbol"])
            last_watch_choice = st.session_state.get("last_watchlist_selection")
            if chosen_symbol in data["Symbol"].tolist() and chosen_symbol != last_watch_choice:
                st.session_state["last_watchlist_selection"] = chosen_symbol
                st.session_state["inspected_symbol"] = chosen_symbol
                st.session_state["watchlist_override"] = True
                st.rerun()
        st.caption("Select a row to load that asset into the individual analysis and AI Trade Analyst above. Only assets inside a watch range, within one ATR of a watch level, or with an invalidated scenario are shown. Refresh the market scan to update.")

        st.markdown("### AI market-wide shortlist")
        st.caption("Ask AI to compare up to 10 prioritized watchlist candidates side by side using the scanner's daily-bar metrics, volume, SPY/QQQ context, and sector-relative strength. This is a research ranking—not a buy signal.")
        ai_api_key_market = st.secrets.get("OPENAI_API_KEY", "")
        if not ai_api_key_market:
            st.info("Add OPENAI_API_KEY in Streamlit Secrets to use the AI market-wide shortlist.")
        else:
            if st.button("Analyze and rank top 10 candidates", type="primary", key="ai_rank_top10"):
                try:
                    from openai import OpenAI
                    ranking_client = OpenAI(api_key=str(ai_api_key_market))
                    shortlist_symbols = watch_df["Symbol"].head(10).tolist()
                    shortlist = []
                    for candidate_symbol in shortlist_symbols:
                        candidate_rows = data[data["Symbol"] == candidate_symbol]
                        if candidate_rows.empty:
                            continue
                        candidate = candidate_rows.iloc[0]
                        shortlist.append({
                            "symbol": candidate_symbol,
                            "asset_class": str(candidate.get("Asset class", "")),
                            "last_daily_price": round(float(candidate["Last"]), 4),
                            "price_date": str(candidate.get("Price date", "")),
                            "scanner_signal": str(candidate.get("Signal", "")),
                            "scanner_score": int(candidate.get("Score", 0)),
                            "signal_reason": str(candidate.get("Signal reason", "")),
                            "daily_trend": str(candidate.get("Trend", "")),
                            "weekly_trend": str(candidate.get("Weekly trend", "")),
                            "risk_classification": str(candidate.get("Risk level", "")),
                            "one_week_return_pct": round(float(candidate["1W %"]), 2) if pd.notna(candidate.get("1W %")) else None,
                            "one_month_return_pct": round(float(candidate["1M %"]), 2) if pd.notna(candidate.get("1M %")) else None,
                            "three_month_return_pct": round(float(candidate["3M %"]), 2) if pd.notna(candidate.get("3M %")) else None,
                            "rsi": round(float(candidate["RSI"]), 1) if pd.notna(candidate.get("RSI")) else None,
                            "annualized_20_day_volatility_pct": round(float(candidate["20D Vol %"]), 1) if pd.notna(candidate.get("20D Vol %")) else None,
                            "latest_daily_volume_vs_prior_20_day_average": round(float(candidate["Latest volume / prior 20D avg"]), 2) if pd.notna(candidate.get("Latest volume / prior 20D avg")) else None,
                            "spy_1_month_return_pct": round(float(candidate["SPY 1M %"]), 2) if pd.notna(candidate.get("SPY 1M %")) else None,
                            "qqq_1_month_return_pct": round(float(candidate["QQQ 1M %"]), 2) if pd.notna(candidate.get("QQQ 1M %")) else None,
                            "relative_vs_spy_percentage_points": round(float(candidate["Relative vs SPY 1M (pp)"]), 2) if pd.notna(candidate.get("Relative vs SPY 1M (pp)")) else None,
                            "relative_vs_qqq_percentage_points": round(float(candidate["1M %"] - candidate["QQQ 1M %"]), 2) if pd.notna(candidate.get("QQQ 1M %")) else None,
                            "sector_etf_proxy": str(candidate.get("Sector ETF", "—")),
                            "relative_vs_sector_percentage_points": round(float(candidate["Relative vs sector 1M (pp)"]), 2) if pd.notna(candidate.get("Relative vs sector 1M (pp)")) else None,
                            "pullback_status": str(watch_df[watch_df["Symbol"] == candidate_symbol]["Pullback status"].iloc[0]),
                            "breakout_status": str(watch_df[watch_df["Symbol"] == candidate_symbol]["Breakout status"].iloc[0]),
                            "pullback_watch_range": str(watch_df[watch_df["Symbol"] == candidate_symbol]["Pullback range"].iloc[0]),
                            "breakout_trigger": round(float(candidate["Breakout trigger"]), 2) if pd.notna(candidate.get("Breakout trigger")) else None
                        })
                    ranking_prompt = (
                        "You are a cautious market research analyst. Rank these candidates from strongest to weakest for further paper-trading research, not for immediate buying. "
                        "Use only supplied data. Do not invent news, catalysts, probabilities, live quotes, fundamentals, or technical indicators. "
                        "Treat daily bars as potentially delayed and volume as provisional if the latest bar is still forming. "
                        "Do not rank solely by scanner score or proximity to a watch level. Weigh daily and weekly trend agreement, momentum, RSI, volatility, volume participation, "
                        "relative strength versus SPY and QQQ, sector-relative strength, and whether the pullback/breakout setup is waiting, near, in range, or invalidated. "
                        "Relative strength is asset 1-month return minus benchmark 1-month return: positive means OUTPERFORMANCE and negative means UNDERPERFORMANCE. "
                        "Check that interpretation arithmetically and never say an asset underperformed a benchmark when the supplied relative value is positive. "
                        "A watch range is not a confirmed entry. A high ranking is not a BUY instruction. "
                        "Return: (1) ranked table with rank, symbol, setup quality (strong/moderate/weak), and concise reason; "
                        "(2) top three worth individual review and why; (3) avoid/deprioritize list and reasons; "
                        "(4) missing evidence/limitations; (5) clear statement that no trade is confirmed from these daily-bar facts alone. "
                        "Keep explanations concise and distinguish facts from interpretation.\n\n"
                        "Candidate data:\n" + json.dumps(shortlist, default=str)
                    )
                    with st.spinner("AI is comparing the prioritized candidates..."):
                        ranking_response = ranking_client.chat.completions.create(
                            model="gpt-4.1-mini",
                            temperature=0.2,
                            messages=[
                                {"role": "system", "content": "You compare market candidates conservatively. Never issue real-trade instructions."},
                                {"role": "user", "content": ranking_prompt}
                            ]
                        )
                    st.session_state["market_ai_ranking"] = ranking_response.choices[0].message.content
                    st.session_state["market_ai_ranking_symbols"] = shortlist_symbols
                except Exception as e:
                    st.error(f"AI market-wide ranking failed: {e}")
            if st.session_state.get("market_ai_ranking"):
                st.markdown("#### AI shortlist results")
                st.caption("Candidates included: " + ", ".join(st.session_state.get("market_ai_ranking_symbols", [])))
                st.markdown(st.session_state["market_ai_ranking"])
    else:
        st.info("No scanned assets are currently near their calculated pullback or breakout watch levels. That's okay—no need to force a trade.")

with paper_tab:
    st.subheader("Virtual account")
    st.info("Simulation only. Scanner and trade-entry references use Yahoo Finance DAILY bars. Open positions are separately checked against frequently refreshed one-minute Yahoo Finance bars while this dashboard session remains open. Neither feed is a guaranteed real-time executable quote. Your paper account is saved in Supabase.")
    prices = dict(zip(data["Symbol"], data["Last"]))
    @st.fragment(run_every="60s")
    def render_intraday_exit_monitor():
        st.markdown("#### Intraday exit monitor")
        st.caption(
            "Checks one-minute Yahoo Finance bars about once per minute while this dashboard session is open. "
            "It stops checking when the dashboard is closed. Quotes may be delayed or missing; this is paper simulation only."
        )
        held = dict(st.session_state.paper_positions)
        if not held:
            st.info("No open positions to monitor.")
            return

        try:
            bars_by_symbol = load_intraday_bars(tuple(sorted(held.keys())))
        except Exception as exc:
            st.warning(f"Intraday data could not be refreshed. No automatic exit was recorded. Details: {exc}")
            return

        now_utc = pd.Timestamp.now(tz="UTC")
        original_cash = float(st.session_state.paper_cash)
        original_realized = float(st.session_state.realized_pnl)
        original_positions = json.loads(json.dumps(st.session_state.paper_positions))
        original_journal = json.loads(json.dumps(st.session_state.paper_journal))
        quote_rows = []
        stale_symbols = []
        triggered = []

        for sym, pos in held.items():
            frame = bars_by_symbol.get(sym)
            if frame is None or frame.empty:
                quote_rows.append({
                    "Symbol": sym, "Intraday price": None, "Bar low": None, "Bar high": None,
                    "Stop": pos.get("stop_price"), "2R target": pos.get("target_price"), "Last bar time": "Unavailable",
                    "Data age": "—", "Monitor": "NO DATA — no auto-exit"
                })
                stale_symbols.append(sym)
                continue

            row = frame.dropna(subset=["Close"]).iloc[-1]
            bar_time = pd.Timestamp(frame.dropna(subset=["Close"]).index[-1])
            if bar_time.tzinfo is None:
                bar_time = bar_time.tz_localize("America/New_York")
            bar_utc = bar_time.tz_convert("UTC")
            age_seconds = max(0.0, (now_utc - bar_utc).total_seconds())
            fresh = age_seconds <= 300

            close_px = float(row["Close"])
            open_px = float(row["Open"]) if "Open" in row and pd.notna(row["Open"]) else close_px
            low_px = float(row["Low"]) if "Low" in row and pd.notna(row["Low"]) else close_px
            high_px = float(row["High"]) if "High" in row and pd.notna(row["High"]) else close_px
            stop_level = float(pos["stop_price"]) if pos.get("stop_price") is not None else None
            target_level = float(pos["target_price"]) if pos.get("target_price") is not None else None
            local_bar_time = bar_time.tz_convert(datetime.now().astimezone().tzinfo)
            monitor_status = "MONITORING" if fresh else "STALE — no auto-exit"

            # Never trigger from stale bars. If both stop and target are touched
            # in the same one-minute candle, assume the stop happened first.
            exit_reason = None
            trigger_price = None
            estimated_fill = None
            gap_note = ""
            if fresh:
                if stop_level is not None and low_px <= stop_level:
                    exit_reason = "STOP (intraday)"
                    trigger_price = stop_level
                    estimated_fill = open_px if open_px < stop_level else stop_level
                    if open_px < stop_level:
                        gap_note = "Opened below stop; estimated fill uses bar open (gap-through)."
                    else:
                        gap_note = "Estimated fill at stop; actual execution can differ."
                elif target_level is not None and high_px >= target_level:
                    exit_reason = "TARGET (intraday)"
                    trigger_price = target_level
                    estimated_fill = open_px if open_px > target_level else target_level
                    gap_note = "Target touched; estimated fill uses target/open, not a broker fill."

            quote_rows.append({
                "Symbol": sym, "Intraday price": close_px, "Bar low": low_px,
                "Bar high": high_px, "Stop": stop_level, "2R target": target_level,
                "Last bar time": local_bar_time.strftime("%b %d %I:%M:%S %p %Z"),
                "Data age": f"{age_seconds / 60:.1f} min",
                "Monitor": monitor_status
            })
            if not fresh:
                stale_symbols.append(sym)

            if exit_reason:
                qty = float(pos.get("quantity", 0.0))
                avg = float(pos.get("average_price", 0.0))
                proceeds = qty * float(estimated_fill)
                pnl = (float(estimated_fill) - avg) * qty
                now_local = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
                st.session_state.paper_cash += proceeds
                st.session_state.realized_pnl += pnl
                st.session_state.paper_journal.insert(0, {
                    "Time": now_local,
                    "Action": "AUTO " + exit_reason,
                    "Symbol": sym,
                    "Quantity": qty,
                    "Trigger price": float(trigger_price),
                    "Observed execution price": float(estimated_fill),
                    "Last bar close": close_px,
                    "Quote bar time": local_bar_time.isoformat(),
                    "Data source": "Yahoo Finance 1-minute OHLC",
                    "Gap / fill note": gap_note,
                    "Value": proceeds,
                    "Realized P/L": pnl
                })
                st.session_state.paper_journal = st.session_state.paper_journal[:500]
                st.session_state.paper_positions.pop(sym, None)
                triggered.append(
                    f"{sym} {exit_reason}: trigger ${trigger_price:,.2f}, estimated fill ${estimated_fill:,.2f}, P/L ${pnl:+,.2f}"
                )

        if triggered:
            try:
                save_account()
            except Exception as exc:
                # Roll back in-memory changes if persistence fails so the next
                # rerun cannot silently treat an unsaved exit as completed.
                st.session_state.paper_cash = original_cash
                st.session_state.realized_pnl = original_realized
                st.session_state.paper_positions = original_positions
                st.session_state.paper_journal = original_journal
                st.error(f"An intraday exit was detected, but saving the paper-account update failed. The simulated account was restored and no exit was recorded: {exc}")
                return
            st.session_state.intraday_exit_notice = " · ".join(triggered)
            st.rerun()

        notice = st.session_state.pop("intraday_exit_notice", None)
        if notice:
            st.success("Simulated intraday exit recorded: " + notice)

        if quote_rows:
            live_df = pd.DataFrame(quote_rows)
            st.dataframe(
                live_df.style.format({
                    "Intraday price": "${:,.4f}", "Bar low": "${:,.4f}",
                    "Bar high": "${:,.4f}", "Stop": "${:,.4f}",
                    "2R target": "${:,.4f}"
                }, na_rep="—"),
                use_container_width=True, hide_index=True
            )
        if stale_symbols:
            st.warning(
                "No automatic exit was evaluated for stale or unavailable intraday data: "
                + ", ".join(stale_symbols)
                + ". A stale quote is never treated as a fresh trigger."
            )
        st.caption(
            "Simulation method: a fresh one-minute candle touching the stop/target can trigger a paper exit. "
            "For a stop gap, the estimated fill uses the candle open when it is below the stop; otherwise it uses the stop. "
            "One-minute OHLC cannot establish the exact tick sequence or a real fill."
        )

    render_intraday_exit_monitor()
    trade_notice = st.session_state.pop("paper_trade_notice", None)
    if trade_notice:
        st.success(trade_notice)
    positions = st.session_state.paper_positions
    market_value = sum(pos["quantity"] * prices.get(sym, pos["average_price"]) for sym, pos in positions.items())
    equity = st.session_state.paper_cash + market_value
    a, b, c, d = st.columns(4)
    a.metric("Cash available", f'${st.session_state.paper_cash:,.2f}')
    b.metric("Position value", f"${market_value:,.2f}")
    c.metric("Account value", f"${equity:,.2f}", f"${equity-1000:+,.2f} vs. start")
    d.metric("Realized P/L", f'${st.session_state.realized_pnl:+,.2f}')
    st.markdown("#### Portfolio risk manager")
    st.caption("Existing positions are kept intact. A separate 1% risk allowance is available for NEW positions opened under this version. The dashboard shows both buckets and their combined estimated stop risk; this policy can temporarily put total account risk above 1%.")
    open_risk_rows = []
    unknown_risk_positions = []
    existing_position_risk = 0.0
    new_position_risk = 0.0
    for open_sym, open_pos in st.session_state.paper_positions.items():
        open_qty = float(open_pos.get("quantity", 0.0))
        open_entry = float(open_pos.get("average_price", 0.0))
        open_stop = open_pos.get("stop_price")
        bucket = open_pos.get("risk_bucket", "existing")
        bucket_label = "New allocation" if bucket == "new" else "Existing position"
        if open_stop is None or open_entry <= 0 or float(open_stop) >= open_entry:
            unknown_risk_positions.append(open_sym)
            open_risk_rows.append({"Symbol": open_sym, "Risk category": bucket_label, "Quantity": open_qty, "Entry": open_entry, "Stop": open_stop, "Estimated risk to stop": None, "Status": "Risk unavailable — review"})
        else:
            one_position_risk = max(0.0, open_entry - float(open_stop)) * open_qty
            if bucket == "new":
                new_position_risk += one_position_risk
            else:
                existing_position_risk += one_position_risk
            open_risk_rows.append({"Symbol": open_sym, "Risk category": bucket_label, "Quantity": open_qty, "Entry": open_entry, "Stop": float(open_stop), "Estimated risk to stop": one_position_risk, "Status": "Estimated"})
    total_open_risk = existing_position_risk + new_position_risk
    new_trade_risk_cap = max(0.0, equity * 0.01)
    remaining_new_risk = max(0.0, new_trade_risk_cap - new_position_risk)
    pm1, pm2, pm3 = st.columns(3)
    pm1.metric("Existing-position risk", f"${existing_position_risk:,.2f}")
    pm2.metric("New-position risk used", f"${new_position_risk:,.2f}")
    pm3.metric("New-position risk available", f"${remaining_new_risk:,.2f}")
    pm4, pm5 = st.columns(2)
    pm4.metric("New-position risk allowance (1%)", f"${new_trade_risk_cap:,.2f}")
    pm5.metric("Combined estimated open risk", f"${total_open_risk:,.2f}")
    if open_risk_rows:
        st.dataframe(pd.DataFrame(open_risk_rows), use_container_width=True, hide_index=True)
    else:
        st.caption("No open positions. Existing and new-position risk are both zero.")
    if unknown_risk_positions:
        st.error("New simulated buys are blocked until stop risk is reviewed for these open positions: " + ", ".join(unknown_risk_positions))
    st.info("Policy: the existing AAPL/MSFT positions are classified as existing and are not changed. New positions share one separate 1% risk allowance. Combined risk is always displayed so the distinction is transparent.")
    st.markdown("#### Risk planner and simulated trade")
    candidate_symbols = data.loc[data["Signal"] == "BUY CANDIDATE", "Symbol"].tolist()
    default_symbol = candidate_symbols[0] if candidate_symbols else data.iloc[0]["Symbol"]
    default_index = data["Symbol"].tolist().index(default_symbol)
    st.caption("The asset selector starts with the highest-ranked scanner candidate when one exists. A buy plan uses the illustrative stop reference and a 2-to-1 reward/risk target. New positions are entered using the displayed daily reference; open-position exits are monitored separately using one-minute bars while the dashboard session is open.")
    action = st.selectbox("Action", ["Buy", "Sell"])
    trade_symbol = st.selectbox("Asset", data["Symbol"].tolist(), index=default_index)
    selected_signal = data.loc[data["Symbol"] == trade_symbol].iloc[0]
    estimated_price = float(prices[trade_symbol])
    price_date = str(selected_signal["Price date"])
    stop_reference = float(selected_signal["Illustrative risk level"])
    risk_pct = st.select_slider("Maximum planned account risk per buy", options=[0.5, 1.0, 1.5, 2.0], value=1.0, format_func=lambda x: f"{x:.1f}%")
    selected_risk_cap = max(0.0, equity * risk_pct / 100.0)
    # Existing legacy positions are displayed separately and do not consume the
    # new-position allowance. All positions opened under this policy share one
    # 1% aggregate allowance.
    new_position_cap = min(selected_risk_cap, new_trade_risk_cap)
    risk_budget = max(0.0, new_position_cap - new_position_risk)
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
    r4.metric("New-position risk available", f"${risk_budget:,.2f}")
    r5.metric("Estimated position size", f"{suggested_qty:.3f}")
    if risk_per_unit > 0:
        st.caption(f"Estimated risk per unit: ${risk_per_unit:,.2f} · Planned new-position risk: ${planned_loss:,.2f} · Existing-position risk: ${existing_position_risk:,.2f} · Already-used new-position risk: ${new_position_risk:,.2f} · Cash available: ${st.session_state.paper_cash:,.2f}")
        if risk_budget <= 0:
            st.warning("No remaining new-position risk allowance. A new simulated buy will be blocked until new-position risk falls or the allowance is reviewed.")
    else:
        st.error("The calculated stop reference is not below the current price. The risk planner cannot size a long buy for this asset.")
    st.warning("Important: intraday exits are paper simulations based on Yahoo Finance one-minute bars, not broker stop orders. Monitoring runs about once per minute only while this dashboard session is open. If the app is closed, data is delayed/missing, or price gaps through a stop, losses can exceed the planned amount. Estimated fills are not guaranteed.")
    with st.form("paper_trade_form"):
        default_qty = max(0.001, round(suggested_qty, 3)) if action == "Buy" else max(0.001, round(min(st.session_state.paper_positions.get(trade_symbol, {}).get("quantity", 0.001), 1.0), 3))
        trade_qty = st.number_input("Quantity (fractional shares/units allowed)", min_value=0.001, value=float(default_qty), step=0.1, format="%.3f")
        acknowledge_price = st.checkbox("I understand this simulated entry uses a daily reference price, not a live executable quote.")
        preview_clicked = st.form_submit_button("Preview quantity")
        confirmed = st.form_submit_button(f"Approve simulated {action.lower()}", type="primary")
    preview_order_value = estimated_price * float(trade_qty)
    preview_risk = max(0.0, risk_per_unit) * float(trade_qty) if action == "Buy" else 0.0
    if preview_clicked:
        st.info(
            f"PREVIEW ONLY — {trade_qty:.3f} {trade_symbol} · "
            f"Estimated order value: ${preview_order_value:,.2f} · "
            f"Estimated added stop risk: ${preview_risk:,.2f} · "
            f"Daily market-data date: {price_date}. "
            "Nothing has been bought or sold."
        )
        if action == "Buy" and trade_qty > suggested_qty + 1e-6:
            st.error(f"Preview exceeds the current risk-and-cash limit of {suggested_qty:.3f} units. Reduce the quantity.")
        elif action == "Buy" and preview_order_value > st.session_state.paper_cash + 1e-8:
            st.error("Preview exceeds available virtual cash.")
        elif action == "Sell" and trade_qty > st.session_state.paper_positions.get(trade_symbol, {}).get("quantity", 0.0) + 1e-8:
            st.error("Preview exceeds the quantity currently held.")
        else:
            st.success("Preview is within the displayed quantity, risk, and cash limits. This is not an executed paper trade.")
    if confirmed and not acknowledge_price:
        st.error("Please acknowledge that this simulated entry uses a daily reference price before recording the trade.")
    if confirmed and acknowledge_price:
        price = float(prices[trade_symbol])
        cost = price * float(trade_qty)
        current = st.session_state.paper_positions.get(trade_symbol, {"quantity": 0.0, "average_price": 0.0})
        if action == "Buy":
            if unknown_risk_positions:
                st.error("Buy blocked: at least one existing position has missing or invalid stop information. Review portfolio risk first.")
            elif risk_budget <= 0:
                st.error("Buy blocked: the separate new-position risk allowance is already fully used.")
            elif risk_per_unit <= 0:
                st.error("Buy blocked: no valid illustrative stop reference is available for this asset.")
            elif trade_symbol in st.session_state.paper_positions:
                st.error("Adding to an existing position is disabled in this prototype. Close the existing position first.")
            elif float(trade_qty) > suggested_qty + 1e-6:
                st.error(f"Buy blocked: quantity exceeds the portfolio-risk-and-cash limit of {suggested_qty:.3f}. Reduce quantity or choose another asset.")
            elif new_position_risk + (float(trade_qty) * risk_per_unit) > new_position_cap + 1e-6:
                st.error("Buy blocked: this order would exceed the separate new-position risk allowance.")
            elif cost > st.session_state.paper_cash + 1e-8:
                st.error("Not enough virtual cash for this purchase.")
            else:
                st.session_state.paper_positions[trade_symbol] = {
                    "quantity": float(trade_qty),
                    "average_price": price,
                    "stop_price": float(stop_reference),
                    "target_price": float(target_reference),
                    "risk_bucket": "new"
                }
                st.session_state.paper_cash -= cost
                st.session_state.paper_journal.insert(0, {"Time": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z"), "Action": "BUY", "Symbol": trade_symbol, "Quantity": float(trade_qty), "Reference price": price, "Value": cost, "Realized P/L": 0.0})
                st.session_state.paper_trade_notice = (
                    f"Simulated buy recorded: {trade_qty:g} {trade_symbol} at ${price:,.4f}. "
                    f"Stop rule ${stop_reference:,.2f}; 2R target ${target_reference:,.2f}. Saved to your account."
                )
                save_account()
                st.rerun()
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
                    st.session_state.paper_positions[trade_symbol] = {**current, "quantity": remaining}
                st.session_state.paper_cash += cost
                st.session_state.realized_pnl += pnl
                st.session_state.paper_journal.insert(0, {"Time": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z"), "Action": "SELL", "Symbol": trade_symbol, "Quantity": float(trade_qty), "Reference price": price, "Value": cost, "Realized P/L": pnl})
                st.session_state.paper_trade_notice = (
                    f"Simulated sale recorded. Realized P/L: ${pnl:+,.2f} before costs. Saved to your account."
                )
                save_account()
                st.rerun()
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
        save_account()
        st.rerun()


# Record/update today's snapshot after any simulated trade or daily-close exit
# has been processed. The database unique key prevents duplicate daily rows.
snapshot_error = None
snapshot_history = []
try:
    snapshot_prices = dict(zip(data["Symbol"], data["Last"]))
    save_daily_snapshot(snapshot_prices)
    snapshot_history = load_snapshot_history()
except Exception as exc:
    snapshot_error = exc

with analytics_tab:
    st.subheader("Paper-trading performance")
    st.caption("Metrics are calculated from the saved paper-account journal and the latest available DAILY reference prices. They are simulation metrics, not verified live-trading results.")

    positions_now = st.session_state.paper_positions
    prices_now = dict(zip(data["Symbol"], data["Last"]))
    open_market_value = sum(
        float(pos.get("quantity", 0.0)) * float(prices_now.get(sym, pos.get("average_price", 0.0)))
        for sym, pos in positions_now.items()
    )
    open_unrealized = sum(
        (float(prices_now.get(sym, pos.get("average_price", 0.0))) - float(pos.get("average_price", 0.0)))
        * float(pos.get("quantity", 0.0))
        for sym, pos in positions_now.items()
    )
    current_equity = float(st.session_state.paper_cash) + open_market_value
    total_pnl = current_equity - 1000.0
    total_return = safe_pct(total_pnl, 1000.0)

    closed = build_closed_trade_metrics(st.session_state.paper_journal)
    closed_pnls = [row["Realized P/L"] for row in closed]
    wins = [x for x in closed_pnls if x > 0]
    losses = [x for x in closed_pnls if x < 0]
    gross_profit = sum(wins)
    gross_loss_abs = abs(sum(losses))
    profit_factor = gross_profit / gross_loss_abs if gross_loss_abs > 0 else None
    win_rate = safe_pct(len(wins), len(closed_pnls))
    avg_win = sum(wins) / len(wins) if wins else 0.0
    avg_loss = sum(losses) / len(losses) if losses else 0.0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Account value", f"${current_equity:,.2f}", f"{total_pnl:+,.2f} vs. $1,000")
    m2.metric("Total return", f"{total_return:+.2f}%")
    m3.metric("Realized P/L", f"${float(st.session_state.realized_pnl):+,.2f}")
    m4.metric("Open unrealized P/L", f"${open_unrealized:+,.2f}")

    st.markdown("#### Closed-trade statistics")
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Closed trade records", len(closed))
    s2.metric("Win rate", f"{win_rate:.1f}%" if closed else "—")
    s3.metric("Average winning record", f"${avg_win:+,.2f}" if wins else "—")
    s4.metric("Average losing record", f"${avg_loss:+,.2f}" if losses else "—")

    if profit_factor is None:
        st.metric("Profit factor", "—", help="Not meaningful until there is at least one losing closed-trade record.")
    else:
        st.metric("Profit factor", f"{profit_factor:.2f}")

    if closed:
        st.markdown("#### Closed-trade journal")
        closed_df = pd.DataFrame(closed)
        st.dataframe(
            closed_df.style.format({
                "Quantity": "{:.4f}",
                "Realized P/L": "${:+,.2f}",
            }),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No positions have been closed yet. Win rate, average win/loss, and profit factor will become meaningful after completed simulated trades.")

    st.markdown("#### Current portfolio allocation")
    allocation_rows = []
    if current_equity > 0:
        for sym, pos in positions_now.items():
            mark = float(prices_now.get(sym, pos.get("average_price", 0.0)))
            value = float(pos.get("quantity", 0.0)) * mark
            allocation_rows.append({
                "Symbol": sym,
                "Market value": value,
                "Portfolio weight": value / current_equity * 100.0,
                "Unrealized P/L": (mark - float(pos.get("average_price", 0.0))) * float(pos.get("quantity", 0.0)),
            })
    if allocation_rows:
        allocation_df = pd.DataFrame(allocation_rows).sort_values("Market value", ascending=False)
        st.dataframe(
            allocation_df.style.format({
                "Market value": "${:,.2f}",
                "Portfolio weight": "{:.1f}%",
                "Unrealized P/L": "${:+,.2f}",
            }),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.caption("No open positions.")

    st.markdown("#### Account value history")
    if snapshot_error is not None:
        st.warning("Daily history is not available yet. Confirm that the paper_account_snapshots table has been created in Supabase, then refresh the dashboard.")
        st.caption(f"Technical detail: {snapshot_error}")
    elif snapshot_history:
        history_df = pd.DataFrame(snapshot_history)
        history_df["snapshot_date"] = pd.to_datetime(history_df["snapshot_date"])
        history_df = history_df.sort_values("snapshot_date").drop_duplicates("snapshot_date", keep="last")
        history_df = history_df.set_index("snapshot_date")
        st.line_chart(history_df["equity"].rename("Account value ($)"), use_container_width=True)
        if len(history_df) >= 2:
            running_peak = history_df["equity"].cummax()
            drawdown_pct = (history_df["equity"] / running_peak - 1.0) * 100.0
            max_drawdown = float(drawdown_pct.min())
            h1, h2 = st.columns(2)
            h1.metric("Maximum drawdown", f"{max_drawdown:.2f}%")
            h2.metric("Recorded days", len(history_df))
            st.caption("Drawdown is calculated from recorded daily snapshots only. It will become more informative as more dates accumulate.")
        else:
            st.info("Your first daily snapshot has been saved. Maximum drawdown will appear after at least two different dates have been recorded.")
        st.dataframe(history_df.reset_index().rename(columns={"snapshot_date": "Date", "equity": "Account value", "cash": "Cash", "position_value": "Position value", "realized_pnl": "Realized P/L", "unrealized_pnl": "Open P/L"}).style.format({"Account value": "${:,.2f}", "Cash": "${:,.2f}", "Position value": "${:,.2f}", "Realized P/L": "${:+,.2f}", "Open P/L": "${:+,.2f}"}), use_container_width=True, hide_index=True)
    else:
        st.info("No daily snapshots have been recorded yet. Refresh the dashboard to create the first one.")

    st.markdown("#### What these numbers do—and don't—tell us")
    st.write(
        "- Total return compares current account equity with the original $1,000 starting balance.\n"
        "- Win rate and average win/loss use recorded SELL and automatic-exit journal entries. Partial exits count as separate closed-trade records in this prototype.\n"
        "- Profit factor compares gross realized gains with gross realized losses. It is unavailable until there is at least one losing closed-trade record.\n"
        "- Maximum drawdown is calculated from the daily snapshots recorded by this app. It is not a full intraday drawdown measure, and it becomes more useful as more dates accumulate.\n"
        "- These results exclude commissions, spreads, slippage, taxes and any execution differences."
    )

st.caption("Version 3.14 limitations: scanner uses daily Yahoo Finance bars; weekly trend is derived from those same daily bars. The optional AI analyst only reviews supplied indicators and reference levels; it does not have live intraday data, news, filings, historical backtesting, broker access, or real order execution. The cloud worker saves rules-based scans with a bounded sector-aware ranking overlay and an AI second-stage research review; the dashboard displays those reports and does not place trades. Snapshots update when the dashboard runs. Simulated trades exclude commissions, spread, slippage, and taxes. The expanded watchlist is a curated starter universe, not every listed asset or token.")
