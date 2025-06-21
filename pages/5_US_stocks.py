import streamlit as st
from bq_utils_streamlit import get_bigquery_client

# Configuration de la page (dans app.py)
st.set_page_config(page_title="Dashboard ETF", layout="wide")

client = get_bigquery_client()

# Pages importées
from sections.st_section_RTW0 import run as run_RTW0
from sections.st_section_SXR8 import run as run_SXR8


# Créer un menu de navigation dans la barre latérale (sans les pages qui apparaissent automatiquement)
page = st.sidebar.radio(
    "Sélectionner un ETF à afficher",
    ["S&P 500", "Russel 2000 US"]
)

# Lancer la fonction appropriée en fonction de la sélection
if page == "S&P 500":
    run_SXR8()
elif page == "Russel 2000 US":
    run_RTW0()
