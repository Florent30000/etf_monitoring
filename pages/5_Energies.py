import streamlit as st
from bq_utils_streamlit import get_bigquery_client

# Configuration de la page (dans app.py)
st.set_page_config(page_title="Dashboard ETF", layout="wide")

client = get_bigquery_client()

# Pages importées
from sections.st_section_NUKL import run as run_NUKL
from sections.st_section_XDW0 import run as run_XDW0
from sections.st_section_DELG import run as run_DELG

# Créer un menu de navigation dans la barre latérale (sans les pages qui apparaissent automatiquement)
page = st.sidebar.radio(
    "Sélectionner un ETF à afficher",
    ["Nucléaire Monde","Fossiles Monde", "Renouvelable Monde"]
)

# Lancer la fonction appropriée en fonction de la sélection
if page == "Nucléaire Monde":
    run_NUKL()
elif page == "Fossiles Monde":
    run_XDW0()
elif page == "Renouvelable Monde":
    run_DELG()