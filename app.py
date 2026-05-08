"""MZ Verifier - Professional Edition"""

import streamlit as st
import pandas as pd
import time
from verifier import (
    check_syntax, check_disposable, check_role_based, 
    check_mx, check_smtp, verify_bulk,
    clean_email, is_obviously_invalid, deduplicate_emails
)
from verifier.smtp_check import is_major_provider


st.set_page_config(
    page_title="MZ Verfier", 
    page_icon="✉", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Custom CSS
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* Professional Header */
    .pro-header {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        color: white;
        position: relative;
        overflow: hidden;
    }
    
    .pro-header::before {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 300px;
        height: 100%;
        background: radial-gradient(circle, rgba(16,185,129,0.15) 0%, transparent 70%);
    }
    
    .pro-header h1 {
        color: white !important;
        margin: 0 !important;
        font-size: 28px !important;
        font-weight: 600 !important;
        letter-spacing: -0.5px;
    }
    
    .pro-header .subtitle {
        color: #94A3B8 !important;
        margin: 6px 0 0 0 !important;
        font-size: 14px !important;
    }
    
    .pro-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: #6EE7B7;
        padding: 6px 14px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 500;
        margin-right: 8px;
    }
    
    .pro-badge-blue {
        background: rgba(59, 130, 246, 0.15);
        border-color: rgba(59, 130, 246, 0.3);
        color: #93C5FD;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #10B981;
        color: white;
        border: none;
        font-weight: 500;
        padding: 0.6rem 1.75rem;
        border-radius: 8px;
        transition: all 0.2s;
        font-size: 14px;
    }
    
    .stButton > button:hover {
        background-color: #059669;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25);
    }
    
    .stDownloadButton > button {
        background-color: #0F172A;
        color: white;
        border-radius: 8px;
        font-weight: 500;
    }
    
    .stDownloadButton > button:hover {
        background-color: #1E293B;
    }
    
    /* Metric cards */
    [data-testid="stMetric"] {
        background: white;
        padding: 1.25rem;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        transition: all 0.2s;
    }
    
    [data-testid="stMetric"]:hover {
        border-color: #10B981;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    
    [data-testid="stMetricLabel"] {
        color: #64748B !important;
        font-size: 11px !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        font-weight: 500;
    }
    
    [data-testid="stMetricValue"] {
        color: #0F172A !important;
        font-weight: 600 !important;
        font-size: 28px !important;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 12px !important;
    }
    
    /* Alert messages */
    .stSuccess {
        background-color: #F0FDF4 !important;
        border-left: 4px solid #10B981 !important;
        border-radius: 8px !important;
    }
    
    .stWarning {
        background-color: #FFFBEB !important;
        border-left: 4px solid #F59E0B !important;
        border-radius: 8px !important;
    }
    
    .stError {
        background-color: #FEF2F2 !important;
        border-left: 4px solid #EF4444 !important;
        border-radius: 8px !important;
    }
    
    .stInfo {
        background-color: #EFF6FF !important;
        border-left: 4px solid #3B82F6 !important;
        border-radius: 8px !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: #F1F5F9;
        padding: 6px;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 6px;
        padding: 10px 24px;
        font-weight: 500;
        color: #64748B;
        font-size: 14px;
    }
    
    .stTabs [aria-selected="true"] {
        background: #0F172A !important;
        color: white !important;
    }
    
    /* Sidebar - Clean Professional */
    section[data-testid="stSidebar"] {
        background: #0F172A;
        border-right: none;
    }
    
    section[data-testid="stSidebar"] > div {
        padding-top: 1rem;
    }
    
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: white !important;
    }
    
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] li {
        color: #CBD5E1 !important;
    }
    
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #CBD5E1;
    }
    
    section[data-testid="stSidebar"] hr {
        border-color: #334155 !important;
        margin: 1rem 0;
    }
    
    /* Sidebar custom items */
    .sidebar-section-title {
        color: #64748B;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.75rem;
        padding-left: 0.5rem;
    }
    
    .sidebar-item {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 8px 10px;
        margin-bottom: 4px;
        border-radius: 6px;
        color: #CBD5E1;
        font-size: 13px;
        transition: all 0.15s;
    }
    
    .sidebar-item-icon {
        width: 20px;
        height: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(16, 185, 129, 0.15);
        border-radius: 4px;
        color: #10B981;
        font-size: 11px;
        font-weight: 600;
    }
    
    .sidebar-item:hover {
        background: rgba(255,255,255,0.05);
    }
    
    .sidebar-item-text {
        flex: 1;
    }
    
    .sidebar-item-name {
        color: white;
        font-weight: 500;
        font-size: 13px;
    }
    
    .sidebar-item-desc {
        color: #64748B;
        font-size: 11px;
        margin-top: 2px;
    }
    
    .sidebar-stat {
        background: rgba(255,255,255,0.05);
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 8px;
    }
    
    .sidebar-stat-label {
        color: #64748B;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }
    
    .sidebar-stat-value {
        color: white;
        font-size: 18px;
        font-weight: 600;
    }
    
    /* Progress bar */
    .stProgress > div > div > div > div {
        background-color: #10B981;
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        padding: 12px 16px;
        font-size: 14px;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #10B981;
        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
    }
    
    /* File uploader */
    [data-testid="stFileUploaderDropzone"] {
        background: #F8FAFC;
        border: 2px dashed #CBD5E1;
        border-radius: 12px;
        padding: 2rem;
    }
    
    /* Section headers */
    .section-title {
        color: #0F172A;
        font-size: 16px;
        font-weight: 600;
        margin: 1.5rem 0 0.75rem 0;
        padding-bottom: 8px;
        border-bottom: 1px solid #E2E8F0;
    }
    
    /* Result card animations */
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(-8px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .result-card {
        animation: slideIn 0.3s ease-out;
    }
</style>
""", unsafe_allow_html=True)

# Professional Header (cleaner, less emojis)
st.markdown("""
<div class="pro-header">
    <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem; position: relative; z-index: 1;">
        <div style="display: flex; align-items: center; gap: 16px;">
            <div style="width: 56px; height: 56px; background: #10B981; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 28px;">
                ✉
            </div>
            <div>
                <h1>MZ Verifier</h1>
                <p class="subtitle">Verify · Validate · Deliver — Built for lead generation</p>
            </div>
        </div>
        <div style="display: flex; gap: 8px; flex-wrap: wrap;">
            <span class="pro-badge">▲ Parallel Processing</span>
            <span class="pro-badge pro-badge-blue">◆ 8 Verification Layers</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


def verify_email_full(email: str) -> dict:
    original_email = email
    email = clean_email(email)
    
    result = {
        "email": email if email else original_email,
        "original_email": original_email,
        "status": "valid",
        "quality": "good",
        "result": "ok",
        "syntax_valid": False,
        "is_disposable": False,
        "is_role_based": False,
        "has_mx": False,
        "smtp_deliverable": None,
        "reason": "",
        "checks_passed": []
    }
    
    is_invalid, invalid_reason = is_obviously_invalid(email)
    if is_invalid:
        result["status"] = "invalid"
        result["quality"] = "bad"
        result["result"] = "invalid"
        result["reason"] = f"Format: {invalid_reason}"
        return result
    
    syntax = check_syntax(email)
    result["syntax_valid"] = syntax["valid"]
    
    if not syntax["valid"]:
        result["status"] = "invalid"
        result["quality"] = "bad"
        result["result"] = "invalid"
        result["reason"] = f"Syntax: {syntax['reason']}"
        return result
    
    result["checks_passed"].append("Syntax")
    
    disposable = check_disposable(email)
    result["is_disposable"] = disposable["is_disposable"]
    
    if disposable["is_disposable"]:
        result["status"] = "invalid"
        result["quality"] = "bad"
        result["result"] = "disposable"
        result["reason"] = "Disposable email provider"
        return result
    
    result["checks_passed"].append("Not disposable")
    
    if is_major_provider(email):
        result["has_mx"] = True
        result["status"] = "risky"
        result["quality"] = "risky"
        result["result"] = "catch_all"
        result["reason"] = "Major provider (Gmail/Yahoo/Outlook)"
        result["checks_passed"].append("Major provider detected")
        
        role = check_role_based(email)
        result["is_role_based"] = role["is_role_based"]
        return result
    
    mx = check_mx(email)
    result["has_mx"] = mx["has_mx"]
    
    if not mx["has_mx"]:
        result["status"] = "invalid"
        result["quality"] = "bad"
        result["result"] = "invalid"
        result["reason"] = f"MX: {mx['reason']}"
        return result
    
    result["checks_passed"].append("MX exists")
    
    smtp = check_smtp(email, mx.get("mx_records", []))
    result["smtp_deliverable"] = smtp["deliverable"]
    result["smtp_reason"] = smtp.get("reason", "")
    
    if smtp["deliverable"] is False:
        result["status"] = "invalid"
        result["quality"] = "bad"
        result["result"] = "invalid"
        result["reason"] = f"SMTP: {smtp['reason']}"
        return result
    elif smtp["deliverable"] is None:
        result["status"] = "risky"
        result["quality"] = "risky"
        result["result"] = "unknown"
        result["reason"] = f"Uncertain: {smtp['reason']}"
        result["checks_passed"].append(f"SMTP: {smtp['reason']}")
    else:
        result["checks_passed"].append("SMTP verified")
    
    role = check_role_based(email)
    result["is_role_based"] = role["is_role_based"]
    
    if role["is_role_based"]:
        if result["status"] == "valid":
            result["status"] = "risky"
            result["quality"] = "risky"
            result["reason"] = "Role-based email"
        return result
    
    if result["status"] == "valid":
        result["reason"] = "All verifications passed"
    return result


def find_email_column(df):
    variations = [
        "email", "Email", "EMAIL", "e-mail", "E-mail", "E-Mail",
        "email_address", "EmailAddress", "Email Address",
        "mail", "Mail", "email1", "primary_email"
    ]
    
    for var in variations:
        if var in df.columns:
            return var
    
    for col in df.columns:
        col_lower = col.lower().strip()
        if "email" in col_lower or col_lower == "mail":
            return col
    
    return None


# Tabs
tab1, tab2 = st.tabs(["Single Email", "Bulk Upload"])

with tab1:
    st.markdown("### Verify Single Email")
    st.caption("Enter an email address to run all 8 verification checks")
    
    col1, col2 = st.columns([4, 1])
    with col1:
        email_input = st.text_input(
            "Email", 
            placeholder="example@domain.com",
            label_visibility="collapsed"
        )
    with col2:
        verify_btn = st.button("Verify Now", type="primary", use_container_width=True)
    
    if verify_btn:
        if not email_input or not email_input.strip():
            st.warning("Please enter an email address")
        else:
            with st.spinner("Running verification..."):
                start_time = time.time()
                result = verify_email_full(email_input)
                elapsed = time.time() - start_time
            
            if result["original_email"] != result["email"]:
                st.info(f"Email cleaned: `{result['original_email']}` → `{result['email']}`")
            
            # Result card
            if result["status"] == "valid":
                st.markdown(f"""
                <div class="result-card" style="background: linear-gradient(135deg, #ECFDF5, #D1FAE5); border-left: 4px solid #10B981; padding: 1.25rem 1.5rem; border-radius: 12px; margin: 1rem 0;">
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <div>
                            <div style="font-size: 18px; font-weight: 600; color: #047857;">Email is Valid</div>
                            <div style="font-size: 13px; color: #047857; margin-top: 4px;">{result['reason']}</div>
                        </div>
                        <div style="text-align: right;">
                            <span style="background: #10B981; color: white; padding: 6px 14px; border-radius: 8px; font-size: 12px; font-weight: 500;">{result['quality']} / {result['result']}</span>
                            <div style="font-size: 12px; color: #047857; margin-top: 6px;">{elapsed:.2f}s</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            elif result["status"] == "risky":
                st.markdown(f"""
                <div class="result-card" style="background: linear-gradient(135deg, #FFFBEB, #FEF3C7); border-left: 4px solid #F59E0B; padding: 1.25rem 1.5rem; border-radius: 12px; margin: 1rem 0;">
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <div>
                            <div style="font-size: 18px; font-weight: 600; color: #92400E;">Email is Risky</div>
                            <div style="font-size: 13px; color: #92400E; margin-top: 4px;">{result['reason']}</div>
                        </div>
                        <div style="text-align: right;">
                            <span style="background: #F59E0B; color: white; padding: 6px 14px; border-radius: 8px; font-size: 12px; font-weight: 500;">{result['quality']} / {result['result']}</span>
                            <div style="font-size: 12px; color: #92400E; margin-top: 6px;">{elapsed:.2f}s</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="result-card" style="background: linear-gradient(135deg, #FEF2F2, #FEE2E2); border-left: 4px solid #EF4444; padding: 1.25rem 1.5rem; border-radius: 12px; margin: 1rem 0;">
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <div>
                            <div style="font-size: 18px; font-weight: 600; color: #991B1B;">Email is Invalid</div>
                            <div style="font-size: 13px; color: #991B1B; margin-top: 4px;">{result['reason']}</div>
                        </div>
                        <div style="text-align: right;">
                            <span style="background: #EF4444; color: white; padding: 6px 14px; border-radius: 8px; font-size: 12px; font-weight: 500;">{result['quality']} / {result['result']}</span>
                            <div style="font-size: 12px; color: #991B1B; margin-top: 6px;">{elapsed:.2f}s</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            if result["checks_passed"]:
                st.info("**Checks completed:** " + " → ".join(result["checks_passed"]))
            
            # Verification cards (cleaner, no emoji icons)
            st.markdown("##### Verification Checks")
            cols = st.columns(5)
            checks = [
                ("Syntax", result["syntax_valid"]),
                ("MX Record", result["has_mx"]),
                ("SMTP", result["smtp_deliverable"] is True),
                ("Disposable", not result["is_disposable"]),
                ("Role-based", not result["is_role_based"]),
            ]
            
            for i, (label, passed) in enumerate(checks):
                with cols[i]:
                    if passed:
                        bg_color = "#ECFDF5"
                        border_color = "#10B981"
                        text_color = "#047857"
                        symbol = "PASS"
                    elif result["smtp_deliverable"] is None and label == "SMTP":
                        bg_color = "#FFFBEB"
                        border_color = "#F59E0B"
                        text_color = "#92400E"
                        symbol = "N/A"
                    else:
                        bg_color = "#FEF2F2"
                        border_color = "#EF4444"
                        text_color = "#991B1B"
                        symbol = "FAIL"
                    
                    st.markdown(f"""
                    <div style="background: {bg_color}; border: 1px solid {border_color}; padding: 14px 12px; border-radius: 10px; text-align: center;">
                        <div style="font-size: 11px; color: {text_color}; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">{label}</div>
                        <div style="font-size: 13px; color: {text_color}; font-weight: 700; letter-spacing: 1px;">{symbol}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            with st.expander("Technical Details"):
                st.json(result)

with tab2:
    st.markdown("### Bulk Email Verification")
    st.caption("Upload a CSV file to verify multiple emails with parallel processing")
    
    with st.expander("Advanced Settings", expanded=False):
        col_set1, col_set2, col_set3 = st.columns(3)
        with col_set1:
            concurrent_setting = st.slider(
                "Concurrent verifications",
                min_value=5, max_value=30, value=15
            )
        with col_set2:
            batch_size_setting = st.slider(
                "Batch size",
                min_value=20, max_value=100, value=50
            )
        with col_set3:
            remove_dupes = st.checkbox(
                "Remove duplicates", 
                value=True
            )
    
    uploaded_file = st.file_uploader("Choose CSV file", type=["csv"])
    
    if uploaded_file is not None:
        try:
            try:
                df = pd.read_csv(uploaded_file)
            except UnicodeDecodeError:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding='latin-1')
            
            if df.empty:
                st.error("CSV file is empty")
            else:
                email_col = find_email_column(df)
                
                if email_col is None:
                    st.error("Could not find email column")
                    st.write("**Available columns:**", list(df.columns))
                else:
                    total_rows = len(df)
                    st.success(f"Found **{total_rows:,}** rows in column: `{email_col}`")
                    
                    raw_emails = df[email_col].astype(str).tolist()
                    cleaned_list = [clean_email(e) for e in raw_emails]
                    non_empty = [e for e in cleaned_list if e]
                    empty_count = total_rows - len(non_empty)
                    
                    if remove_dupes and non_empty:
                        unique_emails, dupe_count, _ = deduplicate_emails(non_empty)
                    else:
                        unique_emails = non_empty
                        dupe_count = 0
                    
                    st.markdown('<div class="section-title">Pre-processing Summary</div>', unsafe_allow_html=True)
                    pre_col1, pre_col2, pre_col3, pre_col4 = st.columns(4)
                    pre_col1.metric("Total Rows", f"{total_rows:,}")
                    pre_col2.metric("Empty / Null", f"{empty_count:,}")
                    pre_col3.metric("Duplicates", f"{dupe_count:,}")
                    pre_col4.metric("To Verify", f"{len(unique_emails):,}")
                    
                    if len(unique_emails) == 0:
                        st.error("No valid emails after cleaning!")
                    else:
                        if len(unique_emails) > 50000:
                            st.warning(f"Limiting to first 50,000 emails")
                            unique_emails = unique_emails[:50000]
                        
                        total_emails = len(unique_emails)
                        estimated_seconds = total_emails * 0.3
                        estimated_minutes = estimated_seconds / 60
                        st.info(f"Estimated time: **{estimated_minutes:.1f} minutes**")
                        
                        with st.expander("Email Preview"):
                            preview_df = pd.DataFrame({"email": unique_emails[:10]})
                            st.dataframe(preview_df, use_container_width=True)
                        
                        if st.button("Start Verification", type="primary", use_container_width=True):
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            time_text = st.empty()
                            
                            start_time = time.time()
                            
                            def update_progress(completed, total):
                                progress = completed / total
                                progress_bar.progress(progress)
                                
                                elapsed = time.time() - start_time
                                if completed > 0:
                                    avg_time = elapsed / completed
                                    remaining = (total - completed) * avg_time
                                    eta_min = remaining / 60
                                    
                                    status_text.markdown(f"**Processing:** {completed:,} / {total:,} ({progress*100:.1f}%)")
                                    time_text.markdown(f"ETA: **{eta_min:.1f} min** | Speed: **{avg_time:.2f}s/email** | Elapsed: **{elapsed/60:.1f} min**")
                            
                            try:
                                results = verify_bulk(
                                    unique_emails,
                                    progress_callback=update_progress,
                                    batch_size=batch_size_setting,
                                    max_concurrent=concurrent_setting
                                )
                                
                                total_time = time.time() - start_time
                                results_df = pd.DataFrame(results)
                                avg_speed = total_time / total_emails
                                
                                if "original_email" in results_df.columns:
                                    results_df = results_df.drop(columns=["original_email"])
                                
                                st.markdown(f"""
                                <div style="background: linear-gradient(135deg, #ECFDF5, #D1FAE5); border-left: 4px solid #10B981; padding: 1.25rem 1.5rem; border-radius: 12px; margin: 1rem 0;">
                                    <div style="font-size: 16px; font-weight: 600; color: #047857;">Verification Complete</div>
                                    <div style="font-size: 13px; color: #047857; margin-top: 4px;">{total_emails:,} emails processed in {total_time/60:.2f} minutes ({avg_speed:.2f}s avg)</div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                st.markdown('<div class="section-title">Results Summary</div>', unsafe_allow_html=True)
                                col1, col2, col3, col4 = st.columns(4)
                                
                                valid = (results_df["status"] == "valid").sum()
                                risky = (results_df["status"] == "risky").sum()
                                invalid = (results_df["status"] == "invalid").sum()
                                
                                col1.metric("Valid", f"{valid:,}", f"{valid/total_emails*100:.1f}%")
                                col2.metric("Risky", f"{risky:,}", f"{risky/total_emails*100:.1f}%")
                                col3.metric("Invalid", f"{invalid:,}", f"{invalid/total_emails*100:.1f}%")
                                col4.metric("Total", f"{total_emails:,}")
                                
                                st.markdown('<div class="section-title">Detailed Breakdown</div>', unsafe_allow_html=True)
                                d1, d2, d3, d4, d5 = st.columns(5)
                                
                                ok_count = (results_df["result"] == "ok").sum()
                                catch_all = (results_df["result"] == "catch_all").sum()
                                invalid_count = (results_df["result"] == "invalid").sum()
                                disposable = (results_df["result"] == "disposable").sum()
                                unknown = (results_df["result"] == "unknown").sum()
                                
                                d1.metric("OK", f"{ok_count:,}")
                                d2.metric("Catch-all", f"{catch_all:,}")
                                d3.metric("Invalid", f"{invalid_count:,}")
                                d4.metric("Disposable", f"{disposable:,}")
                                d5.metric("Unknown", f"{unknown:,}")
                                
                                st.markdown('<div class="section-title">Top Domains</div>', unsafe_allow_html=True)
                                results_df['domain'] = results_df['email'].str.split('@').str[-1]
                                top_domains = results_df['domain'].value_counts().head(10)
                                
                                if not top_domains.empty:
                                    domain_df = pd.DataFrame({
                                        'Domain': top_domains.index,
                                        'Count': top_domains.values
                                    })
                                    st.dataframe(domain_df, use_container_width=True, height=300)
                                
                                results_df_download = results_df.drop(columns=['domain'])
                                
                                csv = results_df_download.to_csv(index=False)
                                st.download_button(
                                    "Download Results CSV",
                                    data=csv,
                                    file_name="verified_emails.csv",
                                    mime="text/csv",
                                    use_container_width=True
                                )
                                
                                st.markdown('<div class="section-title">Results Preview</div>', unsafe_allow_html=True)
                                
                                filter_opt = st.selectbox(
                                    "Filter results", 
                                    ["All", "Valid only", "Risky only", "Invalid only",
                                     "OK", "Catch-all", "Disposable", "Unknown"]
                                )
                                
                                if filter_opt == "Valid only":
                                    display_df = results_df_download[results_df_download["status"] == "valid"]
                                elif filter_opt == "Risky only":
                                    display_df = results_df_download[results_df_download["status"] == "risky"]
                                elif filter_opt == "Invalid only":
                                    display_df = results_df_download[results_df_download["status"] == "invalid"]
                                elif filter_opt == "OK":
                                    display_df = results_df_download[results_df_download["result"] == "ok"]
                                elif filter_opt == "Catch-all":
                                    display_df = results_df_download[results_df_download["result"] == "catch_all"]
                                elif filter_opt == "Disposable":
                                    display_df = results_df_download[results_df_download["result"] == "disposable"]
                                elif filter_opt == "Unknown":
                                    display_df = results_df_download[results_df_download["result"] == "unknown"]
                                else:
                                    display_df = results_df_download
                                
                                st.dataframe(display_df, use_container_width=True, height=400)
                            
                            except Exception as e:
                                st.error(f"Verification error: {str(e)}")
        
        except pd.errors.EmptyDataError:
            st.error("CSV file is empty")
        except pd.errors.ParserError as e:
            st.error(f"CSV parsing error: {str(e)}")
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")


# PROFESSIONAL SIDEBAR (No emojis, clean look)
with st.sidebar:
    # Logo / Brand
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 12px; padding: 8px 4px 20px 4px; border-bottom: 1px solid #334155; margin-bottom: 1.5rem;">
        <div style="width: 36px; height: 36px; background: #10B981; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; font-size: 18px;">✉</div>
        <div>
            <div style="color: white; font-weight: 600; font-size: 15px;">MZ Verifier</div>
            <div style="color: #64748B; font-size: 11px;">v1.0.0</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Status
    st.markdown('<div class="sidebar-section-title">System Status</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="sidebar-stat">
        <div class="sidebar-stat-label">Engine</div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <div style="width: 8px; height: 8px; background: #10B981; border-radius: 50%; box-shadow: 0 0 8px #10B981;"></div>
            <span style="color: white; font-weight: 500; font-size: 13px;">Active</span>
        </div>
    </div>
    <div class="sidebar-stat">
        <div class="sidebar-stat-label">Mode</div>
        <div class="sidebar-stat-value" style="font-size: 14px;">Parallel</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Verification Layers (clean, no emojis)
    st.markdown('<div class="sidebar-section-title">Verification Layers</div>', unsafe_allow_html=True)
    
    layers = [
        ("01", "Email Cleaning", "Normalize input"),
        ("02", "Format Validation", "Quick pre-checks"),
        ("03", "Syntax Check", "RFC 5322 standard"),
        ("04", "Disposable Filter", "Block temp emails"),
        ("05", "Major Provider", "Smart catch-all"),
        ("06", "MX Record", "Domain verification"),
        ("07", "SMTP Verify", "Server-level check"),
        ("08", "Role Detection", "Identify role emails"),
    ]
    
    for num, name, desc in layers:
        st.markdown(f"""
        <div class="sidebar-item">
            <div class="sidebar-item-icon">{num}</div>
            <div class="sidebar-item-text">
                <div class="sidebar-item-name">{name}</div>
                <div class="sidebar-item-desc">{desc}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Result Labels
    st.markdown('<div class="sidebar-section-title">Result Labels</div>', unsafe_allow_html=True)
    
    labels = [
        ("ok", "Verified valid", "#10B981"),
        ("catch_all", "Domain accepts all", "#F59E0B"),
        ("invalid", "Bounced/rejected", "#EF4444"),
        ("disposable", "Temporary email", "#EF4444"),
        ("unknown", "Could not verify", "#64748B"),
    ]
    
    for label, desc, color in labels:
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 10px; padding: 6px 8px; margin-bottom: 4px;">
            <div style="width: 8px; height: 8px; background: {color}; border-radius: 50%;"></div>
            <div style="flex: 1;">
                <div style="color: white; font-size: 12px; font-weight: 500;">{label}</div>
                <div style="color: #64748B; font-size: 10px;">{desc}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("""
    <div style="padding: 8px; text-align: center;">
        <div style="color: #64748B; font-size: 11px;">Built for lead generation</div>
        <div style="color: #475569; font-size: 10px; margin-top: 4px;">MZ Verifier · 2026</div>
    </div>
    """, unsafe_allow_html=True)