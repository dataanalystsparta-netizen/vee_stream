import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px

# --- 1. SET COMPACT GLOBAL CONFIG ---
st.set_page_config(
    page_title="Sparta Telecom Analytics Suite",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. EXECUTIVE THEME RULES (Yellow Header / Professional Palette) ---
st.config.set_option("theme.backgroundColor", "#f8fafc")
st.config.set_option("theme.secondaryBackgroundColor", "#ffffff")
st.config.set_option("theme.textColor", "#0f172a")
st.config.set_option("theme.primaryColor", "#eab308")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght=400;500;600;700&display=swap');
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        font-family: 'Inter', sans-serif;
    }
    .main-title { font-size: 26px; font-weight: 700; color: #0f172a !important; margin-bottom: 2px; }
    .subtitle { font-size: 13px; color: #475569 !important; margin-bottom: 20px; }
    .metric-box { background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 15px 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.02); }
    .metric-label { font-size: 11px; font-weight: 600; color: #475569 !important; text-transform: uppercase; letter-spacing: 0.5px; }
    .metric-number { font-size: 24px; font-weight: 700; color: #0f172a !important; margin-top: 2px; }
    .section-header { font-size: 16px; font-weight: 600; color: #0f172a !important; margin-bottom: 12px; }
    div[data-testid="stTable"] th, div[data-testid="styledDataFrame"] th, .stDataFrame th {
        background-color: #fef08a !important;
        color: #1e293b !important;
        font-weight: 600 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Shared Data Node Ingestion Config
SHEET_ID = '1dUqj3sp5Jva_nYjMzPyGAM6wwNfFINF6IRj5Z94FScU'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

# Helper to normalize numbers completely (Handles floats like 44.0, formats to clean digits)
def normalize_phone_string(series):
    return (
        series.astype(str)
        .str.strip()
        .str.replace(r'\.0$', '', regex=True)  # Remove trailing decimal zero from numeric conversions
        .str.replace(r'\D', '', regex=True)    # Remove any non-numeric formatting characters
    )

# --- 3. ROBUST SPREADSHEET INGEST ENGINE ---
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
    
    # Precise extraction targeting "Phone No." for Leads Sheet
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
    
    if 'Payment Status' in df_s.columns:
        df_s['Cleaned_Payment_Status'] = df_s['Payment Status'].astype(str).str.strip()
        blank_mask = df_s['Cleaned_Payment_Status'].isin(['nan', 'None', '', 'NaN'])
        accepted_mask = df_s['Cleaned_Payment_Status'].str.lower() == 'accepted'
        
        df_s['Cleaned_Payment_Status'] = 'Cancelled'
        df_s.loc[blank_mask, 'Cleaned_Payment_Status'] = 'Pending'
        df_s.loc[accepted_mask, 'Cleaned_Payment_Status'] = 'Live'
    else:
        df_s['Cleaned_Payment_Status'] = 'Pending'
        
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
    
    # Precise extraction targeting "PhoneNo." for Sales Sheet
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
    st.markdown('<div class="main-title">Sparta Executive Management Ledger</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Real-time workspace sync for digital campaigns, lead distribution nodes and conversion performance matrices</div>', unsafe_allow_html=True)

    tab_leads, tab_sales, tab_conversion = st.tabs([
        "📊 Leads Quality Breakdown", 
        "💰 Sales Verification Tracker", 
        "🔄 Leads Conversion Status"
    ])
    
    df_l_filtered = df_leads.copy()
    
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

        if selected_source != "All Sources":
            df_l_filtered = df_l_filtered[df_l_filtered['Mapped_Source'] == selected_source]
        if selected_lead_month != "All Months":
            df_l_filtered = df_l_filtered[df_l_filtered['Month_Display'] == selected_lead_month]

        l_quality_counts = df_l_filtered['Cleaned_Quality_Status'].value_counts().to_dict()
        l_total = len(df_l_filtered)
        l_app = l_quality_counts.get('Approved', 0)
        l_rej = l_quality_counts.get('Rejected', 0)
        l_pen = l_quality_counts.get('Pending', 0)

        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f'<div class="metric-box"><div class="metric-label">Total Allocated</div><div class="metric-number">{l_total:,}</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="metric-box"><div class="metric-label">🟢 Approved</div><div class="metric-number" style="color:#16a34a;">{l_app:,}</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="metric-box"><div class="metric-label">🔴 Rejected</div><div class="metric-number" style="color:#dc2626;">{l_rej:,}</div></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="metric-box"><div class="metric-label">🟡 Pending Threshold</div><div class="metric-number" style="color:#ca8a04;">{l_pen:,}</div></div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)

        col_l_table, col_l_chart = st.columns([4, 5], gap="large")
        
        with col_l_table:
            st.markdown('<div class="section-header">Branch Distribution Matrix</div>', unsafe_allow_html=True)
            if not df_l_filtered.empty:
                raw_l_lb = df_l_filtered.groupby('Agent').agg(
                    Total_Leads=('Agent', 'count'),
                    Approved=('Cleaned_Quality_Status', lambda x: (x == 'Approved').sum()),
                    Rejected=('Cleaned_Quality_Status', lambda x: (x == 'Rejected').sum()),
                    Pending=('Cleaned_Quality_Status', lambda x: (x == 'Pending').sum())
                ).reset_index().sort_values(by='Total_Leads', ascending=False)
                
                l_leaderboard = pd.DataFrame()
                l_leaderboard['Agent'] = raw_l_lb['Agent']
                l_leaderboard['Total_Leads'] = raw_l_lb['Total_Leads']
                
                l_leaderboard['Approved'] = raw_l_lb.apply(lambda r: f"{r['Approved']} ({(r['Approved']/r['Total_Leads'])*100:.1f}%)" if r['Approved'] > 0 else "-", axis=1)
                l_leaderboard['Rejected'] = raw_l_lb.apply(lambda r: f"{r['Rejected']} ({(r['Rejected']/r['Total_Leads'])*100:.1f}%)" if r['Rejected'] > 0 else "-", axis=1)
                l_leaderboard['Pending'] = raw_l_lb.apply(lambda r: f"{r['Pending']} ({(r['Pending']/r['Total_Leads'])*100:.1f}%)" if r['Pending'] > 0 else "-", axis=1)
                
                tot_l_sum = raw_l_lb['Total_Leads'].sum()
                tot_l_app = raw_l_lb['Approved'].sum()
                tot_l_rej = raw_l_lb['Rejected'].sum()
                tot_l_pen = raw_l_lb['Pending'].sum()
                
                l_total_row = pd.DataFrame([{
                    'Agent': 'TOTAL', 'Total_Leads': tot_l_sum,
                    'Approved': f"{tot_l_app} ({(tot_l_app/tot_l_sum)*100:.1f}%)" if tot_l_app > 0 else "-",
                    'Rejected': f"{tot_l_rej} ({(tot_l_rej/tot_l_sum)*100:.1f}%)" if tot_l_rej > 0 else "-",
                    'Pending': f"{tot_l_pen} ({(tot_l_pen/tot_l_sum)*100:.1f}%)" if tot_l_pen > 0 else "-"
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
            st.markdown('<div class="section-header">Allocation Quality Trend Lines</div>', unsafe_allow_html=True)
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
            selected_sales_month = st.selectbox("Sales Processing Window", ["All Months"] + valid_sales_months, key="sales_mth_filter")

        df_s_filtered = df_sales.copy()
        if selected_sales_month != "All Months":
            df_s_filtered = df_s_filtered[df_s_filtered['Month_Display'] == selected_sales_month]

        # Calculate sales status values
        s_status_counts = df_s_filtered['Cleaned_Payment_Status'].value_counts().to_dict()
        s_total = len(df_s_filtered)
        s_live = s_status_counts.get('Live', 0)
        s_canc = s_status_counts.get('Cancelled', 0)
        s_pend = s_status_counts.get('Pending', 0)

        sc1, sc2, sc3, sc4 = st.columns(4)
        sc1.markdown(f'<div class="metric-box"><div class="metric-label">Total Logged Sales</div><div class="metric-number">{s_total:,}</div></div>', unsafe_allow_html=True)
        sc2.markdown(f'<div class="metric-box"><div class="metric-label">🟢 Live (Accepted)</div><div class="metric-number" style="color:#16a34a;">{s_live:,}</div></div>', unsafe_allow_html=True)
        sc3.markdown(f'<div class="metric-box"><div class="metric-label">🔴 Cancelled</div><div class="metric-number" style="color:#dc2626;">{s_canc:,}</div></div>', unsafe_allow_html=True)
        sc4.markdown(f'<div class="metric-box"><div class="metric-label">🟡 Pending Review</div><div class="metric-number" style="color:#ca8a04;">{s_pend:,}</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col_s_table, col_s_chart = st.columns([4, 5], gap="large")
        
        with col_s_table:
            st.markdown('<div class="section-header">Agent Processing Performance Matrix</div>', unsafe_allow_html=True)
            if not df_s_filtered.empty:
                raw_s_lb = df_s_filtered.groupby('Agent').agg(
                    Total_Sales=('Agent', 'count'),
                    Live=('Cleaned_Payment_Status', lambda x: (x == 'Live').sum()),
                    Cancelled=('Cleaned_Payment_Status', lambda x: (x == 'Cancelled').sum()),
                    Pending=('Cleaned_Payment_Status', lambda x: (x == 'Pending').sum())
                ).reset_index().sort_values(by='Total_Sales', ascending=False)
                
                s_leaderboard = pd.DataFrame()
                s_leaderboard['Agent'] = raw_s_lb['Agent']
                s_leaderboard['Total_Sales'] = raw_s_lb['Total_Sales']
                
                s_leaderboard['Live'] = raw_s_lb.apply(lambda r: f"{r['Live']} ({(r['Live']/r['Total_Sales'])*100:.1f}%)" if r['Live'] > 0 else "-", axis=1)
                s_leaderboard['Cancelled'] = raw_s_lb.apply(lambda r: f"{r['Cancelled']} ({(r['Cancelled']/r['Total_Sales'])*100:.1f}%)" if r['Cancelled'] > 0 else "-", axis=1)
                s_leaderboard['Pending'] = raw_s_lb.apply(lambda r: f"{r['Pending']} ({(r['Pending']/r['Total_Sales'])*100:.1f}%)" if r['Pending'] > 0 else "-", axis=1)
                
                tot_s_sum = raw_s_lb['Total_Sales'].sum()
                tot_s_live = raw_s_lb['Live'].sum()
                tot_s_canc = raw_s_lb['Cancelled'].sum()
                tot_s_pend = raw_s_lb['Pending'].sum()
                
                s_total_row = pd.DataFrame([{
                    'Agent': 'TOTAL', 'Total_Sales': tot_s_sum,
                    'Live': f"{tot_s_live} ({(tot_s_live/tot_s_sum)*100:.1f}%)" if tot_s_live > 0 else "-",
                    'Cancelled': f"{tot_s_canc} ({(tot_s_canc/tot_s_sum)*100:.1f}%)" if tot_s_canc > 0 else "-",
                    'Pending': f"{tot_s_pend} ({(tot_s_pend/tot_s_sum)*100:.1f}%)" if tot_s_pend > 0 else "-"
                }])
                s_leaderboard = pd.concat([s_leaderboard, s_total_row], ignore_index=True)
            else:
                s_leaderboard = pd.DataFrame(columns=["Agent", "Total_Sales", "Live", "Cancelled", "Pending"])

            st.dataframe(s_leaderboard.reset_index(drop=True), column_config={
                "Agent": st.column_config.TextColumn("Consultant Name"),
                "Total_Sales": st.column_config.NumberColumn("Total Sales", format="%d"),
                "Live": st.column_config.TextColumn("🟢 Live (%)"),
                "Cancelled": st.column_config.TextColumn("🔴 Cancelled (%)"),
                "Pending": st.column_config.TextColumn("🟡 Pending (%)"),
            }, hide_index=True, use_container_width=True, height=400)
            
        with col_s_chart:
            st.markdown('<div class="section-header">Sales Volume Operational Line Trends</div>', unsafe_allow_html=True)
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
    # WORKSPACE TAB 3: LEADS CONVERSION STATUS (Month from Leads Table)
    # ==========================================
    with tab_conversion:
        left_c_filt, right_c_space = st.columns([1, 1])
        with left_c_filt:
            # Dropdown options are generated directly from the LEADS table
            valid_conv_months = sorted(
                [m for m in df_leads['Month_Display'].unique() if pd.notna(m) and m != 'NaT Unknown' and m != 'Unknown'], 
                key=lambda x: pd.to_datetime(x, format='%b %Y')
            )
            selected_conv_month = st.selectbox("Conversion Timeline Window (Lead Month)", ["All Months"] + valid_conv_months, key="conv_mth_filter")

        # Map each clean phone number in the leads table to its designated display month and parse dates
        phone_lead_meta = df_leads.dropna(subset=['Clean_Phone']).drop_duplicates(subset=['Clean_Phone'])
        phone_to_month = dict(zip(phone_lead_meta['Clean_Phone'], phone_lead_meta['Month_Display']))
        phone_to_pmonth = dict(zip(phone_lead_meta['Clean_Phone'], phone_lead_meta['Parsed_Month']))
        phone_to_pdate = dict(zip(phone_lead_meta['Clean_Phone'], phone_lead_meta['Parsed_Date']))
        phone_to_ddisplay = dict(zip(phone_lead_meta['Clean_Phone'], phone_lead_meta['Day_Display']))

        # Prepare matched sales base records
        df_c_filtered = df_sales.copy()
        
        # Apply strict logic: If WlcmStatus is Cancelled, force status to Cancelled even if payment status is Pending (blank)
        if 'WlcmStatus' in df_c_filtered.columns:
            df_c_filtered.loc[
                (df_c_filtered['Cleaned_Payment_Status'] == 'Pending') & 
                (df_c_filtered['WlcmStatus'].astype(str).str.strip().str.title() == 'Cancelled'),
                'Cleaned_Payment_Status'
            ] = 'Cancelled'

        valid_lead_phones = set(phone_to_month.keys()) - {"", "nan"}
        df_c_filtered = df_c_filtered[df_c_filtered['Clean_Phone'].isin(valid_lead_phones)].copy()

        # Inject the baseline timelines derived from the LEADS worksheet records
        df_c_filtered['Lead_Month_Display'] = df_c_filtered['Clean_Phone'].map(phone_to_month)
        df_c_filtered['Lead_Parsed_Month'] = df_c_filtered['Clean_Phone'].map(phone_to_pmonth)
        df_c_filtered['Lead_Parsed_Date'] = df_c_filtered['Clean_Phone'].map(phone_to_pdate)
        df_c_filtered['Lead_Day_Display'] = df_c_filtered['Clean_Phone'].map(phone_to_ddisplay)

        # Apply the timeline block filter based on the newly attached Lead Month values
        if selected_conv_month != "All Months":
            df_c_filtered = df_c_filtered[df_c_filtered['Lead_Month_Display'] == selected_conv_month]

        # Calculate tracking KPIs for matched subsets
        c_status_counts = df_c_filtered['Cleaned_Payment_Status'].value_counts().to_dict()
        c_total = len(df_c_filtered)
        c_live = c_status_counts.get('Live', 0)
        c_canc = c_status_counts.get('Cancelled', 0)
        c_pend = c_status_counts.get('Pending', 0)

        cc1, cc2, cc3, cc4 = st.columns(4)
        cc1.markdown(f'<div class="metric-box"><div class="metric-label">Total Converted Leads</div><div class="metric-number">{c_total:,}</div></div>', unsafe_allow_html=True)
        cc2.markdown(f'<div class="metric-box"><div class="metric-label">🟢 Live (Accepted)</div><div class="metric-number" style="color:#16a34a;">{c_live:,}</div></div>', unsafe_allow_html=True)
        cc3.markdown(f'<div class="metric-box"><div class="metric-label">🔴 Cancelled</div><div class="metric-number" style="color:#dc2626;">{c_canc:,}</div></div>', unsafe_allow_html=True)
        cc4.markdown(f'<div class="metric-box"><div class="metric-label">🟡 Pending Conversion</div><div class="metric-number" style="color:#ca8a04;">{c_pend:,}</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col_c_table, col_c_chart = st.columns([4, 5], gap="large")
        
        with col_c_table:
            st.markdown('<div class="section-header">Conversion Efficiency Ledger</div>', unsafe_allow_html=True)
            if not df_c_filtered.empty:
                raw_c_lb = df_c_filtered.groupby('Agent').agg(
                    Total_Sales=('Agent', 'count'),
                    Live=('Cleaned_Payment_Status', lambda x: (x == 'Live').sum()),
                    Cancelled=('Cleaned_Payment_Status', lambda x: (x == 'Cancelled').sum()),
                    Pending=('Cleaned_Payment_Status', lambda x: (x == 'Pending').sum())
                ).reset_index().sort_values(by='Total_Sales', ascending=False)
                
                c_leaderboard = pd.DataFrame()
                c_leaderboard['Agent'] = raw_c_lb['Agent']
                c_leaderboard['Total_Sales'] = raw_c_lb['Total_Sales']
                
                c_leaderboard['Live'] = raw_c_lb.apply(lambda r: f"{r['Live']} ({(r['Live']/r['Total_Sales'])*100:.1f}%)" if r['Live'] > 0 else "-", axis=1)
                c_leaderboard['Cancelled'] = raw_c_lb.apply(lambda r: f"{r['Cancelled']} ({(r['Cancelled']/r['Total_Sales'])*100:.1f}%)" if r['Cancelled'] > 0 else "-", axis=1)
                c_leaderboard['Pending'] = raw_c_lb.apply(lambda r: f"{r['Pending']} ({(r['Pending']/r['Total_Sales'])*100:.1f}%)" if r['Pending'] > 0 else "-", axis=1)
                
                tot_c_sum = raw_c_lb['Total_Sales'].sum()
                tot_c_live = raw_c_lb['Live'].sum()
                tot_c_canc = raw_c_lb['Cancelled'].sum()
                tot_c_pend = raw_c_lb['Pending'].sum()
                
                c_total_row = pd.DataFrame([{
                    'Agent': 'TOTAL', 'Total_Sales': tot_c_sum,
                    'Live': f"{tot_c_live} ({(tot_c_live/tot_c_sum)*100:.1f}%)" if tot_c_live > 0 else "-",
                    'Cancelled': f"{tot_c_canc} ({(tot_c_canc/tot_c_sum)*100:.1f}%)" if tot_c_canc > 0 else "-",
                    'Pending': f"{tot_c_pend} ({(tot_c_pend/tot_c_sum)*100:.1f}%)" if tot_c_pend > 0 else "-"
                }])
                c_leaderboard = pd.concat([c_leaderboard, c_total_row], ignore_index=True)
            else:
                c_leaderboard = pd.DataFrame(columns=["Agent", "Total_Sales", "Live", "Cancelled", "Pending"])

            st.dataframe(c_leaderboard.reset_index(drop=True), column_config={
                "Agent": st.column_config.TextColumn("Consultant Name"),
                "Total_Sales": st.column_config.NumberColumn("Total Sales", format="%d"),
                "Live": st.column_config.TextColumn("🟢 Live (%)"),
                "Cancelled": st.column_config.TextColumn("🔴 Cancelled (%)"),
                "Pending": st.column_config.TextColumn("🟡 Pending (%)"),
            }, hide_index=True, use_container_width=True, height=400)
            
        with col_c_chart:
            st.markdown('<div class="section-header">Cross-Matched Lead Velocity Trends</div>', unsafe_allow_html=True)
            if not df_c_filtered.empty:
                # Use Lead baseline dates for line charts to synchronize the view completely
                if selected_conv_month != "All Months":
                    c_trend_df = df_c_filtered.groupby(['Lead_Parsed_Date', 'Lead_Day_Display', 'Cleaned_Payment_Status']).size().reset_index(name='Volume').sort_values('Lead_Parsed_Date')
                    cx_col, cx_lbl = 'Lead_Day_Display', 'Date (Lead Timeline)'
                else:
                    c_trend_df = df_c_filtered.groupby(['Lead_Parsed_Month', 'Lead_Month_Display', 'Cleaned_Payment_Status']).size().reset_index(name='Volume').sort_values('Lead_Parsed_Month')
                    cx_col, cx_lbl = 'Lead_Month_Display', 'Month Block (Lead Timeline)'
                
                fig_c = px.line(trend_df, x=cx_col, y='Volume', color='Cleaned_Payment_Status',
                                labels={cx_col: cx_lbl, 'Volume': 'Sales Volume', 'Cleaned_Payment_Status': 'Status'},
                                color_discrete_map={'Live': '#16a34a', 'Cancelled': '#dc2626', 'Pending': '#ca8a04'}, markers=True)
                fig_c.update_layout(paper_bgcolor='#ffffff', plot_bgcolor='#ffffff', font=dict(family="Inter, sans-serif", size=11),
                                    xaxis=dict(showgrid=False, linecolor='#cbd5e1'), yaxis=dict(showgrid=True, gridcolor='#f1f5f9', title=None),
                                    legend=dict(title=None, orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), height=380, margin=dict(l=15, r=15, t=10, b=10))
                st.plotly_chart(fig_c, use_container_width=True, config={'displayModeBar': False})
            else:
                st.info("No converted lead phone numbers found for this timeline slice.")
