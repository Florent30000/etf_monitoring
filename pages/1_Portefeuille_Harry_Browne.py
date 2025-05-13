import streamlit as st
from bq_utils_streamlit import get_bigquery_client

# Configuration de la page (dans app.py)
st.set_page_config(page_title="Dashboard ETF", layout="wide")

client = get_bigquery_client()

# Pages importées
from sections.st_section_DTLA import run as run_DTLA
from sections.st_section_XD9U import run as run_XD9U
from sections.st_section_XGDU import run as run_XGDU
from sections.st_section_ZPR1 import run as run_ZPR1
from sections.st_Harry_Browne import run as run_compare
from sections.st_section_usd_eur import run as run_usd_eur

# Titre du dashboard
st.title("📊 Suivi de performance des ETF")

# Créer un menu de navigation dans la barre latérale (sans les pages qui apparaissent automatiquement)
page = st.sidebar.radio(
    "Sélectionner un ETF à afficher",
    ["Portefeuille Harry Browne","Obligations US LT", "Actions US", "Or physique", "Obligations US CT", "Parité USD-EUR"]
)

# Lancer la fonction appropriée en fonction de la sélection
if page == "Portefeuille Harry Browne":
    run_compare()
elif page == "Obligations US LT":
    run_DTLA()
elif page == "Actions US":
    run_XD9U()
elif page == "Or physique":
    run_XGDU()
elif page == "Obligations US CT":
    run_ZPR1()
elif page == "Parité USD-EUR":
    run_usd_eur()