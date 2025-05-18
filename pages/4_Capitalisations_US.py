import streamlit as st
from bq_utils_streamlit import get_bigquery_client

# Configuration de la page (dans app.py)
st.set_page_config(page_title="Dashboard ETF", layout="wide")

client = get_bigquery_client()

# Pages importées
from sections.st_section_R1VL import run as run_R1VL
from sections.st_section_XDEW import run as run_XDEW
from sections.st_section_XGDU import run as run_XGDU
from sections.st_section_RTW0 import run as run_RTW0
from sections.st_section_SXR8 import run as run_SXR8


# Créer un menu de navigation dans la barre latérale (sans les pages qui apparaissent automatiquement)
page = st.sidebar.radio(
    "Sélectionner un ETF à afficher",
    ["Largest 1000 US CAP (en EUR)","SP500 Equal weight", "Actions US", "Small cap US", "SP500"]
)

# Lancer la fonction appropriée en fonction de la sélection
if page == "Largest 1000 US CAP (en EUR)":
    run_R1VL()
elif page == "SP500 Equal weight":
    run_XDEW()
elif page == "Actions US":
    run_XGDU()
elif page == "Small cap US":
    run_RTW0()
elif page == "SP500":
    run_SXR8()