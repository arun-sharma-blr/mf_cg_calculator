import streamlit as st
import pandas as pd

def get_user_inputs():
    st.sidebar.header("Mutual Fund Inputs")
    
    # Mapping of month names to numbers
    month_mapping = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
    }
    month_list = list(month_mapping.keys())

    # SIP Start Date - Month and Year on the same line
    col1, col2 = st.sidebar.columns([1, 1])
    with col1:
        sip_start_month_name = st.selectbox("Start Month", month_list, index=0)
    with col2:
        sip_start_year = st.number_input("Start Year", min_value=2000, max_value=pd.Timestamp.now().year, value=2020, step=1)
    
    # Convert selected start month name to a number
    sip_start_month = month_mapping[sip_start_month_name]

    # SIP End Date - Month and Year on the same line
    col3, col4 = st.sidebar.columns([1, 1])
    with col3:
        sip_end_month_name = st.selectbox("End Month", month_list, index=pd.Timestamp.now().month - 1)
    with col4:
        sip_end_year = st.number_input("End Year", min_value=2000, max_value=pd.Timestamp.now().year, value=pd.Timestamp.now().year, step=1)
    
    # Convert selected end month name to a number
    sip_end_month = month_mapping[sip_end_month_name]

    # SIP Date and Amount
    sip_date = st.sidebar.number_input("SIP Date (1-28)", min_value=1, max_value=28, value=1)
    sip_amount = st.sidebar.number_input("SIP Amount (₹)", min_value=1, value=1000)

    # Tax Rates
    stcg_rate = st.sidebar.number_input("Short-Term Capital Gains Tax Rate (%)", min_value=0.0, value=20.0, step=0.1)
    ltcg_rate = st.sidebar.number_input("Long-Term Capital Gains Tax Rate (%)", min_value=0.0, value=12.5, step=0.1)

    # Grandfathering Date
    grandfather_date = st.sidebar.date_input("Select the Grandfathering Date:", value=pd.to_datetime("2018-01-31"))

    # NAV URLs
    st.sidebar.header("NAV Data URLs")
    historical_nav_url = st.sidebar.text_input("Enter Historical NAV URL:")
    latest_nav_url = st.sidebar.text_input("Enter Latest NAV URL:")

    # Redemption options
    redemption_option = st.sidebar.radio("Select Redemption Option:", ["Full Redemption", "Partial Redemption"])
    partial_redeem_amount = st.sidebar.number_input("Amount to Redeem (₹)", min_value=1) if redemption_option == "Partial Redemption" else None

    return {
        "sip_start_month": sip_start_month,
        "sip_start_year": sip_start_year,
        "sip_end_month": sip_end_month,
        "sip_end_year": sip_end_year,
        "sip_date": sip_date,
        "sip_amount": sip_amount,
        "stcg_rate": stcg_rate,
        "ltcg_rate": ltcg_rate,
        "grandfather_date": pd.Timestamp(grandfather_date),
        "historical_nav_url": historical_nav_url,
        "latest_nav_url": latest_nav_url,
        "redemption_option": redemption_option,
        "partial_redeem_amount": partial_redeem_amount
    }
