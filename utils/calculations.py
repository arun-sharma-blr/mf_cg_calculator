import pandas as pd
import numpy as np

def calculate_capital_gains(df, latest_nav, grandfather_date, tax_rate_short, tax_rate_long, holding_period_months, ltcg_threshold):
    # Calculate current value using the latest NAV
    df['current_value'] = df['Units Purchased'] * latest_nav

    # Calculate cost price using either the grandfathered NAV or the purchase NAV
    df['cost_price'] = df.apply(
        lambda row: row['Units Purchased'] * (
            row['Grandfathered NAV']
            if row['Date of Purchase'] <= pd.Timestamp(grandfather_date) and pd.notnull(row['Grandfathered NAV'])
            else row['NAV at Purchase']
        ),
        axis=1
    )

    # Calculate profit
    df['profit'] = df['current_value'] - df['cost_price']

    # Calculate holding period in days
    df['holding_period'] = (pd.Timestamp.now() - df['Date of Purchase']).dt.days

    # Convert holding period to months for comparison
    holding_period_days_threshold = holding_period_months * 30  # Approximate days in a month

    # Determine the type of gain (short-term or long-term)
    df['gain_type'] = np.where(df['holding_period'] < holding_period_days_threshold, 'Short-term', 'Long-term')

    # Calculate tax
    def calculate_tax(row):
        if row['gain_type'] == 'Short-term':
            # Apply STCG tax directly on the profit
            return row['profit'] * (tax_rate_short / 100)
        else:
            # Calculate LTCG taxable amount after threshold
            taxable_ltcg = max(0, row['profit'] - ltcg_threshold)
            return taxable_ltcg * (tax_rate_long / 100) if taxable_ltcg > 0 else 0

    # Apply the tax calculation function
    df['tax'] = df.apply(calculate_tax, axis=1)

    return df
