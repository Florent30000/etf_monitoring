import streamlit as st
from bq_utils_streamlit import get_bigquery_client

# Configuration de la page (dans app.py)
st.set_page_config(page_title="Dashboard ETF", layout="wide")

client = get_bigquery_client()

# Pages importées
from sections.st_section_EUNK import run as run_EUNK
from sections.st_section_XXSC import run as run_XXSC


# Créer un menu de navigation dans la barre latérale (sans les pages qui apparaissent automatiquement)
page = st.sidebar.radio(
    "Sélectionner un ETF à afficher",
    ["MSCI Europe Large cap", "MSCI Europe Small Cap"]
)

# Lancer la fonction appropriée en fonction de la sélection
if page == "MSCI Europe Large cap":
    run_EUNK()
elif page == "MSCI Europe Small Cap":
    run_XXSC()
