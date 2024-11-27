import streamlit as st
import pandas as pd
from components.display import display_summary
from utils.nav_fetcher import fetch_nav_data
from utils.calculations import calculate_capital_gains
from utils.fifo import calculate_fifo_redemption
import requests

st.set_page_config(page_title="Capital Gains Calculator for Equity Mutual Fund SIP", layout="wide")

# Sidebar content
with st.sidebar:
    st.header("Tax Parameters")
    stcg_rate = st.number_input("Short-Term Capital Gains Tax Rate (%)", min_value=0.0, value=20.0, step=0.1)
    ltcg_rate = st.number_input("Long-Term Capital Gains Tax Rate (%)", min_value=0.0, value=12.5, step=0.1)
    holding_period_months = st.number_input("Holding Period (months)", min_value=1, value=12, step=1)
    ltcg_threshold = st.number_input("LTCG Threshold (₹)", min_value=0, value=125000, step=1000)
    #grandfather_date = st.date_input("Grandfathering Date (yyyy/mm/dd)", value=pd.to_datetime("2018-01-31"))
    grandfather_date = pd.to_datetime(
    st.date_input("Grandfathering Date (yyyy/mm/dd)", value=pd.to_datetime("2018-01-31")),
    dayfirst=True
    )

# Title in the main window
st.title("Capital Gains Calculator - Equity Mutual Fund SIP")

# URL Inputs in the Main Window
st.subheader("Enter Mutual Fund NAV URLs - Get them at [https://www.mfapi.in/](https://www.mfapi.in/)")
#st.markdown("Get your MF URLs at [https://www.mfapi.in/](https://www.mfapi.in/)")
historical_nav_url = st.text_input("Enter Historical NAV URL")
latest_nav_url = st.text_input("Enter Latest NAV URL")

