import streamlit as st
import pandas as pd

def get_user_inputs():
    st.sidebar.header("Tax Parameters")
    
    # Tax Rates
    #st.sidebar.subheader("Tax Rates")
    stcg_rate = st.sidebar.number_input("Short-Term Capital Gains Tax Rate (%)", min_value=0.0, value=20.0, step=0.1)
    ltcg_rate = st.sidebar.number_input("Long-Term Capital Gains Tax Rate (%)", min_value=0.0, value=12.5, step=0.1)

    # Holding Period and LTCG Threshold
    #st.sidebar.subheader("Additional Parameters")
    holding_period_months = st.sidebar.number_input("Holding Period (months)", min_value=1, value=12, step=1)
    ltcg_threshold = st.sidebar.number_input("LTCG Threshold (₹)", min_value=0, value=125000, step=1000)

    # Grandfathering Date
    st.sidebar.subheader("Grandfathering Date")
    grandfather_date = st.sidebar.date_input("Select the Grandfathering Date:", value=pd.to_datetime("2018-01-31"))

    return {
        "stcg_rate": stcg_rate,
        "ltcg_rate": ltcg_rate,
        "holding_period_months": holding_period_months,
        "ltcg_threshold": ltcg_threshold,
        "grandfather_date": pd.Timestamp(grandfather_date)
    }
