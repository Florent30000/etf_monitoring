import streamlit as st

st.set_page_config(page_title="Dashboard ETF", layout="wide")

st.title("📊 Suivi de performance des ETF")

st.write("""
Cette application vous permet de suivre les performances d'une sélection d'ETF.""")

st.write("""
La navigation vers les ETF s'effectue via le menu dépliable à gauche de l'écran,
vous donnant accès :
""")   
st.write("""
    - Au portefeuille Harry Browne : visualisation des performances de 4 ETF qui reproduisent cette stratégie diversifiée
""")
st.markdown(
    '<a href="/Portefeuille_Harry_Browne" target="_self">👉 Portefeuille Harry Browne</a>',
    unsafe_allow_html=True
)
st.write("""
    - Au portefeuille personnalisé : comparatif personnalisable des évolutions de votre sélection d'ETF dans un même graphique 
""")
st.markdown(
    '<a href="/Portefeuille_personnalisé" target="_self">👉 Portefeuille personnalisé</a>',
    unsafe_allow_html=True
)
st.write("""
    - Au Podium (top 3) des meilleurs ETF par durée d'investissement (3 mois, 1 an et 3 ans)
""")
st.markdown(
    '<a href="/Podium" target="_self">👉 Podium</a>',
    unsafe_allow_html=True
)
st.write("""
    - Aux ETF catégorisés : géographiquement WORLD / US / EUROPE / ASIA stocks, \
         par secteur spécifique et hard assets (or et bitcoin)
""")
st.markdown(
    '<a href="/WORLD_stocks" target="_self">👉 WORLD stocks</a>',
    unsafe_allow_html=True
)
st.markdown(
    '<a href="/US_stocks" target="_self">👉 US stocks</a>',
    unsafe_allow_html=True
)
st.markdown(
    '<a href="/EUROPE_stocks" target="_self">👉 EUROPE stocks</a>',
    unsafe_allow_html=True
)
st.markdown(
    '<a href="/ASIA_stocks" target="_self">👉 ASIA stocks</a>',
    unsafe_allow_html=True
)
st.markdown(
    '<a href="/SECTOR_specific" target="_self">👉 SECTOR specific</a>',
    unsafe_allow_html=True
)
st.markdown(
    '<a href="/HARD_ASSETS" target="_self">👉 HARD ASSETS</a>',
    unsafe_allow_html=True
)
st.write("""
    - A la parité USD-EUR : mesure l'impact monétaire de ces investissements en EURO sur des actifs en DOLLAR
""")
st.markdown(
    '<a href="/Parité_USD-EUR" target="_self">👉 Parité USD-EUR</a>',
    unsafe_allow_html=True
)


st.write("""
Informations complémentaires sur les ETF:
""")
st.write("""
    - Afin d'être comparables, ils sont tous :
         - à dividendes réinvestis dans l'ETF
         - en mode de réplication physique
         - soit directement côté en EURO, soit convertis du DOLLAR à l'EURO
    - Leur mise à jour est quotidienne : 7h du matin sur la base du cours de clôture de la veille.
""")