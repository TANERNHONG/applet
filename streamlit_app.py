import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(
    page_title="Strategy analyser",
    page_icon=":chart_with_upwards_trend:"
)

df = st.file_uploader("Pick a file.")

@st.cache_data
def convert_for_download(df):
    return df.to_csv().encode("utf-8")

csv = convert_for_download(df)

datetime_stamp = f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"

if st.button("Process files."):
    st.download_button(
        label="Download output as CSV.",
        data=df,
        file_name=f'processed_report_{datetime_stamp}.csv',
        on_click="ignore",
        type="primary",
        mime='text/csv',
        icon=":material/download:",
    )