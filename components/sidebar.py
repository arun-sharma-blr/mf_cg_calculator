import streamlit as st
import pandas as pd

def get_user_inputs():
    st.sidebar.header("Mutual Fund Inputs")
    
    # SIP Inputs
    sip_start_month = st.sidebar.selectbox("Select SIP Start Month:", list(range(1, 13)), index=0)
    sip_start_year = st.sidebar.number_input("Enter SIP Start Year:", min_value=2000, max_value=pd.Timestamp.now().year, value=2020)
    sip_end_month = st.sidebar.selectbox("Select SIP End Month:", list(range(1, 13)), index=pd.Timestamp.now().month - 1)
    sip_end_year = st.sidebar.number_input("Enter SIP End Year:", min_value=2000, max_value=pd.Timestamp.now().year, value=pd.Timestamp.now().year)
    sip_date = st.sidebar.number_input("Enter the SIP date (1-28):", min_value=1, max_value=28, value=1)
    sip_amount = st.sidebar.number_input("Enter SIP amount (₹):", min_value=1, value=1000)

    # Tax Rates
    stcg_rate = st.sidebar.number_input("Short-Term Capital Gains Tax Rate (%):", min_value=0.0, value=20.0)
    ltcg_rate = st.sidebar.number_input("Long-Term Capital Gains Tax Rate (%):", min_value=0.0, value=12.5)

    # Grandfathering Date
    grandfather_date = st.sidebar.date_input("Select the Grandfathering Date:", value=pd.to_datetime("2018-01-31"))

    # NAV URLs
    historical_nav_url = st.sidebar.text_input("Enter Historical NAV URL:")
    latest_nav_url = st.sidebar.text_input("Enter Latest NAV URL:")

    # Redemption options
    redemption_option = st.sidebar.radio("Select Redemption Option:", ["Full Redemption", "Partial Redemption"])
    partial_redeem_amount = st.sidebar.number_input("Enter amount to redeem (₹):", min_value=1) if redemption_option == "Partial Redemption" else None

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
