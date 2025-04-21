import streamlit as st

# Configuration de la page (dans app.py)
st.set_page_config(page_title="Dashboard ETF", layout="wide")

# Pages importées
from st_section_DTLA import run as run_DTLA
from st_section_XD9U import run as run_XD9U
from st_section_XGDU import run as run_XGDU
from st_section_ZPR1 import run as run_ZPR1

# Titre du dashboard
st.title("📊 Bienvenue sur le dashboard des ETF")

# Créer un menu de navigation dans la barre latérale (sans les pages qui apparaissent automatiquement)
page = st.sidebar.radio(
    "Sélectionner un ETF à afficher",
    ["Obligations US LT", "Actions US", "Or physique", "Obligations CT"]
)

# Lancer la fonction appropriée en fonction de la sélection
if page == "Obligations US LT":
    run_DTLA()
elif page == "Actions US":
    run_XD9U()
elif page == "Or physique":
    run_XGDU()
elif page == "Obligations CT":
    run_ZPR1()
