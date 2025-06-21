import streamlit as st
from bq_utils_streamlit import get_bigquery_client

# Configuration de la page (dans app.py)
st.set_page_config(page_title="Dashboard ETF", layout="wide")

client = get_bigquery_client()

# Pages importées
from sections.st_section_DTLA import run as run_DTLA
from sections.st_section_SXR8 import run as run_SXR8
from sections.st_section_XGDU import run as run_XGDU
from sections.st_section_ZPR1 import run as run_ZPR1
from sections.st_Harry_Browne import run as run_compare

# Créer un menu de navigation dans la barre latérale (sans les pages qui apparaissent automatiquement)
page = st.sidebar.radio(
    "Sélectionner un ETF à afficher",
    ["Portefeuille Harry Browne","USD T-Bond 20 yrs (€)", "S&P 500", "Physical Gold", "USD T-Bill 1-3 Month"]
)

# Lancer la fonction appropriée en fonction de la sélection
if page == "Portefeuille Harry Browne":
    run_compare()
elif page == "USD T-Bond 20 yrs (€)":
    run_DTLA()
elif page == "S&P 500":
    run_SXR8()
elif page == "Physical Gold":
    run_XGDU()
elif page == "USD T-Bill 1-3 Month":
    run_ZPR1()
