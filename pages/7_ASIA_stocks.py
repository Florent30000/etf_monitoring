import streamlit as st
from bq_utils_streamlit import get_bigquery_client

# Configuration de la page (dans app.py)
st.set_page_config(page_title="Dashboard ETF", layout="wide")

client = get_bigquery_client()

# Pages importées
from sections.st_section_ETLK import run as run_ETLK
from sections.st_section_CEBL import run as run_CEBL


# Créer un menu de navigation dans la barre latérale (sans les pages qui apparaissent automatiquement)
page = st.sidebar.radio(
    "Sélectionner un ETF à afficher",
    ["MSCI Asia Large cap", "MSCI Asia Emerging markets"]
)

# Lancer la fonction appropriée en fonction de la sélection
if page == "MSCI Asia Large cap":
    run_ETLK()
elif page == "MSCI Asia Emerging markets":
    run_CEBL()
