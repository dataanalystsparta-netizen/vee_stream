import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px
from datetime import datetime
import numpy as np

# --- 1. SET COMPACT GLOBAL CONFIG ---
st.set_page_config(
    page_title="Vee Repairs - Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. PREMIUM EXECUTIVE THEME & INTERFACE CUSTOMIZATION ---
st.config.set_option("theme.backgroundColor", "#f7f8fa")
st.config.set_option("theme.secondaryBackgroundColor", "#ffffff")
st.config.set_option("theme.textColor", "#111827")
st.config.set_option("theme.primaryColor", "#eab308")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --vr-ink: #111827;
    --vr-muted: #64748b;
    --vr-line: #e5e7eb;
    --vr-soft: #f8fafc;
    --vr-yellow: #eab308;
    --vr-yellow-soft: #fef9c3;
    --vr-green: #16a34a;
    --vr-red: #dc2626;
    --vr-amber: #ca8a04;
}

html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"],
[data-testid="stSidebar"], button, input, textarea, select {
    font-family: 'Inter', sans-serif !important;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at 90% 0%, rgba(234,179,8,.055), transparent 25%),
        #f7f8fa;
}

[data-testid="stHeader"] { background: transparent !important; }
.block-container { padding-top: 1.25rem !important; padding-bottom: 3rem !important; max-width: 1500px; }
div[data-testid="stBlock"] { padding: 0 !important; }

