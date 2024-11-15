import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime

# Set up the Streamlit page
st.set_page_config(page_title="Mutual Fund Capital Gains Calculator", layout="centered")
st.title("Mutual Fund Capital Gains Calculator")
st.write("Calculate your capital gains for investments made through the SIP route.")

# Input fields for SIP schedule
sip_start_month = st.selectbox("Select SIP Start Month:", list(range(1, 13)), index=0)
sip_start_year = st.number_input("Enter SIP Start Year:", min_value=2000, max_value=datetime.now().year, value=2020)

sip_end_month = st.selectbox("Select SIP End Month:", list(range(1, 13)), index=datetime.now().month - 1)
sip_end_year = st.number_input("Enter SIP End Year:", min_value=2000, max_value=datetime.now().year, value=datetime.now().year)

# Restrict SIP date to between 1 and 28
sip_date = st.number_input("Enter the SIP date of the month (1-28):", min_value=1, max_value=28, value=1)
sip_amount = st.number_input("Enter your SIP amount (₹):", min_value=1, value=1000)

# Tax rates and grandfathering details
tax_rate_short = 20.0
tax_rate_long = 12.5
grandfather_date = pd.to_datetime("2018-01-31")

# URLs for NAV data
historical_nav_url = st.text_input("Enter the URL for historical NAV data:")
latest_nav_url = st.text_input("Enter the URL for latest NAV data (default: /latest):")

# Function to fetch NAV data
def fetch_nav_data(url):
    if not url:
        return None
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "SUCCESS":
                return pd.DataFrame(data["data"])
            else:
                st.error("Error in response status.")
        else:
            st.error(f"Failed to fetch data. Status code: {response.status_code}")
    except Exception as e:
        st.error(f"An error occurred: {e}")
    return None

# Function to find the closest available NAV date
def get_closest_nav_date(df, target_date):
    available_dates = df['date']
    future_dates = available_dates[available_dates >= target_date]
    if not future_dates.empty:
        return future_dates.min()
    return None

# Add a button to trigger calculations
if st.button("Calculate Gains"):
    # Ensure URLs are not empty before fetching data
    if not historical_nav_url or not latest_nav_url:
        st.error("Please enter both the historical and latest NAV URLs.")
    else:
        # Fetch historical and latest NAV data
        historical_nav_df = fetch_nav_data(historical_nav_url)
        latest_nav_df = fetch_nav_data(latest_nav_url)

        if historical_nav_df is not None:
            historical_nav_df['date'] = pd.to_datetime(historical_nav_df['date'], format='%d-%m-%Y')
            historical_nav_df['nav'] = historical_nav_df['nav'].astype(float)

            # Get the latest NAV if available
            latest_nav = None
            if latest_nav_df is not None:
                latest_nav = float(latest_nav_df.iloc[0]['nav'])

            # Calculate SIP transactions
            units_purchased = []
            total_invested = 0
            current_date = pd.to_datetime(datetime.now().date())

            # Generate SIP transaction dates
            start_date = pd.to_datetime(f"{sip_start_year}-{sip_start_month:02d}-{sip_date:02d}")
            end_date = pd.to_datetime(f"{sip_end_year}-{sip_end_month:02d}-{sip_date:02d}")

            transaction_dates = pd.date_range(start=start_date, end=end_date, freq='MS')
            transaction_dates = [date.replace(day=sip_date) for date in transaction_dates if date <= current_date]

            for transaction_date in transaction_dates:
                # Get NAV on the exact transaction date
                nav_on_date = historical_nav_df[historical_nav_df['date'] == transaction_date]

                # If no NAV data is available, find the closest future date
                if nav_on_date.empty:
                    closest_date = get_closest_nav_date(historical_nav_df, transaction_date)
                    if closest_date is not None:
                        nav_on_date = historical_nav_df[historical_nav_df['date'] == closest_date]
                    else:
                        st.warning(f"No NAV data found for {transaction_date.strftime('%d-%m-%Y')} or any later dates. Skipping.")
                        continue

                nav_price = float(nav_on_date['nav'].iloc[0])
                units = sip_amount / nav_price
                units_purchased.append({'date': transaction_date, 'nav': nav_price, 'units': units})
                total_invested += sip_amount

            # Convert to DataFrame
            investments_df = pd.DataFrame(units_purchased)
            st.write("SIP Transactions", investments_df)

            # Apply Grandfathering Clause
            investments_df['grandfathered_nav'] = np.where(
                investments_df['date'] <= grandfather_date,
                historical_nav_df[historical_nav_df['date'] == grandfather_date]['nav'].values[0],
                investments_df['nav']
            )

            # Calculate gains
            investments_df['holding_period'] = (current_date - investments_df['date']).dt.days
            investments_df['current_value'] = investments_df['units'] * latest_nav if latest_nav else investments_df['units'] * investments_df['nav']
            investments_df['cost_price'] = investments_df['units'] * investments_df['grandfathered_nav']
            investments_df['profit'] = investments_df['current_value'] - investments_df['cost_price']

            # Short-term and long-term gains classification
            investments_df['gain_type'] = np.where(investments_df['holding_period'] < 365, 'Short-term', 'Long-term')
            investments_df['tax_rate'] = np.where(investments_df['gain_type'] == 'Short-term', tax_rate_short, tax_rate_long)
            investments_df['tax'] = investments_df['profit'] * (investments_df['tax_rate'] / 100)

            st.write("Capital Gains Calculation", investments_df)

            # Display totals
            total_profit = investments_df['profit'].sum()
            total_tax = investments_df['tax'].sum()
            st.write(f"**Total Profit**: ₹{total_profit:.2f}")
            st.write(f"**Total Tax Liability**: ₹{total_tax:.2f}")
        else:
            st.error("Failed to fetch historical NAV data.")
