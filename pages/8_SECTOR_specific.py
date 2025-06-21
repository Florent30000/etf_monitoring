import streamlit as st
from bq_utils_streamlit import get_bigquery_client

# Configuration de la page (dans app.py)
st.set_page_config(page_title="Dashboard ETF", layout="wide")

client = get_bigquery_client()

# Pages importées
from sections.st_section_XDWT import run as run_XDWT
from sections.st_section_XDWH import run as run_XDWH
from sections.st_section_XDWI import run as run_XDWI


# Créer un menu de navigation dans la barre latérale (sans les pages qui apparaissent automatiquement)
page = st.sidebar.radio(
    "Sélectionner un ETF à afficher",
    ["MSCI World IT", "MSCI World Health Care", "MSCI World Industrials"]
)

# Lancer la fonction appropriée en fonction de la sélection
if page == "MSCI World IT":
    run_XDWT()
elif page == "MSCI World Health Care":
    run_XDWH()
elif page == "MSCI World Industrials":
    run_XDWI()