import requests
import pandas as pd
import streamlit as st

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

