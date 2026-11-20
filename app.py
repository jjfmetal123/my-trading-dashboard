import streamlit as st
import pandas as pd
import numpy as np
import json
import yfinance as yf
from dashboard_validation_diagnostics import build_edge_diagnostics, build_volatility_transition_study, deoverlap_events, replay_sequence_risk_metrics
from datetime import datetime, date

st.set_page_config(page_title="AI Market Intelligence", page_icon="📈", layout="wide")

st.markdown("""<style>

# MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header[data-testid="stHeader"] {background: rgba(10, 17, 30, .82);}
.stApp {
  background:
    radial-gradient(ellipse at 12% 0%, rgba(30, 105, 125, .13), transparent 34%),
    linear-gradient(180deg, #0b1220 0%, #0e1726 100%);
  color: #e8eef7;
}
[data-testid="stAppViewContainer"] .main .block-container {
  max-width: 1680px;
  padding: 1.35rem clamp(1rem, 2.6vw, 2.5rem) 3rem;
}
h1, h2, h3, h4 { letter-spacing: -.025em; color: #f3f7fc; }
h1 { font-size: clamp(1.75rem, 3vw, 2.35rem) !important; font-weight: 750 !important; }
h2 { font-size: clamp(1.35rem, 2.2vw, 1.75rem) !important; }
h3 { font-size: 1.18rem !important; }
p, li, label, [data-testid="stCaptionContainer"] { line-height: 1.55; }
[data-testid="stCaptionContainer"] { color: #9eafc4; }
/* Keep Streamlit alerts readable in dark mode, including nested severity wrappers. */
[data-testid="stAlert"],
[data-testid="stAlert"] > div,
[data-testid="stAlert"] [data-testid="stMarkdownContainer"] {
  background: #1b2b40 !important;
  color: #f3f7fc !important;
  border: 1px solid #60758d !important;
  border-radius: 12px !important;
  padding: .8rem 1rem;
}
[data-testid="stAlert"] *,
[data-testid="stAlert"] p,
[data-testid="stAlert"] span,
[data-testid="stAlert"] li,
[data-testid="stAlert"] [data-testid="stMarkdownContainer"] * {
  color: #f3f7fc !important;
  opacity: 1 !important;
  -webkit-text-fill-color: #f3f7fc !important;
}
[data-testid="stAlert"] svg { opacity: 1 !important; }
[data-testid="stAlert"] [data-testid="stAlertContent"],
[data-testid="stAlert"] [data-testid="stAlertContent"] > div {
  background: transparent !important;
}
[data-testid="stMetric"] {
  background: linear-gradient(145deg, rgba(24, 39, 58, .92), rgba(16, 28, 44, .88));
  border: 1px solid rgba(148, 163, 184, .17);
  border-radius: 14px; padding: 14px 16px; min-height: 104px;
}
[data-testid="stMetricLabel"] { color: #9fb1c7; font-size: .82rem; }
[data-testid="stMetricValue"] { color: #f3f7fc; font-weight: 720; }
[data-testid="stMetricDelta"] { font-size: .82rem; }
[data-testid="stTabs"] [data-baseweb="tab-list"] {
  gap: 6px; border-bottom: 1px solid rgba(148, 163, 184, .18);
  padding: 5px 2px 10px; background: transparent;
}
[data-testid="stTabs"] button[data-baseweb="tab"] {
  background: rgba(23, 37, 55, .72); border: 1px solid rgba(148, 163, 184, .14);
  border-radius: 10px; color: #b7c5d7; padding: 9px 14px; min-height: 42px;
  font-weight: 600; transition: background .15s ease, border-color .15s ease;
}
[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {
  background: rgba(18, 119, 132, .22); color: #e7fbff;
  border-color: rgba(45, 212, 191, .48);
}
[data-testid="stTabs"] [data-baseweb="tab-highlight"] { background: #2dd4bf; height: 2px; }
[data-testid="stVerticalBlockBorderWrapper"] {
  border-color: rgba(148, 163, 184, .18) !important; border-radius: 14px;
}
[data-testid="stDataFrame"], [data-testid="stTable"] {
  border: 1px solid rgba(148, 163, 184, .16); border-radius: 12px; overflow: hidden;
}
[data-testid="stDataFrame"] > div { border-radius: 12px; }
.stButton > button, [data-testid="stFormSubmitButton"] > button {
  border-radius: 10px; min-height: 42px; font-weight: 650;
  border: 1px solid rgba(148, 163, 184, .24); transition: all .15s ease;
}
.stButton > button[kind="primary"], [data-testid="stFormSubmitButton"] > button[kind="primary"] {
  background: linear-gradient(135deg, #0f8b8d, #116b83); border-color: #20a7a2; color: white;
}
.stButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover {
  border-color: rgba(45, 212, 191, .65); transform: translateY(-1px);
}
input, textarea, [data-baseweb="select"] > div {
  border-radius: 9px !important;
}
hr { border-color: rgba(148, 163, 184, .16); }
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #101c2c, #0c1624);
  border-right: 1px solid rgba(148, 163, 184, .14);
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: #aebed0; }
@media (max-width: 900px) {
  [data-testid="stAppViewContainer"] .main .block-container {
    padding: .9rem .85rem 2rem; max-width: 100%;
  }
  [data-testid="stTabs"] [data-baseweb="tab-list"] {
    overflow-x: auto; flex-wrap: nowrap; scrollbar-width: thin;
    padding-bottom: 8px; gap: 5px;
  }
  [data-testid="stTabs"] button[data-baseweb="tab"] {
    flex: 0 0 auto; white-space: nowrap; padding: 8px 11px; font-size: .84rem;
  }
  [data-testid="stMetric"] { padding: 11px 12px; min-height: 88px; }
  [data-testid="stMetricValue"] { font-size: 1.35rem; }
  [data-testid="stDataFrame"] { max-width: 100%; overflow-x: auto; }
  h1 { margin-bottom: .35rem; }
  .stButton > button { min-height: 46px; }
}
@media (max-width: 600px) {
  [data-testid="stMetric"] { min-height: 82px; }
  [data-testid="stMetricLabel"] { font-size: .74rem; }
  [data-testid="stMetricValue"] { font-size: 1.18rem; }
  [data-testid="stCaptionContainer"] { font-size: .82rem; }
}



/* Login form: make the password label and field unmistakable. */
[data-testid="stForm"] [data-testid="stWidgetLabel"],
[data-testid="stForm"] [data-testid="stWidgetLabel"] *,
[data-testid="stForm"] label,
[data-testid="stForm"] label p {
  color: #f3f7fc !important;
  opacity: 1 !important;
  visibility: visible !important;
  font-size: 1rem !important;
  font-weight: 650 !important;
}
[data-testid="stForm"] [data-testid="stTextInput"] input {
  background: #0b1728 !important;
  color: #ffffff !important;
  border: 1px solid #8ba3bd !important;
  border-radius: 10px !important;
  min-height: 3.1rem !important;
  font-size: 1.05rem !important;
  caret-color: #5eead4 !important;
  -webkit-text-fill-color: #ffffff !important;
}
[data-testid="stForm"] [data-testid="stTextInput"] input:focus {
  border-color: #5eead4 !important;
  box-shadow: 0 0 0 2px rgba(94, 234, 212, .25) !important;
}
[data-testid="stForm"] button[kind="primary"] {
  background: #0f8b8d !important;
  color: #ffffff !important;
  border: 1px solid #5eead4 !important;
  font-weight: 750 !important;
  min-height: 2.8rem !important;
}

/* Contrast and readability hardening for Streamlit's native widgets. */
:root {
  color-scheme: dark;
  --dash-text: #edf4fc;
  --dash-muted: #c0cede;
  --dash-panel: #17263a;
  --dash-panel-strong: #1d3048;
  --dash-border: #52677f;
  --dash-accent: #5eead4;
}
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
  color: var(--dash-text);
}
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] span,
[data-testid="stText"],
[data-testid="stWidgetLabel"] p,
[data-testid="stRadio"] label,
[data-testid="stCheckbox"] label {
  color: var(--dash-text);
}
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p,
small, .stHelp {
  color: var(--dash-muted) !important;
}
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stDateInput"] input,
[data-testid="stTimeInput"] input,
[data-testid="stMultiSelect"] [data-baseweb="select"],
[data-testid="stSelectbox"] [data-baseweb="select"] > div {
  background: #142338 !important;
  color: #f3f7fc !important;
  border-color: #647b95 !important;
  -webkit-text-fill-color: #f3f7fc !important;
}
[data-testid="stTextInput"] input::placeholder,
[data-testid="stNumberInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder {
  color: #b5c4d6 !important;
  opacity: 1;
}
[data-baseweb="select"] *,
[data-baseweb="popover"] *,
[role="listbox"] *,
[role="option"] {
  color: #f3f7fc !important;
}
[data-baseweb="popover"],
[data-baseweb="menu"],
[role="listbox"] {
  background: #17263a !important;
  border: 1px solid #647b95 !important;
}
[role="option"]:hover,
[role="option"][aria-selected="true"] {
  background: #25445a !important;
}
[data-testid="stDataFrame"],
[data-testid="stTable"] {
  color: #edf4fc !important;
}
[data-testid="stDataFrame"] [role="columnheader"],
[data-testid="stDataFrame"] [role="gridcell"],
[data-testid="stTable"] th,
[data-testid="stTable"] td {
  color: #edf4fc !important;
}
[data-testid="stExpander"] {
  background: rgba(23, 38, 58, .72);
  border: 1px solid #52677f !important;
  border-radius: 12px;
}
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span {
  color: #edf4fc !important;
}
[data-testid="stAlert"] p,
[data-testid="stAlert"] li {
  color: #edf4fc !important;
}
.stButton > button,
[data-testid="stFormSubmitButton"] > button,
[data-testid="stDownloadButton"] > button {
  color: #f3f7fc !important;
  background-color: #1c3047;
  border-color: #647b95 !important;
}
.stButton > button:focus-visible,
[data-testid="stFormSubmitButton"] > button:focus-visible,
input:focus-visible,
textarea:focus-visible,
[data-baseweb="select"]:focus-within {
  outline: 2px solid var(--dash-accent) !important;
  outline-offset: 2px !important;
}
button:disabled,
input:disabled,
textarea:disabled,
[data-testid="stSelectbox"] [aria-disabled="true"] {
  color: #c0cede !important;
  opacity: .78 !important;
  -webkit-text-fill-color: #c0cede !important;
}
[data-testid="stMetricLabel"] { color: #c0cede !important; }
[data-testid="stMetricValue"] { color: #f3f7fc !important; }

</style>""", unsafe_allow_html=True)

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
    "Stocks": ["NVDA", "TSLA", "AMD", "MSFT", "AAPL", "AMZN", "META", "GOOGL", "AVGO", "PLTR", "NFLX", "COST", "LLY", "JPM", "ORCL", "CRM", "MU", "COIN", "HOOD", "SOFI", "GILD", "ICE", "CME", "CL"],
    "Gold & silver": ["GLD", "IAU", "SLV", "GDX", "GDXJ", "SGOL"],
    "Oil & energy": ["USO", "BNO", "XLE", "XOP", "OXY", "XOM", "CVX", "UNG", "URA"],
    "Crypto": ["BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD", "DOGE-USD", "ADA-USD", "LTC-USD", "LINK-USD", "AVAX-USD", "BCH-USD"],
    "Rates & dollar": ["TLT", "IEF", "SHY", "UUP", "FXE", "FXY"],
}

