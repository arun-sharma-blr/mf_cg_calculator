import streamlit as st

def display_summary(df):
    # st.write("Detailed Capital Gains Table:")
    st.dataframe(df)

def display_redeemed_summary(df):
    # Use the correct column names based on calculations.py
    if 'current_value' in df.columns and 'profit' in df.columns and 'tax' in df.columns:
        total_value = df['current_value'].sum()
        total_profit = df['profit'].sum()
        total_tax = df['tax'].sum()

        # st.write("Full Redemption Summary:")
        st.write(f"**Total Redeemed Value**: ₹{total_value:.2f}")
        st.write(f"**Total Profit**: ₹{total_profit:.2f}")
        st.write(f"**Total Tax Liability**: ₹{total_tax:.2f}")
    else:
        st.error("Required columns are missing in the DataFrame.")

