import streamlit as st
from sections.st_section_usd_eur import run as run_usd_eur

st.set_page_config(page_title="Parité USD-EUR", layout="wide")
run_usd_eur()