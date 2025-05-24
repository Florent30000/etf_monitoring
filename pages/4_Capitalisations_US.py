import streamlit as st
from bq_utils_streamlit import get_bigquery_client

# Configuration de la page (dans app.py)
st.set_page_config(page_title="Dashboard ETF", layout="wide")

client = get_bigquery_client()

# Pages importées
from sections.st_section_R1VL import run as run_R1VL
from sections.st_section_XDEW import run as run_XDEW
from sections.st_section_XD9U import run as run_XD9U
from sections.st_section_RTW0 import run as run_RTW0
from sections.st_section_SXR8 import run as run_SXR8


# Créer un menu de navigation dans la barre latérale (sans les pages qui apparaissent automatiquement)
page = st.sidebar.radio(
    "Sélectionner un ETF à afficher",
    ["MSCI USA", "SP500", "SP500 Equal weight", "Largest 1000 US CAP (en EUR)",  "Small cap US"]
)

# Lancer la fonction appropriée en fonction de la sélection
if page == "MSCI USA":
    run_XD9U()
elif page == "SP500":
    run_SXR8()
elif page == "SP500 Equal weight":
    run_XDEW()
elif page == "Largest 1000 US CAP (en EUR)":
    run_R1VL()
elif page == "Small cap US":
    run_RTW0()