.vr-header {
    background: rgba(255,255,255,.96);
    border: 1px solid var(--vr-line);
    border-radius: 18px;
    padding: 18px 22px;
    margin-bottom: 14px;
    box-shadow: 0 8px 30px rgba(15,23,42,.045);
}
.vr-brand { display:flex; align-items:center; gap:15px; }
.vr-brand img { width:58px; height:58px; object-fit:contain; }
.vr-eyebrow {
    color:#a16207; font-size:10px; font-weight:800;
    letter-spacing:1.35px; text-transform:uppercase; margin-bottom:3px;
}
.vr-title { color:var(--vr-ink); font-size:25px; line-height:1.15; font-weight:800; letter-spacing:-.6px; }
.vr-subtitle { color:var(--vr-muted); font-size:12px; margin-top:5px; }
.vr-status {
    display:inline-flex; align-items:center; gap:7px;
    padding:7px 11px; border-radius:999px;
    background:#f0fdf4; border:1px solid #bbf7d0;
    color:#166534; font-size:11px; font-weight:700;
}
.vr-dot { width:7px; height:7px; border-radius:50%; background:#22c55e; display:inline-block; }

.vr-section {
    display:flex; align-items:flex-end; justify-content:space-between;
    margin:24px 0 10px;
}
.vr-section-title { font-size:15px; font-weight:800; color:var(--vr-ink); letter-spacing:-.15px; }
.vr-section-note { font-size:11px; color:#94a3b8; }

.vr-filter {
    background:#fff; border:1px solid var(--vr-line); border-radius:14px;
    padding:11px 14px 4px; margin:2px 0 14px;
    box-shadow:0 3px 15px rgba(15,23,42,.025);
}
.vr-filter-label {
    color:#94a3b8; font-size:9px; font-weight:800;
    text-transform:uppercase; letter-spacing:1px; margin-bottom:2px;
}

.metric-box {
    background:#fff; border:1px solid var(--vr-line); border-radius:14px;
    padding:17px 18px; min-height:105px;
    box-shadow:0 5px 20px rgba(15,23,42,.035);
    transition:transform .15s ease, box-shadow .15s ease;
}
.metric-box:hover { transform:translateY(-1px); box-shadow:0 8px 25px rgba(15,23,42,.065); }
.metric-label {
    color:#64748b !important; font-size:9px; font-weight:800;
    text-transform:uppercase; letter-spacing:.8px;
}
.metric-number { color:var(--vr-ink) !important; font-size:25px; font-weight:800; letter-spacing:-.6px; margin-top:6px; }
.metric-caption { color:#94a3b8; font-size:10px; margin-top:4px; }

.breakdown-strip {
    background:#fff; border:1px solid var(--vr-line); border-left:4px solid #facc15;
    border-radius:13px; padding:13px 15px; margin:10px 0;
    box-shadow:0 3px 14px rgba(15,23,42,.025);
}
.breakdown-title {
    color:var(--vr-ink); font-size:10px; font-weight:800;
    text-transform:uppercase; letter-spacing:.8px; display:block; margin-bottom:8px;
}
.breakdown-sub-box { display:flex; flex-wrap:wrap; gap:7px; align-items:center; }
.breakdown-item {
    font-size:11px; color:#334155; font-weight:600; background:#f8fafc;
    padding:5px 9px; border-radius:7px; border:1px solid #e2e8f0;
}

.section-header {
    color:var(--vr-ink) !important; font-size:15px; font-weight:800;
    letter-spacing:-.15px; margin:5px 0 10px;
}
[data-testid="stDataFrame"] {
    border:1px solid var(--vr-line); border-radius:12px; overflow:hidden;
    box-shadow:0 3px 16px rgba(15,23,42,.025);
}
[data-testid="stDataFrame"] [role="columnheader"] {
    background:#f8fafc !important; color:#475569 !important;
    font-weight:800 !important; font-size:11px !important;
}
[data-testid="stDataFrame"] [role="gridcell"] { font-size:11px !important; }
div[data-testid="stTable"] th { background:#fef9c3 !important; color:#334155 !important; }

.stTabs [data-baseweb="tab-list"] {
    gap:5px; background:#fff; border:1px solid var(--vr-line);
    padding:5px; border-radius:14px; box-shadow:0 4px 18px rgba(15,23,42,.035);
}
.stTabs [data-baseweb="tab"] {
    height:43px; padding:0 17px; border-radius:10px;
    color:#64748b; font-size:11px; font-weight:700;
}
.stTabs [aria-selected="true"] {
    background:#111827 !important; color:#fff !important;
}
.stTabs [data-baseweb="tab-highlight"] { display:none; }

.stButton > button {
    border:1px solid #d1d5db !important; border-radius:9px !important;
    font-weight:700 !important; font-size:11px !important;
    min-height:38px; background:#fff !important; color:#374151 !important;
}
.stButton > button:hover { border-color:#eab308 !important; color:#92400e !important; }

[data-testid="stSelectbox"] label, [data-testid="stTextInput"] label {
    color:#64748b !important; font-size:10px !important; font-weight:700 !important;
}
[data-baseweb="select"] > div {
    border-radius:9px !important; border-color:#e5e7eb !important; min-height:38px;
}

.vr-login-wrap { max-width:460px; margin:7vh auto 0; }
.login-card {
    background:#fff; border:1px solid var(--vr-line); border-radius:22px;
    padding:38px 40px; box-shadow:0 18px 55px rgba(15,23,42,.08); text-align:center;
}
.logo-container { display:flex; justify-content:center; margin-bottom:17px; }
.login-header { font-size:23px; font-weight:800; color:var(--vr-ink); letter-spacing:-.4px; }
.login-subtitle { font-size:12px; color:#64748b; margin:7px 0 22px; }
.login-badge {
    display:inline-block; padding:5px 9px; border-radius:999px;
    background:var(--vr-yellow-soft); color:#854d0e; font-size:9px;
    font-weight:800; text-transform:uppercase; letter-spacing:.9px; margin-bottom:14px;
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

if is_ready:
    # Premium application header
    hdr_left, hdr_right = st.columns([7.2, 2.8])
    with hdr_left:
        st.markdown(f"""
        <div class="vr-header">
            <div class="vr-brand">
                <img src="{DASHBOARD_LOGO_URL}">
                <div>
                    <div class="vr-eyebrow">Vee Repairs · Operations Intelligence</div>
                    <div class="vr-title">Leads & Sales Dashboard</div>
                    <div class="vr-subtitle">Lead quality, sales verification and lead-to-sale conversion performance</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with hdr_right:
        st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)
        status_col, refresh_col = st.columns([1.35, 1])
        with status_col:
            st.markdown('<div style="text-align:right;padding-top:4px;"><span class="vr-status"><span class="vr-dot"></span> Data Connected</span></div>', unsafe_allow_html=True)
            st.caption(f"Signed in · {st.session_state['user_email']}")
        with refresh_col:
            if st.button("↻ Refresh", use_container_width=True):
                st.cache_data.clear()
                st.rerun()
        if st.button("Sign out", use_container_width=True):
            st.session_state["authenticated"] = False
            st.session_state["logged_login"] = False
            st.rerun()

    tab_leads, tab_sales, tab_conversion = st.tabs([
        "📊  Leads Quality", 
        "💰  Sales Verification", 
        "🔄  Lead Conversion"
    ])
    
    # ==========================================
    # WORKSPACE TAB 1: LEADS ANALYSIS ENGINE
    # ==========================================
    with tab_leads:
        left_lead_filt, right_lead_filt = st.columns([1, 1])
        with left_lead_filt:
            selected_source = st.selectbox("Lead Distribution Branch", ["All Sources", "Delhi", "Ranchi"], key="lead_src_filter")
        with right_lead_filt:
            valid_lead_months = sorted(
                [m for m in df_leads['Month_Display'].unique() if pd.notna(m) and m != 'NaT Unknown' and m != 'Unknown'], 
                key=lambda x: pd.to_datetime(x, format='%b %Y')
            )
            selected_lead_month = st.selectbox("Timeline Block", ["All Months"] + valid_lead_months, key="lead_mth_filter")

        df_l_filtered = df_leads.copy()
        if selected_source != "All Sources":
            df_l_filtered = df_l_filtered[df_l_filtered['Mapped_Source'] == selected_source]
        if selected_lead_month != "All Months":
            df_l_filtered = df_l_filtered[df_l_filtered['Month_Display'] == selected_lead_month]

        if not df_l_filtered.empty:
            raw_l_lb = df_l_filtered.groupby('Agent').agg(
                Total_Leads=('Agent', 'count'),
                Approved=('Cleaned_Quality_Status', lambda x: (x == 'Approved').sum()),
                Rejected=('Cleaned_Quality_Status', lambda x: (x == 'Rejected').sum()),
                Pending=('Cleaned_Quality_Status', lambda x: (x == 'Pending').sum())
            ).reset_index().sort_values(by='Total_Leads', ascending=False)
            
            l_total = raw_l_lb['Total_Leads'].sum()
            l_app = raw_l_lb['Approved'].sum()
            l_rej = raw_l_lb['Rejected'].sum()
            l_pen = raw_l_lb['Pending'].sum()
        else:
            l_total, l_app, l_rej, l_pen = 0, 0, 0, 0

        p_app = (l_app / l_total * 100) if l_total > 0 else 0
        p_rej = (l_rej / l_total * 100) if l_total > 0 else 0
        p_pen = (l_pen / l_total * 100) if l_total > 0 else 0

        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f'<div class="metric-box"><div class="metric-label">Total Allocated</div><div class="metric-number">{l_total:,}</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="metric-box"><div class="metric-label">🟢 Approved</div><div class="metric-number" style="color:#16a34a;">{l_app:,} <span style="font-size:14px; font-weight:500; color:#475569;">({p_app:.1f}%)</span></div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="metric-box"><div class="metric-label">🔴 Rejected</div><div class="metric-number" style="color:#dc2626;">{l_rej:,} <span style="font-size:14px; font-weight:500; color:#475569;">({p_rej:.1f}%)</span></div></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="metric-box"><div class="metric-label">🟡 Pending Threshold</div><div class="metric-number" style="color:#ca8a04;">{l_pen:,} <span style="font-size:14px; font-weight:500; color:#475569;">({p_pen:.1f}%)</span></div></div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)

        col_l_table, col_l_chart = st.columns([4, 5], gap="large")
        
        with col_l_table:
            st.markdown('<div class="section-header">Branch Distribution Matrix</div>', unsafe_allow_html=True)
            if not df_l_filtered.empty:
                l_leaderboard = pd.DataFrame()
                l_leaderboard['Agent'] = raw_l_lb['Agent']
                l_leaderboard['Total_Leads'] = raw_l_lb['Total_Leads']
                
                l_leaderboard['Approved'] = raw_l_lb.apply(lambda r: f"{r['Approved']} ({(r['Approved']/r['Total_Leads'])*100:.1f}%)" if r['Approved'] > 0 else "-", axis=1)
                l_leaderboard['Rejected'] = raw_l_lb.apply(lambda r: f"{r['Rejected']} ({(r['Rejected']/r['Total_Leads'])*100:.1f}%)" if r['Rejected'] > 0 else "-", axis=1)
                l_leaderboard['Pending'] = raw_l_lb.apply(lambda r: f"{r['Pending']} ({(r['Pending']/r['Total_Leads'])*100:.1f}%)" if r['Pending'] > 0 else "-", axis=1)
                
                l_total_row = pd.DataFrame([{
                    'Agent': 'TOTAL', 'Total_Leads': l_total,
                    'Approved': f"{l_app} ({p_app:.1f}%)" if l_app > 0 else "-",
                    'Rejected': f"{l_rej} ({p_rej:.1f}%)" if l_rej > 0 else "-",
                    'Pending': f"{l_pen} ({p_pen:.1f}%)" if l_pen > 0 else "-"
                }])
                l_leaderboard = pd.concat([l_leaderboard, l_total_row], ignore_index=True)
            else:
                l_leaderboard = pd.DataFrame(columns=["Agent", "Total_Leads", "Approved", "Rejected", "Pending"])

            st.dataframe(l_leaderboard.reset_index(drop=True), column_config={
                "Agent": st.column_config.TextColumn("Consultant Name"),
                "Total_Leads": st.column_config.NumberColumn("Total", format="%d"),
                "Approved": st.column_config.TextColumn("🟢 Approved (%)"),
                "Rejected": st.column_config.TextColumn("🔴 Rejected (%)"),
                "Pending": st.column_config.TextColumn("🟡 Pending (%)"),
            }, hide_index=True, use_container_width=True, height=400)

        with col_l_chart:
            st.markdown('<div class="section-header">Leads Quality Trend</div>', unsafe_allow_html=True)
            if not df_l_filtered.empty:
                if selected_lead_month != "All Months":
                    trend_df = df_l_filtered.groupby(['Parsed_Date', 'Day_Display', 'Cleaned_Quality_Status']).size().reset_index(name='Volume').sort_values('Parsed_Date')
                    x_col, x_lbl = 'Day_Display', 'Date'
                else:
                    trend_df = df_l_filtered.groupby(['Parsed_Month', 'Month_Display', 'Cleaned_Quality_Status']).size().reset_index(name='Volume').sort_values('Parsed_Month')
                    x_col, x_lbl = 'Month_Display', 'Month Block'
                
                fig_l = px.line(trend_df, x=x_col, y='Volume', color='Cleaned_Quality_Status',
                                labels={x_col: x_lbl, 'Volume': 'Leads Volume', 'Cleaned_Quality_Status': 'Status'},
                                color_discrete_map={'Approved': '#16a34a', 'Rejected': '#dc2626', 'Pending': '#ca8a04'}, markers=True)
                fig_l.update_layout(paper_bgcolor='#ffffff', plot_bgcolor='#ffffff', font=dict(family="Inter, sans-serif", size=11),
                                    xaxis=dict(showgrid=False, linecolor='#cbd5e1'), yaxis=dict(showgrid=True, gridcolor='#f1f5f9', title=None),
                                    legend=dict(title=None, orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), height=380, margin=dict(l=15, r=15, t=10, b=10))
                st.plotly_chart(fig_l, use_container_width=True, config={'displayModeBar': False})

    # ==========================================
    # WORKSPACE TAB 2: SALES TRACKER ENGINE 
    # ==========================================
    with tab_sales:
        left_s_filt, right_s_space = st.columns([1, 1])
        with left_s_filt:
            valid_sales_months = sorted(
                [m for m in df_sales['Month_Display'].unique() if pd.notna(m) and m != 'NaT Unknown' and m != 'Unknown'], 
                key=lambda x: pd.to_datetime(x, format='%b %Y')
            )
            selected_sales_month = st.selectbox("Sales Month Filter", ["All Months"] + valid_sales_months, key="sales_mth_filter")

        df_s_filtered = df_sales.copy()
        if selected_sales_month != "All Months":
            df_s_filtered = df_s_filtered[df_s_filtered['Month_Display'] == selected_sales_month]

        if not df_s_filtered.empty:
            raw_s_lb = df_s_filtered.groupby('Agent').agg(
                Total_Sales=('Agent', 'count'),
                Live=('Cleaned_Payment_Status', lambda x: (x == 'Live').sum()),
                Cancelled=('Cleaned_Payment_Status', lambda x: (x == 'Cancelled').sum()),
                Pending=('Cleaned_Payment_Status', lambda x: (x == 'Pending').sum()),
                Revenue=('Live_Amount', 'sum')
            ).reset_index().sort_values(by='Total_Sales', ascending=False)
            
            s_total = raw_s_lb['Total_Sales'].sum()
            s_live = raw_s_lb['Live'].sum()
            s_total_cancel = raw_s_lb['Cancelled'].sum()
            s_pend = raw_s_lb['Pending'].sum()
            s_revenue = raw_s_lb['Revenue'].sum()
        else:
            s_total, s_live, s_total_cancel, s_pend, s_revenue = 0, 0, 0, 0, 0.0

        s_reason_counts = df_s_filtered['Cancel_Reason'].value_counts().to_dict()
        s_wc_cancel = s_reason_counts.get('WC Cancelled', 0)
        s_pay_cancel = s_reason_counts.get('Payment Cancelled', 0)

        ps_live = (s_live / s_total * 100) if s_total > 0 else 0
        ps_canc = (s_total_cancel / s_total * 100) if s_total > 0 else 0
        ps_pend = (s_pend / s_total * 100) if s_total > 0 else 0

        sc1, sc2, sc3, sc4, sc5 = st.columns(5)
        sc1.markdown(f'<div class="metric-box"><div class="metric-label">Total Logged Sales</div><div class="metric-number">{s_total:,}</div></div>', unsafe_allow_html=True)
        sc2.markdown(f'<div class="metric-box"><div class="metric-label">🟢 Live (Accepted)</div><div class="metric-number" style="color:#16a34a;">{s_live:,} <span style="font-size:14px; font-weight:500; color:#475569;">({ps_live:.1f}%)</span></div></div>', unsafe_allow_html=True)
        sc3.markdown(f'<div class="metric-box"><div class="metric-label">🔴 Total Cancelled</div><div class="metric-number" style="color:#dc2626;">{s_total_cancel:,} <span style="font-size:14px; font-weight:500; color:#475569;">({ps_canc:.1f}%)</span></div></div>', unsafe_allow_html=True)
        sc4.markdown(f'<div class="metric-box"><div class="metric-label">🟡 Pending Review</div><div class="metric-number" style="color:#ca8a04;">{s_pend:,} <span style="font-size:14px; font-weight:500; color:#475569;">({ps_pend:.1f}%)</span></div></div>', unsafe_allow_html=True)
        sc5.markdown(f'<div class="metric-box"><div class="metric-label">💰 Live Invoiced Revenue</div><div class="metric-number">£{s_revenue:,.2f}</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # --- ADJUSTED DYNAMIC QUALITY STATUS BREAKDOWN (TAB 2) ---
        if 'Quality status' in df_s_filtered.columns and not df_s_filtered.empty:
            df_s_filtered['Normalized_Quality'] = df_s_filtered['Quality status'].astype(str).str.strip()
            
            s_q_approved = df_s_filtered['Normalized_Quality'].str.lower().isin(['approved', 'approve']).sum()
            s_q_rejected = df_s_filtered['Normalized_Quality'].str.lower().isin(['rejected', 'reject']).sum()
            
            non_explicit = ['nan', 'none', '', 'approved', 'approve', 'rejected', 'reject']
            other_series = df_s_filtered[~df_s_filtered['Normalized_Quality'].str.lower().isin(non_explicit)]
            other_categories = other_series['Normalized_Quality'].value_counts().to_dict()
            
            explicit_sum = s_q_approved + s_q_rejected + sum(other_categories.values())
            
            s_q_pending = max(0, s_total - explicit_sum)
            
            ordered_q_counts = {}
            if s_q_approved > 0: ordered_q_counts['Approved'] = s_q_approved
            if s_q_rejected > 0: ordered_q_counts['Rejected'] = s_q_rejected
            for cat_k, cat_v in other_categories.items():
                ordered_q_counts[cat_k] = cat_v
            if s_q_pending > 0: ordered_q_counts['Quality Pending'] = s_q_pending

            s_q_html = []
            for q_name, q_cnt in ordered_q_counts.items():
                q_pct = (q_cnt / s_total * 100) if s_total > 0 else 0
                s_q_html.append(f'<span class="breakdown-item">✨ <b>{q_name}:</b> {q_cnt:,} ({q_pct:.1f}%)</span>')
            s_q_string = " ".join(s_q_html) if s_q_html else '<span style="font-size:12px; color:#64748b;">No quality status variables found</span>'
        else:
            s_q_pending = s_total
            s_pct_pending = 100.0 if s_total > 0 else 0
            s_q_string = f'<span class="breakdown-item">✨ <b>Quality Pending:</b> {s_q_pending:,} ({s_pct_pending:.1f}%)</span>'

        st.markdown(
            f'<div class="breakdown-strip">'
            f'  <div class="breakdown-title">🛡️ Quality Status Breakdown</div>'
            f'  <div class="breakdown-sub-box">{s_q_string}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        # --- WLCM STATUS BREAKDOWN (TAB 2) ---
        if 'WlcmStatus' in df_s_filtered.columns and not df_s_filtered.empty:
            s_w_counts = df_s_filtered['WlcmStatus'].astype(str).str.strip().value_counts().to_dict()
            s_w_html = []
            for w_name, w_cnt in s_w_counts.items():
                if w_name not in ['nan', 'None', '']:
                    w_pct = (w_cnt / s_total * 100) if s_total > 0 else 0
                    s_w_html.append(f'<span class="breakdown-item">📞 <b>{w_name}:</b> {w_cnt:,} ({w_pct:.1f}%)</span>')
            s_w_string = " ".join(s_w_html) if s_w_html else '<span style="font-size:12px; color:#64748b;">No welcome call status metrics found</span>'
        else:
            s_w_string = '<span style="font-size:12px; color:#64748b;">WlcmStatus column missing or empty in data context</span>'

        st.markdown(
            f'<div class="breakdown-strip">'
            f'  <div class="breakdown-title">👋 Wlcm Status Breakdown</div>'
            f'  <div class="breakdown-sub-box">{s_w_string}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        # --- CANCELLATION BREAKDOWN (TAB 2) ---
        df_s_disallowed_only = df_s_filtered[df_s_filtered['Cancel_Reason'] == 'Payment Cancelled']
        s_sub_cat_counts = df_s_disallowed_only['Disallowed_Subcategory'].value_counts().to_dict()
        
        s_sub_html_items = []
        for cat_name, count in s_sub_cat_counts.items():
            if cat_name not in ['None', 'nan', '']:
                pct = (count / s_pay_cancel * 100) if s_pay_cancel > 0 else 0
                s_sub_html_items.append(f'<span class="breakdown-item">⚠️ <b>{cat_name}:</b> {count:,} ({pct:.1f}%)</span>')
        
        s_sub_cat_string = " ".join(s_sub_html_items) if s_sub_html_items else '<span style="font-size:12px; color:#64748b;">No category text discovered in column metrics</span>'

        st.markdown(
            f'<div class="breakdown-strip">'
            f'  <div class="breakdown-title">🔍 Cancellation Reason Breakdown</div>'
            f'  <div class="breakdown-sub-box" style="margin-bottom: 8px;">'
            f'      <span style="font-size:13px; color:#334155;">📋 <b>Welcome Call Cancelled:</b> {s_wc_cancel:,} records ({(s_wc_cancel/s_total_cancel*100 if s_total_cancel > 0 else 0):.1f}%)</span>'
            f'  </div>'
            f'  <div style="border-top: 1px dashed #cbd5e1; margin: 8px 0;"></div>'
            f'  <div class="breakdown-title" style="font-size:11px; color:#64748b;">🚫 Payment Status Disallowed Subcategories ({s_pay_cancel:,} Total):</div>'
            f'  <div class="breakdown-sub-box">'
            f'      {s_sub_cat_string}'
            f'  </div>'
            f'</div>', 
            unsafe_allow_html=True
        )

        st.markdown("<br>", unsafe_allow_html=True)

        col_s_table, col_s_chart = st.columns([4, 5], gap="large")
        
        with col_s_table:
            st.markdown('<div class="section-header">Agent Sales Performance Matrix</div>', unsafe_allow_html=True)
            if not df_s_filtered.empty:
                s_leaderboard = pd.DataFrame()
                s_leaderboard['Agent'] = raw_s_lb['Agent']
                s_leaderboard['Total_Sales'] = raw_s_lb['Total_Sales']
                
                s_leaderboard['Live'] = raw_s_lb.apply(lambda r: f"{r['Live']} ({(r['Live']/r['Total_Sales'])*100:.1f}%)" if r['Live'] > 0 else "-", axis=1)
                s_leaderboard['Cancelled'] = raw_s_lb.apply(lambda r: f"{r['Cancelled']} ({(r['Cancelled']/r['Total_Sales'])*100:.1f}%)" if r['Cancelled'] > 0 else "-", axis=1)
                s_leaderboard['Pending'] = raw_s_lb.apply(lambda r: f"{r['Pending']} ({(r['Pending']/r['Total_Sales'])*100:.1f}%)" if r['Pending'] > 0 else "-", axis=1)
                s_leaderboard['Revenue'] = raw_s_lb['Revenue']
                
                s_total_row = pd.DataFrame([{
                    'Agent': 'TOTAL', 'Total_Sales': s_total,
                    'Live': f"{s_live} ({ps_live:.1f}%)" if s_live > 0 else "-",
                    'Cancelled': f"{s_total_cancel} ({ps_canc:.1f}%)" if s_total_cancel > 0 else "-",
                    'Pending': f"{s_pend} ({ps_pend:.1f}%)" if s_pend > 0 else "-",
                    'Revenue': s_revenue
                }])
                s_leaderboard = pd.concat([s_leaderboard, s_total_row], ignore_index=True)
            else:
                s_leaderboard = pd.DataFrame(columns=["Agent", "Total_Sales", "Live", "Cancelled", "Pending", "Revenue"])

            st.dataframe(s_leaderboard.reset_index(drop=True), column_config={
                "Agent": st.column_config.TextColumn("Consultant Name"),
                "Total_Sales": st.column_config.NumberColumn("Total Sales", format="%d"),
                "Live": st.column_config.TextColumn("🟢 Live (%)"),
                "Cancelled": st.column_config.TextColumn("🔴 Cancelled (%)"),
                "Pending": st.column_config.TextColumn("🟡 Pending (%)"),
                "Revenue": st.column_config.NumberColumn("💰 Live Revenue", format="£%.2f"),
            }, hide_index=True, use_container_width=True, height=400)
            
        with col_s_chart:
            st.markdown('<div class="section-header">Sales Performance Trends</div>', unsafe_allow_html=True)
            if not df_s_filtered.empty:
                if selected_sales_month != "All Months":
                    s_trend_df = df_s_filtered.groupby(['Parsed_Date', 'Day_Display', 'Cleaned_Payment_Status']).size().reset_index(name='Volume').sort_values('Parsed_Date')
                    sx_col, sx_lbl = 'Day_Display', 'Date'
                else:
                    s_trend_df = df_s_filtered.groupby(['Parsed_Month', 'Month_Display', 'Cleaned_Payment_Status']).size().reset_index(name='Volume').sort_values('Parsed_Month')
                    sx_col, sx_lbl = 'Month_Display', 'Month Block'
                
                fig_s = px.line(s_trend_df, x=sx_col, y='Volume', color='Cleaned_Payment_Status',
                                labels={sx_col: sx_lbl, 'Volume': 'Sales Volume', 'Cleaned_Payment_Status': 'Status'},
                                color_discrete_map={'Live': '#16a34a', 'Cancelled': '#dc2626', 'Pending': '#ca8a04'}, markers=True)
                fig_s.update_layout(paper_bgcolor='#ffffff', plot_bgcolor='#ffffff', font=dict(family="Inter, sans-serif", size=11),
                                    xaxis=dict(showgrid=False, linecolor='#cbd5e1'), yaxis=dict(showgrid=True, gridcolor='#f1f5f9', title=None),
                                    legend=dict(title=None, orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), height=380, margin=dict(l=15, r=15, t=10, b=10))
                st.plotly_chart(fig_s, use_container_width=True, config={'displayModeBar': False})

    # ==========================================
    # WORKSPACE TAB 3: LEADS CONVERSION STATUS
    # ==========================================
    with tab_conversion:
        left_c_filt, right_c_space = st.columns([1, 1])
        with left_c_filt:
            selected_conv_source = st.selectbox("Lead Distribution Branch", ["All Sources", "Delhi", "Ranchi"], key="conv_src_filter")
        with right_c_space:
            valid_conv_months = sorted(
                [m for m in df_leads['Month_Display'].unique() if pd.notna(m) and m != 'NaT Unknown' and m != 'Unknown'], 
                key=lambda x: pd.to_datetime(x, format='%b %Y')
            )
            selected_conv_month = st.selectbox("Lead Month Filter", ["All Months"] + valid_conv_months, key="conv_mth_filter")

        phone_lead_meta = df_leads.dropna(subset=['Clean_Phone']).drop_duplicates(subset=['Clean_Phone'])
        phone_to_month = dict(zip(phone_lead_meta['Clean_Phone'], phone_lead_meta['Month_Display']))
        phone_to_pmonth = dict(zip(phone_lead_meta['Clean_Phone'], phone_lead_meta['Parsed_Month']))
        phone_to_pdate = dict(zip(phone_lead_meta['Clean_Phone'], phone_lead_meta['Parsed_Date']))
        phone_to_ddisplay = dict(zip(phone_lead_meta['Clean_Phone'], phone_lead_meta['Day_Display']))
        phone_to_source = dict(zip(phone_lead_meta['Clean_Phone'], phone_lead_meta['Mapped_Source']))

        # Calculate Total Leads for this tab dynamically based on the active selection metrics
        df_l_total_calc = df_leads.copy()
        if selected_conv_source != "All Sources":
            df_l_total_calc = df_l_total_calc[df_l_total_calc['Mapped_Source'] == selected_conv_source]
        if selected_conv_month != "All Months":
            df_l_total_calc = df_l_total_calc[df_l_total_calc['Month_Display'] == selected_conv_month]
        conv_tab_total_leads = len(df_l_total_calc)

        df_c_filtered = df_sales.copy()
        
        valid_lead_phones = set(phone_to_month.keys()) - {"", "nan"}
        df_c_filtered = df_c_filtered[df_c_filtered['Clean_Phone'].isin(valid_lead_phones)].copy()

        df_c_filtered['Lead_Month_Display'] = df_c_filtered['Clean_Phone'].map(phone_to_month)
        df_c_filtered['Lead_Parsed_Month'] = df_c_filtered['Clean_Phone'].map(phone_to_pmonth)
        df_c_filtered['Lead_Parsed_Date'] = df_c_filtered['Clean_Phone'].map(phone_to_pdate)
        df_c_filtered['Lead_Day_Display'] = df_c_filtered['Clean_Phone'].map(phone_to_ddisplay)
        df_c_filtered['Lead_Mapped_Source'] = df_c_filtered['Clean_Phone'].map(phone_to_source)

        if selected_conv_source != "All Sources":
            df_c_filtered = df_c_filtered[df_c_filtered['Lead_Mapped_Source'] == selected_conv_source]
        if selected_conv_month != "All Months":
            df_c_filtered = df_c_filtered[df_c_filtered['Lead_Month_Display'] == selected_conv_month]

        # ==============================================================================
        # DUAL-METRIC COMPILATION ENGINE (Unique Conversions vs Total Multi-Conversions)
        # ==============================================================================
        if not df_c_filtered.empty:
            # 1. Total Multi-Conversions (Count every transaction row)
            raw_c_lb = df_c_filtered.groupby('Agent').agg(
                Total_Sales_Multi=('Agent', 'count'),
                Live_Multi=('Cleaned_Payment_Status', lambda x: (x == 'Live').sum()),
                Cancelled_Multi=('Cleaned_Payment_Status', lambda x: (x == 'Cancelled').sum()),
                Pending_Multi=('Cleaned_Payment_Status', lambda x: (x == 'Pending').sum()),
                Revenue_Multi=('Live_Amount', 'sum')
            ).reset_index()

            # 2. Unique Conversions (Drop duplicate phone logs per agent hierarchy)
            df_c_unique = df_c_filtered.drop_duplicates(subset=['Agent', 'Clean_Phone']).copy()
            raw_c_lb_unique = df_c_unique.groupby('Agent').agg(
                Total_Sales_Unique=('Agent', 'count'),
                Live_Unique=('Cleaned_Payment_Status', lambda x: (x == 'Live').sum()),
                Cancelled_Unique=('Cleaned_Payment_Status', lambda x: (x == 'Cancelled').sum()),
                Pending_Unique=('Cleaned_Payment_Status', lambda x: (x == 'Pending').sum())
            ).reset_index()

            # Combine summaries 
            raw_c_lb = pd.merge(raw_c_lb, raw_c_lb_unique, on='Agent', how='outer').fillna(0)
            raw_c_lb = raw_c_lb.sort_values(by='Total_Sales_Multi', ascending=False)
            
            # Global Totals
            c_total_multi = int(raw_c_lb['Total_Sales_Multi'].sum())
            c_live_multi = int(raw_c_lb['Live_Multi'].sum())
            c_total_cancel_multi = int(raw_c_lb['Cancelled_Multi'].sum())
            c_pend_multi = int(raw_c_lb['Pending_Multi'].sum())
            c_revenue = raw_c_lb['Revenue_Multi'].sum()

            c_total_unique = int(df_c_filtered.drop_duplicates(subset=['Clean_Phone'])['Clean_Phone'].count())
            c_live_unique = int(df_c_filtered[df_c_filtered['Cleaned_Payment_Status'] == 'Live'].drop_duplicates(subset=['Clean_Phone'])['Clean_Phone'].count())
            c_total_cancel_unique = int(df_c_filtered[df_c_filtered['Cleaned_Payment_Status'] == 'Cancelled'].drop_duplicates(subset=['Clean_Phone'])['Clean_Phone'].count())
            c_pend_unique = int(df_c_filtered[df_c_filtered['Cleaned_Payment_Status'] == 'Pending'].drop_duplicates(subset=['Clean_Phone'])['Clean_Phone'].count())
        else:
            c_total_multi, c_live_multi, c_total_cancel_multi, c_pend_multi, c_revenue = 0, 0, 0, 0, 0.0
            c_total_unique, c_live_unique, c_total_cancel_unique, c_pend_unique = 0, 0, 0, 0
            raw_c_lb = pd.DataFrame()

        c_reason_counts = df_c_filtered['Cancel_Reason'].value_counts().to_dict()
        c_wc_cancel = c_reason_counts.get('WC Cancelled', 0) if 'WC Cancelled' in c_reason_counts else c_reason_counts.get('Welcome Call Cancelled', 0)
        c_pay_cancel = c_reason_counts.get('Payment Cancelled', 0)

        # Rates Calculations
        rate_total_unique = (c_total_unique / conv_tab_total_leads * 100) if conv_tab_total_leads > 0 else 0
        rate_total_multi = (c_total_multi / conv_tab_total_leads * 100) if conv_tab_total_leads > 0 else 0
        
        rate_live_unique = (c_live_unique / conv_tab_total_leads * 100) if conv_tab_total_leads > 0 else 0
        rate_live_multi = (c_live_multi / conv_tab_total_leads * 100) if conv_tab_total_leads > 0 else 0

        rate_cancel_unique = (c_total_cancel_unique / conv_tab_total_leads * 100) if conv_tab_total_leads > 0 else 0
        rate_cancel_multi = (c_total_cancel_multi / conv_tab_total_leads * 100) if conv_tab_total_leads > 0 else 0

        rate_pend_unique = (c_pend_unique / conv_tab_total_leads * 100) if conv_tab_total_leads > 0 else 0
        rate_pend_multi = (c_pend_multi / conv_tab_total_leads * 100) if conv_tab_total_leads > 0 else 0

        section_header("Conversion Overview", "Unique conversion metrics shown first; transaction totals shown in brackets")
        # UI Executive KPI Block Output
        cc0, cc1, cc2, cc3, cc4, cc5 = st.columns(6)
        cc0.markdown(f'<div class="metric-box"><div class="metric-label">Total Leads Pool</div><div class="metric-number">{conv_tab_total_leads:,}</div></div>', unsafe_allow_html=True)
        cc1.markdown(f'<div class="metric-box"><div class="metric-label">Total Converted</div><div class="metric-number">{c_total_unique:,} <span style="font-size:13px; font-weight:500; color:#475569;">({c_total_multi:,})</span><br><span style="font-size:11px; font-weight:600; color:#64748b;">{rate_total_unique:.1f}% ({rate_total_multi:.1f}%)</span></div></div>', unsafe_allow_html=True)
        cc2.markdown(f'<div class="metric-box"><div class="metric-label">🟢 Live (Accepted)</div><div class="metric-number" style="color:#16a34a;">{c_live_unique:,} <span style="font-size:13px; font-weight:500; color:#475569;">({c_live_multi:,})</span><br><span style="font-size:11px; font-weight:600; color:#16a34a;">{rate_live_unique:.1f}% ({rate_live_multi:.1f}%)</span></div></div>', unsafe_allow_html=True)
        cc3.markdown(f'<div class="metric-box"><div class="metric-label">🔴 Total Cancelled</div><div class="metric-number" style="color:#dc2626;">{c_total_cancel_unique:,} <span style="font-size:13px; font-weight:500; color:#475569;">({c_total_cancel_multi:,})</span><br><span style="font-size:11px; font-weight:600; color:#dc2626;">{rate_cancel_unique:.1f}% ({rate_cancel_multi:.1f}%)</span></div></div>', unsafe_allow_html=True)
        cc4.markdown(f'<div class="metric-box"><div class="metric-label">🟡 Pending Conversion</div><div class="metric-number" style="color:#ca8a04;">{c_pend_unique:,} <span style="font-size:13px; font-weight:500; color:#475569;">({c_pend_multi:,})</span><br><span style="font-size:11px; font-weight:600; color:#ca8a04;">{rate_pend_unique:.1f}% ({rate_pend_multi:.1f}%)</span></div></div>', unsafe_allow_html=True)
        cc5.markdown(f'<div class="metric-box"><div class="metric-label">💰 Invoiced Revenue</div><div class="metric-number">£{c_revenue:,.2f}</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # --- ADJUSTED DYNAMIC QUALITY STATUS BREAKDOWN (TAB 3) ---
        if 'Quality status' in df_c_filtered.columns and not df_c_filtered.empty:
            df_c_filtered['Normalized_Quality'] = df_c_filtered['Quality status'].astype(str).str.strip()
            
            c_q_approved = df_c_filtered['Normalized_Quality'].str.lower().isin(['approved', 'approve']).sum()
            c_q_rejected = df_c_filtered['Normalized_Quality'].str.lower().isin(['rejected', 'reject']).sum()
            
            non_explicit_c = ['nan', 'none', '', 'approved', 'approve', 'rejected', 'reject']
            other_series_c = df_c_filtered[~df_c_filtered['Normalized_Quality'].str.lower().isin(non_explicit_c)]
            other_categories_c = other_series_c['Normalized_Quality'].value_counts().to_dict()
            
            explicit_sum_c = c_q_approved + c_q_rejected + sum(other_categories_c.values())
            
            c_q_pending = max(0, c_total_multi - explicit_sum_c)
            
            ordered_c_counts = {}
            if c_q_approved > 0: ordered_c_counts['Approved'] = c_q_approved
            if c_q_rejected > 0: ordered_c_counts['Rejected'] = c_q_rejected
            for cat_ck, cat_cv in other_categories_c.items():
                ordered_c_counts[cat_ck] = cat_cv
            if c_q_pending > 0: ordered_c_counts['Quality Pending'] = c_q_pending

            c_q_html = []
            for q_name, q_cnt in ordered_c_counts.items():
                q_pct = (q_cnt / c_total_multi * 100) if c_total_multi > 0 else 0
                c_q_html.append(f'<span class="breakdown-item">✨ <b>{q_name}:</b> {q_cnt:,} ({q_pct:.1f}%)</span>')
            c_q_string = " ".join(c_q_html) if c_q_html else '<span style="font-size:12px; color:#64748b;">No quality status variables found</span>'
        else:
            c_q_pending = c_total_multi
            c_pct_pending = 100.0 if c_total_multi > 0 else 0
            c_q_string = f'<span class="breakdown-item">✨ <b>Quality Pending:</b> {c_q_pending:,} ({c_pct_pending:.1f}%)</span>'

        st.markdown(
            f'<div class="breakdown-strip">'
            f'  <div class="breakdown-title">🛡️ Quality Status Breakdown</div>'
            f'  <div class="breakdown-sub-box">{c_q_string}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        # --- WLCM STATUS BREAKDOWN (TAB 3) ---
        if 'WlcmStatus' in df_c_filtered.columns and not df_c_filtered.empty:
            c_w_counts = df_c_filtered['WlcmStatus'].astype(str).str.strip().value_counts().to_dict()
            c_w_html = []
            for w_name, w_cnt in c_w_counts.items():
                if w_name not in ['nan', 'None', '']:
                    w_pct = (w_cnt / c_total_multi * 100) if c_total_multi > 0 else 0
                    c_w_html.append(f'<span class="breakdown-item">📞 <b>{w_name}:</b> {w_cnt:,} ({w_pct:.1f}%)</span>')
            c_w_string = " ".join(c_w_html) if c_w_html else '<span style="font-size:12px; color:#64748b;">No welcome call status metrics found</span>'
        else:
            c_w_string = '<span style="font-size:12px; color:#64748b;">WlcmStatus column missing or empty in context</span>'

        st.markdown(
            f'<div class="breakdown-strip">'
            f'  <div class="breakdown-title">👋 Wlcm Status Breakdown</div>'
            f'  <div class="breakdown-sub-box">{c_w_string}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        # --- CANCELLATION BREAKDOWN (TAB 3) ---
        df_c_disallowed_only = df_c_filtered[df_c_filtered['Cancel_Reason'] == 'Payment Cancelled']
        c_sub_cat_counts = df_c_disallowed_only['Disallowed_Subcategory'].value_counts().to_dict()
        
        c_sub_html_items = []
        for cat_name, count in c_sub_cat_counts.items():
            if cat_name not in ['None', 'nan', '']:
                pct = (count / c_pay_cancel * 100) if c_pay_cancel > 0 else 0
                c_sub_html_items.append(f'<span class="breakdown-item">⚠️ <b>{cat_name}:</b> {count:,} ({pct:.1f}%)</span>')
        
        c_sub_cat_string = " ".join(c_sub_html_items) if c_sub_html_items else '<span style="font-size:12px; color:#64748b;">No category text discovered in column metrics</span>'

        st.markdown(
            f'<div class="breakdown-strip">'
            f'  <div class="breakdown-title">🔍 Cancellation Reason Breakdown</div>'
            f'  <div class="breakdown-sub-box" style="margin-bottom: 8px;">'
            f'      <span style="font-size:13px; color:#334155;">📋 <b>Welcome Call Cancelled:</b> {c_wc_cancel:,} records ({(c_wc_cancel/c_total_cancel_multi*100 if c_total_cancel_multi > 0 else 0):.1f}%)</span>'
            f'  </div>'
            f'  <div style="border-top: 1px dashed #cbd5e1; margin: 8px 0;"></div>'
            f'  <div class="breakdown-title" style="font-size:11px; color:#64748b;">🚫 Payment Status Cancelled Subcategories ({c_pay_cancel:,} Total):</div>'
            f'  <div class="breakdown-sub-box">'
            f'      {c_sub_cat_string}'
            f'  </div>'
            f'</div>', 
            unsafe_allow_html=True
        )

        st.markdown("<br>", unsafe_allow_html=True)

        section_header("Conversion Performance", "Consultant conversion volume and lead-origin trend")
        col_c_table, col_c_chart = st.columns([4, 5], gap="large")
        
        with col_c_table:
            st.markdown('<div class="section-header">Agent Conversion & Revenue Summary</div>', unsafe_allow_html=True)
            if not df_c_filtered.empty:
                c_leaderboard = pd.DataFrame()
                c_leaderboard['Agent'] = raw_c_lb['Agent']
                
                # Format Leaderboard Rows to show: Unique (Total Volume) with Bracketed Percentages
                c_leaderboard['Total_Converted'] = raw_c_lb.apply(
                    lambda r: f"{int(r['Total_Sales_Unique'])} ({int(r['Total_Sales_Multi'])})", axis=1
                )
                
                c_leaderboard['Live'] = raw_c_lb.apply(
                    lambda r: f"{int(r['Live_Unique'])} ({int(r['Live_Multi'])}) — [{(r['Live_Unique']/r['Total_Sales_Unique']*100 if r['Total_Sales_Unique'] > 0 else 0):.1f}% | {(r['Live_Multi']/r['Total_Sales_Multi']*100 if r['Total_Sales_Multi'] > 0 else 0):.1f}%]", axis=1
                )
                
                c_leaderboard['Cancelled'] = raw_c_lb.apply(
                    lambda r: f"{int(r['Cancelled_Unique'])} ({int(r['Cancelled_Multi'])}) — [{(r['Cancelled_Unique']/r['Total_Sales_Unique']*100 if r['Total_Sales_Unique'] > 0 else 0):.1f}% | {(r['Cancelled_Multi']/r['Total_Sales_Multi']*100 if r['Total_Sales_Multi'] > 0 else 0):.1f}%]", axis=1
                )
                
                c_leaderboard['Pending'] = raw_c_lb.apply(
                    lambda r: f"{int(r['Pending_Unique'])} ({int(r['Pending_Multi'])}) — [{(r['Pending_Unique']/r['Total_Sales_Unique']*100 if r['Total_Sales_Unique'] > 0 else 0):.1f}% | {(r['Pending_Multi']/r['Total_Sales_Multi']*100 if r['Total_Sales_Multi'] > 0 else 0):.1f}%]", axis=1
                )
                
                c_leaderboard['Revenue'] = raw_c_lb['Revenue_Multi']
                
                # Append Summary Total Row
                c_total_row = pd.DataFrame([{
                    'Agent': 'TOTAL',
                    'Total_Converted': f"{c_total_unique} ({c_total_multi})",
                    'Live': f"{c_live_unique} ({c_live_multi}) — [{c_live_unique/c_total_unique*100 if c_total_unique > 0 else 0:.1f}% | {c_live_multi/c_total_multi*100 if c_total_multi > 0 else 0:.1f}%]",
                    'Cancelled': f"{c_total_cancel_unique} ({c_total_cancel_multi}) — [{c_total_cancel_unique/c_total_unique*100 if c_total_unique > 0 else 0:.1f}% | {c_total_cancel_multi/c_total_multi*100 if c_total_multi > 0 else 0:.1f}%]",
                    'Pending': f"{c_pend_unique} ({c_pend_multi}) — [{c_pend_unique/c_total_unique*100 if c_total_unique > 0 else 0:.1f}% | {c_pend_multi/c_total_multi*100 if c_total_multi > 0 else 0:.1f}%]",
                    'Revenue': c_revenue
                }])
                c_leaderboard = pd.concat([c_leaderboard, c_total_row], ignore_index=True)
            else:
                c_leaderboard = pd.DataFrame(columns=["Agent", "Total_Converted", "Live", "Cancelled", "Pending", "Revenue"])

            st.dataframe(c_leaderboard.reset_index(drop=True), column_config={
                "Agent": st.column_config.TextColumn("Consultant Name"),
                "Total_Converted": st.column_config.TextColumn("Unique (Total) Volume"),
                "Live": st.column_config.TextColumn("🟢 Live Metrics [Uniq% | Multi%]"),
                "Cancelled": st.column_config.TextColumn("🔴 Cancelled Metrics [Uniq% | Multi%]"),
                "Pending": st.column_config.TextColumn("🟡 Pending Metrics [Uniq% | Multi%]"),
                "Revenue": st.column_config.NumberColumn("💰 Live Revenue", format="£%.2f"),
            }, hide_index=True, use_container_width=True, height=400)
            
        with col_c_chart:
            st.markdown('<div class="section-header">Lead Conversion Over Time (Total Volumes)</div>', unsafe_allow_html=True)
            if not df_c_filtered.empty:
                if selected_conv_month != "All Months":
                    c_trend_df = df_c_filtered.groupby(['Lead_Parsed_Date', 'Lead_Day_Display', 'Cleaned_Payment_Status']).size().reset_index(name='Volume').sort_values('Lead_Parsed_Date')
                    cx_col, sx_lbl = 'Lead_Day_Display', 'Date'
                else:
                    c_trend_df = df_c_filtered.groupby(['Lead_Parsed_Month', 'Lead_Month_Display', 'Cleaned_Payment_Status']).size().reset_index(name='Volume').sort_values('Lead_Parsed_Month')
                    cx_col, sx_lbl = 'Lead_Month_Display', 'Month'
                
                fig_c = px.line(c_trend_df, x=cx_col, y='Volume', color='Cleaned_Payment_Status',
                                labels={cx_col: sx_lbl, 'Volume': 'Sales Volume', 'Cleaned_Payment_Status': 'Status'},
                                color_discrete_map={'Live': '#16a34a', 'Cancelled': '#dc2626', 'Pending': '#ca8a04'}, markers=True)
                fig_c.update_layout(paper_bgcolor='#ffffff', plot_bgcolor='#ffffff', font=dict(family="Inter, sans-serif", size=11),
                                    xaxis=dict(showgrid=False, linecolor='#cbd5e1'), yaxis=dict(showgrid=True, gridcolor='#f1f5f9', title=None),
                                    legend=dict(title=None, orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), height=380, margin=dict(l=15, r=15, t=10, b=10))
                st.plotly_chart(fig_c, use_container_width=True, config={'displayModeBar': False})
            else:
                st.info("No converted leads found for this month filter.")
