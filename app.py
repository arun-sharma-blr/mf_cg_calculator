import streamlit as st
import pandas as pd
from components.sidebar import get_user_inputs
from components.display import display_summary, display_redeemed_summary
from utils.nav_fetcher import fetch_nav_data
from utils.calculations import calculate_capital_gains
from utils.fifo import calculate_fifo_redemption

st.set_page_config(page_title="Mutual Fund Capital Gains Calculator", layout="wide")
st.title("Mutual Fund Capital Gains Calculator")

# Get user inputs from the sidebar
user_inputs = get_user_inputs()

# Add a button to trigger calculations
if st.button("Calculate Gains"):
    # Fetch NAV data
    historical_nav_df = fetch_nav_data(user_inputs['historical_nav_url'])
    latest_nav_df = fetch_nav_data(user_inputs['latest_nav_url'])

    if historical_nav_df is None or latest_nav_df is None:
        st.error("Failed to fetch NAV data. Please check the URLs.")
    else:
        # Parse dates in historical NAV DataFrame
        historical_nav_df['date'] = pd.to_datetime(historical_nav_df['date'], format='%d-%m-%Y', errors='coerce')
        historical_nav_df = historical_nav_df.sort_values(by='date')

        latest_nav = float(latest_nav_df.iloc[0]['nav'])
        current_date = pd.Timestamp.now()

        # Prepare SIP transactions
        investments = []
        start_date = pd.to_datetime(f"{user_inputs['sip_start_year']}-{user_inputs['sip_start_month']:02d}-{user_inputs['sip_date']:02d}")
        end_date = pd.to_datetime(f"{user_inputs['sip_end_year']}-{user_inputs['sip_end_month']:02d}-{user_inputs['sip_date']:02d}")
        transaction_dates = pd.date_range(start=start_date, end=end_date, freq='MS')

        # Loop through each SIP transaction date and fetch NAV data
        for transaction_date in transaction_dates:
            nav_on_date = historical_nav_df[historical_nav_df['date'] == pd.Timestamp(transaction_date)]

            if nav_on_date.empty:
                nav_on_date = historical_nav_df[historical_nav_df['date'] > pd.Timestamp(transaction_date)].head(1)

            if nav_on_date.empty:
                st.warning(f"No NAV data available for date: {transaction_date}. Skipping this transaction.")
                continue

            nav_price = float(nav_on_date['nav'].iloc[0])
            units = user_inputs['sip_amount'] / nav_price

            cost_nav = nav_price
            grandfathered_nav = None
            if transaction_date <= user_inputs['grandfather_date']:
                grandfathered_nav_df = historical_nav_df[historical_nav_df['date'] == user_inputs['grandfather_date']]
                if not grandfathered_nav_df.empty:
                    grandfathered_nav = float(grandfathered_nav_df['nav'].iloc[0])
                    cost_nav = grandfathered_nav

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
                'Gain Type': 'Short-term' if (current_date - transaction_date).days < 365 else 'Long-term',
                'tax_rate': user_inputs['stcg_rate'] if (current_date - transaction_date).days < 365 else user_inputs['ltcg_rate'],
                'tax': ((units * latest_nav) - (units * cost_nav)) * (user_inputs['stcg_rate'] / 100) if (current_date - transaction_date).days < 365 else ((units * latest_nav) - (units * cost_nav)) * (user_inputs['ltcg_rate'] / 100)
            })

        investments_df = pd.DataFrame(investments)

        if investments_df.empty:
            st.error("No investments found. Please check your inputs.")
        else:
            investments_df = calculate_capital_gains(
                investments_df, latest_nav, user_inputs['grandfather_date'],
                user_inputs['stcg_rate'], user_inputs['ltcg_rate']
            )

            # Display the detailed capital gains table only for Full Redemption
            if user_inputs['redemption_option'] == "Full Redemption":
                st.write("Detailed Capital Gains Table:")
                display_summary(investments_df)
                st.write("Full Redemption Summary:")
                display_redeemed_summary(investments_df)

            # Handle Partial Redemption
            elif user_inputs['redemption_option'] == "Partial Redemption":
                partial_redeem_amount = user_inputs['partial_redeem_amount']
                
                # Check if investments_df has the required columns before proceeding
                required_columns = ['Date of Purchase', 'Units Purchased', 'NAV at Purchase', 
                                    'Grandfathered NAV', 'NAV Used for Cost Calculation', 
                                    'Current NAV', 'current_value', 'cost_price', 'profit', 'tax']
                
                missing_columns = [col for col in required_columns if col not in investments_df.columns]
                if missing_columns:
                    st.error(f"The DataFrame is missing the following columns: {missing_columns}")
                else:
                    # Proceed with FIFO redemption only if DataFrame is properly populated
                    redeemed_df = calculate_fifo_redemption(investments_df, partial_redeem_amount, latest_nav)
                    
                    # Check if any units were redeemed
                    if not redeemed_df.empty:
                        st.write("Redeemed DataFrame after partial redemption:")
                        st.dataframe(redeemed_df)  # Display the DataFrame once

                        # Display the summary for partial redemption
                        total_redeemed_value = redeemed_df['current_value'].sum()
                        total_redeemed_profit = redeemed_df['profit'].sum()
                        total_redeemed_tax = redeemed_df['tax'].sum()

                        st.write("Partial Redemption Summary:")
                        st.write(f"**Total Redeemed Value**: ₹{total_redeemed_value:.2f}")
                        st.write(f"**Total Profit for Partial Redemption**: ₹{total_redeemed_profit:.2f}")
                        st.write(f"**Total Tax Liability for Partial Redemption**: ₹{total_redeemed_tax:.2f}")
                    else:
                        st.error("No units were redeemed. Please check your inputs.")

