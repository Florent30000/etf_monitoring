import streamlit as st
from bq_utils_streamlit import get_bigquery_client

# Configuration de la page (dans app.py)
st.set_page_config(page_title="Dashboard ETF", layout="wide")

client = get_bigquery_client()

# Pages importées
from sections.st_portefeuille_perso import run as run_perso
from sections.st_section_DTLA import run as run_DTLA
from sections.st_section_SXR8 import run as run_SXR8
from sections.st_section_XGDU import run as run_XGDU
from sections.st_section_ZPR1 import run as run_ZPR1
from sections.st_section_RTW0 import run as run_RTW0
from sections.st_section_EUNL import run as run_EUNL
from sections.st_section_IS3N import run as run_IS3N
from sections.st_section_XDWT import run as run_XDWT
from sections.st_section_XDWH import run as run_XDWH
from sections.st_section_XDWI import run as run_XDWI
from sections.st_section_BITC import run as run_BITC
from sections.st_section_EUNK import run as run_EUNK
from sections.st_section_XXSC import run as run_XXSC
from sections.st_section_ETLK import run as run_ETLK
from sections.st_section_CEBL import run as run_CEBL

# Créer un menu de navigation dans la barre latérale (sans les pages qui apparaissent automatiquement)
page = st.sidebar.radio(
    "Sélectionner un ETF à afficher",
    ["Portefeuille personnalisé","USD T-Bond 20 yrs (€)", "S&P 500", "Physical Gold", "USD T-Bill 1-3 Month",
     "Russel 2000 US", "MSCI World Large cap", "MSCI World Emerging markets", "MSCI World IT",
     "MSCI World Health Care", "MSCI World Industrials", "Physical Bitcoin", "MSCI Europe Large cap",
     "MSCI Europe Small Cap", "MSCI Asia Large cap", "MSCI Asia Emerging markets"
     ]
)

# Lancer la comparaison
if page == "Portefeuille personnalisé":
    run_perso()
elif page == "USD T-Bond 20 yrs (€)":
    run_DTLA()
elif page == "S&P 500":
    run_SXR8()
elif page == "Physical Gold":
    run_XGDU()
elif page == "USD T-Bill 1-3 Month":
    run_ZPR1()
elif page == "Russel 2000 US":
    run_RTW0()
elif page == "MSCI World Large cap":
    run_EUNL()
elif page == "MSCI World Emerging markets":
    run_IS3N()
elif page == "MSCI World IT":
    run_XDWT()
elif page == "MSCI World Health Care":
    run_XDWH()
elif page == "MSCI World Industrials":
    run_XDWI()
elif page == "Physical Bitcoin":
    run_BITC()
elif page == "MSCI Europe Large cap":
    run_EUNK()
elif page == "MSCI Europe Small Cap":
    run_XXSC()
elif page == "MSCI Asia Large cap":
    run_ETLK()
elif page == "MSCI Asia Emerging markets":
    run_CEBL()

