import streamlit as st
from sections.st_classement import run as run_classement

st.set_page_config(page_title="Classement ETF", layout="wide")
run_classement()