# Input SIP details in the main window
if historical_nav_url and latest_nav_url:
    st.subheader("Enter SIP Details")
    col1, col2 = st.columns([1, 1])
    with col1:
        sip_start_month = st.selectbox("Start Month", list(range(1, 13)), format_func=lambda x: pd.to_datetime(f"2000-{x:02d}-01").strftime('%b'))
    with col2:
        sip_start_year = st.number_input("Start Year", min_value=2000, max_value=pd.Timestamp.now().year, value=2020)

    col3, col4 = st.columns([1, 1])
    with col3:
        sip_end_month = st.selectbox("End Month", list(range(1, 13)), format_func=lambda x: pd.to_datetime(f"2000-{x:02d}-01").strftime('%b'))
    with col4:
        sip_end_year = st.number_input("End Year", min_value=2000, max_value=pd.Timestamp.now().year, value=pd.Timestamp.now().year)

    col5, col6 = st.columns([1, 1])
    with col5:
        sip_date = st.number_input("SIP Date (1-28)", min_value=1, max_value=28, value=1)
    with col6:
        sip_amount = st.number_input("SIP Amount (₹)", min_value=1, value=1000)

    st.subheader("Select Redemption Option")
    #redemption_option = st.radio("Select Redemption Option:", ["Full Redemption", "Partial Redemption"])
    #redemption_option = st.radio("",["Full Redemption", "Partial Redemption"])
    redemption_option = st.radio(
    label="",  # Empty label
    options=["Full Redemption", "Partial Redemption"],
    label_visibility="collapsed"  # Hides the label
    )
    partial_redeem_amount = st.number_input("Amount to Redeem (₹)", min_value=1) if redemption_option == "Partial Redemption" else None

    if st.button("Calculate Gains"):
        historical_nav_df = fetch_nav_data(historical_nav_url)
        latest_nav_df = fetch_nav_data(latest_nav_url)

        if historical_nav_df is None or latest_nav_df is None:
            st.error("Failed to fetch NAV data. Please check the URLs.")
        else:
            historical_nav_df['date'] = pd.to_datetime(historical_nav_df['date'], format='%d-%m-%Y', errors='coerce', dayfirst=True)
            historical_nav_df = historical_nav_df.sort_values(by='date')

            latest_nav = float(latest_nav_df.iloc[0]['nav'])
            response = requests.get(latest_nav_url)
            if response.status_code == 200:
                latest_nav_data = response.json()
                scheme_name = latest_nav_data.get('meta', {}).get('scheme_name', 'Unknown Scheme Name')
            else:
                scheme_name = 'Unknown Scheme Name'
            current_date = pd.Timestamp.now()

            investments = []
            # Calculate Start and End Dates based on user inputs
            start_date = pd.to_datetime(f"{sip_start_year}-{sip_start_month:02d}-{sip_date:02d}")
            end_date = pd.to_datetime(f"{sip_end_year}-{sip_end_month:02d}-{sip_date:02d}")

            # Generate SIP transaction dates
            transaction_dates = pd.date_range(start=start_date, end=end_date, freq='MS').to_series()

            # Adjust all transaction dates to the correct SIP date
            transaction_dates = transaction_dates.apply(lambda x: x.replace(day=sip_date)).tolist()


            for transaction_date in transaction_dates:
                nav_on_date = historical_nav_df[historical_nav_df['date'] == pd.Timestamp(transaction_date)]

                if nav_on_date.empty:
                    nav_on_date = historical_nav_df[historical_nav_df['date'] > pd.Timestamp(transaction_date)].head(1)

                if nav_on_date.empty:
                    st.warning(f"No NAV data available for date: {transaction_date}. Skipping this transaction.")
                    continue

                nav_price = float(nav_on_date['nav'].iloc[0])
                units = sip_amount / nav_price

                cost_nav = nav_price
                grandfathered_nav = None
                if transaction_date <= pd.Timestamp(grandfather_date):
                    grandfathered_nav_df = historical_nav_df[historical_nav_df['date'] == grandfather_date]
                    if not grandfathered_nav_df.empty:
                        grandfathered_nav = float(grandfathered_nav_df['nav'].iloc[0])
                        cost_nav = grandfathered_nav

                # Debugging information to verify the logic
                #st.write(f"Transaction Date: {transaction_date}")
                #st.write(f"Grandfathering Date: {grandfather_date}")
                #st.write(f"Grandfathered NAV DataFrame: {grandfathered_nav_df}")
                #st.write(f"Grandfathered NAV: {grandfathered_nav}")
                #st.write(f"Cost NAV: {cost_nav}")

                investments.append({
                    'Date of Purchase': transaction_date,
                    'Units Purchased': units,
                    'NAV at Purchase': nav_price,
                    'Grandfathered NAV': grandfathered_nav,
                    'NAV Used for Cost Calculation': cost_nav,
                    'Current NAV': latest_nav,
                    'current_value': units * latest_nav,
                    'cost_price': units * cost_nav,
                    'profit': (units * latest_nav) - (units * cost_nav),
                    'Holding Period (days)': (current_date - transaction_date).days,
                    'Gain Type': 'Short-term' if (current_date - transaction_date).days < holding_period_months * 30 else 'Long-term',
                })

            investments_df = pd.DataFrame(investments)

            if investments_df.empty:
                st.error("No investments found. Please check your inputs.")
            else:
                # Total Holdings
                total_units = investments_df['Units Purchased'].sum()
                total_holding_value = total_units * latest_nav

                # Redemption Handling
                if redemption_option == "Partial Redemption":
                    if partial_redeem_amount > total_holding_value:
                        st.error(f"The amount entered ({partial_redeem_amount:.2f}) exceeds the total holdings ({total_holding_value:.2f}). Please enter a valid amount.")
                        st.stop()
                    else:
                        redeemed_df = calculate_fifo_redemption(
                            investments_df,
                            partial_redeem_amount,
                            latest_nav,
                            grandfather_date,
                            stcg_rate,
                            ltcg_rate,
                            holding_period_months,
                            ltcg_threshold
                        )
                        detailed_df = redeemed_df
                else:
                    detailed_df = investments_df

                # Gains Calculations
                long_term_gains = detailed_df.loc[detailed_df['Gain Type'] == 'Long-term', 'profit'].sum()
                short_term_gains = detailed_df.loc[detailed_df['Gain Type'] == 'Short-term', 'profit'].sum()
                taxable_ltcg = max(0, long_term_gains - ltcg_threshold)
                ltcg_tax = taxable_ltcg * (ltcg_rate / 100)
                stcg_tax = short_term_gains * (stcg_rate / 100)
                total_tax = ltcg_tax + stcg_tax

                # Display Summary
                st.subheader("Summary")
                st.write(f"**Scheme Name**: {scheme_name}")
                st.write(f"**Total Units**: {total_units:.2f}")
                st.write(f"**Latest NAV**: ₹{latest_nav:.2f}")
                st.write(f"**Total Holding Value**: ₹{total_holding_value:.2f}")
                if redemption_option == "Partial Redemption":
                    redeemed_units = partial_redeem_amount / latest_nav
                    st.write(f"**Redemption Amount**: ₹{partial_redeem_amount:.2f}")
                    st.write(f"**Redemption Units**: {redeemed_units:.2f}")
                st.write(f"**Long Term Capital Gains**: ₹{long_term_gains:.2f}")
                st.write(f"**Taxable LTCG (above threshold)**: ₹{taxable_ltcg:.2f}")
                st.write(f"**Short Term Capital Gains**: ₹{short_term_gains:.2f}")
                st.write(f"**LTCG Tax**: ₹{ltcg_tax:.2f}")
                st.write(f"**STCG Tax**: ₹{stcg_tax:.2f}")
                st.write(f"**Total Tax**: ₹{total_tax:.2f}")

                # Round all numeric columns
                detailed_df = detailed_df.round(2)
                # Display Detailed Table
                #st.subheader("Detailed Capital Gains Table")
                display_summary(detailed_df, redemption_option)
