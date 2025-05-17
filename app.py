import streamlit as st

st.set_page_config(page_title="Dashboard ETF", layout="wide")
st.title("📊 Suivi de performance des ETF")

st.write("""
Ce tableau de bord vous permet de suivre les performances d'une sélection d'ETF.

    La navigation vers les ETF s'effectue via le menu dépliable à gauche de l'écran, vous donnant accès :
        - Aux ETF sectorisés : énergie, poids des entreprises etc...
        - Au portefeuille personnalisé : comparaison sur le même graphique de votre sélection d'ETF
        - Au portefeuille Harry Brown : visualisation des performances de 4 ETF qui reproduisent cette stratégie diversifiée
        - à la parité USD-EUR : mesure l'impact monétaire de ces investissements en EURO sur des actifs en DOLLAR
        - Au top 3 des meilleurs ETF sur les catégories 3 mois, 6 mois, 1 an, 3 ans et 5 ans
         
    Informations techniques :
        - Les ETF sont mis à jour quotidiennement à 7h du matin sur le base des cours de clôture de la veille.
        - Les ETF sont soit directement en EURO, soit converti en DOLLAR au cours historique
""")