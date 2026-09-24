import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
from html import escape

st.set_page_config(
    page_title="Vee Repairs · Operations Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================================================================
# VEE REPAIRS · PREMIUM OPERATIONS COMMAND CENTRE
# The underlying source / transformation logic is retained. The UI layer has
# been redesigned around the supplied Sparta Agent Portal reference.
# ==============================================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

:root {
    --navy: #0B1736;
    --navy-2: #122451;
    --blue: #2563EB;
    --cyan: #06B6D4;
    --gold: #EAB308;
    --gold-soft: #FEF9C3;
    --green: #10B981;
    --amber: #F59E0B;
    --red: #EF4444;
    --ink: #0F172A;
    --slate-700: #334155;
    --slate-600: #475569;
    --slate-500: #64748B;
    --slate-400: #94A3B8;
    --slate-300: #CBD5E1;
    --slate-200: #E2E8F0;
    --slate-100: #F1F5F9;
    --surface: #FFFFFF;
    --page: #F3F6FA;
}

html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"],
[data-testid="stSidebar"], button, input, textarea, select {
    font-family: 'Inter', sans-serif !important;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at 6% -3%, rgba(37,99,235,.09), transparent 28%),
        radial-gradient(circle at 97% 2%, rgba(234,179,8,.08), transparent 25%),
        var(--page);
}

[data-testid="stHeader"] {
    background: rgba(243,246,250,.72) !important;
    backdrop-filter: blur(14px);
}

.block-container {
    max-width: 1540px;
    padding: 1rem 1.35rem 2.6rem 1.35rem !important;
}

