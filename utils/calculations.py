import pandas as pd
import numpy as np

def calculate_capital_gains(df, latest_nav, grandfather_date, tax_rate_short, tax_rate_long):
    # Calculate current value using the latest NAV
    df['current_value'] = df['Units Purchased'] * latest_nav
    
    # Calculate cost price using either the grandfathered NAV or the purchase NAV
    df['cost_price'] = df.apply(
        lambda row: row['Units Purchased'] * (row['Grandfathered NAV'] if row['Date of Purchase'] <= grandfather_date and pd.notnull(row['Grandfathered NAV']) else row['NAV at Purchase']),
        axis=1
    )
    
    # Calculate profit
    df['profit'] = df['current_value'] - df['cost_price']
    
    # Calculate holding period
    df['holding_period'] = (pd.Timestamp.now() - df['Date of Purchase']).dt.days
    
    # Determine the type of gain (short-term or long-term)
    df['gain_type'] = np.where(df['holding_period'] < 365, 'Short-term', 'Long-term')
    
    # Determine the applicable tax rate based on gain type
    df['tax_rate'] = np.where(df['gain_type'] == 'Short-term', tax_rate_short, tax_rate_long)
    
    # Calculate tax based on profit
    df['tax'] = df['profit'] * (df['tax_rate'] / 100)
    
    return df
