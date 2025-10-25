import streamlit as st
import pandas as pd
import numpy as np
import datetime

st.set_page_config(
    page_title="Strategy analyser",
    page_icon=":chart_with_upwards_trend:"
)

df = st.file_uploader("Pick a file.")

datetime_stamp = f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"

st.download_button(
    label="Download data as CSV.",
    data=df,
    file_name=f'processed_report_{datetime_stamp}.csv',
    mime='text/csv'
)