/* ------------------------------ SIDEBAR -------------------------------- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #09132E 0%, #0D1B3D 58%, #0A1531 100%);
    border-right: 1px solid rgba(255,255,255,.07);
}
[data-testid="stSidebar"] * { color: #EAF0FF; }
[data-testid="stSidebar"] .stCaption { color: #9FB3DC !important; }
[data-testid="stSidebar"] [data-testid="stButton"] button {
    background: rgba(255,255,255,.065) !important;
    border: 1px solid rgba(255,255,255,.11) !important;
    color: #FFFFFF !important;
    border-radius: 10px !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] button:hover {
    background: rgba(255,255,255,.11) !important;
    border-color: rgba(255,255,255,.18) !important;
}
.sidebar-profile {
    margin: .3rem 0 1.05rem;
    padding: 15px;
    border: 1px solid rgba(255,255,255,.10);
    border-radius: 16px;
    background: linear-gradient(135deg, rgba(255,255,255,.09), rgba(255,255,255,.035));
    box-shadow: inset 0 1px 0 rgba(255,255,255,.055);
}
.sidebar-avatar {
    width: 42px; height: 42px; border-radius: 12px;
    display:flex; align-items:center; justify-content:center;
    background: linear-gradient(135deg, var(--blue), var(--cyan));
    color:#fff; font-size:1.0rem; font-weight:900;
    box-shadow: 0 8px 22px rgba(37,99,235,.22);
}
.sidebar-kicker {
    margin-top: 11px; font-size: .64rem; text-transform:uppercase;
    letter-spacing:1.4px; font-weight:850; color:#9FB3DC !important;
}
.sidebar-name { margin-top: 2px; color:#fff !important; font-size:1.02rem; font-weight:800; }
.sidebar-section {
    margin: 16px 0 7px; font-size:.64rem; color:#7E93BF !important;
    text-transform:uppercase; letter-spacing:1.15px; font-weight:850;
}
.sidebar-stat {
    display:flex; justify-content:space-between; align-items:center;
    padding: 8px 10px; margin: 5px 0; border-radius:9px;
    background: rgba(255,255,255,.045); border:1px solid rgba(255,255,255,.06);
    font-size:.70rem;
}
.sidebar-stat b { color:#fff; }

/* ------------------------------- HERO ---------------------------------- */
.hero-shell {
    position:relative; overflow:hidden; border-radius:23px; padding:22px 24px;
    color:#fff; border:1px solid rgba(255,255,255,.08);
    background:
        radial-gradient(circle at 83% 18%, rgba(6,182,212,.23), transparent 24%),
        radial-gradient(circle at 4% 100%, rgba(59,130,246,.28), transparent 31%),
        radial-gradient(circle at 62% 115%, rgba(234,179,8,.10), transparent 24%),
        linear-gradient(135deg, #09142F 0%, #10285E 55%, #153C73 100%);
    box-shadow: 0 18px 45px rgba(15,23,42,.14);
}
.hero-shell::after {
    content:""; position:absolute; width:250px; height:250px; right:-78px; top:-128px;
    border-radius:999px; border:1px solid rgba(255,255,255,.08);
    box-shadow: 0 0 0 34px rgba(255,255,255,.025), 0 0 0 68px rgba(255,255,255,.018);
}
.hero-kicker { position:relative; z-index:2; font-size:.67rem; text-transform:uppercase; letter-spacing:1.6px; font-weight:900; color:#8DB4FF; margin-bottom:4px; }
.hero-title { position:relative; z-index:2; font-size:1.78rem; line-height:1.05; font-weight:900; letter-spacing:-.04em; }
.hero-sub { position:relative; z-index:2; color:#C5D4F3; font-size:.80rem; margin-top:6px; line-height:1.45; }
.hero-meta { position:relative; z-index:2; display:flex; flex-wrap:wrap; gap:7px; margin-top:14px; }
.hero-chip { display:inline-flex; align-items:center; gap:6px; padding:5px 9px; border-radius:999px; border:1px solid rgba(255,255,255,.10); background:rgba(255,255,255,.07); color:#EAF0FF; font-size:.61rem; font-weight:800; }
.hero-status-card { height:100%; padding:17px; border-radius:18px; background:rgba(255,255,255,.055); border:1px solid rgba(255,255,255,.09); }
.hero-status-label { color:#9FB5DA; font-size:.62rem; text-transform:uppercase; letter-spacing:1.1px; font-weight:900; }
.hero-status-value { color:#fff; font-size:1.0rem; font-weight:850; margin-top:4px; }
.live-dot { display:inline-block; width:7px; height:7px; border-radius:50%; background:#34D399; margin-right:6px; box-shadow:0 0 0 4px rgba(52,211,153,.10); }

/* --------------------------- FILTER DECK ------------------------------- */
.filter-shell {
    margin: 12px 0 17px; padding: 12px 14px 5px; border-radius:16px;
    background:rgba(255,255,255,.80); border:1px solid rgba(226,232,240,.95);
    box-shadow:0 8px 22px rgba(15,23,42,.04); backdrop-filter:blur(10px);
}
.filter-kicker { font-size:.63rem; color:var(--slate-500); font-weight:900; text-transform:uppercase; letter-spacing:1.15px; margin-bottom:7px; }
.filter-note { font-size:.66rem; color:var(--slate-400); margin-top:0; }
.quick-pill {
    display:inline-flex; align-items:center; padding:4px 8px; border-radius:999px;
    background:#EAF1FF; color:#1D4ED8; font-size:.59rem; font-weight:850;
    margin-top: 5px;
}

/* ------------------------------ SECTION -------------------------------- */
.section-row { display:flex; justify-content:space-between; align-items:flex-end; gap:10px; margin:19px 0 9px; }
.section-title { display:flex; align-items:center; gap:10px; color:var(--ink); font-size:1.0rem; font-weight:900; letter-spacing:-.02em; }
.section-icon { width:31px; height:31px; border-radius:9px; display:inline-flex; align-items:center; justify-content:center; background:#EAF1FF; color:var(--blue); font-size:.87rem; box-shadow:inset 0 0 0 1px rgba(37,99,235,.08); }
.section-note { color:var(--slate-400); font-size:.66rem; text-align:right; }

/* -------------------------------- KPIs --------------------------------- */
.kpi-card {
    min-height:103px; padding:13px 14px; border-radius:16px; background:rgba(255,255,255,.92);
    border:1px solid var(--slate-200); box-shadow:0 7px 20px rgba(15,23,42,.045);
    transition:transform .18s ease, box-shadow .18s ease;
}
.kpi-card:hover { transform:translateY(-2px); box-shadow:0 13px 28px rgba(15,23,42,.075); }
.kpi-label { color:var(--slate-500); font-size:.60rem; font-weight:900; text-transform:uppercase; letter-spacing:.75px; }
.kpi-value { margin-top:6px; color:var(--ink); font-size:1.5rem; line-height:1; font-weight:900; letter-spacing:-.045em; }
.kpi-sub { margin-top:6px; color:var(--slate-400); font-size:.61rem; line-height:1.35; }
.kpi-accent { height:3px; width:100%; border-radius:99px; margin-bottom:10px; background:linear-gradient(90deg,var(--blue),var(--cyan)); }

/* ------------------------------ CARDS --------------------------------- */
.panel {
    border:1px solid var(--slate-200); border-radius:16px; background:rgba(255,255,255,.93);
    box-shadow:0 7px 20px rgba(15,23,42,.04); padding:13px 14px;
}
.panel-title { color:var(--ink); font-size:.78rem; font-weight:900; }
.panel-sub { color:var(--slate-400); font-size:.62rem; margin-top:2px; line-height:1.4; }
.action-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:11px; margin:2px 0 3px; }
.action-card { min-height:120px; padding:14px; border-radius:15px; border:1px solid var(--slate-200); background:rgba(255,255,255,.94); box-shadow:0 7px 20px rgba(15,23,42,.04); position:relative; overflow:hidden; }
.action-card::after { content:""; position:absolute; width:96px; height:96px; right:-32px; top:-38px; border-radius:999px; border:1px solid rgba(37,99,235,.08); }
.action-top { display:flex; align-items:center; gap:8px; }
.action-icon { width:30px; height:30px; border-radius:9px; display:flex; align-items:center; justify-content:center; font-size:.82rem; font-weight:900; }
.action-label { color:var(--slate-600); font-size:.60rem; text-transform:uppercase; letter-spacing:.7px; font-weight:900; }
.action-count { color:var(--ink); margin-top:8px; font-size:1.45rem; line-height:1; font-weight:900; letter-spacing:-.04em; }
.action-copy { margin-top:6px; color:var(--slate-500); font-size:.65rem; line-height:1.4; max-width:93%; }

/* ------------------------------ FUNNEL -------------------------------- */
.funnel-card { padding:14px 15px; border-radius:16px; border:1px solid var(--slate-200); background:rgba(255,255,255,.93); box-shadow:0 7px 20px rgba(15,23,42,.04); }
.funnel-row { display:grid; grid-template-columns:95px 1fr 72px; gap:8px; align-items:center; margin:11px 0; }
.funnel-name { color:var(--slate-700); font-size:.66rem; font-weight:850; }
.funnel-track { height:10px; border-radius:99px; background:#EDF2F7; overflow:hidden; }
.funnel-fill { height:100%; border-radius:99px; min-width:3px; }
.funnel-value { color:var(--ink); font-size:.64rem; text-align:right; font-weight:900; }

/* --------------------------- COMPARISON -------------------------------- */
.compare-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:8px; }
.compare-card { min-height:84px; padding:10px 11px; border-radius:13px; border:1px solid var(--slate-200); background:linear-gradient(180deg,#fff,#f8fafc); box-shadow:0 5px 16px rgba(15,23,42,.03); }
.compare-label { color:var(--slate-500); font-size:.58rem; text-transform:uppercase; letter-spacing:.7px; font-weight:900; }
.compare-value { color:var(--ink); font-size:1.06rem; font-weight:900; margin-top:4px; }
.compare-base { color:var(--slate-400); font-size:.59rem; margin-top:2px; }
.delta { display:inline-block; margin-top:6px; padding:3px 7px; border-radius:999px; font-size:.57rem; font-weight:900; }
.delta-up { background:#ECFDF5; color:#047857; }
.delta-down { background:#FEF2F2; color:#B91C1C; }
.delta-flat { background:#F1F5F9; color:#64748B; }

/* ------------------------------ TABS ---------------------------------- */
.stTabs [data-baseweb="tab-list"] { gap:6px; padding:5px; border-radius:15px; background:#fff; border:1px solid var(--slate-200); box-shadow:0 5px 18px rgba(15,23,42,.035); }
.stTabs [data-baseweb="tab"] { min-height:43px; padding:0 17px; border-radius:10px; color:var(--slate-500); font-size:.69rem; font-weight:850; }
.stTabs [aria-selected="true"] { color:#fff !important; background:var(--navy) !important; }
.stTabs [data-baseweb="tab-highlight"] { display:none; }

/* ----------------------------- INPUTS --------------------------------- */
div[data-baseweb="select"] > div, [data-testid="stDateInput"] input, [data-testid="stTextInput"] input {
    border-radius:10px !important; border-color:#D8E1ED !important; background:rgba(255,255,255,.96) !important;
}
[data-testid="stDateInput"] label, [data-testid="stSelectbox"] label, [data-testid="stMultiSelect"] label {
    color:var(--slate-600) !important; font-size:.61rem !important; font-weight:850 !important; text-transform:uppercase; letter-spacing:.55px;
}
[data-testid="stRadio"] label { font-size:.64rem !important; font-weight:750 !important; }
.stButton > button { border-radius:10px !important; font-size:.67rem !important; font-weight:850 !important; min-height:38px; }
.stButton > button:hover { transform:translateY(-1px); box-shadow:0 6px 14px rgba(15,23,42,.07); }

/* ------------------------------ TABLE --------------------------------- */
[data-testid="stDataFrame"] { border-radius:13px; overflow:hidden; border:1px solid var(--slate-200); box-shadow:0 5px 18px rgba(15,23,42,.035); background:#fff; }
[data-testid="stDataFrame"] [role="columnheader"] { background:#F8FAFC !important; color:#475569 !important; font-size:.66rem !important; font-weight:850 !important; }
[data-testid="stDataFrame"] [role="gridcell"] { font-size:.67rem !important; }

/* ---------------------------- STATUS CHIPS ----------------------------- */
.status-chip { display:inline-flex; align-items:center; gap:5px; padding:4px 7px; border-radius:999px; font-size:.57rem; font-weight:900; }
.status-good { background:#ECFDF5; color:#047857; }
.status-warn { background:#FFF7ED; color:#C2410C; }
.status-bad { background:#FEF2F2; color:#B91C1C; }
.status-neutral { background:#F1F5F9; color:#475569; }

/* ----------------------------- FOOTER --------------------------------- */
.footer { text-align:center; color:var(--slate-400); font-size:.60rem; padding-top:16px; }

@media (max-width: 900px) {
    .block-container { padding-left:.9rem !important; padding-right:.9rem !important; }
    .hero-title { font-size:1.45rem; }
    .action-grid { grid-template-columns:1fr; }
    .compare-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }
}
</style>
""", unsafe_allow_html=True)

# Active Asset Links
DASHBOARD_LOGO_URL = "https://raw.githubusercontent.com/dataanalystsparta-netizen/logos/refs/heads/main/vee.png"
LOGIN_LOGO_URL = "https://raw.githubusercontent.com/dataanalystsparta-netizen/logos/refs/heads/main/vee.png"

# Workbook Config
SHEET_ID = '1dUqj3sp5Jva_nYjMzPyGAM6wwNfFINF6IRj5Z94FScU'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

# --- 3. SECURE AUTHENTICATION & AUDIT TRAIL LOG SYSTEM ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "logged_login" not in st.session_state:
    st.session_state["logged_login"] = False

def log_login_event(email):
    try:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        client = gspread.authorize(creds)
        ss = client.open_by_key(SHEET_ID)
        try:
            log_sheet = ss.worksheet('logins')
        except gspread.exceptions.WorksheetNotFound:
            log_sheet = ss.add_worksheet(title='logins', rows='100', cols='3')
            log_sheet.append_row(['Timestamp', 'User Corporate Email', 'Activity Profile Status'])
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_sheet.append_row([current_time, email, 'Login Success'])
    except Exception:
        pass

def check_login():
    email_input = st.session_state["login_email"].strip().lower()
    password_input = st.session_state["login_password"].strip()
    allowed_users = st.secrets.get("users", {})
    if email_input in allowed_users and str(allowed_users[email_input]) == password_input:
        st.session_state["authenticated"] = True
        st.session_state["user_email"] = email_input
        del st.session_state["login_password"]
    else:
        st.error("Invalid email pattern or matching verification credentials.")

if not st.session_state["authenticated"]:
    st.session_state["logged_login"] = False
    st.markdown(f"""
        <div class="vr-login-wrap">
            <div class="login-card">
                <div class="logo-container">
                    <img src="{LOGIN_LOGO_URL}" width="92" style="display:block;margin:0 auto;">
                </div>
                <div class="login-badge">Secure Business Dashboard</div>
                <div class="login-header">Vee Repairs</div>
                <div class="login-subtitle">Leads & Sales Intelligence · Sign in to continue</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    _, form_col, _ = st.columns([1, 1.2, 1])
    with form_col:
        with st.form(key="login_gateway_form"):
            st.text_input("Email Address", key="login_email", placeholder="name@veerepairs.com")
            st.text_input("Security Access Password", type="password", key="login_password", placeholder="••••••••")
            st.form_submit_button("Verify Identity & Connect", on_click=check_login, use_container_width=True)
    st.stop()

if st.session_state["authenticated"] and not st.session_state["logged_login"]:
    log_login_event(st.session_state["user_email"])
    st.session_state["logged_login"] = True

# --- 4. BACKEND CONSOLE METRIC PROCESSOR ---
def normalize_phone_string(series):
    return (
        series.astype(str)
        .str.strip()
        .str.replace(r'\.0$', '', regex=True)
        .str.replace(r'\D', '', regex=True)
    )

def section_header(title, note=None):
    note_html = f'<div class="vr-section-note">{note}</div>' if note else ''
    st.markdown(
        f'<div class="vr-section"><div class="vr-section-title">{title}</div>{note_html}</div>',
        unsafe_allow_html=True
    )

def filter_header():
    st.markdown('<div class="vr-filter"><div class="vr-filter-label">Dashboard controls</div>', unsafe_allow_html=True)


@st.cache_data(ttl=60)
def fetch_dashboard_data():
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    client = gspread.authorize(creds)
    ss = client.open_by_key(SHEET_ID)
    
    # === A. INGEST LEADS WORKSHEET ===
    raw_leads = ss.worksheet('leads').get_all_records()
    df_l = pd.DataFrame(raw_leads)
    df_l.columns = df_l.columns.str.strip()
    
    if 'Source' in df_l.columns:
        df_l['Mapped_Source'] = df_l['Source'].astype(str).str.strip()
        df_l['Mapped_Source'] = df_l['Mapped_Source'].replace(['nan', 'None', '', 'NaN'], None)
        df_l['Mapped_Source'] = df_l['Mapped_Source'].fillna('Delhi')
        df_l.loc[df_l['Mapped_Source'] != 'Delhi', 'Mapped_Source'] = 'Ranchi'
    else:
        df_l['Mapped_Source'] = 'Delhi'
        
    df_l['Parsed_Date'] = pd.to_datetime(df_l['Date'], errors='coerce')
    missing_l_dates = df_l['Parsed_Date'].isna()
    if missing_l_dates.any():
        df_l.loc[missing_l_dates, 'Parsed_Date'] = pd.to_datetime(df_l.loc[missing_l_dates, 'Date'], dayfirst=True, errors='coerce')
        
    df_l['Parsed_Month'] = pd.to_datetime(df_l['Month'], errors='coerce')
    missing_l_months = df_l['Parsed_Month'].isna()
    if missing_l_months.any():
        df_l.loc[missing_l_months, 'Parsed_Month'] = pd.to_datetime(df_l.loc[missing_l_months, 'Month'], dayfirst=True, errors='coerce')
        
    df_l = df_l.dropna(subset=['Parsed_Date']).copy()
    df_l['Day_Display'] = df_l['Parsed_Date'].dt.strftime('%Y-%m-%d')
    df_l['Month_Display'] = df_l['Parsed_Month'].dt.strftime('%b %Y')
    
    if 'Agent' not in df_l.columns and 'Agent Name' in df_l.columns:
        df_l['Agent'] = df_l['Agent Name']
    df_l['Agent'] = df_l['Agent'].astype(str).str.strip().str.title().replace(['Nan', 'None', ''], 'Unassigned')
    
    if 'Phone No.' in df_l.columns:
        df_l['Clean_Phone'] = normalize_phone_string(df_l['Phone No.'])
    elif 'PhoneNo' in df_l.columns:
        df_l['Clean_Phone'] = normalize_phone_string(df_l['PhoneNo'])
    else:
        df_l['Clean_Phone'] = ""

    if 'Quality Status' in df_l.columns:
        df_l['Quality Status'] = df_l['Quality Status'].astype(str).str.strip()
        df_l['Cleaned_Quality_Status'] = df_l['Quality Status'].apply(
            lambda v: 'Approved' if v.lower() in ['approved', 'approve'] else ('Rejected' if v.lower() in ['rejected', 'reject'] else 'Pending')
        )
    else:
        df_l['Cleaned_Quality_Status'] = 'Pending'
        
    # === B. INGEST SALES WORKSHEET ===
    raw_sales = ss.worksheet('sales').get_all_records()
    df_s = pd.DataFrame(raw_sales)
    df_s.columns = df_s.columns.str.strip()
    
    if 'Amount' in df_s.columns:
        df_s['Parsed_Amount'] = pd.to_numeric(
            df_s['Amount'].astype(str).str.replace(r'[^\d.]', '', regex=True), 
            errors='coerce'
        ).fillna(0.0)
    else:
        df_s['Parsed_Amount'] = 0.0

    df_s['Cancel_Reason'] = 'None'
    df_s['Disallowed_Subcategory'] = 'None'

    if 'Payment Status' in df_s.columns:
        df_s['Raw_Payment_Status'] = df_s['Payment Status'].astype(str).str.strip()
        df_s['Cleaned_Payment_Status'] = 'Cancelled'
        
        blank_mask = df_s['Raw_Payment_Status'].isin(['nan', 'None', '', 'NaN'])
        accepted_mask = df_s['Raw_Payment_Status'].str.lower() == 'accepted'
        
        df_s.loc[blank_mask, 'Cleaned_Payment_Status'] = 'Pending'
        df_s.loc[accepted_mask, 'Cleaned_Payment_Status'] = 'Live'
        
        is_cancelled_mask = df_s['Cleaned_Payment_Status'] == 'Cancelled'
        df_s.loc[is_cancelled_mask, 'Cancel_Reason'] = 'Payment Cancelled'
        df_s.loc[is_cancelled_mask, 'Disallowed_Subcategory'] = df_s.loc[is_cancelled_mask, 'Raw_Payment_Status']
    else:
        df_s['Raw_Payment_Status'] = 'Pending'
        df_s['Cleaned_Payment_Status'] = 'Pending'

    if 'WlcmStatus' in df_s.columns:
        wc_cancel_mask = (df_s['Cleaned_Payment_Status'] == 'Pending') & (df_s['WlcmStatus'].astype(str).str.strip().str.title() == 'Cancelled')
        df_s.loc[wc_cancel_mask, 'Cancel_Reason'] = 'WC Cancelled'
        df_s.loc[wc_cancel_mask, 'Cleaned_Payment_Status'] = 'Cancelled'
        
    df_s['Live_Amount'] = 0.0
    df_s.loc[df_s['Cleaned_Payment_Status'] == 'Live', 'Live_Amount'] = df_s['Parsed_Amount']
        
    df_s['Parsed_Date'] = pd.to_datetime(df_s['Date'], errors='coerce')
    missing_s_dates = df_s['Parsed_Date'].isna()
    if missing_s_dates.any():
        df_s.loc[missing_s_dates, 'Parsed_Date'] = pd.to_datetime(df_s.loc[missing_s_dates, 'Date'], dayfirst=True, errors='coerce')
        
    df_s['Parsed_Month'] = pd.to_datetime(df_s['Month'], errors='coerce')
    missing_s_months = df_s['Parsed_Month'].isna()
    if missing_s_months.any():
        df_s.loc[missing_s_months, 'Parsed_Month'] = pd.to_datetime(df_s.loc[missing_s_months, 'Month'], dayfirst=True, errors='coerce')
        
    df_s = df_s.dropna(subset=['Parsed_Date']).copy()
    df_s['Day_Display'] = df_s['Parsed_Date'].dt.strftime('%Y-%m-%d')
    df_s['Month_Display'] = df_s['Parsed_Month'].dt.strftime('%b %Y')
    
    df_s['Agent'] = df_s['Agent'].astype(str).str.strip().str.title().replace(['Nan', 'None', ''], 'Unassigned')
    
    if 'PhoneNo.' in df_s.columns:
        df_s['Clean_Phone'] = normalize_phone_string(df_s['PhoneNo.'])
    elif 'PhoneNo' in df_s.columns:
        df_s['Clean_Phone'] = normalize_phone_string(df_s['PhoneNo'])
    elif 'Phone No.' in df_s.columns:
        df_s['Clean_Phone'] = normalize_phone_string(df_s['Phone No.'])
    else:
        df_s['Clean_Phone'] = ""
        
    return df_l, df_s

try:
    df_leads, df_sales = fetch_dashboard_data()
    is_ready = True
except Exception as e:
    st.error(f"Sync issue with active sheet data nodes: {e}")
    is_ready = False

# ==============================================================================
# PRESENTATION HELPERS
# ==============================================================================

def initials(value):
    parts = [p for p in str(value).replace('@', ' ').split() if p]
    return ''.join(p[0] for p in parts[:2]).upper() or 'V'


def pct(value, total):
    return (float(value) / float(total) * 100.0) if total else 0.0


def date_only(series):
    parsed = pd.to_datetime(series, errors='coerce')
    return parsed.dt.date


def clamp_date(value, lower, upper):
    if value < lower:
        return lower
    if value > upper:
        return upper
    return value


def period_range(preset, today, min_date, max_date):
    if preset == 'Today':
        start = end = today
    elif preset == 'Last 7 Days':
        end = today
        start = today - timedelta(days=6)
    elif preset == 'Last 30 Days':
        end = today
        start = today - timedelta(days=29)
    elif preset == 'This Week':
        start = today - timedelta(days=today.weekday())
        end = today
    elif preset == 'This Month':
        start = today.replace(day=1)
        end = today
    elif preset == 'Last Month':
        first_this = today.replace(day=1)
        end = first_this - timedelta(days=1)
        start = end.replace(day=1)
    elif preset == 'This Quarter':
        q_month = ((today.month - 1) // 3) * 3 + 1
        start = date(today.year, q_month, 1)
        end = today
    elif preset == 'YTD':
        start = date(today.year, 1, 1)
        end = today
    elif preset == 'All Time':
        start = min_date
        end = max_date
    else:
        start = min_date
        end = max_date
    return clamp_date(start, min_date, max_date), clamp_date(end, min_date, max_date)


def render_period_filter(prefix, title, min_date, max_date, default_preset='This Month'):
    min_date = min_date or date.today()
    max_date = max_date or date.today()
    if min_date > max_date:
        min_date, max_date = max_date, min_date
    today = date.today()
    today_for_range = clamp_date(today, min_date, max_date)

    preset_key = f'{prefix}_period_preset'
    start_key = f'{prefix}_period_start'
    end_key = f'{prefix}_period_end'

    if preset_key not in st.session_state:
        st.session_state[preset_key] = default_preset
    if start_key not in st.session_state or end_key not in st.session_state:
        s, e = period_range(default_preset, today_for_range, min_date, max_date)
        st.session_state[start_key] = s
        st.session_state[end_key] = e

    options = ['This Month', 'Today', 'Last 7 Days', 'Last 30 Days', 'This Week', 'Last Month', 'This Quarter', 'YTD', 'All Time', 'Custom']
    with st.container(border=True):
        st.markdown(f'<div class="filter-kicker">{escape(title)}</div>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns([1.9, 1.1, 1.1, 0.75], gap='small')
        with c1:
            preset = st.radio('Quick Range', options, index=options.index(st.session_state[preset_key]), horizontal=True, key=preset_key, label_visibility='collapsed')
        if preset != 'Custom':
            s, e = period_range(preset, today_for_range, min_date, max_date)
            st.session_state[start_key] = s
            st.session_state[end_key] = e
        with c2:
            st.caption('START DATE')
            start_date = st.date_input('Start Date', key=start_key, min_value=min_date, max_value=max_date, disabled=(preset != 'Custom'), label_visibility='collapsed')
        with c3:
            st.caption('END DATE')
            end_date = st.date_input('End Date', key=end_key, min_value=min_date, max_value=max_date, disabled=(preset != 'Custom'), label_visibility='collapsed')
        with c4:
            days = (end_date - start_date).days + 1 if end_date >= start_date else 0
            st.caption('WINDOW')
            unit = 's' if days != 1 else ''
            st.markdown(f'<span class="quick-pill">{days} day{unit}</span>', unsafe_allow_html=True)
    if start_date > end_date:
        st.error('Start Date must be on or before End Date.')
        st.stop()
    return start_date, end_date


def filter_frame(df, start_date, end_date, source=None, agent=None, status=None, month=None):
    out = df.copy()
    out = out[(out['Parsed_Date'].dt.date >= start_date) & (out['Parsed_Date'].dt.date <= end_date)].copy()
    if source and source != 'All Sources' and 'Mapped_Source' in out.columns:
        out = out[out['Mapped_Source'] == source]
    if agent and agent != 'All Consultants' and 'Agent' in out.columns:
        out = out[out['Agent'] == agent]
    if status and len(status) > 0:
        if 'Cleaned_Quality_Status' in out.columns:
            out = out[out['Cleaned_Quality_Status'].isin(status)]
        elif 'Cleaned_Payment_Status' in out.columns:
            out = out[out['Cleaned_Payment_Status'].isin(status)]
    if month and month != 'All Months' and 'Month_Display' in out.columns:
        out = out[out['Month_Display'] == month]
    return out


def latest_month_options(df, start_date, end_date):
    tmp = df[(df['Parsed_Date'].dt.date >= start_date) & (df['Parsed_Date'].dt.date <= end_date)].copy()
    vals = []
    if 'Month_Display' in tmp.columns:
        vals = [v for v in tmp['Month_Display'].dropna().unique().tolist() if str(v) not in {'Unknown', 'NaT Unknown'}]
    vals.sort(key=lambda x: pd.to_datetime(x, format='%b %Y', errors='coerce'))
    return vals


def chart_base(fig, height=330):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter, sans-serif', size=11, color='#475569'),
        margin=dict(l=8, r=8, t=8, b=8),
        height=height,
        legend=dict(title=None, orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        hoverlabel=dict(bgcolor='#0F172A', font=dict(color='#FFFFFF')),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor='#CBD5E1')
    fig.update_yaxes(showgrid=True, gridcolor='#EEF2F7', zeroline=False, title=None)
    return fig


def panel_header(title, subtitle=''):
    sub = f'<div class="panel-sub">{escape(subtitle)}</div>' if subtitle else ''
    st.markdown(f'<div class="panel-title">{escape(title)}</div>{sub}', unsafe_allow_html=True)


def section(title, icon='◆', note=''):
    note_html = f'<div class="section-note">{escape(note)}</div>' if note else ''
    st.markdown(f'<div class="section-row"><div class="section-title"><span class="section-icon">{escape(icon)}</span>{escape(title)}</div>{note_html}</div>', unsafe_allow_html=True)


def kpi(label, value, sub='', accent='linear-gradient(90deg,#2563EB,#06B6D4)'):
    st.markdown(f'''
    <div class="kpi-card">
        <div class="kpi-accent" style="background:{accent};"></div>
        <div class="kpi-label">{escape(str(label))}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{escape(str(sub))}</div>
    </div>
    ''', unsafe_allow_html=True)


def comparison_cards(items):
    html = []
    for label, current, previous, is_rate, base_text in items:
        if is_rate:
            value_text = f'{current:.1f}%'
            delta = current - previous
            delta_text = f'↑ {abs(delta):.1f} pp' if delta > .05 else f'↓ {abs(delta):.1f} pp' if delta < -.05 else '→ 0.0 pp'
        else:
            value_text = f'{int(current):,}'
            delta = current - previous
            delta_text = f'↑ {abs(int(delta)):,}' if delta > 0 else f'↓ {abs(int(delta)):,}' if delta < 0 else '→ 0'
        direction = 'up' if delta > .05 else 'down' if delta < -.05 else 'flat'
        if not is_rate:
            direction = 'up' if delta > 0 else 'down' if delta < 0 else 'flat'
        html.append(f'''
        <div class="compare-card">
            <div class="compare-label">{escape(label)}</div>
            <div class="compare-value">{value_text}</div>
            <div class="compare-base">{escape(base_text)}</div>
            <span class="delta delta-{direction}">{delta_text}</span>
        </div>
        ''')
    st.markdown('<div class="compare-grid">' + ''.join(html) + '</div>', unsafe_allow_html=True)


def action_cards(items):
    html = []
    for title, count, icon, bg, fg, copy in items:
        html.append(f'''
        <div class="action-card">
            <div class="action-top"><div class="action-icon" style="background:{bg};color:{fg};">{escape(icon)}</div><div class="action-label">{escape(title)}</div></div>
            <div class="action-count">{count:,}</div>
            <div class="action-copy">{escape(copy)}</div>
        </div>
        ''')
    st.markdown('<div class="action-grid">' + ''.join(html) + '</div>', unsafe_allow_html=True)


def status_style(value):
    s = str(value).lower()
    if any(x in s for x in ['approved', 'approve', 'live', 'accepted']):
        return 'background:#ECFDF5;color:#047857;font-weight:800;'
    if any(x in s for x in ['pending', 'paper', 'follow', 'committed']):
        return 'background:#FFF7ED;color:#C2410C;font-weight:800;'
    if any(x in s for x in ['rejected', 'reject', 'cancel']):
        return 'background:#FEF2F2;color:#B91C1C;font-weight:800;'
    return ''


def safe_num(value):
    try:
        return float(value)
    except Exception:
        return 0.0


def build_conversion_view(leads, sales, start_date, end_date, source='All Sources', month='All Months', agent='All Consultants'):
    lead_pool = leads[(leads['Parsed_Date'].dt.date >= start_date) & (leads['Parsed_Date'].dt.date <= end_date)].copy()
    if source != 'All Sources':
        lead_pool = lead_pool[lead_pool['Mapped_Source'] == source]
    if agent != 'All Consultants':
        lead_pool = lead_pool[lead_pool['Agent'] == agent]
    if month != 'All Months':
        lead_pool = lead_pool[lead_pool['Month_Display'] == month]

    phone_meta = lead_pool.dropna(subset=['Clean_Phone']).drop_duplicates(subset=['Clean_Phone']).copy()
    valid_phones = set(phone_meta['Clean_Phone']) - {'', 'nan'}
    sales_view = sales[sales['Clean_Phone'].isin(valid_phones)].copy()
    if sales_view.empty:
        return lead_pool, sales_view
    sales_view['Lead_Source'] = sales_view['Clean_Phone'].map(dict(zip(phone_meta['Clean_Phone'], phone_meta['Mapped_Source'])))
    sales_view['Lead_Agent'] = sales_view['Clean_Phone'].map(dict(zip(phone_meta['Clean_Phone'], phone_meta['Agent'])))
    sales_view['Lead_Date'] = sales_view['Clean_Phone'].map(dict(zip(phone_meta['Clean_Phone'], phone_meta['Parsed_Date'])))
    sales_view['Lead_Month'] = sales_view['Clean_Phone'].map(dict(zip(phone_meta['Clean_Phone'], phone_meta['Month_Display'])))
    return lead_pool, sales_view


def render_diagnostic_breakdowns(frame, total_count, context='sales'):
    left, right = st.columns(2, gap='medium')

    with left:
        if 'Quality status' in frame.columns and not frame.empty:
            q = frame['Quality status'].astype(str).str.strip()
            low = q.str.lower()
            approved = int(low.isin(['approved', 'approve']).sum())
            rejected = int(low.isin(['rejected', 'reject']).sum())
            explicit_other_mask = ~low.isin(['nan', 'none', '', 'approved', 'approve', 'rejected', 'reject'])
            others = q[explicit_other_mask].value_counts().to_dict()
            explicit_sum = approved + rejected + sum(others.values())
            pending = max(0, int(total_count) - explicit_sum)
            rows = []
            if approved:
                rows.append(('Approved', approved))
            if rejected:
                rows.append(('Rejected', rejected))
            rows.extend([(str(k), int(v)) for k,v in others.items()])
            if pending:
                rows.append(('Quality Pending', pending))
            qdf = pd.DataFrame(rows, columns=['Status','Count'])
            if not qdf.empty:
                qdf['Share'] = qdf['Count'] / max(1, int(total_count)) * 100
            section('Quality status breakdown', '🛡', f'{context.title()} records: {total_count:,}')
            st.dataframe(qdf, column_config={
                'Status': st.column_config.TextColumn('Quality status'),
                'Count': st.column_config.NumberColumn('Count', format='%d'),
                'Share': st.column_config.NumberColumn('Share', format='%.1f%%'),
            }, hide_index=True, use_container_width=True, height=min(270, 56 + 34 * len(qdf)))
        else:
            section('Quality status breakdown', '🛡', 'Source column unavailable or empty')
            st.info('No Quality status breakdown is available in this dataset.')

    with right:
        if 'WlcmStatus' in frame.columns and not frame.empty:
            w = frame['WlcmStatus'].astype(str).str.strip()
            w = w[~w.str.lower().isin(['nan', 'none', ''])]
            wdf = w.value_counts().reset_index()
            wdf.columns = ['Status','Count']
            if not wdf.empty:
                wdf['Share'] = wdf['Count'] / max(1, int(total_count)) * 100
            section('Welcome call status breakdown', '☎', f'{context.title()} records: {total_count:,}')
            if not wdf.empty:
                st.dataframe(wdf, column_config={
                    'Status': st.column_config.TextColumn('WlcmStatus'),
                    'Count': st.column_config.NumberColumn('Count', format='%d'),
                    'Share': st.column_config.NumberColumn('Share', format='%.1f%%'),
                }, hide_index=True, use_container_width=True, height=min(270, 56 + 34 * len(wdf)))
            else:
                st.info('WlcmStatus is present but contains no usable values.')
        else:
            section('Welcome call status breakdown', '☎', 'Source column unavailable or empty')
            st.info('No Welcome Call status breakdown is available in this dataset.')


def render_cancellation_breakdown(frame, total_cancelled):
    section('Cancellation intelligence', '!', 'Welcome Call vs Payment cancellation pathways and payment subcategories')
    wc_count = int((frame['Cancel_Reason'] == 'WC Cancelled').sum()) if 'Cancel_Reason' in frame.columns else 0
    pay_count = int((frame['Cancel_Reason'] == 'Payment Cancelled').sum()) if 'Cancel_Reason' in frame.columns else 0
    cards = pd.DataFrame([
        {'Pathway':'Welcome Call Cancelled','Count':wc_count,'Share':pct(wc_count,total_cancelled)},
        {'Pathway':'Payment Cancelled','Count':pay_count,'Share':pct(pay_count,total_cancelled)},
        {'Pathway':'Other / Unclassified','Count':max(0,total_cancelled-wc_count-pay_count),'Share':pct(max(0,total_cancelled-wc_count-pay_count),total_cancelled)},
    ])
    st.dataframe(cards, column_config={
        'Pathway': st.column_config.TextColumn('Cancellation pathway'),
        'Count': st.column_config.NumberColumn('Count', format='%d'),
        'Share': st.column_config.NumberColumn('Share', format='%.1f%%'),
    }, hide_index=True, use_container_width=True, height=170)

    pay = frame[frame['Cancel_Reason'] == 'Payment Cancelled'].copy() if 'Cancel_Reason' in frame.columns else pd.DataFrame()
    if not pay.empty and 'Disallowed_Subcategory' in pay.columns:
        sub = pay['Disallowed_Subcategory'].replace(['None','nan',''], pd.NA).dropna().value_counts().reset_index()
        sub.columns = ['Subcategory','Count']
        if not sub.empty:
            sub['Share of payment cancellations'] = sub['Count'] / max(1, pay_count) * 100
            st.dataframe(sub, column_config={
                'Subcategory': st.column_config.TextColumn('Payment cancellation subcategory'),
                'Count': st.column_config.NumberColumn('Count', format='%d'),
                'Share of payment cancellations': st.column_config.NumberColumn('Share', format='%.1f%%'),
            }, hide_index=True, use_container_width=True, height=min(290, 58 + 34 * len(sub)))


# ==============================================================================
# SESSION / DATA
# ==============================================================================
try:
    df_leads, df_sales = fetch_dashboard_data()
    is_ready = True
except Exception as e:
    st.error(f'Sync issue with active sheet data nodes: {e}')
    is_ready = False

if is_ready:
    # -------------------------------------------------------------------------
    # Sidebar identity + controls
    # -------------------------------------------------------------------------
    with st.sidebar:
        st.markdown(f'''
        <div class="sidebar-profile">
            <div class="sidebar-avatar">{escape(initials(st.session_state['user_email']))}</div>
            <div class="sidebar-kicker">Signed in as</div>
            <div class="sidebar-name">{escape(st.session_state['user_email'])}</div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown('<div class="sidebar-section">Data estate</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sidebar-stat"><span>Leads loaded</span><b>{len(df_leads):,}</b></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sidebar-stat"><span>Sales loaded</span><b>{len(df_sales):,}</b></div>', unsafe_allow_html=True)
        lead_min = df_leads['Parsed_Date'].min().date() if not df_leads.empty else date.today()
        lead_max = df_leads['Parsed_Date'].max().date() if not df_leads.empty else date.today()
        sales_min = df_sales['Parsed_Date'].min().date() if not df_sales.empty else date.today()
        sales_max = df_sales['Parsed_Date'].max().date() if not df_sales.empty else date.today()
        estate_min = min(lead_min, sales_min)
        estate_max = max(lead_max, sales_max)
        st.markdown(f'<div class="sidebar-stat"><span>Coverage</span><b>{estate_min.strftime("%d %b %Y")} → {estate_max.strftime("%d %b %Y")}</b></div>', unsafe_allow_html=True)

        st.markdown('<div class="sidebar-section">Actions</div>', unsafe_allow_html=True)
        if st.button('↻  Refresh connected data', use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        if st.button('↪  Sign out', use_container_width=True):
            st.session_state['authenticated'] = False
            st.session_state['logged_login'] = False
            st.rerun()

        st.markdown('<div style="position:fixed;bottom:18px;width:225px;color:#6F86B7;font-size:.60rem;line-height:1.45;">Vee Repairs · Operations Intelligence<br>Connected Google Sheets reporting</div>', unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # Hero
    # -------------------------------------------------------------------------
    hero_left, hero_right = st.columns([3.25, 1.15], gap='small')
    with hero_left:
        st.markdown('''
        <div class="hero-shell">
            <div class="hero-kicker">Vee Repairs · Operations Intelligence</div>
            <div class="hero-title">Leads, Sales & Conversion Command Centre</div>
            <div class="hero-sub">A consolidated view of lead quality, sales verification, cancellations, revenue and lead-to-sale performance.</div>
            <div class="hero-meta">
                <span class="hero-chip">✦ Live reporting layer</span>
                <span class="hero-chip">◉ Quality intelligence</span>
                <span class="hero-chip">↗ Revenue tracking</span>
                <span class="hero-chip">◎ Conversion analytics</span>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    with hero_right:
        st.markdown(f'''
        <div class="hero-shell" style="height:100%;padding:18px;">
            <div class="hero-status-card">
                <div class="hero-status-label">DATA STATUS</div>
                <div class="hero-status-value"><span class="live-dot"></span>Connected</div>
                <div class="hero-status-label" style="margin-top:16px;">ACCESS</div>
                <div class="hero-status-value" style="font-size:.79rem;overflow-wrap:anywhere;">{escape(st.session_state['user_email'])}</div>
                <div class="hero-status-label" style="margin-top:15px;">COVERAGE</div>
                <div class="hero-status-value" style="font-size:.75rem;">{estate_min.strftime('%d %b %Y')} → {estate_max.strftime('%d %b %Y')}</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # Tabs
    # -------------------------------------------------------------------------
    tab_overview, tab_leads, tab_sales, tab_conversion = st.tabs([
        '⌂  Executive Overview',
        '📊  Leads Quality',
        '💰  Sales Verification',
        '↗  Lead Conversion',
    ])

    # ======================================================================
    # EXECUTIVE OVERVIEW
    # ======================================================================
    with tab_overview:
        section('Executive reporting period', '◷', 'A high-level control deck for cross-functional reporting')
        ov_start, ov_end = render_period_filter('overview', 'REPORTING PERIOD', estate_min, estate_max, default_preset='This Month')

        ov_leads = df_leads[(df_leads['Parsed_Date'].dt.date >= ov_start) & (df_leads['Parsed_Date'].dt.date <= ov_end)].copy()
        ov_sales = df_sales[(df_sales['Parsed_Date'].dt.date >= ov_start) & (df_sales['Parsed_Date'].dt.date <= ov_end)].copy()
        ov_total = len(ov_leads)
        ov_approved = int((ov_leads['Cleaned_Quality_Status'] == 'Approved').sum())
        ov_rejected = int((ov_leads['Cleaned_Quality_Status'] == 'Rejected').sum())
        ov_pending = int((ov_leads['Cleaned_Quality_Status'] == 'Pending').sum())
        ov_live = int((ov_sales['Cleaned_Payment_Status'] == 'Live').sum())
        ov_cancel = int((ov_sales['Cleaned_Payment_Status'] == 'Cancelled').sum())
        ov_pending_sales = int((ov_sales['Cleaned_Payment_Status'] == 'Pending').sum())
        ov_revenue = safe_num(ov_sales['Live_Amount'].sum())

        ov_phone_meta = ov_leads.dropna(subset=['Clean_Phone']).drop_duplicates(subset=['Clean_Phone']).copy()
        ov_valid_phones = set(ov_phone_meta['Clean_Phone']) - {'', 'nan'}
        ov_conv = ov_sales[ov_sales['Clean_Phone'].isin(ov_valid_phones)].copy()
        ov_unique_conv = int(ov_conv.drop_duplicates(subset=['Clean_Phone'])['Clean_Phone'].count()) if not ov_conv.empty else 0
        ov_unique_live = int(ov_conv[ov_conv['Cleaned_Payment_Status'] == 'Live'].drop_duplicates(subset=['Clean_Phone'])['Clean_Phone'].count()) if not ov_conv.empty else 0
        ov_conversion_rate = pct(ov_unique_conv, ov_total)
        ov_live_rate = pct(ov_unique_live, ov_total)

        period_days = max(1, (ov_end - ov_start).days + 1)
        prev_end = ov_start - timedelta(days=1)
        prev_start = prev_end - timedelta(days=period_days - 1)
        prev_leads = df_leads[(df_leads['Parsed_Date'].dt.date >= prev_start) & (df_leads['Parsed_Date'].dt.date <= prev_end)].copy()
        prev_sales = df_sales[(df_sales['Parsed_Date'].dt.date >= prev_start) & (df_sales['Parsed_Date'].dt.date <= prev_end)].copy()
        prev_total = len(prev_leads)
        prev_approved = int((prev_leads['Cleaned_Quality_Status'] == 'Approved').sum())
        prev_ov_phone = prev_leads.dropna(subset=['Clean_Phone']).drop_duplicates(subset=['Clean_Phone'])
        prev_valid = set(prev_ov_phone['Clean_Phone']) - {'', 'nan'}
        prev_conv = prev_sales[prev_sales['Clean_Phone'].isin(prev_valid)]
        prev_unique_conv = int(prev_conv.drop_duplicates(subset=['Clean_Phone'])['Clean_Phone'].count()) if not prev_conv.empty else 0
        prev_live = int(prev_sales['Cleaned_Payment_Status'].eq('Live').sum())
        prev_rev = safe_num(prev_sales['Live_Amount'].sum())

        section('Period performance', '✦', f'{ov_start.strftime("%d %b %Y")} → {ov_end.strftime("%d %b %Y")}')
        k1, k2, k3, k4, k5 = st.columns(5, gap='small')
        with k1: kpi('Applications', f'{ov_total:,}', f'{pct(ov_approved, ov_total):.1f}% approved', 'linear-gradient(90deg,#2563EB,#06B6D4)')
        with k2: kpi('Quality Approved', f'{ov_approved:,}', f'{pct(ov_approved, ov_total):.1f}% of applications', 'linear-gradient(90deg,#10B981,#34D399)')
        with k3: kpi('Unique Converted', f'{ov_unique_conv:,}', f'{ov_conversion_rate:.1f}% of lead pool', 'linear-gradient(90deg,#7C3AED,#A78BFA)')
        with k4: kpi('Unique Live', f'{ov_unique_live:,}', f'{ov_live_rate:.1f}% of lead pool', 'linear-gradient(90deg,#059669,#34D399)')
        with k5: kpi('Live Revenue', f'£{ov_revenue:,.2f}', f'{ov_live:,} live transactions', 'linear-gradient(90deg,#CA8A04,#EAB308)')

        section('Performance pulse', '≈', 'Current selected period compared with the immediately preceding period of equal length')
        comparison_cards([
            ('Applications', ov_total, prev_total, False, f'Previous: {prev_total:,}'),
            ('Approval rate', pct(ov_approved, ov_total), pct(prev_approved, prev_total), True, f'Previous: {pct(prev_approved, prev_total):.1f}%'),
            ('Unique converted', ov_unique_conv, prev_unique_conv, False, f'Previous: {prev_unique_conv:,}'),
            ('Live transactions', ov_live, prev_live, False, f'Previous live: {prev_live:,}'),
        ])

        funnel_col, pulse_col = st.columns([1.05, 1.95], gap='medium')
        with funnel_col:
            section('Pipeline snapshot', '◎', 'Selected-period operating flow')
            stage_rows = [
                ('Applications', ov_total, '#2563EB'),
                ('Approved', ov_approved, '#10B981'),
                ('Converted', ov_unique_conv, '#7C3AED'),
                ('Live', ov_unique_live, '#059669'),
            ]
            funnel_html = []
            denom = max(ov_total, 1)
            for name, value, color in stage_rows:
                width = min(100.0, pct(value, denom))
                funnel_html.append(f'<div class="funnel-row"><div class="funnel-name">{name}</div><div class="funnel-track"><div class="funnel-fill" style="width:{width:.1f}%;background:{color};"></div></div><div class="funnel-value">{value:,} · {width:.1f}%</div></div>')
            st.markdown('<div class="funnel-card">' + ''.join(funnel_html) + '</div>', unsafe_allow_html=True)

        with pulse_col:
            section('Operational attention', '⚡', 'Queues worth reviewing in the selected period')
            action_cards([
                ('Pending quality', ov_pending, '!', '#FFF7ED', '#C2410C', 'Applications still sitting outside an approved or rejected outcome.'),
                ('Pending sales', ov_pending_sales, '◌', '#FFF7ED', '#B45309', 'Sales logged without a completed payment outcome.'),
                ('Cancelled sales', ov_cancel, '×', '#FEF2F2', '#B91C1C', 'Cancelled transactions for QA / customer / payment review.'),
            ])
            st.markdown(f'<div class="panel" style="margin-top:10px;"><div class="panel-title">Period activity</div><div class="panel-sub">Average applications per calendar day: <b>{ov_total / period_days:.1f}</b> · Live revenue per live sale: <b>£{(ov_revenue / ov_live if ov_live else 0):,.2f}</b> · Previous-period revenue: <b>£{prev_rev:,.2f}</b></div></div>', unsafe_allow_html=True)

        section('Branch / source health', '◈', 'Lead volume, quality and downstream conversion by mapped source')
        source_rows = []
        for src in ['Delhi', 'Ranchi']:
            ld = ov_leads[ov_leads['Mapped_Source'] == src]
            phones = set(ld['Clean_Phone'].dropna()) - {'', 'nan'}
            cv = ov_sales[ov_sales['Clean_Phone'].isin(phones)]
            unique_cv = cv.drop_duplicates(subset=['Clean_Phone']) if not cv.empty else cv
            source_rows.append({
                'Source': src,
                'Applications': len(ld),
                'Approved %': pct((ld['Cleaned_Quality_Status'] == 'Approved').sum(), len(ld)),
                'Unique Converted': len(unique_cv),
                'Unique Conversion %': pct(len(unique_cv), len(ld)),
                'Live Revenue': safe_num(cv.loc[cv['Cleaned_Payment_Status'] == 'Live', 'Live_Amount'].sum()) if not cv.empty else 0,
            })
        source_df = pd.DataFrame(source_rows)
        if not source_df.empty:
            total_row = pd.DataFrame([{
                'Source':'TOTAL', 'Applications':int(source_df['Applications'].sum()),
                'Approved %':pct(ov_approved, ov_total), 'Unique Converted':int(ov_unique_conv),
                'Unique Conversion %':pct(ov_unique_conv, ov_total), 'Live Revenue':ov_revenue
            }])
            source_display = pd.concat([source_df, total_row], ignore_index=True)
            st.dataframe(source_display, column_config={
                'Source': st.column_config.TextColumn('Source'),
                'Applications': st.column_config.NumberColumn('Applications', format='%d'),
                'Approved %': st.column_config.NumberColumn('Approval', format='%.1f%%'),
                'Unique Converted': st.column_config.NumberColumn('Unique Converted', format='%d'),
                'Unique Conversion %': st.column_config.NumberColumn('Conversion', format='%.1f%%'),
                'Live Revenue': st.column_config.NumberColumn('Live Revenue', format='£%.2f'),
            }, hide_index=True, use_container_width=True, height=175)

        left_chart, right_chart = st.columns(2, gap='medium')
        with left_chart:
            section('Application rhythm', '↗', 'Daily application volume across the selected period')
            if not ov_leads.empty:
                daily = ov_leads.groupby(ov_leads['Parsed_Date'].dt.date).size().reset_index(name='Applications')
                daily.columns = ['Date', 'Applications']
                fig = px.area(daily, x='Date', y='Applications')
                fig.update_traces(line=dict(color='#2563EB', width=2), fillcolor='rgba(37,99,235,.12)')
                chart_base(fig, 300)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar':False})
            else:
                st.info('No applications in the selected period.')
        with right_chart:
            section('Revenue rhythm', '£', 'Live revenue by sale date')
            if not ov_sales.empty:
                rev = ov_sales.groupby(ov_sales['Parsed_Date'].dt.date)['Live_Amount'].sum().reset_index()
                rev.columns = ['Date', 'Revenue']
                fig = px.bar(rev, x='Date', y='Revenue')
                fig.update_traces(marker_color='#EAB308')
                chart_base(fig, 300)
                fig.update_yaxes(tickprefix='£')
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar':False})
            else:
                st.info('No sales in the selected period.')

    # ======================================================================
    # LEADS QUALITY
    # ======================================================================
    with tab_leads:
        section('Leads reporting controls', '◷', 'Independent date range + source + consultant + calendar-month view')
        l_start, l_end = render_period_filter('leads', 'LEAD DATE RANGE', lead_min, lead_max, default_preset='This Month')
        lf1, lf2, lf3, lf4 = st.columns([1.05, 1.05, 1.25, 1.25], gap='small')
        with lf1:
            lead_source = st.selectbox('Distribution branch', ['All Sources', 'Delhi', 'Ranchi'], key='leads_source_v2')
        with lf2:
            lead_agents = ['All Consultants'] + sorted(df_leads['Agent'].dropna().astype(str).unique().tolist())
            lead_agent = st.selectbox('Consultant', lead_agents, key='leads_agent_v2')
        with lf3:
            lead_months = ['All Months'] + latest_month_options(df_leads, l_start, l_end)
            lead_month = st.selectbox('Calendar month', lead_months, key='leads_month_v2')
        with lf4:
            lead_statuses = st.multiselect('Status focus', ['Approved','Rejected','Pending'], default=[], key='leads_status_v2')

        leads_view = filter_frame(df_leads, l_start, l_end, source=lead_source, agent=lead_agent, month=lead_month)
        if lead_statuses:
            leads_view = leads_view[leads_view['Cleaned_Quality_Status'].isin(lead_statuses)].copy()

        l_total = len(leads_view)
        l_app = int((leads_view['Cleaned_Quality_Status'] == 'Approved').sum())
        l_rej = int((leads_view['Cleaned_Quality_Status'] == 'Rejected').sum())
        l_pen = int((leads_view['Cleaned_Quality_Status'] == 'Pending').sum())
        l_app_rate = pct(l_app, l_total)

        section('Quality snapshot', '✦', f'{l_total:,} records in the current lead view')
        c1,c2,c3,c4,c5 = st.columns(5, gap='small')
        with c1: kpi('Total leads', f'{l_total:,}', 'Current filtered volume')
        with c2: kpi('Approved', f'{l_app:,}', f'{l_app_rate:.1f}% of view', 'linear-gradient(90deg,#10B981,#34D399)')
        with c3: kpi('Rejected', f'{l_rej:,}', f'{pct(l_rej,l_total):.1f}% of view', 'linear-gradient(90deg,#EF4444,#F87171)')
        with c4: kpi('Pending', f'{l_pen:,}', f'{pct(l_pen,l_total):.1f}% of view', 'linear-gradient(90deg,#F59E0B,#FBBF24)')
        approval_ratio = f'{l_app / l_rej:.1f}×' if l_rej else '—'
        with c5: kpi('Approval / rejection', approval_ratio, 'Approved records per rejected record', 'linear-gradient(90deg,#7C3AED,#A78BFA)')

        section('Quality action centre', '⚡', 'The queues most likely to need operational review')
        action_cards([
            ('Pending threshold', l_pen, '◌', '#FFF7ED', '#C2410C', 'Unresolved applications that still need a quality outcome.'),
            ('Rejected queue', l_rej, '×', '#FEF2F2', '#B91C1C', 'Rejected applications available for root-cause and feedback analysis.'),
            ('Approved throughput', l_app, '✓', '#ECFDF5', '#047857', 'Applications that passed the recorded quality status in this view.'),
        ])

        left, right = st.columns([1.04, 1.96], gap='medium')
        with left:
            section('Quality mix', '◉', 'Distribution of current filtered statuses')
            if l_total:
                qdf = pd.DataFrame({'Status':['Approved','Rejected','Pending'],'Count':[l_app,l_rej,l_pen]})
                fig = px.pie(qdf, names='Status', values='Count', hole=.66, color='Status', color_discrete_map={'Approved':'#10B981','Rejected':'#EF4444','Pending':'#F59E0B'})
                fig.update_traces(textposition='outside', textinfo='percent+label', hovertemplate='%{label}: %{value:,}<extra></extra>')
                chart_base(fig, 320)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar':False})
            else:
                st.info('No lead records match the current filters.')
        with right:
            section('Leads quality trend', '↗', 'Daily when the period is short; monthly when the period is broad')
            if l_total:
                span = (l_end - l_start).days
                trend = leads_view.copy()
                if span <= 62:
                    trend['Bucket'] = trend['Parsed_Date'].dt.strftime('%d %b')
                    sort_col = 'Parsed_Date'
                    grouped = trend.groupby([sort_col,'Bucket','Cleaned_Quality_Status']).size().reset_index(name='Volume').sort_values(sort_col)
                    x = 'Bucket'
                elif span <= 180:
                    trend['BucketDate'] = trend['Parsed_Date'].dt.to_period('W').apply(lambda x: x.start_time)
                    trend['Bucket'] = trend['BucketDate'].dt.strftime('%d %b')
                    grouped = trend.groupby(['BucketDate','Bucket','Cleaned_Quality_Status']).size().reset_index(name='Volume').sort_values('BucketDate')
                    x = 'Bucket'
                else:
                    trend['BucketDate'] = trend['Parsed_Date'].dt.to_period('M').dt.to_timestamp()
                    trend['Bucket'] = trend['BucketDate'].dt.strftime('%b %Y')
                    grouped = trend.groupby(['BucketDate','Bucket','Cleaned_Quality_Status']).size().reset_index(name='Volume').sort_values('BucketDate')
                    x = 'Bucket'
                fig = px.line(grouped, x=x, y='Volume', color='Cleaned_Quality_Status', markers=True, color_discrete_map={'Approved':'#10B981','Rejected':'#EF4444','Pending':'#F59E0B'})
                chart_base(fig, 330)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar':False})
            else:
                st.info('No lead records match the current filters.')

        section('Consultant quality leaderboard', '◈', 'Volume first, then status mix for easy operational scanning')
        if not leads_view.empty:
            lb = leads_view.groupby('Agent').agg(
                Total=('Agent','size'),
                Approved=('Cleaned_Quality_Status', lambda x: (x=='Approved').sum()),
                Rejected=('Cleaned_Quality_Status', lambda x: (x=='Rejected').sum()),
                Pending=('Cleaned_Quality_Status', lambda x: (x=='Pending').sum()),
            ).reset_index().sort_values('Total', ascending=False)
            lb['Approval'] = lb.apply(lambda r: pct(r['Approved'], r['Total']), axis=1)
            lb['Pending %'] = lb.apply(lambda r: pct(r['Pending'], r['Total']), axis=1)
            st.dataframe(lb, column_config={
                'Agent': st.column_config.TextColumn('Consultant'),
                'Total': st.column_config.NumberColumn('Total', format='%d'),
                'Approved': st.column_config.NumberColumn('Approved', format='%d'),
                'Rejected': st.column_config.NumberColumn('Rejected', format='%d'),
                'Pending': st.column_config.NumberColumn('Pending', format='%d'),
                'Approval': st.column_config.NumberColumn('Approval', format='%.1f%%'),
                'Pending %': st.column_config.NumberColumn('Pending %', format='%.1f%%'),
            }, hide_index=True, use_container_width=True, height=min(440, 64 + 34 * len(lb)))
        else:
            st.info('No consultant data in the current view.')

    # ======================================================================
    # SALES VERIFICATION
    # ======================================================================
    with tab_sales:
        section('Sales reporting controls', '◷', 'Independent date range + month + consultant + outcome filters')
        s_start, s_end = render_period_filter('sales', 'SALE DATE RANGE', sales_min, sales_max, default_preset='This Month')
        sf1, sf2, sf3, sf4 = st.columns([1.15, 1.25, 1.15, 1.25], gap='small')
        with sf1:
            sales_agents = ['All Consultants'] + sorted(df_sales['Agent'].dropna().astype(str).unique().tolist())
            sales_agent = st.selectbox('Consultant', sales_agents, key='sales_agent_v2')
        with sf2:
            sales_months = ['All Months'] + latest_month_options(df_sales, s_start, s_end)
            sales_month = st.selectbox('Calendar month', sales_months, key='sales_month_v2')
        with sf3:
            sales_statuses = st.multiselect('Outcome focus', ['Live','Pending','Cancelled'], default=[], key='sales_status_v2')
        with sf4:
            revenue_view = st.selectbox('Revenue lens', ['Live revenue only','All logged amount'], key='sales_revenue_lens_v2')

        sales_view = filter_frame(df_sales, s_start, s_end, agent=sales_agent, month=sales_month)
        if sales_statuses:
            sales_view = sales_view[sales_view['Cleaned_Payment_Status'].isin(sales_statuses)].copy()

        s_total = len(sales_view)
        s_live = int((sales_view['Cleaned_Payment_Status'] == 'Live').sum())
        s_cancel = int((sales_view['Cleaned_Payment_Status'] == 'Cancelled').sum())
        s_pending = int((sales_view['Cleaned_Payment_Status'] == 'Pending').sum())
        s_rev = safe_num(sales_view['Live_Amount'].sum())
        s_amount = safe_num(sales_view['Parsed_Amount'].sum())
        revenue_display_value = s_rev if revenue_view == 'Live revenue only' else s_amount
        revenue_display_label = 'Live revenue' if revenue_view == 'Live revenue only' else 'Logged amount'
        revenue_display_sub = f'Live-only recognised amount £{s_rev:,.2f}' if revenue_view != 'Live revenue only' else f'Gross logged amount £{s_amount:,.2f}'
        s_wc_cancel = int((sales_view['Cancel_Reason'] == 'WC Cancelled').sum())
        s_pay_cancel = int((sales_view['Cancel_Reason'] == 'Payment Cancelled').sum())

        section('Sales snapshot', '✦', f'{s_total:,} sales records in the current sale-date view')
        a,b,c,d,e = st.columns(5, gap='small')
        with a: kpi('Logged sales', f'{s_total:,}', 'Current filtered volume')
        with b: kpi('Live', f'{s_live:,}', f'{pct(s_live,s_total):.1f}% of logged', 'linear-gradient(90deg,#10B981,#34D399)')
        with c: kpi('Pending', f'{s_pending:,}', f'{pct(s_pending,s_total):.1f}% of logged', 'linear-gradient(90deg,#F59E0B,#FBBF24)')
        with d: kpi('Cancelled', f'{s_cancel:,}', f'{pct(s_cancel,s_total):.1f}% of logged', 'linear-gradient(90deg,#EF4444,#F87171)')
        with e: kpi(revenue_display_label, f'£{revenue_display_value:,.2f}', revenue_display_sub, 'linear-gradient(90deg,#CA8A04,#EAB308)')

        section('Sales action centre', '⚡', 'Cancellation and pending queues separated into operational causes')
        action_cards([
            ('Welcome call cancelled', s_wc_cancel, '☎', '#FFF7ED', '#C2410C', 'Sales held or cancelled because the Welcome Call status drove the cancellation.'),
            ('Payment cancelled', s_pay_cancel, '£', '#FEF2F2', '#B91C1C', 'Sales cancelled through the payment-status pathway and its recorded subcategory.'),
            ('Pending review', s_pending, '◌', '#FFF7ED', '#A16207', 'Logged sales without an accepted payment status in the current view.'),
        ])

        left, right = st.columns([1.55, 1], gap='medium')
        with left:
            section('Sales performance trend', '↗', 'Volume by outcome across the selected period')
            if not sales_view.empty:
                span = (s_end - s_start).days
                temp = sales_view.copy()
                if span <= 62:
                    temp['Bucket'] = temp['Parsed_Date'].dt.strftime('%d %b')
                    temp['BucketDate'] = temp['Parsed_Date'].dt.normalize()
                elif span <= 180:
                    temp['BucketDate'] = temp['Parsed_Date'].dt.to_period('W').apply(lambda x: x.start_time)
                    temp['Bucket'] = temp['BucketDate'].dt.strftime('%d %b')
                else:
                    temp['BucketDate'] = temp['Parsed_Date'].dt.to_period('M').dt.to_timestamp()
                    temp['Bucket'] = temp['BucketDate'].dt.strftime('%b %Y')
                trend = temp.groupby(['BucketDate','Bucket','Cleaned_Payment_Status']).size().reset_index(name='Volume').sort_values('BucketDate')
                fig = px.line(trend, x='Bucket', y='Volume', color='Cleaned_Payment_Status', markers=True, color_discrete_map={'Live':'#10B981','Pending':'#F59E0B','Cancelled':'#EF4444'})
                chart_base(fig, 345)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar':False})
            else:
                st.info('No sales match the current filters.')
        with right:
            section('Outcome mix', '◉', 'Current sales distribution')
            mix = pd.DataFrame({'Status':['Live','Pending','Cancelled'],'Count':[s_live,s_pending,s_cancel]})
            if s_total:
                fig = px.pie(mix, names='Status', values='Count', hole=.66, color='Status', color_discrete_map={'Live':'#10B981','Pending':'#F59E0B','Cancelled':'#EF4444'})
                fig.update_traces(textposition='outside', textinfo='percent+label', hovertemplate='%{label}: %{value:,}<extra></extra>')
                chart_base(fig, 345)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar':False})
            else:
                st.info('No sales match the current filters.')

        section('Consultant sales leaderboard', '◈', 'Sales volume, outcome mix and live revenue')
        if not sales_view.empty:
            slb = sales_view.groupby('Agent').agg(
                Total=('Agent','size'),
                Live=('Cleaned_Payment_Status', lambda x:(x=='Live').sum()),
                Pending=('Cleaned_Payment_Status', lambda x:(x=='Pending').sum()),
                Cancelled=('Cleaned_Payment_Status', lambda x:(x=='Cancelled').sum()),
                Revenue=('Live_Amount','sum'),
            ).reset_index().sort_values('Total', ascending=False)
            slb['Live %'] = slb.apply(lambda r:pct(r['Live'],r['Total']), axis=1)
            slb['Cancel %'] = slb.apply(lambda r:pct(r['Cancelled'],r['Total']), axis=1)
            st.dataframe(slb, column_config={
                'Agent': st.column_config.TextColumn('Consultant'),
                'Total': st.column_config.NumberColumn('Total', format='%d'),
                'Live': st.column_config.NumberColumn('Live', format='%d'),
                'Pending': st.column_config.NumberColumn('Pending', format='%d'),
                'Cancelled': st.column_config.NumberColumn('Cancelled', format='%d'),
                'Live %': st.column_config.NumberColumn('Live %', format='%.1f%%'),
                'Cancel %': st.column_config.NumberColumn('Cancel %', format='%.1f%%'),
                'Revenue': st.column_config.NumberColumn('Live Revenue', format='£%.2f'),
            }, hide_index=True, use_container_width=True, height=min(445, 64 + 34 * len(slb)))
        else:
            st.info('No consultant sales data in the current view.')

        render_diagnostic_breakdowns(sales_view, s_total, context='sales')
        render_cancellation_breakdown(sales_view, s_cancel)

    # ======================================================================
    # LEAD CONVERSION
    # ======================================================================
    with tab_conversion:
        section('Conversion cohort controls', '◷', 'Conversion is attributed to the original lead cohort, preserving the existing Vee Repairs model')
        c_start, c_end = render_period_filter('conversion', 'LEAD COHORT DATE RANGE', lead_min, lead_max, default_preset='This Month')
        cf1, cf2, cf3 = st.columns([1.25, 1.25, 1.25], gap='small')
        with cf1:
            conv_source = st.selectbox('Lead source', ['All Sources','Delhi','Ranchi'], key='conv_source_v2')
        with cf2:
            conv_agents = ['All Consultants'] + sorted(df_leads['Agent'].dropna().astype(str).unique().tolist())
            conv_agent = st.selectbox('Lead consultant', conv_agents, key='conv_agent_v2')
        with cf3:
            conv_months = ['All Months'] + latest_month_options(df_leads, c_start, c_end)
            conv_month = st.selectbox('Lead cohort month', conv_months, key='conv_month_v2')

        conv_leads, conv_sales = build_conversion_view(df_leads, df_sales, c_start, c_end, conv_source, conv_month, conv_agent)
        conv_multi = len(conv_sales)
        conv_unique = int(conv_sales.drop_duplicates(subset=['Clean_Phone'])['Clean_Phone'].count()) if not conv_sales.empty else 0
        conv_live_multi = int((conv_sales['Cleaned_Payment_Status'] == 'Live').sum()) if not conv_sales.empty else 0
        conv_cancel_multi = int((conv_sales['Cleaned_Payment_Status'] == 'Cancelled').sum()) if not conv_sales.empty else 0
        conv_pending_multi = int((conv_sales['Cleaned_Payment_Status'] == 'Pending').sum()) if not conv_sales.empty else 0
        conv_live_unique = int(conv_sales[conv_sales['Cleaned_Payment_Status'] == 'Live'].drop_duplicates(subset=['Clean_Phone'])['Clean_Phone'].count()) if not conv_sales.empty else 0
        conv_cancel_unique = int(conv_sales[conv_sales['Cleaned_Payment_Status'] == 'Cancelled'].drop_duplicates(subset=['Clean_Phone'])['Clean_Phone'].count()) if not conv_sales.empty else 0
        conv_pending_unique = int(conv_sales[conv_sales['Cleaned_Payment_Status'] == 'Pending'].drop_duplicates(subset=['Clean_Phone'])['Clean_Phone'].count()) if not conv_sales.empty else 0
        conv_revenue = safe_num(conv_sales['Live_Amount'].sum()) if not conv_sales.empty else 0.0
        conv_lead_pool = len(conv_leads)

        section('Conversion snapshot', '✦', 'Unique customer conversions are shown first; transaction volume remains visible as the secondary metric')
        q1,q2,q3,q4,q5,q6 = st.columns(6, gap='small')
        with q1: kpi('Lead pool', f'{conv_lead_pool:,}', 'Cohort denominator')
        with q2: kpi('Unique converted', f'{conv_unique:,}', f'{pct(conv_unique,conv_lead_pool):.1f}% conversion', 'linear-gradient(90deg,#7C3AED,#A78BFA)')
        with q3: kpi('Unique live', f'{conv_live_unique:,}', f'{pct(conv_live_unique,conv_lead_pool):.1f}% of lead pool', 'linear-gradient(90deg,#10B981,#34D399)')
        with q4: kpi('Unique cancelled', f'{conv_cancel_unique:,}', f'{pct(conv_cancel_unique,conv_lead_pool):.1f}% of lead pool', 'linear-gradient(90deg,#EF4444,#F87171)')
        with q5: kpi('Pending', f'{conv_pending_unique:,}', f'{pct(conv_pending_unique,conv_lead_pool):.1f}% of lead pool', 'linear-gradient(90deg,#F59E0B,#FBBF24)')
        with q6: kpi('Live revenue', f'£{conv_revenue:,.2f}', f'{conv_live_multi:,} live transactions', 'linear-gradient(90deg,#CA8A04,#EAB308)')

        section('Conversion funnel', '◎', 'Lead cohort → unique conversion → unique live')
        funnel_left, funnel_right = st.columns([1.05, 1.95], gap='medium')
        with funnel_left:
            funnel_html = []
            base = max(conv_lead_pool,1)
            for label,value,color in [('Lead pool',conv_lead_pool,'#2563EB'),('Unique converted',conv_unique,'#7C3AED'),('Unique live',conv_live_unique,'#059669')]:
                width = pct(value,base)
                funnel_html.append(f'<div class="funnel-row"><div class="funnel-name">{label}</div><div class="funnel-track"><div class="funnel-fill" style="width:{width:.1f}%;background:{color};"></div></div><div class="funnel-value">{value:,} · {width:.1f}%</div></div>')
            st.markdown('<div class="funnel-card">' + ''.join(funnel_html) + '</div>', unsafe_allow_html=True)
        with funnel_right:
            comparison_cards([
                ('Unique vs multi', conv_unique, conv_multi, False, f'Transactions: {conv_multi:,}'),
                ('Live unique', pct(conv_live_unique,conv_unique), pct(conv_live_multi,conv_multi), True, f'Multi live: {pct(conv_live_multi,conv_multi):.1f}%'),
                ('Cancelled unique', pct(conv_cancel_unique,conv_unique), pct(conv_cancel_multi,conv_multi), True, f'Multi cancelled: {pct(conv_cancel_multi,conv_multi):.1f}%'),
                ('Pending unique', pct(conv_pending_unique,conv_unique), pct(conv_pending_multi,conv_multi), True, f'Multi pending: {pct(conv_pending_multi,conv_multi):.1f}%'),
            ])
            st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)
            action_cards([
                ('Welcome call cancellations', int((conv_sales['Cancel_Reason'] == 'WC Cancelled').sum()) if not conv_sales.empty else 0, '☎', '#FFF7ED', '#C2410C', 'Conversion records that became cancelled through the Welcome Call pathway.'),
                ('Payment cancellations', int((conv_sales['Cancel_Reason'] == 'Payment Cancelled').sum()) if not conv_sales.empty else 0, '£', '#FEF2F2', '#B91C1C', 'Conversion records cancelled by payment status, including recorded subcategories.'),
                ('Repeat transaction rows', max(0, conv_multi - conv_unique), '↺', '#EEF2FF', '#4338CA', 'Additional transaction rows beyond the unique phone-based conversion count.'),
            ])

        render_diagnostic_breakdowns(conv_sales, conv_multi, context='conversion')
        render_cancellation_breakdown(conv_sales, conv_cancel_multi)

        conv_chart_left, conv_chart_right = st.columns([1.65, 1], gap='medium')
        with conv_chart_left:
            section('Lead-origin conversion trend', '↗', 'Conversion outcomes plotted against the original lead cohort date')
            if not conv_sales.empty:
                temp = conv_sales.copy()
                span = (c_end - c_start).days
                if span <= 62:
                    temp['BucketDate'] = pd.to_datetime(temp['Lead_Date']).dt.normalize()
                    temp['Bucket'] = temp['BucketDate'].dt.strftime('%d %b')
                elif span <= 180:
                    temp['BucketDate'] = pd.to_datetime(temp['Lead_Date']).dt.to_period('W').apply(lambda x:x.start_time)
                    temp['Bucket'] = temp['BucketDate'].dt.strftime('%d %b')
                else:
                    temp['BucketDate'] = pd.to_datetime(temp['Lead_Date']).dt.to_period('M').dt.to_timestamp()
                    temp['Bucket'] = temp['BucketDate'].dt.strftime('%b %Y')
                trend = temp.groupby(['BucketDate','Bucket','Cleaned_Payment_Status']).size().reset_index(name='Volume').sort_values('BucketDate')
                fig = px.line(trend, x='Bucket', y='Volume', color='Cleaned_Payment_Status', markers=True, color_discrete_map={'Live':'#10B981','Pending':'#F59E0B','Cancelled':'#EF4444'})
                chart_base(fig, 350)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar':False})
            else:
                st.info('No sales can be attributed to the selected lead cohort.')
        with conv_chart_right:
            section('Source conversion mix', '◈', 'Unique converted customers by source')
            if not conv_sales.empty:
                src = conv_sales.drop_duplicates(subset=['Clean_Phone']).groupby('Lead_Source').size().reset_index(name='Unique Converted')
                fig = px.bar(src, x='Lead_Source', y='Unique Converted', color='Lead_Source', color_discrete_map={'Delhi':'#2563EB','Ranchi':'#EAB308'})
                chart_base(fig, 350)
                fig.update_traces(marker_line_width=0)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar':False})
            else:
                st.info('No attributed conversions in this cohort.')

        section('Consultant conversion leaderboard', '◈', 'Unique / multi volume, status mix and live revenue')
        if not conv_sales.empty:
            unique_agent = conv_sales.drop_duplicates(subset=['Agent','Clean_Phone']).copy()
            raw = conv_sales.groupby('Agent').agg(
                Multi=('Agent','size'),
                Live=('Cleaned_Payment_Status', lambda x:(x=='Live').sum()),
                Cancelled=('Cleaned_Payment_Status', lambda x:(x=='Cancelled').sum()),
                Pending=('Cleaned_Payment_Status', lambda x:(x=='Pending').sum()),
                Revenue=('Live_Amount','sum'),
            ).reset_index()
            uq = unique_agent.groupby('Agent').agg(Unique=('Agent','size')).reset_index()
            board = raw.merge(uq, on='Agent', how='left')
            board['Conversion / cohort %'] = board['Unique'] / max(1, conv_lead_pool) * 100
            board['Live % unique'] = conv_sales[conv_sales['Cleaned_Payment_Status']=='Live'].drop_duplicates(subset=['Agent','Clean_Phone']).groupby('Agent').size().reindex(board['Agent']).fillna(0).values / board['Unique'].replace(0,1).values * 100
            board = board.sort_values('Unique', ascending=False)
            total_board = pd.DataFrame([{
                'Agent':'TOTAL', 'Multi':conv_multi, 'Live':conv_live_multi, 'Cancelled':conv_cancel_multi, 'Pending':conv_pending_multi,
                'Revenue':conv_revenue, 'Unique':conv_unique, 'Conversion / cohort %':pct(conv_unique,conv_lead_pool), 'Live % unique':pct(conv_live_unique,conv_unique)
            }])
            board_display = pd.concat([board, total_board], ignore_index=True)
            st.dataframe(board_display, column_config={
                'Agent': st.column_config.TextColumn('Consultant'),
                'Unique': st.column_config.NumberColumn('Unique converted', format='%d'),
                'Multi': st.column_config.NumberColumn('Transactions', format='%d'),
                'Live': st.column_config.NumberColumn('Live', format='%d'),
                'Cancelled': st.column_config.NumberColumn('Cancelled', format='%d'),
                'Pending': st.column_config.NumberColumn('Pending', format='%d'),
                'Conversion / cohort %': st.column_config.NumberColumn('Cohort conversion', format='%.1f%%'),
                'Live % unique': st.column_config.NumberColumn('Live / unique', format='%.1f%%'),
                'Revenue': st.column_config.NumberColumn('Live revenue', format='£%.2f'),
            }, hide_index=True, use_container_width=True, height=min(470, 64 + 35 * len(board_display)))
        else:
            st.info('No conversion data in the current cohort.')

    # -------------------------------------------------------------------------
    # Footer
    # -------------------------------------------------------------------------
    st.markdown('<div class="footer">Vee Repairs · Operations Intelligence · Connected Google Sheets data layer · Use the date controls independently on each workspace tab.</div>', unsafe_allow_html=True)
