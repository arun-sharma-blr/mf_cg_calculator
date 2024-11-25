import pandas as pd
import streamlit as st
from utils.calculations import calculate_capital_gains

def calculate_fifo_redemption(df, redeem_amount, latest_nav, grandfather_date, tax_rate_short, tax_rate_long, holding_period_months, ltcg_threshold):
    redeemed_units = []
    remaining_amount = redeem_amount

    # Check if the DataFrame is valid
    if df.empty or 'Units Purchased' not in df.columns:
        st.write("DataFrame is empty or missing required columns.")
        return pd.DataFrame()

    # Sort transactions by date (FIFO)
    df = df.sort_values(by='Date of Purchase')

    # Debugging: Show initial conditions
    #st.write(f"Total Redeem Amount: ₹{redeem_amount}")
    #st.write(f"Latest NAV: ₹{latest_nav:.2f}")
    #st.write(f"Total Value of All Units: ₹{df['Units Purchased'].sum() * latest_nav:.2f}")

    # Loop through each row in the DataFrame to process redemptions
    for index, row in df.iterrows():
        if remaining_amount <= 0:
            break

        # Calculate the value of the available units at the current NAV
        available_units_value = row['Units Purchased'] * latest_nav

        if available_units_value <= remaining_amount:
            # Redeem all units in this row
            redeemed_row = row.copy()
            redeemed_row['current_value'] = available_units_value
            redeemed_row['profit'] = redeemed_row['current_value'] - redeemed_row['cost_price']
            redeemed_units.append(redeemed_row)

            remaining_amount -= available_units_value
        else:
            # Partially redeem units from this row
            units_to_redeem = remaining_amount / latest_nav
            proportion = units_to_redeem / row['Units Purchased']

            # Create a copy of the row and adjust for partial redemption
            redeemed_row = row.copy()
            redeemed_row['Units Purchased'] = units_to_redeem
            redeemed_row['current_value'] = units_to_redeem * latest_nav
            redeemed_row['cost_price'] = row['cost_price'] * proportion
            redeemed_row['profit'] = redeemed_row['current_value'] - redeemed_row['cost_price']
            redeemed_units.append(redeemed_row)

            remaining_amount = 0

    # Convert redeemed units to a DataFrame
    redeemed_df = pd.DataFrame(redeemed_units)

    # Check if any units were redeemed
    if redeemed_df.empty:
        st.write("No units were redeemed.")
        return pd.DataFrame()

    # Apply the updated capital gains logic on the redeemed DataFrame
    redeemed_df = calculate_capital_gains(
        redeemed_df, latest_nav, grandfather_date, tax_rate_short, tax_rate_long, holding_period_months, ltcg_threshold
    )

    # Debug: Show the final redeemed DataFrame
    #st.write("Final Redeemed DataFrame after applying capital gains:")
    #st.dataframe(redeemed_df)

    return redeemed_df