SECTOR_ETF = {
    "NVDA": "SMH", "AMD": "SMH", "AVGO": "SMH", "MU": "SMH",
    "AAPL": "XLK", "MSFT": "XLK", "ORCL": "XLK", "CRM": "XLK",
    "TSLA": "XLY", "AMZN": "XLY", "COST": "XLP", "LLY": "XLV",
    "JPM": "XLF", "COIN": "XLF", "HOOD": "XLF", "SOFI": "XLF", "ICE": "XLF", "CME": "XLF", "GILD": "XLV", "CL": "XLP",
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
st.caption("Market intelligence · Strategy research · Paper-trading analytics · Adaptive risk monitoring")
st.warning("Research and simulation only—not financial advice. Scanner scores are rules-based. The optional AI analyst provides a second opinion, not a prediction or guarantee. Yahoo Finance data may be delayed, incomplete, or unavailable. This app does not place real orders.")

@st.cache_data(ttl=300, show_spinner=False)
def load_history(tickers, period="1y"):
    raw = yf.download(list(tickers), period=period, interval="1d", auto_adjust=True,
                      group_by="ticker", progress=False, threads=False, timeout=20)
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
        group_by="ticker", progress=False, threads=False, prepost=False, timeout=20
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

def load_snapshot_history():
    """Read preserved snapshots from the retired virtual account archive."""
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

@st.cache_data(ttl=60, show_spinner=False)
def load_bot_intelligence_replays():
    """Read-only simulated replay outcomes for the Bot Intelligence Center."""
    client = get_supabase_client()
    result = (
        client.table("paper_execution_replays")
        .select("id,event_id,model_version,symbol,status,entry_date,exit_date,quantity,entry_price,exit_price,net_realized_pnl,return_pct,result,updated_at")
        .order("updated_at", desc=True)
        .limit(5000)
        .execute()
    )
    return result.data or []

@st.cache_data(ttl=60, show_spinner=False)
def load_bot_intelligence_signal_context():
    """Read-only setup and regime labels for replay event attribution."""
    client = get_supabase_client()
    result = (
        client.table("strategy_signal_observations")
        .select("id,setup_type,signal,market_regime,setup_score")
        .limit(5000)
        .execute()
    )
    return result.data or []
@st.cache_data(ttl=30, show_spinner=False)
def load_latest_paper_trade_decisions():
    """Load recent paper-only decision audit rows; this never mutates an account."""
    client = get_supabase_client()
    result = (
        client.table("paper_trade_decisions")
        .select("symbol,status,reason,quote_timestamp,quote_feed,bid,ask,midpoint,spread_pct,quantity,estimated_notional,estimated_risk_dollars,current_reward_risk,broker_order_id,client_order_id,decision,updated_at")
        .order("updated_at", desc=True)
        .limit(100)
        .execute()
    )
    return result.data or []

@st.cache_data(ttl=30, show_spinner=False)
def load_latest_paper_trade_decisions():
    """Load recent paper-only decision audit rows; this never mutates an account."""
    client = get_supabase_client()
    result = (
        client.table("paper_trade_decisions")
        .select("symbol,status,reason,quote_timestamp,quote_feed,bid,ask,midpoint,spread_pct,quantity,estimated_notional,estimated_risk_dollars,current_reward_risk,broker_order_id,client_order_id,decision,updated_at")
        .order("updated_at", desc=True)
        .limit(100)
        .execute()
    )
    return result.data or []

@st.cache_data(ttl=15, show_spinner=False)
def load_latest_alpaca_paper_account_snapshot():
    """Read the latest worker-persisted GET-only Alpaca paper brokerage snapshot."""
    client = get_supabase_client()
    result = (
        client.table("alpaca_paper_account_snapshots")
        .select("snapshot_fetched_at,source,status,currency,cash,portfolio_value,buying_power,equity,last_equity,is_market_open,next_open,next_close,positions,open_orders,recent_orders,updated_at")
        .eq("account_id", "primary-paper-account")
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None

@st.cache_data(ttl=30, show_spinner=False)
def load_latest_paper_execution_guardrail():
    """Load the latest Alpaca paper-account daily-loss guardrail; read-only."""
    client = get_supabase_client()
    result = (
        client.table("paper_execution_guardrails")
        .select("trading_date,starting_equity,current_equity,daily_pnl,daily_loss_pct,halted,halt_reason,updated_at")
        .order("trading_date", desc=True)
        .order("updated_at", desc=True)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None

@st.cache_data(ttl=60, show_spinner=False)
def load_latest_historical_portfolio_replay():
    """Load the newest historical shared-capital replay, preferring V7 when present."""
    client = get_supabase_client()
    result = (
        client.table("paper_portfolio_replay_runs")
        .select("model_version,as_of_date,updated_at,total_return_pct,final_equity,max_drawdown_pct,closed_trades,result")
        .in_("model_version", ["HISTORICAL_PORTFOLIO_REPLAY_V7", "HISTORICAL_PORTFOLIO_REPLAY_V6"])
        .order("updated_at", desc=True)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None

@st.cache_data(ttl=60, show_spinner=False)
def load_prior_historical_portfolio_replay():
    """Load V6 for a source-history fingerprint comparison with the V7 replay."""
    client = get_supabase_client()
    result = (
        client.table("paper_portfolio_replay_runs")
        .select("model_version,as_of_date,updated_at,result")
        .eq("model_version", "HISTORICAL_PORTFOLIO_REPLAY_V6")
        .order("updated_at", desc=True)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None

def load_strategy_signal_events():
    """Load persisted first-seen signals and their observed forward outcomes."""
    client = get_supabase_client()
    result = (
        client.table("strategy_signal_observations")
        .select("symbol,signal_date,setup_type,signal,entry_price,stop_reference,target_reference,setup_score,market_regime,outcomes,created_at,updated_at")
        .order("signal_date", desc=True)
        .limit(5000)
        .execute()
    )
    return result.data or []

# Retired Supabase virtual account: load the historical record read-only.
paper_account_available = True
paper_account_error = None
try:
    db = get_supabase_client()
    if not st.session_state.get("paper_db_loaded", False):
        result = db.table("paper_account").select("*").eq("account_id", ACCOUNT_ID).limit(1).execute()
        saved = result.data[0] if result.data else {}
        st.session_state.paper_cash = float(saved.get("cash") or 0.0)
        st.session_state.realized_pnl = float(saved.get("realized_pnl") or 0.0)
        st.session_state.paper_positions = saved.get("positions") or {}
        st.session_state.paper_journal = saved.get("journal") or []
        st.session_state.paper_account_updated_at = saved.get("updated_at")
        st.session_state.paper_db_loaded = True
except Exception as exc:
    paper_account_available = False
    paper_account_error = exc
    st.error("Archived virtual-account history could not be loaded. No account was recreated or changed.")
    st.caption(f"Supabase error type: {type(exc).__name__}. Check the read-only history connection.")

if paper_account_available:
    st.sidebar.info("Legacy $1,000 virtual account retired · archive is read-only")
else:
    st.sidebar.warning("Legacy virtual-account archive unavailable · no trading controls")

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
    st.session_state.scan_data = pd.DataFrame()

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
        try:
            history = load_history(fetch_tickers, lookback)
        except Exception as exc:
            history = {}
            st.warning(f"Market history could not be downloaded. Other dashboard tabs remain available. Error type: {type(exc).__name__}.")
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
if data is None:
    data = pd.DataFrame()
if data.empty:
    st.warning("Market data is currently unavailable. The other dashboard sections remain available; retry the scan when data service recovers.")
else:
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

def _safe_format_number(value, template):
    """Format numeric values without crashing on null or malformed DB fields."""
    if value is None:
        return "—"
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return str(value)
    if not np.isfinite(number):
        return "—"
    return template.format(number)

command_tab, scanner_tab, paper_tab, analytics_tab, validation_tab, intelligence_tab, cloud_tab = st.tabs(["🚀 Command center", "📊 Market scanner", "🗃️ Retired virtual account", "📚 Archived performance", "🧪 Strategy validation", "🏆 Bot intelligence", "☁️ Cloud scanner"])

with command_tab:
    @st.fragment(run_every="60s")
    def render_command_center():
        st.subheader("🚀 Trading command center")
        st.caption("A live overview of the cloud worker's latest completed scan, AI research review, market leadership and paper-portfolio risk. Refreshes from Supabase every 60 seconds.")
        if st.button("↻ Refresh command center", key="refresh_command_center"):
            load_latest_cloud_scan.clear()
            load_latest_historical_portfolio_replay.clear()
            load_prior_historical_portfolio_replay.clear()
        try:
            scan = load_latest_cloud_scan()
        except Exception as exc:
            scan = None
            st.error(f"Could not load the latest cloud intelligence: {exc}")
        if not scan:
            st.warning("No cloud scan is available yet. The worker may still be starting or the first scan has not completed.")
        else:
            review = scan.get("ai_review") or {}
            health = review.get("scan_health") or {}
            report = review.get("report") or {}
            portfolio = review.get("portfolio_risk") or {}
            rotation = review.get("sector_rotation") or []
            setup = review.get("setup_validation") or {}
            scanned_at = scan.get("scanned_at")
            try:
                scan_dt = pd.to_datetime(scanned_at, utc=True)
                age_min = max(0, int((pd.Timestamp.now(tz="UTC") - scan_dt).total_seconds() / 60))
                scan_label = scan_dt.tz_convert("America/Chicago").strftime("%b %d · %I:%M:%S %p CT")
            except Exception:
                age_min, scan_label = None, str(scanned_at or "Unavailable")
            coverage = health.get("coverage_pct")
            coverage_label = f"{float(coverage):.1f}%" if coverage is not None else "—"
            equity = portfolio.get("equity_reference")
            equity_label = f"${float(equity):,.2f}" if equity is not None else "—"
            top_three = report.get("top_three_for_individual_review") or []
            candidates = report.get("ranked_candidates") or []
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Universe coverage", coverage_label, f"{health.get('analyzed_symbols', scan.get('symbol_count', 0))}/{health.get('requested_symbols', '—')} symbols")
            c2.metric("Last completed scan", f"{age_min} min ago" if age_min is not None else "—", scan_label)
            c3.metric("Paper equity reference", equity_label, f"{portfolio.get('position_count', 0)} open positions")
            c4.metric("Worker", f"V{review.get('worker_version', '—')}", f"AI: {scan.get('ai_model') or 'not available'}")
            if age_min is not None and age_min > 35:
                st.warning("Cloud scan is older than expected. Check worker health before relying on this snapshot.")
            elif age_min is not None:
                st.success("Cloud scan is reporting recently completed data.")
            st.divider()
            left, right = st.columns([1.2, 1])
            with left:
                st.markdown("#### 🧠 AI market read")
                if report.get("market_read"):
                    st.write(report["market_read"])
                else:
                    st.info("The latest scan has no completed AI market read.")
                if top_three:
                    st.markdown("**Priority symbols for individual review**")
                    st.write(" · ".join(str(x) for x in top_three[:5]))
                cautions = report.get("important_cautions") or []
                if cautions:
                    with st.expander("AI risk notes", expanded=True):
                        for note in cautions[:5]:
                            st.markdown(f"- {note}")
            with right:
                st.markdown("#### 🧭 Market leadership")
                if rotation:
                    rot_df = pd.DataFrame(rotation)
                    fields = [c for c in ["group", "rotation_state", "return_1m_pct", "relative_1m_vs_spy_pp", "momentum_score"] if c in rot_df.columns]
                    rot_df = rot_df[fields].copy()
                    rot_df = rot_df.rename(columns={"group":"Market group","rotation_state":"State","return_1m_pct":"1M return %","relative_1m_vs_spy_pp":"Vs SPY (pp)","momentum_score":"Momentum"})
                    st.dataframe(rot_df.style.format({c:"{:+.2f}" for c in ["1M return %","Vs SPY (pp)","Momentum"] if c in rot_df.columns}), use_container_width=True, hide_index=True)
                    st.caption("Leadership is inferred from proxy price performance, not measured capital flows.")
                else:
                    st.info("Sector/asset rotation data is unavailable in this scan.")
            st.divider()
            st.markdown("#### 🏆 AI research shortlist")
            if candidates:
                cand_df = pd.DataFrame(candidates)
                keep = [c for c in ["rank","symbol","stance","rationale","key_risk","what_would_improve"] if c in cand_df.columns]
                cand_df = cand_df[keep].copy()
                cand_df = cand_df.rename(columns={"rank":"Rank","symbol":"Symbol","stance":"Research stance","rationale":"Why it ranked","key_risk":"Main risk","what_would_improve":"What would improve it"})
                st.dataframe(cand_df, use_container_width=True, hide_index=True)
                st.caption("AI ranks setup quality from the worker's supplied daily-bar facts. This is a research queue, not a buy signal. Review current quotes and the individual chart before acting.")
            else:
                st.info("No AI shortlist was saved with the latest scan.")
            with st.expander("Deep diagnostics · portfolio risk, historical replay & walk-forward evidence", expanded=False):
                p1, p2 = st.columns([1, 1])
                with p1:
                    st.markdown("#### 🛡️ Portfolio concentration")
                    sector_weights = portfolio.get("sector_weights_pct") or {}
                    if sector_weights:
                        sector_df = pd.DataFrame([{"Sector":k,"Weight %":v} for k,v in sector_weights.items()]).sort_values("Weight %",ascending=False)
                        st.dataframe(sector_df.style.format({"Weight %":"{:.1f}%"}), use_container_width=True, hide_index=True)
                        st.metric("Largest sector weight", f"{float(portfolio.get('largest_sector_weight_pct',0)):.1f}%")
                    else:
                        st.info("No portfolio concentration snapshot is available.")

                    held_rows = portfolio.get("positions") or []
                    if held_rows:
                        st.markdown("**Current holdings · estimated weights**")
                        held_df = pd.DataFrame(held_rows)
                        held_columns = [c for c in ["symbol", "sector_group", "market_value", "weight_pct", "annualized_volatility_pct"] if c in held_df.columns]
                        held_df = held_df[held_columns].rename(columns={
                            "symbol": "Symbol", "sector_group": "Sector",
                            "market_value": "Market value $", "weight_pct": "Portfolio weight %",
                            "annualized_volatility_pct": "60D annualized volatility %",
                        })
                        st.dataframe(held_df.style.format({
                            "Market value $": "${:,.2f}",
                            "Portfolio weight %": "{:.2f}%",
                            "60D annualized volatility %": "{:.1f}%",
                        }, na_rep="—"), use_container_width=True, hide_index=True)

                    correlated = portfolio.get("top_correlated_pairs") or []
                    if correlated:
                        st.markdown("**Most correlated holdings · 60 trading days**")
                        corr_df = pd.DataFrame(correlated[:5]).rename(columns={
                            "pair": "Pair", "correlation_60d": "Correlation",
                            "overlapping_sessions": "Overlapping sessions",
                        })
                        st.dataframe(corr_df.style.format({"Correlation": "{:+.2f}", "Overlapping sessions": "{:.0f}"}), use_container_width=True, hide_index=True)
                        high_pairs = [x for x in correlated if abs(float(x.get("correlation_60d") or 0)) >= 0.80]
                        if high_pairs:
                            st.warning(f"{len(high_pairs)} holding pair(s) have absolute 60-day correlation of at least 0.80. Different tickers may still behave like one concentrated bet.")
                    if portfolio.get("data_note"):
                        st.caption(portfolio["data_note"])
                with p2:
                    st.markdown("#### 🧪 Historical setup behavior")
                    setups = setup.get("setups") or {}
                    if setups:
                        rows = []
                        for name, metrics in setups.items():
                            train = metrics.get("training") or {}
                            test = metrics.get("out_of_sample") or {}
                            rows.append({
                                "Setup": name.title(),
                                "De-overlapped events": metrics.get("event_count", 0),
                                "Train 5D win rate": train.get("win_rate_5d_pct"),
                                "OOS 5D win rate": test.get("win_rate_5d_pct"),
                                "Train 5D expectancy": train.get("expectancy_5d_pct"),
                                "OOS 5D expectancy": test.get("expectancy_5d_pct"),
                                "OOS 20D win rate": test.get("win_rate_20d_pct"),
                                "OOS 20D expectancy": test.get("expectancy_20d_pct"),
                            })
                        hist_df = pd.DataFrame(rows)
                        st.dataframe(hist_df.style.format({c:"{:+.2f}%" if "expectancy" in c.lower() else "{:.1f}%" for c in hist_df.columns if c not in ["Setup","De-overlapped events"]}, na_rep="—"), use_container_width=True, hide_index=True)
                        st.caption(f"Chronological 70/30 per-symbol split · {setup.get('de_overlapped_event_count', 0):,} non-overlapping events from {setup.get('raw_event_count', 0):,} raw candidates · 20-session cooldown across setup types.")
                        st.caption("Out-of-sample is the later 30% of each symbol's history. This is a historical holdout, not a rolling walk-forward or proof of future performance; transaction costs and survivorship-bias adjustments are not included.")
                    else:
                        st.info("Historical setup study is unavailable.")
                st.divider()
                st.markdown("#### 🧮 Shared-capital historical portfolio replay")
                try:
                    replay_row = load_latest_historical_portfolio_replay()
                except Exception as exc:
                    replay_row = None
                    st.warning(f"Historical portfolio replay could not be loaded: {exc}")
                if replay_row:
                    replay_result = replay_row.get("result") or {}
                    walk = replay_result.get("walk_forward") or {}
                    cost_sensitivity = replay_result.get("out_of_sample_cost_sensitivity") or {}
                    model_label = replay_row.get("model_version", "Unknown model")
                    as_of_label = replay_row.get("as_of_date", "Unknown date")
                    st.caption(f"{model_label} · Market data through {as_of_label} · Saved {replay_row.get('updated_at', 'time unavailable')}")
                    m1, m2, m3, m4 = st.columns(4)
                    ret = replay_row.get("total_return_pct")
                    m1.metric("Historical holdout", f"{float(ret):+.2f}%" if ret is not None else "—")
                    equity_value = replay_row.get("final_equity")
                    m2.metric("Ending equity", f"${float(equity_value):,.2f}" if equity_value is not None else "—")
                    dd = replay_row.get("max_drawdown_pct")
                    m3.metric("Maximum drawdown", f"{float(dd):.2f}%" if dd is not None else "—")
                    m4.metric("Closed trades", f"{int(replay_row.get('closed_trades') or 0):,}")
                    drawdown_rows = []
                    for label, key in (
                        ("Current drawdown", "current_drawdown_pct"),
                        ("Current underwater sessions", "current_underwater_sessions"),
                        ("Longest underwater stretch (sessions)", "longest_underwater_sessions"),
                        ("Maximum drawdown peak date", "max_drawdown_peak_date"),
                        ("Maximum drawdown trough date", "max_drawdown_trough_date"),
                    ):
                        value = replay_result.get(key)
                        if value is not None:
                            if key.endswith("_pct"):
                                display_value = f"{float(value):.2f}%"
                            elif key.endswith("_sessions"):
                                display_value = f"{int(value):,}"
                            else:
                                display_value = str(value)
                            drawdown_rows.append({"Drawdown diagnostic": label, "Value": display_value})
                    recovered = replay_result.get("is_recovered_to_prior_peak")
                    if recovered is not None:
                        drawdown_rows.append({
                            "Drawdown diagnostic": "Recovered to prior equity peak",
                            "Value": "Yes" if recovered else "No",
                        })
                    if drawdown_rows:
                        st.markdown("##### Drawdown duration & recovery")
                        st.dataframe(pd.DataFrame(drawdown_rows), use_container_width=True, hide_index=True)
                        st.caption("Drawdown depth and duration use daily closing equity marks; intraday peak-to-trough movement may be larger.")
                    exposure = replay_result.get("exposure_quality") or {}
                    exposure_rows = []
                    for label, key, suffix in (
                        ("Peak single-stock exposure", "max_single_symbol_exposure_pct", "%"),
                        ("Peak single-sector exposure", "max_single_sector_exposure_pct", "%"),
                        ("Peak top-three stock exposure", "max_top_three_symbols_exposure_pct", "%"),
                        ("Peak single-stock concentration (HHI)", "max_symbol_exposure_hhi_pct2", " pct²"),
                        ("Exposure-weighted average pair correlation", "max_weighted_average_pair_correlation", ""),
                        ("High-correlation pair-weight share", "max_high_correlation_pair_weight_share_pct", "%"),
                        ("Date of peak single-stock exposure", "max_single_symbol_exposure_date", ""),
                        ("Date of peak sector exposure", "max_single_sector_exposure_date", ""),
                    ):
                        value = exposure.get(key)
                        if value is not None:
                            display_value = f"{float(value):.2f}{suffix}" if key.endswith("_pct") or key.endswith("_pct2") else str(value)
                            exposure_rows.append({"Exposure diagnostic": label, "Value": display_value})
                    if exposure_rows:
                        st.markdown("##### Portfolio concentration")
                        st.dataframe(pd.DataFrame(exposure_rows), use_container_width=True, hide_index=True)
                        st.caption("Peak exposures are measured against daily marked portfolio equity. HHI is the sum of squared single-symbol exposure percentages. Correlation uses trailing aligned daily returns for concurrently held symbols; high-correlation pair share is the portion of pairwise exposure-product weight with correlation at or above 0.70. Insufficient history is reported as unavailable, not zero.")
                    stress = replay_result.get("market_stress_quality") or {}
                    if stress:
                        stress_rows = []
                        for label, key in (
                            ("SPY down at least 1% (daily)", "daily_benchmark_down_1pct"),
                            ("SPY down at least 2% (daily)", "daily_benchmark_down_2pct"),
                            ("SPY down at least 5% (rolling 5 sessions)", "rolling_5_session_benchmark_down_5pct"),
                        ):
                            scenario = stress.get(key) or {}
                            stress_rows.append({
                                "Historical stress condition": label,
                                "Sessions": scenario.get("sessions", 0),
                                "Portfolio loss sessions": scenario.get("portfolio_loss_sessions", 0),
                                "Average portfolio return": (
                                    f"{float(scenario['average_portfolio_return_pct']):+.2f}%"
                                    if scenario.get("average_portfolio_return_pct") is not None else "—"
                                ),
                                "Worst portfolio return": (
                                    f"{float(scenario['worst_portfolio_return_pct']):+.2f}%"
                                    if scenario.get("worst_portfolio_return_pct") is not None else "—"
                                ),
                                "Average vs. SPY": (
                                    f"{float(scenario['average_portfolio_minus_benchmark_pct']):+.2f} pp"
                                    if scenario.get("average_portfolio_minus_benchmark_pct") is not None else "—"
                                ),
                            })
                        st.markdown("##### Historical market selloff behavior")
                        st.dataframe(pd.DataFrame(stress_rows), use_container_width=True, hide_index=True)
                        st.caption("Conditional historical observations using the supplied SPY history. Five-session selloff windows may overlap. These results are not a forecast or a simulated sudden correlation/liquidity shock.")
                    risk_budget = replay_result.get("portfolio_risk_budget") or {}
                    if risk_budget.get("status") == "COMPLETED":
                        utilization = float(risk_budget.get("peak_utilization_pct") or 0)
                        budget_rows = [
                            {"Portfolio risk budget": "Configured stop-risk budget", "Value": f"{float(risk_budget.get('risk_budget_pct_equity') or 0):.2f}% of equity"},
                            {"Portfolio risk budget": "Peak planned open risk", "Value": f"{float(risk_budget.get('peak_open_risk_pct_equity') or 0):.2f}% of equity"},
                            {"Portfolio risk budget": "Peak budget utilization", "Value": f"{utilization:.1f}%"},
                            {"Portfolio risk budget": "Remaining budget at peak", "Value": f"{float(risk_budget.get('remaining_budget_pct_equity') or 0):+.2f}% of equity"},
                            {"Portfolio risk budget": "Peak date", "Value": risk_budget.get("peak_date") or "—"},
                            {"Portfolio risk budget": "Snapshots above budget", "Value": int(risk_budget.get("over_budget_snapshots") or 0)},
                        ]
                        st.markdown("##### Portfolio stop-risk budget")
                        st.dataframe(pd.DataFrame(budget_rows), use_container_width=True, hide_index=True)
                        risk_contributors = risk_budget.get("symbol_contributions_at_peak_risk") or []
                        if risk_contributors:
                            st.markdown("**Largest contributors at peak portfolio stop-risk**")
                            st.dataframe(pd.DataFrame([{
                                "Symbol": row.get("symbol"),
                                "Planned stop-risk": f"{float(row.get('planned_open_risk_pct_equity') or 0):.3f}%",
                                "Share of budget": f"{float(row.get('risk_budget_share_pct') or 0):.1f}%",
                                "Share of open risk": f"{float(row.get('share_of_portfolio_open_risk_pct') or 0):.1f}%",
                            } for row in risk_contributors]), use_container_width=True, hide_index=True)
                        st.caption(risk_budget.get("interpretation") or "Historical replay diagnostic only; not a live order gate.")
                    elif risk_budget.get("status"):
                        st.caption(f"Portfolio risk budget: {risk_budget.get('status')}")
                    shock = replay_result.get("portfolio_shock_scenarios") or {}
                    if shock.get("scenarios"):
                        shock_rows = []
                        for scenario in shock.get("scenarios", []):
                            shock_rows.append({
                                "Scenario": scenario.get("name"),
                                "Estimated equity loss": f"{float(scenario.get('estimated_equity_loss_pct') or 0):.2f}%",
                                "Loss per $10,000": f"${float(scenario.get('estimated_equity_loss_per_10000') or 0):,.2f}",
                                "Exposure snapshot": scenario.get("exposure_date") or "—",
                            })
                        st.markdown("##### Deterministic portfolio shock scenarios")
                        st.dataframe(pd.DataFrame(shock_rows), use_container_width=True, hide_index=True)
                        st.caption(shock.get("interpretation") or "Independent sensitivity scenarios; not forecasts. Do not add scenario losses together.")
                        contributors = shock.get("symbol_contributions_at_peak_gross_exposure") or []
                        if contributors:
                            st.markdown("**Largest individual shock contributors at peak gross exposure**")
                            contributor_rows = [{
                                "Symbol": row.get("symbol"),
                                "Exposure": f"{float(row.get('exposure_pct') or 0):.2f}%",
                                "Planned open risk": f"{float(row.get('planned_open_risk_pct') or 0):.2f}%",
                                "Loss at -10%": f"{float(row.get('loss_at_10pct_drop_pct') or 0):.2f}%",
                                "Loss at -20%": f"{float(row.get('loss_at_20pct_drop_pct') or 0):.2f}%",
                            } for row in contributors]
                            st.dataframe(pd.DataFrame(contributor_rows), use_container_width=True, hide_index=True)
                            st.caption("Per-symbol price-shock contributions use each symbol's exposure at the same peak-gross-exposure snapshot; planned open risk is the modeled distance to stop after assumed baseline execution costs.")

                    quality = replay_result.get("trade_quality") or {}
                    quality_rows = []
                    for label, key, suffix in (
                        ("Maximum consecutive losses", "max_consecutive_losses", ""),
                        ("Worst losing-streak P&L", "worst_losing_streak_net_pnl", "$"),
                        ("Maximum consecutive wins", "max_consecutive_wins", ""),
                        ("Top winner share of gross profits", "top_winner_share_of_gross_profit_pct", "%"),
                        ("Top 3 winners share of gross profits", "top_three_winners_share_of_gross_profit_pct", "%"),
                        ("Average win / average loss", "average_win_to_average_loss", "x"),
                        ("Trades with valid P&L", "trades_with_valid_net_pnl", ""),
                    ):
                        value = quality.get(key)
                        if value is not None:
                            if key.endswith("_pnl"):
                                display_value = f"{suffix}{float(value):,.2f}"
                            elif key.endswith("_pct"):
                                display_value = f"{float(value):.1f}{suffix}"
                            elif key.endswith("_ratio"):
                                display_value = f"{float(value):.2f}{suffix}"
                            else:
                                display_value = f"{int(value):,}{suffix}"
                            quality_rows.append({"Trade quality diagnostic": label, "Value": display_value})
                    if quality_rows:
                        st.markdown("##### Losing streaks & profit concentration")
                        st.dataframe(pd.DataFrame(quality_rows), use_container_width=True, hide_index=True)
                        st.caption("Profit concentration measures the share of gross winning-trade profits contributed by the largest winners. Streaks are ordered by exit date; these are historical diagnostics, not predictive guarantees.")
                    cost_rows = []
                    for key, label in (
                        ("baseline", "Baseline"),
                        ("moderate", "Moderate cost"),
                        ("severe", "Severe cost"),
                        ("fixed_share_moderate", "Fixed-share moderate"),
                        ("fixed_share_severe", "Fixed-share severe"),
                    ):
                        scenario = cost_sensitivity.get(key) or {}
                        if scenario:
                            cost_rows.append({
                                "Scenario": label,
                                "Spread bps": scenario.get("spread_bps"),
                                "Slippage bps": scenario.get("slippage_bps"),
                                "Return %": scenario.get("total_return_pct"),
                                "Max drawdown %": scenario.get("max_drawdown_pct"),
                                "Profit factor": scenario.get("profit_factor"),
                            })
                    if cost_rows:
                        st.markdown("##### Holdout execution-cost stress")
                        cost_df = pd.DataFrame(cost_rows)
                        st.dataframe(
                            cost_df.style.format({
                                "Spread bps": "{:.0f}",
                                "Slippage bps": "{:.0f}",
                                "Return %": "{:+.2f}%",
                                "Max drawdown %": "{:.2f}%",
                                "Profit factor": "{:.3f}",
                            }, na_rep="—"),
                            use_container_width=True, hide_index=True
                        )
                        st.caption(
                            (cost_sensitivity.get("interpretation") or "") +
                            " Fixed-share cases freeze baseline accepted quantities; they are not pure friction-only comparisons."
                        )
                    fold_rows = walk.get("windows_detail") or []
                    sufficient_training_folds = [row for row in fold_rows if row.get("training_sample_sufficient")]
                    positive_training_folds = sum(
                        1 for row in sufficient_training_folds if float(row.get("test_return_pct") or 0) > 0
                    )
                    supported_test_folds = int(walk.get("windows_with_at_least_10_closed_trades") or 0)
                    thin_test_folds = int(walk.get("windows_with_insufficient_closed_trade_evidence") or 0)
                    supported_cost_folds = int(walk.get("supported_windows_at_moderate_cost") or 0)
                    positive_supported_cost_folds = int(walk.get("supported_windows_positive_at_moderate_cost") or 0)
                    median_cost_fold = walk.get("median_test_return_at_moderate_cost_pct")
                    worst_cost_fold = walk.get("worst_test_return_at_moderate_cost_pct")
                    wf_cols = st.columns(4)
                    wf_cols[0].metric(
                        "Test periods with ≥10 trades",
                        f"{supported_test_folds}/{int(walk.get('windows') or 0)}"
                    )
                    wf_cols[1].metric(
                        "Positive supported periods after costs",
                        f"{positive_supported_cost_folds}/{supported_cost_folds}"
                    )
                    wf_cols[2].metric(
                        "Median fold return after costs",
                        f"{float(median_cost_fold):+.2f}%" if median_cost_fold is not None else "—"
                    )
                    wf_cols[3].metric("Thin-evidence periods", f"{thin_test_folds:,}")
                    st.caption(
                        f"Walk-forward design: {int(walk.get('training_sessions') or 126)} training sessions / "
                        f"{int(walk.get('test_sessions') or 63)} unseen test sessions per fold · "
                        f"{int(walk.get('total_test_closed_trades') or 0):,} closed test trades total. "
                        "A fold needs at least 10 closed trades to count as supported evidence."
                    )
                    moderate_cost_return = (cost_sensitivity.get("moderate") or {}).get("total_return_pct")
                    enough_supported_folds = supported_cost_folds >= 3
                    majority_positive_after_costs = (
                        enough_supported_folds and positive_supported_cost_folds * 2 > supported_cost_folds
                    )
                    if not enough_supported_folds:
                        st.warning(
                            "UNPROVEN: fewer than three walk-forward test periods have at least 10 closed trades. "
                            "The available results are exploratory, not evidence of a dependable edge."
                        )
                    elif majority_positive_after_costs and median_cost_fold is not None and float(median_cost_fold) > 0:
                        st.success(
                            "POSITIVE HISTORICAL EVIDENCE: a majority of adequately sampled unseen periods were positive "
                            "after moderate assumed costs. This is not proof of future profitability or permission to trade live."
                        )
                    else:
                        st.warning(
                            "WEAK OR NEGATIVE EVIDENCE: adequately sampled unseen periods do not show consistent positive "
                            "returns after moderate assumed costs. Keep the strategy simulation-only while investigating."
                        )
                    if moderate_cost_return is not None and float(moderate_cost_return) <= 0:
                        st.caption(
                            "The separate 70/30 moderate-cost holdout is non-positive; do not let positive individual folds "
                            "override that conflicting result."
                        )
                    if worst_cost_fold is not None:
                        st.caption(f"Worst adequately sampled moderate-cost fold: {float(worst_cost_fold):+.2f}%.")
                    try:
                        prior_row = load_prior_historical_portfolio_replay()
                        current_fingerprint = replay_result.get("history_fingerprint")
                        prior_fingerprint = (prior_row.get("result") or {}).get("history_fingerprint") if prior_row else None
                        if current_fingerprint and prior_fingerprint and current_fingerprint != prior_fingerprint:
                            st.warning(
                                "Market-history fingerprint changed since V6. The V6-to-V7 return difference is not a clean code-only comparison; "
                                "the underlying historical price data was revised."
                            )
                    except Exception as exc:
                        st.caption(f"Prior replay fingerprint comparison unavailable: {exc}")
                    if walk.get("windows_with_insufficient_training_events"):
                        st.caption(
                            f"{int(walk.get('windows_with_insufficient_training_events'))} walk-forward period(s) had too few training events; "
                            "the first fold had no training events and should not count as evidence of a validated edge."
                        )

                    standalone = replay_result.get("out_of_sample_asset_class_only") or {}
                    accepted = replay_result.get("out_of_sample_by_asset_class") or {}
                    pooled = walk.get("aggregate_test_by_asset_class") or {}
                    pooled_cost = walk.get("aggregate_moderate_cost_test_by_asset_class") or {}
                    asset_rows = []
                    for key, label in (("CRYPTO", "Crypto"), ("NON_CRYPTO", "Stocks / ETFs / other")):
                        solo = standalone.get(key) or {}
                        mixed = accepted.get(key) or {}
                        wf_asset = pooled.get(key) or {}
                        wf_cost = pooled_cost.get(key) or {}
                        asset_rows.append({
                            "Asset class": label,
                            "Standalone OOS return %": solo.get("total_return_pct"),
                            "Standalone max DD %": solo.get("max_drawdown_pct"),
                            "Standalone trades": solo.get("closed_trades"),
                            "Mixed-portfolio trades": mixed.get("trades"),
                            "Mixed-portfolio trade P&L $": mixed.get("total_net_pnl"),
                            "Walk-forward pooled P&L $": wf_asset.get("total_net_pnl"),
                            "Walk-forward moderate-cost P&L $": wf_cost.get("total_net_pnl"),
                        })
                    asset_df = pd.DataFrame(asset_rows)
                    st.dataframe(
                        asset_df.style.format({
                            "Standalone OOS return %": "{:+.2f}%",
                            "Standalone max DD %": "{:.2f}%",
                            "Standalone trades": "{:,.0f}",
                            "Mixed-portfolio trades": "{:,.0f}",
                            "Mixed-portfolio trade P&L $": "${:+,.2f}",
                            "Walk-forward pooled P&L $": "${:+,.2f}",
                            "Walk-forward moderate-cost P&L $": "${:+,.2f}",
                        }, na_rep="—"),
                        use_container_width=True, hide_index=True
                    )
                    st.caption(
                        "Standalone rows each start with separate fresh capital. Mixed-portfolio P&L is the closed-trade contribution "
                        "from trades accepted in the combined shared-cash run. Walk-forward pooled P&L sums closed trades across test folds; "
                        "it is not a compounded portfolio return. Moderate costs assume 20 bps spread and 10 bps slippage."
                    )
                    # Compare entry setups across the chronological test folds, not just the overall portfolio.
                    setup_pooled = walk.get("aggregate_test_by_setup") or {}
                    setup_pooled_cost = walk.get("aggregate_moderate_cost_test_by_setup") or {}
                    setup_rows = []
                    for setup_key in sorted(set(setup_pooled) | set(setup_pooled_cost)):
                        base_setup = setup_pooled.get(setup_key) or {}
                        cost_setup = setup_pooled_cost.get(setup_key) or {}
                        setup_positive_folds = 0
                        setup_adequate_folds = 0
                        for fold in fold_rows:
                            if not fold.get("training_sample_sufficient"):
                                continue
                            fold_setup = (fold.get("test_by_setup") or {}).get(setup_key) or {}
                            fold_cost_setup = (fold.get("test_moderate_cost_by_setup") or {}).get(setup_key) or {}
                            if int(fold_setup.get("trades") or 0) > 0:
                                setup_adequate_folds += 1
                                fold_pnl = float(fold_setup.get("total_net_pnl") or 0)
                                if fold_pnl > 0:
                                    setup_positive_folds += 1
                        setup_rows.append({
                            "Entry setup": setup_key.title(),
                            "Baseline trades": base_setup.get("trades"),
                            "Baseline P&L $": base_setup.get("total_net_pnl"),
                            "Baseline PF": base_setup.get("profit_factor"),
                            "Moderate-cost trades": cost_setup.get("trades"),
                            "Moderate-cost P&L $": cost_setup.get("total_net_pnl"),
                            "Moderate-cost PF": cost_setup.get("profit_factor"),
                            "Positive adequate folds": f"{setup_positive_folds}/{setup_adequate_folds}",
                        })
                    if setup_rows:
                        st.markdown("##### Entry-setup walk-forward attribution")
                        setup_df = pd.DataFrame(setup_rows)
                        st.dataframe(
                            setup_df.style.format({
                                "Baseline trades": "{:,.0f}",
                                "Baseline P&L $": "${:+,.2f}",
                                "Baseline PF": "{:.3f}",
                                "Moderate-cost trades": "{:,.0f}",
                                "Moderate-cost P&L $": "${:+,.2f}",
                                "Moderate-cost PF": "{:.3f}",
                            }, na_rep="—"),
                            use_container_width=True, hide_index=True
                        )
                        st.caption(
                            "P&L and profit factor are pooled across non-overlapping test folds. "
                            "Positive-fold counts include only folds with adequate training and at least one closed trade for that setup. "
                            "This is diagnostic attribution, not a recommendation to disable either setup."
                        )
                    fold_detail_rows = []
                    for fold in walk.get("windows_detail") or []:
                        by_class = fold.get("test_by_asset_class") or {}
                        by_class_cost = fold.get("test_moderate_cost_by_asset_class") or {}
                        crypto_pnl = (by_class.get("CRYPTO") or {}).get("total_net_pnl")
                        noncrypto_pnl = (by_class.get("NON_CRYPTO") or {}).get("total_net_pnl")
                        crypto_cost_pnl = (by_class_cost.get("CRYPTO") or {}).get("total_net_pnl")
                        noncrypto_cost_pnl = (by_class_cost.get("NON_CRYPTO") or {}).get("total_net_pnl")
                        fold_detail_rows.append({
                            "Fold": fold.get("window"),
                            "Test period": f"{fold.get('test_start', '—')} to {fold.get('test_end', '—')}",
                            "Training events": fold.get("training_events"),
                            "Training boundary signals excluded": fold.get("training_boundary_signals_excluded", 0),
                            "Training adequate": "Yes" if fold.get("training_sample_sufficient") else "No",
                            "Test events": fold.get("test_events"),
                            "Test boundary signals excluded": fold.get("test_boundary_signals_excluded", 0),
                            "Closed test trades": fold.get("test_closed_trades"),
                            "Combined return %": fold.get("test_return_pct"),
                            "Moderate-cost return %": fold.get("test_moderate_cost_return_pct"),
                            "Crypto P&L $": crypto_pnl,
                            "Non-crypto P&L $": noncrypto_pnl,
                            "Crypto moderate-cost P&L $": crypto_cost_pnl,
                            "Non-crypto moderate-cost P&L $": noncrypto_cost_pnl,
                        })
                    if fold_detail_rows:
                        st.markdown("##### Walk-forward fold detail")
                        fold_df = pd.DataFrame(fold_detail_rows)
                        st.dataframe(
                            fold_df.style.format({
                                "Combined return %": "{:+.2f}%",
                                "Moderate-cost return %": "{:+.2f}%",
                                "Crypto P&L $": "${:+,.2f}",
                                "Non-crypto P&L $": "${:+,.2f}",
                                "Crypto moderate-cost P&L $": "${:+,.2f}",
                                "Non-crypto moderate-cost P&L $": "${:+,.2f}",
                            }, na_rep="—"),
                            use_container_width=True, hide_index=True
                        )
                    if model_label.endswith("_V6"):
                        st.info("V7 adds isolated crypto/non-crypto portfolios and pooled asset-class walk-forward attribution. The dashboard will switch to V7 when that run is saved.")
                else:
                    st.info("No historical portfolio replay is saved yet. The cloud worker will populate this panel after its historical simulation completes.")

                missing = health.get("missing_symbols") or []
                stale = health.get("stale_symbols") or []
                if missing or stale:
                    st.warning(f"Data quality: {len(missing)} missing symbol(s) · {len(stale)} potentially stale price(s). Review the cloud scanner's Scan health panel before acting on rankings.")
                limitations = report.get("data_limitations") or []
                if limitations:
                    with st.expander("Data limitations"):
                        for item in limitations:
                            st.markdown(f"- {item}")
                st.caption(f"Scan ID: {scan.get('id','—')} · Saved: {scan_label} · Data: {scan.get('data_source','unspecified')} · Read-only research snapshot.")
    render_command_center()


with validation_tab:
    st.subheader("🧪 Strategy validation lab")
    st.caption("Tracks each eligible signal once, at its first observed daily close, then records what happened over 1, 3, 5, 10 and 20 subsequent trading sessions. Results update as new daily bars arrive.")
    if st.button("↻ Refresh validation data", key="refresh_validation_events"):
        load_strategy_signal_events.clear()
        load_latest_cloud_scan.clear()
    try:
        validation_events = load_strategy_signal_events()
    except Exception as exc:
        validation_events = []
        st.error(f"Could not load signal observations: {exc}")
    outcome_rows = []
    for event in validation_events:
        outcomes = event.get("outcomes") or {}
        for horizon, result in outcomes.items():
            if str(horizon).startswith("_") or not isinstance(result, dict):
                continue
            row = {
                "Symbol": event.get("symbol"),
                "Signal date": event.get("signal_date"),
                "Setup": event.get("setup_type"),
                "Signal": event.get("signal"),
                "Regime": event.get("market_regime"),
                "Horizon": horizon,
                "Return %": result.get("close_return_pct"),
                "MFE %": result.get("mfe_pct"),
                "MAE %": result.get("mae_pct"),
                "SPY return %": result.get("spy_return_pct"),
                "Excess vs SPY (pp)": result.get("excess_vs_spy_pp"),
                "Win": result.get("win"),
                "Stop/target result": (result.get("stop_target_test") or {}).get("result"),
                "Stop/target session": (result.get("stop_target_test") or {}).get("session"),
                "Rule return %": (result.get("stop_target_test") or {}).get("strategy_return_pct"),
            }
            outcome_rows.append(row)
    shadow_rows = []
    for event in validation_events:
        outcomes = event.get("outcomes") or {}
        snapshot = outcomes.get("_shadow_opportunity") if isinstance(outcomes, dict) else None
        if not isinstance(snapshot, dict):
            continue
        try:
            score = float(snapshot.get("shadow_opportunity_score"))
        except (TypeError, ValueError, OverflowError):
            continue
        if not np.isfinite(score):
            continue
        lower = min(90, int(max(0, min(100, score)) // 10) * 10)
        score_band = "00-49" if lower < 50 else (f"{lower:02d}-100" if lower == 90 else f"{lower:02d}-{lower+9}")
        for horizon in ("5d", "10d", "20d"):
            result = outcomes.get(horizon)
            if not isinstance(result, dict) or result.get("close_return_pct") is None:
                continue
            shadow_rows.append({
                "Symbol": event.get("symbol"), "Signal date": event.get("signal_date"),
                "Setup": event.get("setup_type"), "Regime": event.get("market_regime"),
                "Shadow score band": score_band, "Horizon": horizon,
                "Return %": result.get("close_return_pct"),
                "Excess vs SPY (pp)": result.get("excess_vs_spy_pp"),
                "Win": result.get("win"),
            })
    if shadow_rows:
        st.markdown("#### 🧠 Shadow opportunity score: realized forward performance")
        shadow_df = pd.DataFrame(shadow_rows)
        shadow_summary = (shadow_df.groupby(
            ["Setup", "Regime", "Shadow score band", "Horizon"], dropna=False
        ).agg(
            Events=("Return %", "count"),
            Win_rate_pct=("Win", lambda x: 100.0 * x.dropna().astype(bool).mean() if x.dropna().size else np.nan),
            Avg_return_pct=("Return %", "mean"),
            Median_return_pct=("Return %", "median"),
            Avg_excess_vs_SPY_pp=("Excess vs SPY (pp)", "mean"),
        ).reset_index())
        shadow_summary["Evidence"] = np.where(shadow_summary["Events"] >= 30, "SUPPORTED (n≥30)", "LOW SAMPLE")
        st.dataframe(shadow_summary.style.format({
            "Win_rate_pct":"{:.1f}%", "Avg_return_pct":"{:+.2f}%",
            "Median_return_pct":"{:+.2f}%", "Avg_excess_vs_SPY_pp":"{:+.2f}%"
        }, na_rep="—"), use_container_width=True, hide_index=True)
        st.caption("Scores are frozen at first observation. Results are descriptive, regime-conditioned and de-overlapped only in the worker's reliability summary; this raw table is not de-overlapped. A 30-event threshold is an evidence label, not proof of predictive edge. Shadow scores have no trading authority.")
    else:
        st.info("Shadow opportunity validation is collecting frozen scores and matured outcomes. Results will appear as 5-, 10- and 20-session outcomes mature.")

    st.markdown("#### 🧪 De-overlapped worker validation")
    try:
        latest_validation_scan = load_latest_cloud_scan()
        shadow_validation = ((latest_validation_scan or {}).get("ai_review") or {}).get("shadow_opportunity_validation") or {}
    except Exception as exc:
        shadow_validation = {}
        st.caption(f"Could not load the worker's de-overlapped validation snapshot: {exc}")
    if shadow_validation.get("summaries"):
        st.caption(
            f"Worker snapshot: {shadow_validation.get('status', '—')} · "
            f"{shadow_validation.get('deoverlapped_event_count', 0):,} de-overlapped scored events · "
            f"{shadow_validation.get('minimum_sample_count', 30)} observations required per supported group · "
            f"{shadow_validation.get('cooldown_sessions', 20)}-session same-symbol/setup cooldown."
        )
        deoverlap_rows = []
        for item in shadow_validation.get("summaries") or []:
            deoverlap_rows.append({
                "Setup": item.get("setup_type"),
                "Regime": item.get("market_regime"),
                "Score band": item.get("score_bucket"),
                "Horizon": f"{item.get('horizon_sessions')} sessions",
                "Events": item.get("sample_count"),
                "Evidence": item.get("sample_status"),
                "Win rate": item.get("win_rate_pct"),
                "95% Wilson low": item.get("win_rate_wilson_95_low_pct"),
                "95% Wilson high": item.get("win_rate_wilson_95_high_pct"),
                "Avg return": item.get("average_forward_return_pct"),
                "Median return": item.get("median_forward_return_pct"),
                "Avg excess vs SPY": item.get("average_excess_vs_spy_pp"),
                "Benchmark n": item.get("benchmark_matched_count"),
                "Avg net @20bps": (item.get("cost_sensitivity_round_trip") or {}).get("20bps", {}).get("average_return_pct"),
                "Win @20bps": (item.get("cost_sensitivity_round_trip") or {}).get("20bps", {}).get("win_rate_pct"),
                "Avg net @40bps": (item.get("cost_sensitivity_round_trip") or {}).get("40bps", {}).get("average_return_pct"),
                "Win @40bps": (item.get("cost_sensitivity_round_trip") or {}).get("40bps", {}).get("win_rate_pct"),
                "Avg net @60bps": (item.get("cost_sensitivity_round_trip") or {}).get("60bps", {}).get("average_return_pct"),
                "Win @60bps": (item.get("cost_sensitivity_round_trip") or {}).get("60bps", {}).get("win_rate_pct"),
            })
        deoverlap_df = pd.DataFrame(deoverlap_rows)
        st.dataframe(deoverlap_df.style.format({
            "Win rate": "{:.1f}%", "95% Wilson low": "{:.1f}%",
            "95% Wilson high": "{:.1f}%", "Avg return": "{:+.2f}%",
            "Median return": "{:+.2f}%", "Avg excess vs SPY": "{:+.2f}%", "Avg net @20bps": "{:+.2f}%", "Win @20bps": "{:.1f}%", "Avg net @40bps": "{:+.2f}%", "Win @40bps": "{:.1f}%", "Avg net @60bps": "{:+.2f}%", "Win @60bps": "{:.1f}%",
        }, na_rep="—"), use_container_width=True, hide_index=True)
        st.caption(
            "This is the worker's de-overlapped, regime-conditioned summary. Wilson intervals describe historical win-rate uncertainty; "
            "they are not calibrated probabilities. Cross-symbol dependence and changing market conditions remain. "
            "The 20/40/60 bps columns are flat assumed round-trip cost sensitivities, not measured fills or a complete execution model. "
            "A supported sample label is not proof of edge. Shadow validation has no authority over ranking, sizing, gates or orders."
        )

        period_rows = shadow_validation.get("period_stability", {}).get("summaries") or []
        if period_rows:
            st.markdown("##### Calendar-year stability")
            period_df = pd.DataFrame([{
                "Setup": item.get("setup_type"), "Score band": item.get("score_bucket"), "Regime": item.get("market_regime"),
                "Signal year": item.get("signal_year"), "Horizon": str(item.get("horizon_sessions")) + " sessions",
                "Events": item.get("sample_count"), "Evidence": item.get("sample_status"),
                "Win rate": item.get("win_rate_pct"), "Average return": item.get("average_forward_return_pct"),
                "Median return": item.get("median_forward_return_pct"),
                "Average excess vs SPY": item.get("average_excess_vs_spy_pp"),
            } for item in period_rows])
            st.dataframe(period_df.style.format({"Win rate": "{:.1f}%", "Average return": "{:+.2f}%", "Median return": "{:+.2f}%", "Average excess vs SPY": "{:+.2f}%"}, na_rep="—"), use_container_width=True, hide_index=True)
            st.caption("Calendar year is assigned by signal date. This exposes time variation; it is not a forward holdout or proof of persistence.")

        selection_research = shadow_validation.get("strategy_selection_research") or {}
        selection_rows = selection_research.get("summaries") or []
        st.markdown("##### Evidence-based strategy research screen")
        if selection_rows:
            selection_df = pd.DataFrame([{
                "Assessment": item.get("assessment"),
                "Setup": item.get("setup_type"),
                "Score band": item.get("score_bucket"),
                "Regime": item.get("market_regime"),
                "Horizon": str(item.get("horizon_sessions")) + " sessions",
                "Events": item.get("sample_count"),
                "Net avg @40bps": item.get("average_net_return_40bps_pct"),
                "Benchmark n": item.get("benchmark_matched_count"),
                "Supported years": item.get("supported_year_count"),
                "Positive years": item.get("positive_net_year_count"),
                "Spearman": item.get("score_return_spearman"),
            } for item in selection_rows])
            st.dataframe(selection_df.style.format({"Net avg @40bps": "{:+.2f}%", "Spearman": "{:+.3f}"}, na_rep="—"), use_container_width=True, hide_index=True)
            st.caption(
                "ROBUST RESEARCH CANDIDATE is deliberately difficult to earn: minimum sample and benchmark coverage, "
                "positive average return after assumed 40 bps round-trip costs, at least two supported calendar years "
                "with every supported year positive after costs, and positive score/return rank association. "
                "This is a retrospective research filter, not an optimizer, recommendation, or authorization to trade."
            )
        else:
            st.info("No strategy combination currently qualifies for the research screen. Insufficient evidence is a valid result.")

        holdout_rows = (shadow_validation.get("temporal_holdout_validation") or {}).get("summaries") or []
        st.markdown("##### Chronological out-of-sample holdout")
        if holdout_rows:
            holdout_df = pd.DataFrame([{
                "Assessment": item.get("assessment"), "Setup": item.get("setup_type"),
                "Score band": item.get("score_bucket"), "Regime": item.get("market_regime"),
                "Horizon": str(item.get("horizon_sessions")) + " sessions",
                "Reference n": item.get("reference_sample_count"),
                "Holdout n": item.get("holdout_sample_count"),
                "Holdout net avg @40bps": item.get("holdout_average_net_return_40bps_pct"),
                "Holdout win rate @40bps": item.get("holdout_win_rate_after_40bps_pct"),
                "Benchmark n": item.get("holdout_benchmark_matched_count"),
                "Holdout excess vs SPY": item.get("holdout_average_excess_vs_spy_pp"),
            } for item in holdout_rows])
            st.dataframe(holdout_df.style.format({
                "Holdout net avg @40bps": "{:+.2f}%",
                "Holdout win rate @40bps": "{:.1f}%",
                "Holdout excess vs SPY": "{:+.2f}pp",
            }, na_rep="—"), use_container_width=True, hide_index=True)
            holdout_meta = shadow_validation.get("temporal_holdout_validation") or {}
            st.caption(
                f"Chronological split boundary: {holdout_meta.get('holdout_start_signal_date') or 'unavailable'}. "
                "The final 30% of unique signal dates is held out from the first 70%; same-day events stay together. "
                "This is a time-ordered historical holdout, not a guarantee of independence from prior research or future performance."
            )
        else:
            st.info("Not enough distinct signal dates to construct a chronological holdout.")

        decay_rows = (shadow_validation.get("strategy_decay_monitor") or {}).get("summaries") or []
        st.markdown("##### Strategy decay / deterioration monitor")
        if decay_rows:
            decay_df = pd.DataFrame([{
                "Assessment": item.get("assessment"), "Setup": item.get("setup_type"),
                "Score band": item.get("score_bucket"), "Regime": item.get("market_regime"),
                "Horizon": str(item.get("horizon_sessions")) + " sessions",
                "Older n": item.get("older_sample_count"), "Recent n": item.get("recent_sample_count"),
                "Older net avg @40bps": item.get("older_average_net_return_40bps_pct"),
                "Recent net avg @40bps": item.get("recent_average_net_return_40bps_pct"),
                "Older net excess vs SPY": item.get("older_average_net_excess_vs_spy_40bps_pp"),
                "Recent net excess vs SPY": item.get("recent_average_net_excess_vs_spy_40bps_pp"),
                "Excess change": item.get("change_percentage_points"),
                "95% CI low": item.get("change_ci_95_low_pp"),
                "95% CI high": item.get("change_ci_95_high_pp"),
                "Matched days old/new": f"{item.get('older_benchmark_matched_days', 0)}/{item.get('recent_benchmark_matched_days', 0)}",
            } for item in decay_rows])
            st.dataframe(decay_df.style.format({
                "Older net avg @40bps": "{:+.2f}%",
                "Recent net avg @40bps": "{:+.2f}%",
                "Older net excess vs SPY": "{:+.2f}pp",
                "Recent net excess vs SPY": "{:+.2f}pp",
                "Excess change": "{:+.2f}pp",
                "95% CI low": "{:+.2f}pp",
                "95% CI high": "{:+.2f}pp",
            }, na_rep="—"), use_container_width=True, hide_index=True)
            st.caption(
                "Decay warnings use per-signal-date averages, require sufficient SPY-matched dates in both halves, "
                "and require positive older net excess plus at least 0.50pp deterioration with the approximate 95% "
                "horizon-aware Newey-West HAC interval below zero. Same-day symbols are grouped together and "
                "serial dependence up to horizon minus one is allowed for. This is exploratory, not a "
                "formal hypothesis test or fully cross-sectionally cluster-robust; warnings never disable strategies."
            )

        association_rows = shadow_validation.get("score_return_association", {}).get("summaries") or []
        if association_rows:
            st.markdown("##### Does a higher score rank better?")
            association_df = pd.DataFrame([{
                "Setup": item.get("setup_type"), "Regime": item.get("market_regime"),
                "Horizon": str(item.get("horizon_sessions")) + " sessions", "Events": item.get("sample_count"),
                "Evidence": item.get("sample_status"), "Score/return Spearman": item.get("score_return_spearman"),
            } for item in association_rows])
            st.dataframe(association_df.style.format({"Score/return Spearman": "{:+.3f}"}, na_rep="—"), use_container_width=True, hide_index=True)
            st.caption("Spearman measures rank association between frozen score and realized return within setup/regime/horizon. Positive is directionally encouraging, near zero means weak ordering, and negative means higher scores tended to fare worse. It is descriptive, not a calibrated probability or causal result.")
    else:
        st.info(
            "No persisted de-overlapped shadow summary is available yet. It will appear after a worker scan successfully "
            "updates the signal ledger and saves its validation snapshot."
        )

    if validation_events:
        total_events = len(validation_events)
        completed_5d = sum(1 for r in outcome_rows if r["Horizon"] == "5d")
        completed_20d = sum(1 for r in outcome_rows if r["Horizon"] == "20d")
        latest_capture = max((str(e.get("created_at") or "") for e in validation_events), default="")
        latest_signal_date = max((str(e.get("signal_date") or "") for e in validation_events), default="")
        st.caption(f"Pipeline status: {total_events:,} observations saved · newest signal date {latest_signal_date or '—'} · latest database capture {latest_capture or '—'}")
        v1, v2, v3, v4 = st.columns(4)
        v1.metric("Unique signal events", f"{total_events:,}")
        v2.metric("With 5-session result", f"{completed_5d:,}")
        v3.metric("With 20-session result", f"{completed_20d:,}")
        v4.metric("Awaiting outcomes", f"{total_events - completed_20d:,}")
        st.markdown("#### Realized forward outcomes by setup and horizon")
        if outcome_rows:
            outcomes_df = pd.DataFrame(outcome_rows)
            summary = (outcomes_df.groupby(["Setup", "Regime", "Horizon"], dropna=False)
                       .agg(Events=("Win", "count"),
                            Win_rate_pct=("Win", lambda x: 100.0 * x.dropna().astype(bool).mean() if x.dropna().size else np.nan),
                            Avg_return_pct=("Return %", "mean"),
                            Median_return_pct=("Return %", "median"),
                            Avg_MFE_pct=("MFE %", "mean"),
                            Avg_MAE_pct=("MAE %", "mean"),
                            Avg_excess_vs_SPY_pp=("Excess vs SPY (pp)", "mean"),
                            Rule_avg_return_pct=("Rule return %", "mean"),
                            Target_hits=("Stop/target result", lambda x: int((x == "TARGET").sum())),
                            Stop_hits=("Stop/target result", lambda x: int((x == "STOP").sum())),
                            Ambiguous_bars=("Stop/target result", lambda x: int((x == "AMBIGUOUS_SAME_DAY").sum())))
                       .reset_index()
                       .sort_values(["Setup", "Horizon", "Regime"]))
            st.dataframe(summary.style.format({
                "Win_rate_pct":"{:.1f}%", "Avg_return_pct":"{:+.2f}%",
                "Median_return_pct":"{:+.2f}%", "Avg_MFE_pct":"{:+.2f}%",
                "Avg_MAE_pct":"{:+.2f}%", "Avg_excess_vs_SPY_pp":"{:+.2f}%",
                "Rule_avg_return_pct":"{:+.2f}%"
            }, na_rep="—"), use_container_width=True, hide_index=True)

            # Evidence-qualified edge view: shared pure helpers mirror worker
            # score buckets and symbol/setup de-overlap. Still close-to-close only.
            evidence_events = deoverlap_events(validation_events, cooldown_sessions=20)

            edge_rows = build_edge_diagnostics(evidence_events)
            if edge_rows:
                edge_summary = pd.DataFrame(edge_rows)
                st.markdown("#### Evidence-qualified net-edge diagnostics")
                st.caption(
                    "20-session de-overlap per symbol/setup; "
                    + f"{len(evidence_events):,} retained events. Groups use the worker-aligned "
                    "5/10/20-session horizons, setup-score bands (00–49, 50–59 … 90–100), "
                    "and signal-time regime. Net scenarios subtract assumed round-trip costs "
                    "of 10/20/40/60 bps from historical close-to-close means. Return support "
                    "requires 30 observations; benchmark-excess support requires 20 matched "
                    "SPY observations. Unsupported values are exploratory, not validated edge."
                )
                st.dataframe(edge_summary.style.format({
                    "Gross_mean_return_pct": "{:+.2f}%",
                    "Gross_mean_excess_pp": "{:+.2f}pp",
                    "Mean return after 10bp %": "{:+.2f}%",
                    "Mean return after 20bp %": "{:+.2f}%",
                    "Mean return after 40bp %": "{:+.2f}%",
                    "Mean return after 60bp %": "{:+.2f}%",
                    "Mean excess after 20bp pp": "{:+.2f}pp",
                }, na_rep="—"), use_container_width=True, hide_index=True)
            else:
                st.info("Not enough matured, valid forward returns to calculate de-overlapped net-edge diagnostics.")
            st.markdown("#### Latest completed signal outcomes")
            recent = outcomes_df.sort_values(["Signal date", "Symbol"], ascending=[False, True]).head(100)
            st.dataframe(recent.style.format({
                "Return %":"{:+.2f}%", "MFE %":"{:+.2f}%", "MAE %":"{:+.2f}%",
                "SPY return %":"{:+.2f}%", "Excess vs SPY (pp)":"{:+.2f}%",
                "Rule return %":"{:+.2f}%"
            }, na_rep="—"), use_container_width=True, hide_index=True)
        else:
            st.info("Signals have been recorded. Forward-outcome columns will populate after enough subsequent daily sessions have elapsed.")
        st.caption("A signal is recorded once per symbol, date and setup, using a hypothetical entry at that signal-day close, a 1.5-ATR stop and a 2R target. Horizons use the next completed daily sessions. MFE/MAE are intraperiod excursions. Stop/target checks use daily OHLC, with same-day double touches marked ambiguous. Benchmark excess is close-to-close versus SPY. This is a rule simulation, not confirmed executable fills.")
    else:
        st.info("No signal observations have been recorded yet. The cloud worker will begin populating this table on its next successful market scan.")
    st.markdown("#### Validation methodology")
    st.write("- First-seen eligible BUY CANDIDATE and WATCH signals with PULLBACK WATCH or BREAKOUT WATCH setups are frozen at their initial daily close.")
    st.write("- Market regime is captured at signal time using SPY's 50/200-day trend and 20-day return.")
    st.write("- Each event is followed for 1, 3, 5, 10 and 20 subsequent trading sessions.")
    st.write("- Returns are compared with SPY over the same horizon; MFE and MAE show the best and worst observed price excursion.")
    st.warning("Stop/target results use daily OHLC bars: if both levels are touched in the same session, that event is marked ambiguous rather than guessing which came first. Gap fills are approximated from the daily open. The test still excludes slippage, commissions, taxes, dividends, partial fills and portfolio constraints. Signals can overlap, and the universe is curated rather than survivorship-bias-free. Do not interpret these statistics as proof of a tradable edge.")


with cloud_tab:
    @st.fragment(run_every="60s")
    def render_cloud_scanner():
        st.subheader("☁️ Cloud market scanner")
        st.caption("Dashboard V3.44 · Cloud worker version is reported with the latest saved scan when available.")
        st.caption(
            "Latest rules-based scan produced by the Render background worker and saved in Supabase. "
            "Uses Yahoo Finance daily bars; this is a screening report, not an AI verdict or trade instruction."
        )
        refresh_cloud = st.button("Refresh cloud results", key="refresh_cloud_results")
        if refresh_cloud:
            load_latest_cloud_scan.clear()
            load_latest_paper_trade_decisions.clear()
            load_latest_paper_execution_guardrail.clear()
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
            scan_health = (cloud_scan.get("ai_review") or {}).get("scan_health") or {}
            if scan_health:
                st.markdown("#### 🩺 Scan health & data coverage")
                h1, h2, h3, h4 = st.columns(4)
                h1.metric("Usable symbols", f"{scan_health.get('analyzed_symbols', 0)}/{scan_health.get('requested_symbols', 0)}")
                h2.metric("Coverage", f"{scan_health.get('coverage_pct', 0):.1f}%")
                h3.metric("Stale symbols", int(scan_health.get("stale_count", 0)))
                h4.metric("Latest price date", str(scan_health.get("latest_price_date") or "Unavailable"))
                missing_details = scan_health.get("missing_details") or []
                missing_symbols = scan_health.get("missing_symbols") or []
                if missing_symbols:
                    with st.expander(f"Symbols without usable history ({len(missing_symbols)})"):
                        if missing_details:
                            st.dataframe(pd.DataFrame(missing_details).rename(columns={"symbol": "Symbol", "reason": "Why unavailable"}), use_container_width=True, hide_index=True)
                        else:
                            st.write(", ".join(missing_symbols))
                stale_symbols = scan_health.get("stale_symbols") or []
                if stale_symbols:
                    with st.expander(f"Potentially stale daily prices ({len(stale_symbols)})"):
                        st.dataframe(pd.DataFrame(stale_symbols).rename(columns={"symbol": "Symbol", "price_date": "Price date", "age_calendar_days": "Age (calendar days)", "threshold_days": "Warning threshold (days)", "reason": "Why flagged"}), use_container_width=True, hide_index=True)
                status = scan_health.get("status", "UNKNOWN")
                if status == "COMPLETE":
                    st.success("All requested symbols analyzed; no prices crossed the freshness warning thresholds.")
                elif status in ("PARTIAL_AND_STALE", "PARTIAL", "STALE"):
                    st.warning(f"Data-quality status: {status}. Review missing symbols and stale prices before relying on rankings.")
                st.caption(scan_health.get("freshness_method", "Freshness warnings use calendar-day thresholds and may need holiday/provider context."))
                st.caption(scan_health.get("note", "Coverage is based on symbols with sufficient usable daily history."))

            st.divider()
            st.markdown("### 🛰️ Alpaca live paper account")
            st.caption(
                "Broker-reported account, holdings, and orders from the Alpaca paper API. "
                "Read-only GET data persisted by the cloud worker; separate from the dashboard's $1,000 virtual simulation."
            )
            refresh_broker = st.button("↻ Refresh broker snapshot", key="refresh_alpaca_broker_snapshot")
            if refresh_broker:
                load_latest_alpaca_paper_account_snapshot.clear()
            try:
                broker_snapshot = load_latest_alpaca_paper_account_snapshot()
            except Exception as exc:
                broker_snapshot = None
                st.error("The Alpaca paper-account snapshot could not be loaded.")
                st.caption(f"Technical detail: {exc}")

            if not broker_snapshot:
                st.info(
                    "No persisted Alpaca broker snapshot is available yet. "
                    "The worker must be running with the new snapshot migration applied before live broker values appear."
                )
            else:
                snapshot_time = broker_snapshot.get("snapshot_fetched_at")
                snapshot_age_seconds = None
                try:
                    fetched_dt = pd.to_datetime(snapshot_time, utc=True)
                    snapshot_age_seconds = max(0.0, (pd.Timestamp.now(tz="UTC") - fetched_dt).total_seconds())
                except Exception:
                    pass
                if snapshot_age_seconds is None:
                    st.warning("Broker snapshot timestamp is invalid; freshness cannot be verified.")
                elif snapshot_age_seconds > 180:
                    st.warning(f"Broker snapshot is stale ({snapshot_age_seconds / 60:.1f} minutes old). Do not treat these values as current.")
                else:
                    st.success(f"Latest Alpaca paper snapshot · {snapshot_age_seconds:.0f}s old")
                st.caption(
                    f"Source: {broker_snapshot.get('source') or 'Alpaca paper API'} · "
                    f"Fetched: {snapshot_time or 'unknown'} · Persisted: {broker_snapshot.get('updated_at') or 'unknown'}"
                )
                if str(broker_snapshot.get("status") or "").upper() not in ("ACTIVE", "ACTIVE_TRADING"):
                    st.warning(f"Alpaca account status: {broker_snapshot.get('status') or 'UNKNOWN'}")

                def broker_money(value):
                    try:
                        return f"{float(value):,.2f}"
                    except (TypeError, ValueError):
                        return "Unavailable"

                a1, a2, a3, a4 = st.columns(4)
                a1.metric("Broker equity", ("$" + broker_money(broker_snapshot.get("equity"))) if broker_snapshot.get("equity") is not None else "Unavailable")
                a2.metric("Cash", ("$" + broker_money(broker_snapshot.get("cash"))) if broker_snapshot.get("cash") is not None else "Unavailable")
                a3.metric("Buying power", ("$" + broker_money(broker_snapshot.get("buying_power"))) if broker_snapshot.get("buying_power") is not None else "Unavailable")
                a4.metric("Portfolio value", ("$" + broker_money(broker_snapshot.get("portfolio_value"))) if broker_snapshot.get("portfolio_value") is not None else "Unavailable")
                market_state = "OPEN" if broker_snapshot.get("is_market_open") is True else "CLOSED" if broker_snapshot.get("is_market_open") is False else "UNKNOWN"
                st.caption(
                    f"Broker status: {broker_snapshot.get('status') or 'Unknown'} · "
                    f"Market clock: {market_state} · "
                    f"Next open: {broker_snapshot.get('next_open') or '—'} · "
                    f"Next close: {broker_snapshot.get('next_close') or '—'} · "
                    f"Currency: {broker_snapshot.get('currency') or '—'}"
                )

                positions = broker_snapshot.get("positions") or []
                st.markdown(f"#### Open positions ({len(positions)})")
                if positions:
                    position_df = pd.DataFrame(positions)
                    position_columns = [x for x in [
                        "symbol", "qty", "side", "avg_entry_price", "current_price",
                        "market_value", "cost_basis", "unrealized_pl", "unrealized_plpc",
                        "asset_class", "change_today"
                    ] if x in position_df.columns]
                    position_df = position_df[position_columns].rename(columns={
                        "symbol": "Symbol", "qty": "Quantity", "side": "Side",
                        "avg_entry_price": "Avg entry", "current_price": "Current price",
                        "market_value": "Market value", "cost_basis": "Cost basis",
                        "unrealized_pl": "Unrealized P/L", "unrealized_plpc": "Unrealized P/L %",
                        "asset_class": "Asset class", "change_today": "Today's change"
                    })
                    st.dataframe(position_df, use_container_width=True, hide_index=True)
                else:
                    st.info("Alpaca reports no open positions.")

                open_orders = broker_snapshot.get("open_orders") or []
                st.markdown(f"#### Working orders ({len(open_orders)})")
                if open_orders:
                    order_rows = []
                    for order in open_orders:
                        order_rows.append({
                            "Symbol": order.get("symbol"), "Side": order.get("side"),
                            "Status": order.get("status"), "Type": order.get("type"),
                            "Quantity": order.get("qty"), "Filled": order.get("filled_qty"),
                            "Limit price": order.get("limit_price"), "Stop price": order.get("stop_price"),
                            "Order class": order.get("order_class"), "Order ID": order.get("id"),
                            "Submitted": order.get("submitted_at")
                        })
                        for leg in order.get("legs") or []:
                            if isinstance(leg, dict):
                                order_rows.append({
                                    "Symbol": leg.get("symbol") or order.get("symbol"),
                                    "Side": leg.get("side"), "Status": leg.get("status"),
                                    "Type": leg.get("type"), "Quantity": leg.get("qty"),
                                    "Filled": leg.get("filled_qty"), "Limit price": leg.get("limit_price"),
                                    "Stop price": leg.get("stop_price"),
                                    "Order class": "BRACKET LEG", "Order ID": leg.get("id"),
                                    "Submitted": leg.get("submitted_at")
                                })
                    st.dataframe(pd.DataFrame(order_rows), use_container_width=True, hide_index=True)
                else:
                    st.info("Alpaca reports no currently working orders.")

                recent_orders = broker_snapshot.get("recent_orders") or []
                st.markdown(f"#### Recent order history ({len(recent_orders)} of up to 100)")
                if recent_orders:
                    recent_df = pd.DataFrame(recent_orders)
                    recent_columns = [x for x in [
                        "symbol", "side", "lifecycle_state", "type", "order_class",
                        "qty", "filled_qty", "remaining_qty", "filled_avg_price",
                        "limit_price", "stop_price", "submitted_at", "updated_at", "filled_at",
                        "canceled_at", "id", "replaces", "replaced_by"
                    ] if x in recent_df.columns]
                    recent_df = recent_df[recent_columns].rename(columns={
                        "symbol": "Symbol", "side": "Side", "lifecycle_state": "Lifecycle",
                        "type": "Type", "order_class": "Order class", "qty": "Quantity",
                        "filled_qty": "Filled", "remaining_qty": "Remaining",
                        "filled_avg_price": "Avg fill price", "limit_price": "Limit price",
                        "stop_price": "Stop price", "submitted_at": "Submitted",
                        "updated_at": "Updated", "filled_at": "Filled at",
                        "canceled_at": "Canceled at", "id": "Order ID",
                        "replaces": "Replaces", "replaced_by": "Replaced by"
                    })
                    st.dataframe(recent_df, use_container_width=True, hide_index=True)
                else:
                    st.info("No recent broker order history was included in this snapshot.")
                st.caption(
                    "Broker values are reported by Alpaca paper trading, not simulated. "
                    "This panel does not submit, replace, or cancel orders. "
                    "Unrealized P/L is broker-reported; realized P/L is not inferred from account equity."
                )

            st.divider()
            st.markdown("### 🤖 Alpaca paper-trading decisions")
            st.caption(
                "Read-only decision audit from the separate Alpaca paper workflow. "
                "Fresh quotes and risk gates are evaluated by the cloud worker. "
                "The order switch remains OFF until the full broker lifecycle is validated and explicitly enabled."
            )
            try:
                decision_rows = load_latest_paper_trade_decisions()
            except Exception as exc:
                decision_rows = []
                st.warning("Paper decision history is not available yet.")
                st.caption(f"Technical detail: {exc}")
            try:
                guardrail = load_latest_paper_execution_guardrail()
            except Exception as exc:
                guardrail = None
                st.warning("Alpaca daily-loss guardrail status is unavailable.")
                st.caption(f"Technical detail: {exc}")
            if guardrail:
                st.markdown("#### 🛡️ Alpaca paper risk guardrail")
                g1, g2, g3, g4 = st.columns(4)
                g1.metric("Daily P&L", f"${float(guardrail.get('daily_pnl') or 0):,.2f}")
                g2.metric("Daily loss", f"{float(guardrail.get('daily_loss_pct') or 0):.2f}%")
                g3.metric("Starting equity", f"${float(guardrail.get('starting_equity') or 0):,.2f}")
                g4.metric("Entry circuit breaker", "HALTED" if guardrail.get("halted") else "CLEAR")
                if guardrail.get("halted"):
                    st.warning(f"New paper entries are blocked: {guardrail.get('halt_reason') or 'Daily loss guardrail active'}.")
                st.caption(f"Trading date: {guardrail.get('trading_date')} · Updated: {guardrail.get('updated_at')}")
            else:
                st.info("No Alpaca daily-loss guardrail snapshot has been recorded yet.")

            if decision_rows:
                decision_df = pd.DataFrame(decision_rows)
                statuses = decision_df.get("status", pd.Series(dtype=str)).fillna("UNKNOWN")
                ready_count = int(statuses.isin(["READY_NOT_SUBMITTED", "READY_FOR_PAPER_ORDER"]).sum())
                broker_lifecycle_count = int((statuses.str.startswith("BROKER_") & ~statuses.eq("BROKER_UNKNOWN")).sum())
                submitted_count = int(statuses.isin(["ORDER_SUBMITTED", "ORDER_ALREADY_EXISTS"]).sum()) + broker_lifecycle_count
                blocked_count = int(statuses.eq("BLOCKED").sum())
                invalid_broker_data_count = int(statuses.eq("BROKER_DATA_INVALID").sum())

                def _lifecycle_columns(item):
                    decision = item.get("decision") if isinstance(item.get("decision"), dict) else {}
                    lifecycle = decision.get("broker_lifecycle") if isinstance(decision.get("broker_lifecycle"), dict) else {}
                    legs = lifecycle.get("legs") if isinstance(lifecycle.get("legs"), list) else []
                    exit_states = [str(leg.get("lifecycle_state") or "UNKNOWN") for leg in legs if isinstance(leg, dict)]
                    protection = decision.get("position_protection") if isinstance(decision.get("position_protection"), dict) else {}
                    quantity_validation = decision.get("broker_quantity_validation", "UNAVAILABLE")
                    replacement = decision.get("broker_replacement_chain") if isinstance(decision.get("broker_replacement_chain"), dict) else {}
                    protection_order_id = decision.get("broker_protection_order_id")
                    stop_leg = protection.get("stop") if isinstance(protection.get("stop"), dict) else {}
                    target_leg = protection.get("target") if isinstance(protection.get("target"), dict) else {}
                    return pd.Series({
                        "broker_state": lifecycle.get("lifecycle_state"),
                        "broker_quantity_validation": quantity_validation,
                        "replacement_chain_status": replacement.get("status"),
                        "replacement_chain_order_ids": " → ".join(str(x) for x in replacement.get("order_ids", [])),
                        "protection_order_id": protection_order_id,
                        "filled_shares": lifecycle.get("filled_qty"),
                        "remaining_shares": lifecycle.get("remaining_qty"),
                        "exit_leg_states": ", ".join(exit_states),
                        "position_protection_status": protection.get("status"),
                        "position_protection_reason": protection.get("reason"),
                        "position_qty": protection.get("position_qty"),
                        "stop_exit_qty": stop_leg.get("remaining_qty"),
                        "target_exit_qty": target_leg.get("remaining_qty"),
                    })

                lifecycle_df = decision_df.apply(_lifecycle_columns, axis=1)

                def _portfolio_exposure_columns(item):
                    decision = item.get("decision") if isinstance(item.get("decision"), dict) else {}
                    return pd.Series({
                        "current_gross_exposure_dollars": decision.get("current_gross_exposure_dollars"),
                        "gross_exposure_limit_dollars": decision.get("gross_exposure_limit_dollars"),
                        "remaining_gross_exposure_dollars": decision.get("remaining_gross_exposure_dollars"),
                        "gross_exposure_utilization_pct": decision.get("gross_exposure_utilization_pct"),
                        "largest_existing_position_symbol": decision.get("largest_existing_position_symbol"),
                        "largest_existing_position_dollars": decision.get("largest_existing_position_dollars"),
                        "largest_existing_position_pct_equity": decision.get("largest_existing_position_pct_equity"),
                        "candidate_position_pct_equity": decision.get("candidate_position_pct_equity"),
                        "projected_gross_exposure_dollars": decision.get("projected_gross_exposure_dollars"),
                        "projected_largest_position_pct_equity": decision.get("projected_largest_position_pct_equity"),
                        "current_aggregate_open_risk_dollars": decision.get("current_aggregate_open_risk_dollars"),
                        "aggregate_open_risk_limit_dollars": decision.get("aggregate_open_risk_limit_dollars"),
                        "remaining_aggregate_open_risk_dollars": decision.get("remaining_aggregate_open_risk_dollars"),
                        "aggregate_open_risk_utilization_pct": decision.get("aggregate_open_risk_utilization_pct"),
                        "projected_aggregate_open_risk_dollars": decision.get("projected_aggregate_open_risk_dollars"),
                        "aggregate_open_risk_utilization_after_candidate_pct": decision.get("aggregate_open_risk_utilization_after_candidate_pct"),
                        "projected_aggregate_open_risk_pct_equity": decision.get("projected_aggregate_open_risk_pct_equity"),
                        "candidate_incremental_stop_risk_pct_equity": decision.get("candidate_incremental_stop_risk_pct_equity"),
                        "candidate_share_of_risk_budget_pct": decision.get("candidate_share_of_risk_budget_pct"),
                        "candidate_share_of_projected_open_risk_pct": decision.get("candidate_share_of_projected_open_risk_pct"),
                        "projected_gross_exposure_utilization_pct": decision.get("projected_gross_exposure_utilization_pct"),
                        "candidate_incremental_gross_exposure_pct_equity": decision.get("candidate_incremental_gross_exposure_pct_equity"),
                        "opportunity_model_status": decision.get("opportunity_model_status"),
                        "shadow_opportunity_score": decision.get("shadow_opportunity_score"),
                        "shadow_opportunity_components": decision.get("shadow_opportunity_components"),
                        "shadow_opportunity_component_count": decision.get("shadow_opportunity_component_count"),
                        "historical_reliability_status": decision.get("historical_reliability_status"),
                        "historical_reliability_supported_horizons": decision.get("historical_reliability_supported_horizons"),
                        "historical_reliability_best_supported_sample_count": decision.get("historical_reliability_best_supported_sample_count"),
                        "shadow_opportunity_policy_effect": decision.get("shadow_opportunity_policy_effect"),
                        "prior_candidate_reserved_risk_dollars": decision.get("prior_candidate_reserved_risk_dollars"),
                        "prior_candidate_reserved_count": decision.get("prior_candidate_reserved_count"),
                        "candidate_reserved_risk_dollars": decision.get("candidate_reserved_risk_dollars"),
                        "candidate_correlation_status": decision.get("candidate_correlation_status"),
                        "highest_ranked_candidate_correlation": decision.get("highest_ranked_candidate_correlation"),
                        "most_correlated_higher_ranked_symbol": decision.get("most_correlated_higher_ranked_symbol"),
                        "candidate_correlation_observations": decision.get("candidate_correlation_observations"),
                        "high_correlation_flag": decision.get("high_correlation_flag"),
                        "held_position_correlation_status": decision.get("held_position_correlation_status"),
                        "highest_held_position_correlation": decision.get("highest_held_position_correlation"),
                        "most_correlated_held_symbol": decision.get("most_correlated_held_symbol"),
                        "held_position_correlation_observations": decision.get("held_position_correlation_observations"),
                        "high_held_correlation_flag": decision.get("high_held_correlation_flag"),
                        "portfolio_diversification_status": decision.get("portfolio_diversification_status"),
                        "current_portfolio_weighted_correlation": decision.get("current_portfolio_weighted_correlation"),
                        "current_portfolio_diversification_score": decision.get("current_portfolio_diversification_score"),
                        "candidate_diversification_status": decision.get("candidate_diversification_status"),
                        "candidate_weighted_held_correlation": decision.get("candidate_weighted_held_correlation"),
                        "candidate_diversification_score": decision.get("candidate_diversification_score"),
                        "diversification_holdings_count": decision.get("diversification_holdings_count"),
                        "diversification_observations": decision.get("diversification_observations"),
                        "portfolio_risk_forecast_status": decision.get("portfolio_risk_forecast_status"),
                        "portfolio_risk_lookback_sessions": decision.get("portfolio_risk_lookback_sessions"),
                        "portfolio_risk_holdings_count": decision.get("portfolio_risk_holdings_count"),
                        "portfolio_risk_basis_gross_dollars": decision.get("portfolio_risk_basis_gross_dollars"),
                        "portfolio_annualized_volatility_pct": decision.get("portfolio_annualized_volatility_pct"),
                        "portfolio_historical_var_95_1d_dollars": decision.get("portfolio_historical_var_95_1d_dollars"),
                        "portfolio_historical_es_95_1d_dollars": decision.get("portfolio_historical_es_95_1d_dollars"),
                        "portfolio_historical_var_95_5d_dollars": decision.get("portfolio_historical_var_95_5d_dollars"),
                        "portfolio_historical_es_95_5d_dollars": decision.get("portfolio_historical_es_95_5d_dollars"),
                        "portfolio_historical_max_drawdown_pct": decision.get("portfolio_historical_max_drawdown_pct"),
                        "portfolio_current_drawdown_pct": decision.get("portfolio_current_drawdown_pct"),
                        "portfolio_drawdown_episodes": decision.get("portfolio_drawdown_episodes"),
                        "portfolio_drawdown_recovered_episodes": decision.get("portfolio_drawdown_recovered_episodes"),
                        "portfolio_current_underwater_sessions": decision.get("portfolio_current_underwater_sessions"),
                        "portfolio_longest_underwater_sessions": decision.get("portfolio_longest_underwater_sessions"),
                        "portfolio_average_recovery_sessions": decision.get("portfolio_average_recovery_sessions"),
                        "portfolio_longest_recovery_sessions": decision.get("portfolio_longest_recovery_sessions"),
                        "portfolio_down_days_pct": decision.get("portfolio_down_days_pct"),
                        "portfolio_worst_day_date": decision.get("portfolio_worst_day_date"),
                        "portfolio_worst_day_loss_dollars": decision.get("portfolio_worst_day_loss_dollars"),
                        "portfolio_worst_5d_start_date": decision.get("portfolio_worst_5d_start_date"),
                        "portfolio_worst_5d_end_date": decision.get("portfolio_worst_5d_end_date"),
                        "portfolio_worst_5d_loss_dollars": decision.get("portfolio_worst_5d_loss_dollars"),
                        "market_stress_status": decision.get("market_stress_status"),
                        "spy_worst_day_date": decision.get("spy_worst_day_date"),
                        "spy_worst_day_return_pct": decision.get("spy_worst_day_return_pct"),
                        "portfolio_return_on_spy_worst_day_pct": decision.get("portfolio_return_on_spy_worst_day_pct"),
                        "portfolio_loss_on_spy_worst_day_dollars": decision.get("portfolio_loss_on_spy_worst_day_dollars"),
                        "spy_worst_5d_start_date": decision.get("spy_worst_5d_start_date"),
                        "spy_worst_5d_end_date": decision.get("spy_worst_5d_end_date"),
                        "spy_worst_5d_return_pct": decision.get("spy_worst_5d_return_pct"),
                        "portfolio_return_on_spy_worst_5d_pct": decision.get("portfolio_return_on_spy_worst_5d_pct"),
                        "portfolio_loss_on_spy_worst_5d_dollars": decision.get("portfolio_loss_on_spy_worst_5d_dollars"),
                        "portfolio_avg_return_on_5_worst_spy_days_pct": decision.get("portfolio_avg_return_on_5_worst_spy_days_pct"),
                        "portfolio_worst_return_on_5_worst_spy_days_pct": decision.get("portfolio_worst_return_on_5_worst_spy_days_pct"),
                        "portfolio_loss_on_5_worst_spy_days_dollars": decision.get("portfolio_loss_on_5_worst_spy_days_dollars"),
                        "portfolio_worst_day_contributors": decision.get("portfolio_worst_day_contributors"),
                        "downside_status": decision.get("downside_status"),
                        "downside_observations": decision.get("downside_observations"),
                        "downside_benchmark_avg_return_pct": decision.get("downside_benchmark_avg_return_pct"),
                        "portfolio_avg_return_on_down_market_days_pct": decision.get("portfolio_avg_return_on_down_market_days_pct"),
                        "portfolio_downside_beta": decision.get("portfolio_downside_beta"),
                        "portfolio_downside_capture_pct": decision.get("portfolio_downside_capture_pct"),
                        "portfolio_downside_correlation": decision.get("portfolio_downside_correlation"),
                        "downside_holding_diagnostics": decision.get("downside_holding_diagnostics"),
                        "regime_status": decision.get("regime_status"),
                        "regime_observations": decision.get("regime_observations"),
                        "current_market_trend_regime": decision.get("current_market_trend_regime"),
                        "current_market_volatility_regime": decision.get("current_market_volatility_regime"),
                        "current_market_regime": decision.get("current_market_regime"),
                        "current_spy_realized_volatility_pct": decision.get("current_spy_realized_volatility_pct"),
                        "regime_performance": decision.get("regime_performance"),
                        "regime_holding_diagnostics": decision.get("regime_holding_diagnostics"),
                        "historical_signal_reliability": decision.get("historical_signal_reliability"),
                    })

                exposure_df = decision_df.apply(_portfolio_exposure_columns, axis=1)
                decision_df = pd.concat([decision_df, lifecycle_df, exposure_df], axis=1)
                protection_statuses = decision_df.get("position_protection_status", pd.Series(index=decision_df.index, dtype=object))
                protection_alert_count = int((
                    protection_statuses.notna()
                    & ~protection_statuses.isin(["PROTECTED", "NO_OPEN_POSITION", "NOT_CURRENT_POSITION_ENTRY"])
                ).sum())
                d1, d2, d3, d4, d5, d6 = st.columns(6)
                d1.metric("Recent decisions", len(decision_df))
                d2.metric("Ready (not submitted)", ready_count)
                d3.metric("Broker orders / lifecycle", submitted_count)
                d4.metric("Blocked by risk gates", blocked_count)
                d5.metric("Protection audit alerts", protection_alert_count)
                d6.metric("Invalid broker data", invalid_broker_data_count)
                decision_columns = [
                    "symbol", "status", "broker_state", "broker_quantity_validation",
                    "replacement_chain_status", "replacement_chain_order_ids", "protection_order_id",
                    "filled_shares", "remaining_shares",
                    "position_protection_status", "position_protection_reason",
                    "position_qty", "stop_exit_qty", "target_exit_qty",
                    "exit_leg_states", "reason", "quote_feed", "quote_timestamp",
                    "bid", "ask", "midpoint", "spread_pct", "quantity",
                    "estimated_notional", "estimated_risk_dollars",
                    "current_gross_exposure_dollars", "gross_exposure_limit_dollars",
                    "remaining_gross_exposure_dollars", "gross_exposure_utilization_pct",
                    "largest_existing_position_symbol", "largest_existing_position_dollars",
                    "largest_existing_position_pct_equity", "candidate_position_pct_equity",
                    "projected_gross_exposure_dollars", "projected_largest_position_pct_equity",
                    "current_aggregate_open_risk_dollars", "aggregate_open_risk_limit_dollars",
                    "remaining_aggregate_open_risk_dollars", "aggregate_open_risk_utilization_pct",
                    "projected_aggregate_open_risk_dollars", "aggregate_open_risk_utilization_after_candidate_pct",
                    "prior_candidate_reserved_risk_dollars", "prior_candidate_reserved_count",
                    "candidate_reserved_risk_dollars",
                    "candidate_correlation_status", "highest_ranked_candidate_correlation",
                    "most_correlated_higher_ranked_symbol", "candidate_correlation_observations",
                    "high_correlation_flag",
                    "held_position_correlation_status", "highest_held_position_correlation",
                    "most_correlated_held_symbol", "held_position_correlation_observations",
                    "high_held_correlation_flag",
                    "portfolio_diversification_status", "current_portfolio_weighted_correlation",
                    "current_portfolio_diversification_score", "candidate_diversification_status",
                    "candidate_weighted_held_correlation", "candidate_diversification_score",
                    "diversification_holdings_count", "diversification_observations",
                    "historical_signal_reliability",
                    "portfolio_risk_forecast_status",
                    "portfolio_risk_lookback_sessions",
                    "portfolio_risk_holdings_count",
                    "portfolio_risk_basis_gross_dollars",
                    "portfolio_annualized_volatility_pct",
                    "portfolio_historical_var_95_1d_dollars",
                    "portfolio_historical_es_95_1d_dollars",
                    "portfolio_historical_var_95_5d_dollars",
                    "portfolio_historical_es_95_5d_dollars",
                    "portfolio_historical_max_drawdown_pct",
                    "portfolio_current_drawdown_pct",
                    "portfolio_drawdown_episodes", "portfolio_drawdown_recovered_episodes",
                    "portfolio_current_underwater_sessions", "portfolio_longest_underwater_sessions",
                    "portfolio_average_recovery_sessions", "portfolio_longest_recovery_sessions",
                    "portfolio_down_days_pct",
                    "portfolio_worst_day_date",
                    "portfolio_worst_day_loss_dollars",
                    "portfolio_worst_5d_start_date",
                    "portfolio_worst_5d_end_date",
                    "portfolio_worst_5d_loss_dollars",
                    "market_stress_status",
                    "spy_worst_day_date",
                    "spy_worst_day_return_pct",
                    "portfolio_return_on_spy_worst_day_pct",
                    "portfolio_loss_on_spy_worst_day_dollars",
                    "spy_worst_5d_start_date",
                    "spy_worst_5d_end_date",
                    "spy_worst_5d_return_pct",
                    "portfolio_return_on_spy_worst_5d_pct",
                    "portfolio_loss_on_spy_worst_5d_dollars",
                    "portfolio_avg_return_on_5_worst_spy_days_pct",
                    "portfolio_worst_return_on_5_worst_spy_days_pct",
                    "portfolio_loss_on_5_worst_spy_days_dollars",
                    "portfolio_worst_day_contributors",
                    "rolling_performance_status", "rolling_performance_method",
                    "rolling_performance_observations", "rolling_performance_windows",
                    "downside_status", "downside_observations",
                    "downside_benchmark_avg_return_pct",
                    "portfolio_avg_return_on_down_market_days_pct",
                    "portfolio_downside_beta", "portfolio_downside_capture_pct",
                    "portfolio_downside_correlation", "downside_holding_diagnostics",
                    "regime_status", "regime_observations",
                    "current_market_trend_regime", "current_market_volatility_regime",
                    "current_market_regime", "current_spy_realized_volatility_pct",
                    "regime_performance", "regime_holding_diagnostics",
                    "current_reward_risk", "broker_order_id", "updated_at"
                ]
                visible = [col for col in decision_columns if col in decision_df.columns]
                decision_df = decision_df[visible].rename(columns={
                    "symbol": "Symbol", "status": "Decision", "broker_state": "Broker state",
                    "broker_quantity_validation": "Broker quantity data",
                    "replacement_chain_status": "Replacement chain",
                    "replacement_chain_order_ids": "Order chain IDs",
                    "protection_order_id": "Order used for protection audit",
                    "filled_shares": "Filled shares", "remaining_shares": "Remaining shares",
                    "position_protection_status": "Position protection",
                    "position_protection_reason": "Protection reason", "position_qty": "Open shares",
                    "stop_exit_qty": "Stop remaining shares", "target_exit_qty": "Target remaining shares",
                    "exit_leg_states": "Protective exit legs", "reason": "Gate result",
                    "quote_feed": "Quote feed", "quote_timestamp": "Quote timestamp (UTC)",
                    "bid": "Bid", "ask": "Ask", "midpoint": "Midpoint",
                    "spread_pct": "Spread %", "quantity": "Shares",
                    "estimated_notional": "Est. notional", "estimated_risk_dollars": "Est. risk $",
                    "current_gross_exposure_dollars": "Gross exposure $",
                    "gross_exposure_limit_dollars": "Gross limit $",
                    "remaining_gross_exposure_dollars": "Gross room $",
                    "gross_exposure_utilization_pct": "Gross used %",
                    "largest_existing_position_symbol": "Largest holding",
                    "largest_existing_position_dollars": "Largest holding $",
                    "largest_existing_position_pct_equity": "Largest holding % equity",
                    "candidate_position_pct_equity": "Candidate % equity",
                    "projected_gross_exposure_dollars": "Projected gross $",
                    "projected_largest_position_pct_equity": "Projected largest % equity",
                    "current_aggregate_open_risk_dollars": "Open stop risk $",
                    "aggregate_open_risk_limit_dollars": "Stop-risk limit $",
                    "remaining_aggregate_open_risk_dollars": "Stop-risk room $",
                    "aggregate_open_risk_utilization_pct": "Stop-risk used %",
                    "projected_aggregate_open_risk_dollars": "Projected stop risk $",
                    "aggregate_open_risk_utilization_after_candidate_pct": "Projected stop-risk used %",
                    "prior_candidate_reserved_risk_dollars": "Earlier candidates reserved $",
                    "prior_candidate_reserved_count": "Earlier candidates reserved",
                    "candidate_reserved_risk_dollars": "This candidate reserved $",
                    "candidate_correlation_status": "Correlation data",
                    "highest_ranked_candidate_correlation": "Correlation vs higher rank",
                    "most_correlated_higher_ranked_symbol": "Most correlated symbol",
                    "candidate_correlation_observations": "Correlation sessions",
                    "high_correlation_flag": "High correlation flag",
                    "current_reward_risk": "Current R:R", "broker_order_id": "Alpaca order ID",
                    "updated_at": "Last evaluated"
                })
                number_formats = {
                    "Bid": "${:,.2f}", "Ask": "${:,.2f}", "Midpoint": "${:,.2f}",
                    "Spread %": "{:.3f}%", "Est. notional": "${:,.2f}",
                    "Est. risk $": "${:,.2f}", "Gross exposure $": "${:,.2f}",
                    "Gross limit $": "${:,.2f}", "Gross room $": "${:,.2f}",
                    "Gross used %": "{:.1f}%", "Largest holding $": "${:,.2f}",
                    "Largest holding % equity": "{:.1f}%", "Candidate % equity": "{:.1f}%",
                    "Projected gross $": "${:,.2f}", "Projected largest % equity": "{:.1f}%",
                    "Open stop risk $": "${:,.2f}", "Stop-risk limit $": "${:,.2f}",
                    "Stop-risk room $": "${:,.2f}", "Stop-risk used %": "{:.1f}%",
                    "Projected stop risk $": "${:,.2f}", "Projected stop-risk used %": "{:.1f}%",
                    "Earlier candidates reserved $": "${:,.2f}", "This candidate reserved $": "${:,.2f}",
                    "Correlation vs higher rank": "{:.2f}",
                    "Current R:R": "{:.2f}"
                }
                # Portfolio regime diagnostics are repeated on each candidate decision row;
                # render the shared snapshot once, outside the per-symbol audit table.
                regime_row = next((
                    item for item in decision_rows
                    if isinstance(item, dict)
                    and isinstance(item.get("decision"), dict)
                    and item["decision"].get("regime_status") == "AVAILABLE"
                ), None)
                if regime_row:
                    regime_data = regime_row["decision"]
                    st.markdown("#### 🌦️ Portfolio performance by market regime")
                    st.caption(
                        "Historical portfolio behavior grouped by SPY trend and volatility. "
                        "Descriptive only; these readings do not change candidate rankings, sizing, or order decisions."
                    )
                    trend_label = str(regime_data.get("current_market_trend_regime") or "Unavailable")
                    vol_label = str(regime_data.get("current_market_volatility_regime") or "Unavailable")
                    regime_label = str(regime_data.get("current_market_regime") or "Unavailable")
                    realized_vol = regime_data.get("current_spy_realized_volatility_pct")
                    regime_observations = regime_data.get("regime_observations")
                    q1, q2, q3, q4 = st.columns(4)
                    q1.metric("Current SPY trend", trend_label)
                    q2.metric("Current SPY volatility", vol_label)
                    q3.metric("Current combined regime", regime_label)
                    q4.metric(
                        "SPY 20-day realized vol",
                        f"{realized_vol:.1f}%" if isinstance(realized_vol, (int, float)) else "Unavailable",
                    )
                    st.caption(
                        f"Usable aligned sessions: {regime_observations if regime_observations is not None else 'Unavailable'}"
                    )
                    regime_rows = regime_data.get("regime_performance")
                    if isinstance(regime_rows, list) and regime_rows:
                        regime_table = pd.DataFrame([
                            row for row in regime_rows if isinstance(row, dict)
                        ])
                        if not regime_table.empty:
                            regime_table = regime_table.rename(columns={
                                "regime": "Market regime",
                                "trend_regime": "Trend",
                                "volatility_regime": "Volatility",
                                "observations": "Sessions",
                                "portfolio_avg_daily_return_pct": "Portfolio avg daily %",
                                "benchmark_avg_daily_return_pct": "SPY avg daily %",
                                "average_daily_excess_return_pct": "Avg daily excess %",
                                "portfolio_win_rate_pct": "Portfolio up days %",
                                "portfolio_worst_day_pct": "Worst portfolio day %",
                            })
                            regime_formats = {
                                col: "{:.3f}%" for col in [
                                    "Portfolio avg daily %", "SPY avg daily %",
                                    "Avg daily excess %", "Portfolio up days %",
                                    "Worst portfolio day %",
                                ] if col in regime_table.columns
                            }
                            st.dataframe(
                                regime_table.style.format(regime_formats),
                                use_container_width=True, hide_index=True
                            )
                    holding_rows = regime_data.get("regime_holding_diagnostics")
                    if isinstance(holding_rows, list) and holding_rows:
                        with st.expander("Per-holding performance inside each regime"):
                            holding_table = pd.DataFrame([
                                row for row in holding_rows if isinstance(row, dict)
                            ])
                            if not holding_table.empty:
                                holding_table = holding_table.rename(columns={
                                    "regime": "Market regime",
                                    "symbol": "Symbol",
                                    "side": "Side",
                                    "observations": "Sessions",
                                    "holding_avg_daily_return_pct": "Holding avg daily %",
                                    "weighted_portfolio_contribution_pct": "Weighted contribution %",
                                })
                                holding_formats = {
                                    col: "{:.3f}%" for col in [
                                        "Holding avg daily %", "Weighted contribution %"
                                    ] if col in holding_table.columns
                                }
                                st.dataframe(
                                    holding_table.style.format(holding_formats),
                                    use_container_width=True, hide_index=True
                                )
                elif decision_rows:
                    regime_status = next((
                        item.get("decision", {}).get("regime_status")
                        for item in decision_rows if isinstance(item, dict)
                        and isinstance(item.get("decision"), dict)
                        and item["decision"].get("regime_status")
                    ), "UNAVAILABLE")
                    st.markdown("#### 🌦️ Portfolio performance by market regime")
                    st.info(f"Regime diagnostics: {str(regime_status).replace('_', ' ').lower()}.")
                safe_decision_formats = {
                    col: (lambda value, template=template: _safe_format_number(value, template))
                    for col, template in number_formats.items()
                    if col in decision_df.columns
                }
                st.dataframe(
                    decision_df.style.format(safe_decision_formats),
                    use_container_width=True, hide_index=True
                )
                st.caption("READY_NOT_SUBMITTED is not an order. Invalid broker fill quantities are separately flagged as BROKER_DATA_INVALID; unavailable fill metadata is not treated as valid. Position protection is marked PROTECTED only when both active bracket exits exactly match the broker-reported open share quantity. All broker data is read-only. Quote timestamps are UTC.")
            else:
                st.info("No Alpaca paper decisions have been recorded yet. The dashboard's Supabase virtual paper account is separate.")

            st.markdown("#### Signal counts")
            if counts:
                count_cols = st.columns(min(len(counts), 4))
                for idx, (signal_name, signal_count) in enumerate(sorted(counts.items())):
                    count_cols[idx % len(count_cols)].metric(str(signal_name), int(signal_count))
            else:
                st.info("This scan did not include signal counts.")

            st.markdown("#### Candidate overlap / correlation")
            if watchlist:
                basket_reference = next(
                    (item for item in watchlist if isinstance(item, dict)
                     and item.get("portfolio_diversification_status") == "AVAILABLE"),
                    watchlist[0] if isinstance(watchlist[0], dict) else {},
                )
                basket_status = basket_reference.get("portfolio_diversification_status", "UNAVAILABLE")
                basket_score = basket_reference.get("current_portfolio_diversification_score")
                basket_corr = basket_reference.get("current_portfolio_weighted_correlation")
                b1, b2, b3 = st.columns(3)
                b1.metric(
                    "Current basket diversification",
                    f"{basket_score:.1f}/100" if isinstance(basket_score, (int, float)) else "Unavailable",
                )
                b2.metric(
                    "Current weighted correlation",
                    f"{basket_corr:.2f}" if isinstance(basket_corr, (int, float)) else "Unavailable",
                )
                b3.metric("Basket data status", str(basket_status).replace("_", " ").title())
                st.caption(
                    "Current basket score summarizes pairwise daily-return correlation weighted by "
                    "the product of the held positions' market values. It is unavailable unless "
                    "at least two valid holdings have sufficient aligned history."
                )
                risk_status = basket_reference.get("portfolio_risk_forecast_status", "UNAVAILABLE")
                r1, r2, r3, r4, r5 = st.columns(5)
                r1.metric(
                    "Historical 1-day VaR (95%)",
                    "$" + "{:,.0f}".format(basket_reference["portfolio_historical_var_95_1d_dollars"])
                    if isinstance(basket_reference.get("portfolio_historical_var_95_1d_dollars"), (int, float))
                    else "Unavailable",
                )
                r2.metric(
                    "Historical 1-day expected shortfall",
                    "$" + "{:,.0f}".format(basket_reference["portfolio_historical_es_95_1d_dollars"])
                    if isinstance(basket_reference.get("portfolio_historical_es_95_1d_dollars"), (int, float))
                    else "Unavailable",
                )
                r3.metric(
                    "Historical 5-day VaR (95%)",
                    "$" + "{:,.0f}".format(basket_reference["portfolio_historical_var_95_5d_dollars"])
                    if isinstance(basket_reference.get("portfolio_historical_var_95_5d_dollars"), (int, float))
                    else "Unavailable",
                )
                r4.metric(
                    "Annualized realized volatility",
                    "{:.1f}%".format(basket_reference["portfolio_annualized_volatility_pct"])
                    if isinstance(basket_reference.get("portfolio_annualized_volatility_pct"), (int, float))
                    else "Unavailable",
                )
                r5.metric(
                    "60-session max drawdown",
                    "{:.1f}%".format(basket_reference["portfolio_historical_max_drawdown_pct"])
                    if isinstance(basket_reference.get("portfolio_historical_max_drawdown_pct"), (int, float))
                    else "Unavailable",
                )
                st.caption(
                    "Historical risk status: " + str(risk_status) + ". Dollar VaR/expected-shortfall figures are "
                    "scaled to gross position notional, not account equity. Historical simulation only; "
                    "not a prediction, loss limit, or trade gate. Requires fresh broker data and at least "
                    "40 aligned daily observations."
                )
                rolling_status = basket_reference.get("rolling_performance_status", "UNAVAILABLE")
                rolling_rows = basket_reference.get("rolling_performance_windows") or []
                st.markdown("**Rolling portfolio performance (20 / 60 / 120 sessions)**")
                if rolling_status == "AVAILABLE" and rolling_rows:
                    rolling_df = pd.DataFrame(rolling_rows).rename(columns={
                        "window_sessions": "Window (sessions)",
                        "sessions": "Observations",
                        "portfolio_total_return_pct": "Portfolio return %",
                        "benchmark_total_return_pct": "SPY return %",
                        "excess_return_pct_points": "Excess return (pp)",
                        "annualized_volatility_pct": "Annualized volatility %",
                        "maximum_drawdown_pct": "Maximum drawdown %",
                        "win_rate_pct": "Win rate %",
                        "worst_day_pct": "Worst day %",
                    })
                    st.dataframe(
                        rolling_df.style.format({
                            "Portfolio return %": "{:.2f}%",
                            "SPY return %": "{:.2f}%",
                            "Excess return (pp)": "{:.2f}",
                            "Annualized volatility %": "{:.2f}%",
                            "Maximum drawdown %": "{:.2f}%",
                            "Win rate %": "{:.1f}%",
                            "Worst day %": "{:.2f}%",
                        }),
                        use_container_width=True, hide_index=True,
                    )
                else:
                    st.caption("Rolling performance unavailable: " + str(rolling_status).replace("_", " ").lower() + ".")
                st.caption(
                    "Method: today's signed market-value weights are applied to historical daily returns. "
                    "This is a constant-weight approximation, not actual historical fills, changing position sizes, "
                    "or realized broker P&L. Descriptive only; it does not affect candidate ranking, sizing, or orders."
                )
                stress_1, stress_2 = st.columns(2)
                stress_1.metric(
                    "Worst observed day",
                    "$" + "{:,.0f}".format(basket_reference["portfolio_worst_day_loss_dollars"])
                    if isinstance(basket_reference.get("portfolio_worst_day_loss_dollars"), (int, float))
                    else "Unavailable",
                    str(basket_reference.get("portfolio_worst_day_date") or "No date"),
                )
                stress_2.metric(
                    "Worst rolling 5-session loss",
                    "$" + "{:,.0f}".format(basket_reference["portfolio_worst_5d_loss_dollars"])
                    if isinstance(basket_reference.get("portfolio_worst_5d_loss_dollars"), (int, float))
                    else "Unavailable",
                    str(basket_reference.get("portfolio_worst_5d_start_date") or "No start") +
                    " to " + str(basket_reference.get("portfolio_worst_5d_end_date") or "No end"),
                )
                contributors = basket_reference.get("portfolio_worst_day_contributors") or []
                if basket_reference.get("market_stress_status") == "AVAILABLE":
                    st.markdown("**Broad-market historical stress scenarios (SPY)**")
                    stress_a, stress_b, stress_c = st.columns(3)
                    stress_a.metric("Portfolio loss on SPY worst day", "$" + "{:,.0f}".format(basket_reference["portfolio_loss_on_spy_worst_day_dollars"]), str(basket_reference["spy_worst_day_date"]))
                    stress_b.metric("Portfolio loss on SPY worst 5 sessions", "$" + "{:,.0f}".format(basket_reference["portfolio_loss_on_spy_worst_5d_dollars"]), str(basket_reference["spy_worst_5d_start_date"]) + " to " + str(basket_reference["spy_worst_5d_end_date"]))
                    stress_c.metric("Loss on 5 worst SPY days", "$" + "{:,.0f}".format(basket_reference["portfolio_loss_on_5_worst_spy_days_dollars"]), "Five separate sessions")
                    st.caption("These replay the portfolio holdings and long/short weights on the same historical dates as SPY selloffs. They are historical scenarios, not predictions or trading limits.")
                else:
                    st.caption("Broad-market stress scenarios unavailable: SPY history or aligned held-position history is insufficient.")
                if contributors:
                    st.markdown("**Largest contributors on the worst observed day**")
                    contributor_df = pd.DataFrame(contributors)
                    contributor_df = contributor_df.rename(columns={
                        "symbol": "Symbol", "side": "Side", "market_value": "Market value ($)",
                        "underlying_return_pct": "Underlying return %",
                        "pnl_contribution_dollars": "P&L contribution ($)",
                    })
                    st.dataframe(
                        contributor_df.style.format({
                            "Market value ($)": "\u0024{:,.0f}",
                            "Underlying return %": "{:.2f}%",
                            "P&L contribution ($)": "\u0024{:,.0f}",
                        }),
                        use_container_width=True, hide_index=True,
                    )
                correlation_df = pd.DataFrame(watchlist)
                correlation_columns = [
                    col for col in [
                        "symbol", "signal", "adjusted_score",
                        "candidate_correlation_status",
                        "most_correlated_higher_ranked_symbol",
                        "highest_ranked_candidate_correlation",
                        "candidate_correlation_observations", "high_correlation_flag",
                        "candidate_diversification_status", "candidate_weighted_held_correlation",
                        "candidate_diversification_score", "diversification_holdings_count",
                        "portfolio_risk_forecast_status", "portfolio_risk_basis_gross_dollars",
                        "portfolio_annualized_volatility_pct", "portfolio_historical_var_95_1d_dollars",
                        "portfolio_historical_es_95_1d_dollars", "portfolio_historical_var_95_5d_dollars",
                        "portfolio_historical_es_95_5d_dollars", "portfolio_historical_max_drawdown_pct",
                        "portfolio_current_drawdown_pct", "portfolio_down_days_pct",
                        "portfolio_worst_day_date", "portfolio_worst_day_loss_dollars",
                        "portfolio_worst_5d_start_date", "portfolio_worst_5d_end_date",
                        "portfolio_worst_5d_loss_dollars",
                        "market_stress_status", "spy_worst_day_date", "spy_worst_day_return_pct",
                        "portfolio_return_on_spy_worst_day_pct", "portfolio_loss_on_spy_worst_day_dollars",
                        "spy_worst_5d_start_date", "spy_worst_5d_end_date", "spy_worst_5d_return_pct",
                        "portfolio_return_on_spy_worst_5d_pct", "portfolio_loss_on_spy_worst_5d_dollars",
                        "portfolio_avg_return_on_5_worst_spy_days_pct",
                        "portfolio_worst_return_on_5_worst_spy_days_pct",
                        "portfolio_loss_on_5_worst_spy_days_dollars",
                    ] if col in correlation_df.columns
                ]
                if correlation_columns:
                    correlation_df = correlation_df[correlation_columns].rename(columns={
                        "symbol": "Candidate", "signal": "Signal",
                        "adjusted_score": "Rank score",
                        "candidate_correlation_status": "Data status",
                        "most_correlated_higher_ranked_symbol": "Compared with higher-ranked",
                        "highest_ranked_candidate_correlation": "Daily-return correlation",
                        "candidate_correlation_observations": "Overlapping sessions",
                        "high_correlation_flag": "High overlap (>= 0.80)",
                        "candidate_diversification_status": "Held-basket data status",
                        "candidate_weighted_held_correlation": "Exposure-weighted held correlation",
                        "candidate_diversification_score": "Diversification score (0–100)",
                        "diversification_holdings_count": "Held positions compared",
                        "portfolio_risk_forecast_status": "Risk forecast status",
                        "portfolio_risk_basis_gross_dollars": "Gross exposure basis ($)",
                        "portfolio_annualized_volatility_pct": "Annualized volatility %",
                        "portfolio_historical_var_95_1d_dollars": "Historical 1D VaR 95% ($)",
                        "portfolio_historical_es_95_1d_dollars": "Historical 1D ES 95% ($)",
                        "portfolio_historical_var_95_5d_dollars": "Historical 5D VaR 95% ($)",
                        "portfolio_historical_es_95_5d_dollars": "Historical 5D ES 95% ($)",
                        "portfolio_historical_max_drawdown_pct": "60-session max drawdown %",
                        "portfolio_current_drawdown_pct": "Current drawdown %",
                        "portfolio_down_days_pct": "Down sessions %",
                        "portfolio_worst_day_date": "Worst observed day",
                        "portfolio_worst_day_loss_dollars": "Worst day loss ($)",
                        "portfolio_worst_5d_start_date": "Worst 5D start",
                        "portfolio_worst_5d_end_date": "Worst 5D end",
                        "portfolio_worst_5d_loss_dollars": "Worst 5D loss ($)",
                        "market_stress_status": "Market stress status",
                        "spy_worst_day_date": "SPY worst day",
                        "spy_worst_day_return_pct": "SPY worst day return %",
                        "portfolio_return_on_spy_worst_day_pct": "Portfolio return on SPY worst day %",
                        "portfolio_loss_on_spy_worst_day_dollars": "Portfolio loss on SPY worst day ($)",
                        "spy_worst_5d_start_date": "SPY worst 5D start",
                        "spy_worst_5d_end_date": "SPY worst 5D end",
                        "spy_worst_5d_return_pct": "SPY worst 5D return %",
                        "portfolio_return_on_spy_worst_5d_pct": "Portfolio return on SPY worst 5D %",
                        "portfolio_loss_on_spy_worst_5d_dollars": "Portfolio loss on SPY worst 5D ($)",
                        "portfolio_avg_return_on_5_worst_spy_days_pct": "Avg portfolio return on 5 worst SPY days %",
                        "portfolio_worst_return_on_5_worst_spy_days_pct": "Worst portfolio return on 5 worst SPY days %",
                        "portfolio_loss_on_5_worst_spy_days_dollars": "Loss on 5 worst SPY days ($)",
                    })
                    st.dataframe(
                        correlation_df.style.format({
                            "Daily-return correlation": "{:.2f}",
                            "Exposure-weighted held correlation": "{:.2f}",
                            "Diversification score (0–100)": "{:.1f}",
                            "Gross exposure basis ($)": "\u0024{:,.0f}",
                            "Historical 1D VaR 95% ($)": "\u0024{:,.0f}",
                            "Historical 1D ES 95% ($)": "\u0024{:,.0f}",
                            "Historical 5D VaR 95% ($)": "\u0024{:,.0f}",
                            "Historical 5D ES 95% ($)": "\u0024{:,.0f}",
                            "Annualized volatility %": "{:.1f}%",
                            "60-session max drawdown %": "{:.1f}%",
                            "Current drawdown %": "{:.1f}%",
                            "Down sessions %": "{:.1f}%",
                            "Worst day loss ($)": "\u0024{:,.0f}",
                            "Worst 5D loss ($)": "\u0024{:,.0f}",
                            "Portfolio loss on SPY worst day ($)": "\u0024{:,.0f}",
                            "Portfolio loss on SPY worst 5D ($)": "\u0024{:,.0f}",
                            "Loss on 5 worst SPY days ($)": "\u0024{:,.0f}",
                            "SPY worst day return %": "{:.2f}%",
                            "Portfolio return on SPY worst day %": "{:.2f}%",
                            "SPY worst 5D return %": "{:.2f}%",
                            "Portfolio return on SPY worst 5D %": "{:.2f}%",
                            "Avg portfolio return on 5 worst SPY days %": "{:.2f}%",
                            "Worst portfolio return on 5 worst SPY days %": "{:.2f}%",
                        }),
                        use_container_width=True, hide_index=True,
                    )
                    st.caption(
                        "Pearson correlation of aligned daily returns over up to 60 sessions; "
                        "at least 40 overlapping observations required. This is a diagnostic "
                        "between ranked candidates. The held-basket metric is weighted by broker-reported "
                        "market value and requires at least 40 aligned sessions for every compared holding. "
                        "Higher diversification scores indicate lower positive co-movement; diagnostic only, "
                        "not a trade block or forecast."
                    )
            else:
                st.info("No ranked candidates are available for correlation comparison.")

            st.markdown("#### Top-ranked cloud scan results")
            if ranked:
                ranked_df = pd.DataFrame(ranked)
                display_columns = [
                    col for col in [
                        "symbol", "asset_class", "score", "adjusted_score", "portfolio_fit_score", "portfolio_fit_adjustment", "portfolio_sector_exposure_pct", "portfolio_fit_note", "signal_score", "sector_group", "sector_rotation_state", "sector_adjustment", "relative_1m_vs_spy_pp", "relative_1m_vs_sector_pp", "trend_points", "momentum_points", "rsi_points", "weekly_points", "volatility_penalty", "signal", "trend",
                        "weekly_trend", "risk", "last", "price_date",
                        "return_1w_pct", "return_1m_pct", "return_3m_pct",
                        "rsi", "annualized_volatility_pct", "setup_type", "setup_status", "setup_quality_score", "setup_entry_reference", "setup_stop_reference", "setup_target_reference", "setup_reward_risk", "setup_distance_to_entry_pct", "atr_pct", "reason"
                    ] if col in ranked_df.columns
                ]
                ranked_df = ranked_df[display_columns].rename(columns={
                    "symbol": "Symbol", "asset_class": "Asset class", "score": "Technical score",
                    "adjusted_score": "Refined rank score", "portfolio_fit_score": "Portfolio-fit score", "portfolio_fit_adjustment": "Fit adjustment", "portfolio_sector_exposure_pct": "Existing sector exposure %", "portfolio_fit_note": "Portfolio note", "signal_score": "Mechanical signal score", "sector_group": "Sector group",
                    "sector_rotation_state": "Sector state", "sector_adjustment": "Sector adjustment",
                    "relative_1m_vs_spy_pp": "1M vs SPY (pp)", "relative_1m_vs_sector_pp": "1M vs sector ETF (pp)",
                    "volatility_penalty": "Volatility penalty", "trend_points": "Trend points",
                    "momentum_points": "Momentum points", "rsi_points": "RSI points", "weekly_points": "Weekly points",
                    "signal": "Signal", "trend": "Daily trend", "weekly_trend": "Weekly trend",
                    "risk": "Risk", "last": "Last daily price", "price_date": "Price date",
                    "return_1w_pct": "1W %", "return_1m_pct": "1M %",
                    "return_3m_pct": "3M %", "rsi": "RSI",
                    "annualized_volatility_pct": "Annualized volatility %",
                    "setup_type": "Setup type", "setup_status": "Setup status",
                    "setup_quality_score": "Setup quality", "setup_entry_reference": "Entry reference",
                    "setup_stop_reference": "Stop reference", "setup_target_reference": "Target reference",
                    "setup_reward_risk": "Illustrative R:R", "setup_distance_to_entry_pct": "Distance to entry %", "atr_pct": "ATR %",
                    "reason": "Screen rationale"
                })
                formatters = {
                    "Last daily price": "${:,.2f}", "1W %": "{:+.2f}%",
                    "1M %": "{:+.2f}%", "3M %": "{:+.2f}%",
                    "RSI": "{:.1f}", "Annualized volatility %": "{:.1f}%",
                    "Entry reference": "${:,.2f}", "Stop reference": "${:,.2f}", "Target reference": "${:,.2f}",
                    "Illustrative R:R": "{:.2f}", "Distance to entry %": "{:+.2f}%", "ATR %": "{:.2f}%"
                }
                st.dataframe(ranked_df.style.format(
                    {k: v for k, v in formatters.items() if k in ranked_df.columns}
                ), use_container_width=True, hide_index=True)
            else:
                st.info("The latest scan did not store ranked results.")

            # Multi-scenario setup diagnostics from the same daily-bar scan.
            if ranked:
                setup_df_all = pd.DataFrame(ranked)
                if "setup_type" in setup_df_all.columns:
                    st.markdown("#### 🎯 Setup quality & scenario levels")
                    setup_counts = setup_df_all["setup_type"].fillna("Unavailable").value_counts().to_dict()
                    setup_cols = st.columns(4)
                    setup_cols[0].metric("Pullback watches", int(setup_counts.get("PULLBACK WATCH", 0)))
                    setup_cols[1].metric("Breakout watches", int(setup_counts.get("BREAKOUT WATCH", 0)))
                    setup_cols[2].metric("Extended", int(setup_counts.get("EXTENDED — DO NOT CHASE", 0)))
                    setup_cols[3].metric("No clear setup", int(setup_counts.get("NO CLEAR SETUP", 0)))
                    setup_view = setup_df_all[setup_df_all["setup_type"].isin(["PULLBACK WATCH", "BREAKOUT WATCH", "EXTENDED — DO NOT CHASE"])].copy()
                    setup_fields = [c for c in ["symbol", "setup_type", "setup_status", "setup_quality_score", "last", "setup_entry_reference", "setup_stop_reference", "setup_target_reference", "setup_reward_risk", "setup_distance_to_entry_pct", "atr_pct"] if c in setup_view.columns]
                    if setup_fields:
                        setup_view = setup_view[setup_fields].rename(columns={
                            "symbol": "Symbol", "setup_type": "Setup type", "setup_status": "Status",
                            "setup_quality_score": "Quality score", "last": "Last daily close",
                            "setup_entry_reference": "Entry reference", "setup_stop_reference": "Stop reference",
                            "setup_target_reference": "Target reference", "setup_reward_risk": "Illustrative R:R",
                            "setup_distance_to_entry_pct": "Distance to reference %", "atr_pct": "ATR %"
                        })
                        st.dataframe(setup_view.style.format({
                            c: "${:,.2f}" for c in ["Last daily close", "Entry reference", "Stop reference", "Target reference"] if c in setup_view.columns
                        } | {c: "{:.1f}" for c in ["Quality score", "Illustrative R:R"] if c in setup_view.columns} | {c: "{:+.2f}%" for c in ["Distance to reference %"] if c in setup_view.columns} | {c: "{:.2f}%" for c in ["ATR %"] if c in setup_view.columns}), use_container_width=True, hide_index=True)
                    st.caption("Entry, stop and target values are ATR-based historical daily-bar scenario references for research only. They are not live quotes, confirmed support/resistance, trade instructions or guaranteed fills. Descriptive forward event-study results appear below; they are not a validated trading strategy.")

            st.markdown("#### Cloud watchlist")
            if watchlist:
                watch_df = pd.DataFrame(watchlist)
                watch_columns = [
                    col for col in [
                        "symbol", "score", "adjusted_score", "portfolio_fit_score", "portfolio_fit_adjustment", "portfolio_sector_exposure_pct", "portfolio_fit_note", "signal_score", "sector_group", "sector_rotation_state", "relative_1m_vs_spy_pp", "relative_1m_vs_sector_pp", "signal", "weekly_trend", "return_1m_pct", "rsi", "risk"
                    ] if col in watch_df.columns
                ]
                watch_df = watch_df[watch_columns].rename(columns={
                    "symbol": "Symbol", "score": "Technical score", "adjusted_score": "Refined rank score", "portfolio_fit_score": "Portfolio-fit score", "portfolio_fit_adjustment": "Fit adjustment", "portfolio_sector_exposure_pct": "Existing sector exposure %", "portfolio_fit_note": "Portfolio note", "signal_score": "Mechanical signal score",
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

            portfolio_risk = (cloud_scan.get("ai_review") or {}).get("portfolio_risk") or {}
            if portfolio_risk:
                st.divider()
                st.markdown("### 🛡️ Portfolio concentration & correlation")
                st.caption(f"Cloud worker version: {portfolio_risk.get('worker_version', (cloud_scan.get('ai_review') or {}).get('worker_version', 'Not recorded'))}")
                st.caption(portfolio_risk.get("data_note", "Read-only portfolio snapshot from the latest scan."))
                if portfolio_risk.get("status") == "unavailable":
                    st.warning(portfolio_risk.get("reason", "Portfolio risk context unavailable."))
                else:
                    pc = st.columns(4)
                    pc[0].metric("Positions", portfolio_risk.get("position_count", 0))
                    pc[1].metric("Equity reference", f'${float(portfolio_risk.get("equity_reference", 0)):,.2f}')
                    pc[2].metric("Position value", f'${float(portfolio_risk.get("position_value_reference", 0)):,.2f}')
                    pc[3].metric("Largest sector", f'{float(portfolio_risk.get("largest_sector_weight_pct", 0)):.1f}%')
                    sector_weights = portfolio_risk.get("sector_weights_pct") or {}
                    if sector_weights:
                        sw = pd.DataFrame([{"Sector / group": k, "Portfolio weight %": v} for k,v in sector_weights.items()])
                        st.dataframe(sw, use_container_width=True, hide_index=True)
                    corr_rows = portfolio_risk.get("top_correlated_pairs") or []
                    if corr_rows:
                        st.markdown("**Most correlated held-position pairs (60-day daily returns)**")
                        st.dataframe(pd.DataFrame(corr_rows), use_container_width=True, hide_index=True)
                    st.caption("Portfolio-fit score is a bounded research-priority adjustment for existing holdings and sector concentration. It is not an order recommendation. Price references may be stale outside market hours.")

            validation = (cloud_scan.get("ai_review") or {}).get("setup_validation") or {}
            if validation:
                st.divider()
                st.markdown("### 🧪 Historical setup validation")
                st.caption(validation.get("method", "Descriptive historical event study; not a forecast."))
                setup_metrics = validation.get("setups") or {}
                for setup_name, metrics in setup_metrics.items():
                    st.markdown(f"**{setup_name.title()}**")
                    vc = st.columns(4)
                    vc[0].metric("Historical events", metrics.get("event_count", 0))
                    vc[1].metric("5-day win rate", f"{metrics['win_rate_5d_pct']:.1f}%" if metrics.get("win_rate_5d_pct") is not None else "—")
                    vc[2].metric("10-day average", f"{metrics['average_return_10d_pct']:+.2f}%" if metrics.get("average_return_10d_pct") is not None else "—")
                    vc[3].metric("20-day average", f"{metrics['average_return_20d_pct']:+.2f}%" if metrics.get("average_return_20d_pct") is not None else "—")
                    ex = st.columns(4)
                    ex[0].metric("5D avg favorable move", f"{metrics['average_mfe_5d_pct']:+.2f}%" if metrics.get("average_mfe_5d_pct") is not None else "—")
                    ex[1].metric("5D avg adverse move", f"{metrics['average_mae_5d_pct']:+.2f}%" if metrics.get("average_mae_5d_pct") is not None else "—")
                    ex[2].metric("20D avg favorable move", f"{metrics['average_mfe_20d_pct']:+.2f}%" if metrics.get("average_mfe_20d_pct") is not None else "—")
                    ex[3].metric("20D avg adverse move", f"{metrics['average_mae_20d_pct']:+.2f}%" if metrics.get("average_mae_20d_pct") is not None else "—")
                st.caption("Historical observations are not live signals or evidence of future profitability. Favorable/adverse excursions show best/worst intraperiod price movement, not an achievable fill. Events may overlap; returns exclude trading costs and survivorship-bias adjustments.")

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

            st.caption("V3.18 refined ranking uses continuous trend, momentum, RSI, weekly alignment, relative strength versus SPY and the mapped sector ETF, plus a volatility penalty. Setup diagnostics classify pullback/breakout watches and extended conditions using daily ATR and prior 20-day ranges; scenario levels are research references only. A bounded sector-rotation overlay is then applied. The separate mechanical signal score and BUY CANDIDATE/WATCH labels remain unchanged; unmapped assets receive no sector adjustment.")
            st.warning(
                "The scanner uses Yahoo Finance daily bars. The AI is a second opinion based only on the supplied scan facts; it does not verify live quotes, news, filings, fundamentals, or intraday conditions. Rankings are research prioritization, not buy/sell signals or instructions to trade. The cloud worker is observation-only."
            )
        else:
            st.info(
                "No cloud scan report is available yet. Confirm the Render worker is running and has saved "
                "a report to Supabase, then use Refresh cloud results."
            )

    try:
        render_cloud_scanner()
    except Exception as exc:
        # A cloud-panel rendering/data-shape error must not prevent the
        # independent scanner, virtual account, and performance tabs rendering.
        st.error("The cloud scanner panel encountered an unexpected data/rendering error.")
        st.caption(f"Cloud panel error type: {type(exc).__name__}. Other dashboard sections remain available.")

with scanner_tab:
    if data.empty:
        st.info("Market Scanner is waiting for usable market data. Choose a market group and run the scan again when data is available.")
    else:
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
    
    
        pass

with paper_tab:
    st.subheader("🗃️ Legacy $1,000 virtual account — retired")
    st.info(
        "This Supabase simulation account is retired. Its historical positions and journal are "
        "preserved for reference only. This dashboard no longer opens, closes, resets, or monitors "
        "simulated positions. All new paper-trading activity belongs in Alpaca Paper Trading."
    )
    if paper_account_available:
        archived_positions = st.session_state.get("paper_positions") or {}
        archived_journal = st.session_state.get("paper_journal") or []
        st.caption(
            f"Archived record only · {len(archived_positions)} position record(s) · "
            f"{len(archived_journal)} journal entr(y/ies) · "
            f"last saved: {st.session_state.get('paper_account_updated_at') or 'not recorded'}"
        )
        if archived_positions:
            st.markdown("#### Archived positions")
            st.dataframe(pd.DataFrame([
                {"Symbol": symbol, **position} for symbol, position in archived_positions.items()
            ]), use_container_width=True, hide_index=True)
        if archived_journal:
            st.markdown("#### Archived trade journal")
            st.dataframe(pd.DataFrame(archived_journal), use_container_width=True, hide_index=True)
    else:
        st.warning("The archived record could not be loaded. No replacement account was created.")


# The virtual account is retired: only read preserved snapshots; never append new rows.
snapshot_error = None
snapshot_history = []
if paper_account_available:
    try:
        snapshot_history = load_snapshot_history()
    except Exception as exc:
        snapshot_error = exc


with analytics_tab:
    st.subheader("Archived virtual-account performance")
    st.caption(
        "Read-only historical snapshots from the retired $1,000 Supabase simulation account. "
        "No current market marks are applied to archived positions and no new snapshots are recorded."
    )
    if not paper_account_available:
        st.warning("Archived performance is unavailable because the historical record could not be loaded.")
    elif snapshot_error:
        st.error(f"Historical snapshots could not be loaded: {snapshot_error}")
    elif snapshot_history:
        history_df = pd.DataFrame(snapshot_history)
        history_df["snapshot_date"] = pd.to_datetime(history_df["snapshot_date"])
        history_df = history_df.sort_values("snapshot_date").drop_duplicates("snapshot_date", keep="last")
        history_df = history_df.set_index("snapshot_date")
        st.line_chart(history_df["equity"].rename("Archived account value ($)"), use_container_width=True)
        st.dataframe(history_df.reset_index(), use_container_width=True, hide_index=True)
    else:
        st.info("No historical performance snapshots are available in the archive.")


with intelligence_tab:
    st.subheader("🏆 Bot Intelligence & Achievement Center")
    st.caption("A read-only scorecard built from simulated historical paper replays. It rewards repeatable process and risk discipline—not lucky wins. These are not Alpaca broker fills and this panel cannot change trading permissions.")
    if st.button("↻ Refresh intelligence center", key="refresh_bot_intelligence"):
        load_bot_intelligence_replays.clear()
        load_bot_intelligence_signal_context.clear()
    try:
        replay_rows = load_bot_intelligence_replays()
        signal_context = load_bot_intelligence_signal_context()
    except Exception as exc:
        replay_rows = []
        signal_context = []
        st.error(f"Could not load replay evidence: {type(exc).__name__}")
    # Volatility-transition response research: SPY trailing realized volatility
    # defines transitions using a threshold shifted one session to avoid lookahead.
    st.markdown("#### 🌡️ Volatility-transition response (1 / 5 / 10 / 20 sessions)")
    st.caption("Retrospective research only. Regimes use SPY 20-session realized volatility versus a full trailing 252-session 75th-percentile history, shifted one session so today's regime never uses today's threshold update. Strategy outcomes come from persisted signal observations; Yahoo daily history can be delayed, revised, incomplete, and is not point-in-time.")
    try:
        transition_history = load_history(("SPY",), period="5y")
        transition_signals = load_strategy_signal_events()
        if "SPY" not in transition_history or transition_history["SPY"].empty:
            st.info("SPY daily history is unavailable; volatility-transition study is waiting for source bars.")
        else:
            transition_close = transition_history["SPY"]["Close"]
            transition_study = build_volatility_transition_study(transition_close, transition_signals)
            transition_cols = st.columns(3)
            transition_cols[0].metric("Detected transitions", len(transition_study["transitions"]))
            transition_cols[1].metric("Signal observations loaded", len(transition_signals))
            transition_cols[2].metric("Matched response groups", len(transition_study["rows"]))
            coverage = transition_study["diagnostics"]
            with st.expander("Signal coverage & exclusions", expanded=True):
                coverage_cols = st.columns(4)
                coverage_cols[0].metric("Matched signals", coverage["matched_signals"])
                coverage_cols[1].metric("Valid outcome observations", coverage["valid_outcome_observations"])
                coverage_cols[2].metric("Dates outside SPY history", coverage["date_not_in_spy_history"])
                coverage_cols[3].metric("No prior transition", coverage["no_prior_transition"])
                st.caption(
                    f"Loaded {coverage['signals_total']} signals · "
                    f"{coverage['invalid_signal_dates']} invalid dates · "
                    f"{coverage['transition_day_excluded']} transition-day signals excluded · "
                    f"{coverage['outside_20_session_window']} older than 20 sessions · "
                    f"{coverage['signals_with_valid_outcomes']} matched signals had at least one valid stored outcome. "
                    "Signals are assigned only to the latest preceding transition, so overlapping windows are not double-counted."
                )
            transition_cols = st.columns(2)
            transition_cols[0].metric("High-volatility sessions", int((transition_study["regime"] == "HIGH").sum()))
            transition_cols[1].metric("Baseline sessions", int((transition_study["regime"] == "BASELINE").sum()))
            if transition_study["transitions"]:
                transition_frame = pd.DataFrame(transition_study["transitions"]).tail(12)
                st.dataframe(transition_frame, use_container_width=True, hide_index=True)
            if transition_study["rows"]:
                response_frame = pd.DataFrame(transition_study["rows"])
                st.dataframe(response_frame, use_container_width=True, hide_index=True)
            else:
                st.info("No signal outcomes currently align to the first 20 sessions after a detected SPY volatility transition. More history or matched observations are needed.")
            st.caption("Age buckets are measured in SPY trading sessions after each transition: session 1, sessions 2–5, 6–10, and 11–20. Rows are grouped by transition direction, setup, and persisted 1d/5d/10d/20d outcome horizon. Samples under 30 are exploratory; this is not a readiness score or trading instruction.")
    except Exception as exc:
        st.warning(f"Volatility-transition research is temporarily unavailable: {type(exc).__name__}")

    replay_df = pd.DataFrame(replay_rows)
    context_df = pd.DataFrame(signal_context)
    if not replay_df.empty and not context_df.empty:
        replay_df = replay_df.merge(context_df, how="left", left_on="event_id", right_on="id", suffixes=("", "_signal"))
    if replay_df.empty:
        st.info("No replay evidence is available yet. Achievements will appear as completed simulated outcomes are recorded.")
    else:
        for col in ("net_realized_pnl", "return_pct", "entry_price", "exit_price", "quantity"):
            if col in replay_df:
                replay_df[col] = pd.to_numeric(replay_df[col], errors="coerce")
        closed_status = replay_df["status"].astype(str).str.upper().str.startswith("CLOSED")
        closed = replay_df[closed_status & replay_df["net_realized_pnl"].notna()].copy()
        open_count = int((~closed_status).sum())
        closed_missing_pnl_count = int((closed_status & replay_df["net_realized_pnl"].isna()).sum())
        if not closed.empty:
            closed["is_win"] = closed["net_realized_pnl"] > 0
            closed["result_data"] = closed["result"].apply(lambda value: value if isinstance(value, dict) else {})
            closed["sizing_data"] = closed["result_data"].apply(lambda value: value.get("sizing") or {})
            def _within_recorded_risk_budget(sizing):
                """Fail closed on missing, malformed, non-finite, or non-positive risk budgets."""
                if not isinstance(sizing, dict) or sizing.get("status") != "SIZED":
                    return False
                try:
                    projected = float(sizing.get("projected_position_risk"))
                    budget = float(sizing.get("trade_risk_budget"))
                except (TypeError, ValueError, OverflowError):
                    return False
                return bool(np.isfinite(projected) and np.isfinite(budget) and budget > 0 and 0 <= projected <= budget)

            closed["risk_disciplined"] = closed["sizing_data"].apply(_within_recorded_risk_budget)
            n_closed = len(closed)
            wins = int(closed["is_win"].sum())
            win_rate = wins / n_closed * 100
            total_pnl = float(closed["net_realized_pnl"].sum())
            avg_return = float(closed["return_pct"].mean()) if closed["return_pct"].notna().any() else np.nan
            discipline_rate = float(closed["risk_disciplined"].mean() * 100)
            sequence_risk = replay_sequence_risk_metrics(closed.to_dict("records"))
            # A transparent process score: risk-budget adherence (50%), win rate (25%),
            # and positive aggregate replay P/L (25%). It is descriptive, not predictive.
            pnl_component = 25.0 if total_pnl > 0 else (12.5 if total_pnl == 0 else 0.0)
            score = int(round(50 * discipline_rate / 100 + 25 * win_rate / 100 + pnl_component))
            grade = "A" if score >= 90 else "B" if score >= 80 else "C" if score >= 70 else "D" if score >= 60 else "Needs work"
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Process score", f"{score}/100", grade)
            m2.metric("Closed replay outcomes", f"{n_closed}", f"{open_count} open / unresolved · {closed_missing_pnl_count} closed missing P/L")
            m3.metric("Replay win rate", f"{win_rate:.1f}%")
            m4.metric("Net simulated P/L", f"${total_pnl:,.2f}")
            st.progress(max(0.0, min(1.0, score / 100)), text=f"Process score · {grade}")
            st.caption(f"Risk-budget adherence: {discipline_rate:.1f}% · Average closed replay return: {avg_return:.2f}% · Formula: 50% risk adherence + 25% win rate + 25% aggregate P/L sign. Current sample: {n_closed} closed outcomes.")
            st.markdown("#### 🧯 Loss-streak & drawdown intelligence")
            r1, r2, r3 = st.columns(3)
            r1.metric("Current consecutive losses", sequence_risk["current_loss_streak"])
            r2.metric("Longest loss streak", sequence_risk["max_loss_streak"])
            r3.metric("Replay sequence drawdown", f"${sequence_risk['max_sequence_drawdown']:,.2f}")
            st.caption("These are chronological isolated-replay diagnostics, ordered by exit date. Replay events are independently sized and are not netted into a portfolio; this is not Alpaca account drawdown or a portfolio-equity curve.")
            st.markdown("#### 🎖️ Achievements")
            achievements = [
                ("🛡️ Risk-aware operator", "At least 90% of closed replays stayed within their recorded per-trade risk budget.", discipline_rate >= 90 and n_closed >= 5),
                ("🎯 First ten evaluated", "Ten closed simulated outcomes recorded.", n_closed >= 10),
                ("🏅 Fifty-trade sample", "Fifty closed simulated outcomes recorded; enough to begin more meaningful comparisons.", n_closed >= 50),
                ("🔥 Positive replay aggregate", "Aggregate net simulated P/L is positive across closed outcomes.", total_pnl > 0 and n_closed >= 10),
                ("🧠 Model diversity", "At least three distinct replay model versions have been evaluated.", closed["model_version"].nunique() >= 3),
            ]
            ach_cols = st.columns(2)
            for idx, (name, detail, earned) in enumerate(achievements):
                with ach_cols[idx % 2]:
                    if earned:
                        st.success(f"{name} · UNLOCKED\n\n{detail}")
                    else:
                        st.info(f"{name} · IN PROGRESS\n\n{detail}")
            st.markdown("#### 📊 Strategy / model leaderboard")
            leaderboard = (
                closed.groupby("model_version", dropna=False)
                .agg(Closed=("id", "count"), Win_Rate=("is_win", "mean"),
                     Net_PnL=("net_realized_pnl", "sum"), Avg_Return=("return_pct", "mean"),
                     Risk_Adherence=("risk_disciplined", "mean"))
                .reset_index()
            )
            leaderboard = leaderboard[leaderboard["Closed"] >= 5].copy()
            if leaderboard.empty:
                st.caption("Leaderboard rankings unlock at five closed outcomes per model. This prevents tiny samples from looking like proven winners.")
            else:
                leaderboard["Win rate %"] = leaderboard.pop("Win_Rate") * 100
                leaderboard["Risk adherence %"] = leaderboard.pop("Risk_Adherence") * 100
                leaderboard["Average return %"] = leaderboard.pop("Avg_Return")
                leaderboard = leaderboard.rename(columns={"model_version": "Model", "Closed": "Closed outcomes", "Net_PnL": "Net simulated P/L"})
                leaderboard = leaderboard.sort_values(["Net simulated P/L", "Win rate %"], ascending=False)
                st.dataframe(leaderboard, use_container_width=True, hide_index=True)
            st.markdown("#### 🧭 Setup & volatility-regime intelligence")
            st.caption("Each segment is linked to its original signal. Rankings require at least five closed replay outcomes; smaller samples remain unranked.")
            for dimension, heading in (("setup_type", "Setup leaderboard"), ("market_regime", "Market-regime leaderboard")):
                if dimension not in closed.columns:
                    continue
                segment = closed[closed[dimension].notna()].copy()
                if segment.empty:
                    continue
                summary = segment.groupby(dimension).agg(Closed=("id", "count"), Wins=("is_win", "sum"), Net_PnL=("net_realized_pnl", "sum"), Avg_Return=("return_pct", "mean")).reset_index()
                summary["Win rate %"] = summary["Wins"] / summary["Closed"] * 100
                summary["Evidence"] = np.where(summary["Closed"] >= 5, "Rank eligible", "Early sample")
                summary = summary.rename(columns={dimension: "Segment", "Closed": "Closed outcomes", "Net_PnL": "Net simulated P/L", "Avg_Return": "Average return %"}).sort_values("Closed outcomes", ascending=False)
                st.markdown("**" + heading + "**")
                st.dataframe(summary[["Segment", "Closed outcomes", "Wins", "Win rate %", "Average return %", "Net simulated P/L", "Evidence"]], use_container_width=True, hide_index=True)
                for _, row in summary[summary["Closed outcomes"] >= 5].iterrows():
                    if row["Average return %"] < 0:
                        st.warning(str(row["Segment"]) + ": negative average replay return (" + format(row["Average return %"], ".2f") + "%). Flagged for research only; no strategy settings or permissions are changed.")
                    elif row["Average return %"] > 0:
                        st.success(str(row["Segment"]) + ": positive average replay return (" + format(row["Average return %"], ".2f") + "%). Observational, not proof of an edge.")
            if "market_regime" in closed.columns and closed["market_regime"].dropna().nunique() < 2:
                st.caption("Only one market regime is represented in closed replays; regime-to-regime comparisons are not yet supported.")

            st.markdown("#### 🧾 Recent evaluated outcomes")
            recent = closed.sort_values("updated_at", ascending=False).head(20)
            display = recent[["symbol", "model_version", "status", "entry_date", "exit_date", "net_realized_pnl", "return_pct", "risk_disciplined"]].copy()
            display = display.rename(columns={"symbol": "Symbol", "model_version": "Model", "status": "Replay result", "entry_date": "Entry", "exit_date": "Exit", "net_realized_pnl": "Net simulated P/L", "return_pct": "Return %", "risk_disciplined": "Within risk budget"})
            st.dataframe(display, use_container_width=True, hide_index=True)
            st.caption("Scoring is descriptive and sample-size aware. Open/unresolved replays are excluded from win rate and realized P/L. No XP, badge, grade, or leaderboard position changes strategy readiness, sizing, risk gates, or order routing.")
        else:
            st.info(f"{len(replay_df)} replay records found, but none has a closed outcome with realized simulated P/L yet. Open and unresolved records are not scored as wins or losses.")

