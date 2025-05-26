import streamlit as st
from bq_utils_streamlit import get_bigquery_client

# Configuration de la page (dans app.py)
st.set_page_config(page_title="Dashboard ETF", layout="wide")

client = get_bigquery_client()

# Pages importées
from sections.st_portefeuille_perso import run as run_perso
from sections.st_section_DTLA import run as run_DTLA
from sections.st_section_XD9U import run as run_XD9U
from sections.st_section_XGDU import run as run_XGDU
from sections.st_section_ZPR1 import run as run_ZPR1
from sections.st_section_R1VL import run as run_R1VL
from sections.st_section_XDEW import run as run_XDEW
from sections.st_section_RTW0 import run as run_RTW0
from sections.st_section_SXR8 import run as run_SXR8
from sections.st_section_NUKL import run as run_NUKL
from sections.st_section_XDW0 import run as run_XDW0
from sections.st_section_DELG import run as run_DELG
from sections.st_section_XMLD import run as run_XMLD

# Créer un menu de navigation dans la barre latérale (sans les pages qui apparaissent automatiquement)
page = st.sidebar.radio(
    "Sélectionner un ETF à afficher",
    ["Portefeuille personnalisé","Oblig. US LT (€)", "MSCI USA", "Or physique", "Oblig. US CT",
     "SP500", "SP500 Equal weight", "Largest 1000 US CAP (€)",  "Small cap US","Nucléaire Monde",
     "Fossiles Monde", "Renouvelable Monde", "Intelligence Artificielle"]
)

# Lancer la comparaison
if page == "Portefeuille personnalisé":
    run_perso()
elif page == "Oblig. US LT (€)":
    run_DTLA()
elif page == "MSCI USA":
    run_XD9U()
elif page == "Or physique":
    run_XGDU()
elif page == "Oblig. US CT":
    run_ZPR1()
elif page == "SP500":
    run_SXR8()
elif page == "SP500 Equal weight":
    run_XDEW()
elif page == "Largest 1000 US CAP (€)":
    run_R1VL()
elif page == "Small cap US":
    run_RTW0()
elif page == "Nucléaire Monde":
    run_NUKL()
elif page == "Fossiles Monde":
    run_XDW0()
elif page == "Renouvelable Monde":
    run_DELG()
elif page == "Intelligence Artificielle":
    run_XMLD()

