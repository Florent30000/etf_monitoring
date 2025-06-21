import streamlit as st
from bq_utils_streamlit import get_bigquery_client

# Configuration de la page (dans app.py)
st.set_page_config(page_title="Dashboard ETF", layout="wide")

client = get_bigquery_client()

# Pages importées
from sections.st_section_XGDU import run as run_XGDU
from sections.st_section_BITC import run as run_BITC

# Créer un menu de navigation dans la barre latérale (sans les pages qui apparaissent automatiquement)
page = st.sidebar.radio(
    "Sélectionner un ETF à afficher",
    ["Physical Gold", "Physical Bitcoin"]
)

# Lancer la fonction appropriée en fonction de la sélection
if page == "Physical Gold":
    run_XGDU()
elif page == "Physical Bitcoin":
    run_BITC()