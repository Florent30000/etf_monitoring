import streamlit as st
from sections.st_podium import run as run_podium

st.set_page_config(page_title="Classement ETF", layout="wide")
run_podium()