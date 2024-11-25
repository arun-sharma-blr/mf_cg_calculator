import streamlit as st

def display_summary(df, redemption_type):
    """
    Display the detailed capital gains table with appropriate formatting.
    
    Parameters:
        df (DataFrame): The DataFrame containing the detailed capital gains data.
        redemption_type (str): The type of redemption (e.g., "Full Redemption" or "Partial Redemption").
    """
    # Add a descriptive header for the table based on the redemption type
    st.subheader(f"Detailed Capital Gains Table - {redemption_type}")

    # Format the DataFrame
    df = df.copy()
    df.index = df.index + 1  # Start the index from 1
    df['Date of Purchase'] = df['Date of Purchase'].dt.strftime('%d-%m-%Y')  # Format the date

    # Drop unnecessary columns
    columns_to_display = [
        'Date of Purchase',
        'Units Purchased',
        'NAV at Purchase',
        'Grandfathered NAV',
        'NAV Used for Cost Calculation',
        'Current NAV',
        'current_value',
        'cost_price',
        'profit',
        'Holding Period (days)', 
        'Gain Type'
    ]
    df = df[columns_to_display]

    # Rename columns for better readability
    df.rename(columns={
        'Date of Purchase': 'SIP Date',
        'Units Purchased': 'Units',
        'NAV at Purchase': 'NAV (Purchase)',
        'Grandfathered NAV': 'Grandfathered NAV',
        'NAV Used for Cost Calculation': 'NAV (Cost)',
        'Current NAV': 'NAV (Current)',
        'current_value': 'Current Value',
        'cost_price': 'Cost Price',
        'profit': 'Profit',
        'Holding Period (days)': 'Days Held',
        'Gain Type': 'Gain Type'
    }, inplace=True)

    # Display the formatted DataFrame
    st.dataframe(df)



#def display_summary(df):
    # st.write("Detailed Capital Gains Table:")
#    st.dataframe(df)

#def display_redeemed_summary(df):
    # Use the correct column names based on calculations.py
#    if 'current_value' in df.columns and 'profit' in df.columns and 'tax' in df.columns:
#        total_value = df['current_value'].sum()
#        total_profit = df['profit'].sum()
#        total_tax = df['tax'].sum()

        # st.write("Full Redemption Summary:")
#        st.write(f"**Total Redeemed Value**: ₹{total_value:.2f}")
#        st.write(f"**Total Profit**: ₹{total_profit:.2f}")
#        st.write(f"**Total Tax Liability**: ₹{total_tax:.2f}")
#    else:
#        st.error("Required columns are missing in the DataFrame.")