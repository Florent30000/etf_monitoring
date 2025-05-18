import streamlit as st
from bq_utils_streamlit import get_bigquery_client

# Configuration de la page (dans app.py)
st.set_page_config(page_title="Dashboard ETF", layout="wide")

client = get_bigquery_client()

# Pages importées
from sections.st_portefeuille_perso import run as run_perso

# Créer un menu de navigation dans la barre latérale (sans les pages qui apparaissent automatiquement)
page = st.sidebar.radio(
    "Sélectionner un ETF à afficher",
    ["Portefeuille personnalisé","Obligations US LT", "Actions US", "Or physique", "Obligations US CT"]
)

# Lancer la comparaison
run_perso()
