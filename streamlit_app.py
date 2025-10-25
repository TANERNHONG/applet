import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Strategy analyser",
    page_icon=":chart_with_upwards_trend:"
)

file = st.file_uploader("Pick a file.")