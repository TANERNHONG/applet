import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(
    page_title="Strategy analyser",
    page_icon=":chart_with_upwards_trend:"
)

file = st.file_uploader("Pick a file.")

try:
    df = pd.read_excel(file)

    @st.cache_data
    def convert_for_download(df):
        return df.to_csv().encode("utf-8")

    datetime_stamp = f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"

    if st.button("Process files."):
        csv = convert_for_download(df)
        st.download_button(
            label="Download output as CSV.",
            data=csv,
            file_name=f'processed_report_{datetime_stamp}.csv',
            on_click="ignore",
            type="primary",
            mime='text/csv',
            icon=":material/download:",
        )

except Exception:
    st.warning("The file uploaded is not readable. Try again.")