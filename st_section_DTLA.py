import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import yfinance as yf

def run():
    # --- Connexion à la base ---
    db_path = "./data/etf_data.db"
    table_name = "dtla_l"
    engine = create_engine(f"sqlite:///{db_path}")

    # --- Définir le ticker comme le nom de la table ---
    ticker = table_name.upper().replace("_", ".")

    # --- Lecture des données ---
    df = pd.read_sql_table(table_name, con=engine)
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    df.sort_index(inplace=True)

    # Définir la plage de dates disponibles
    min_date = df.index.min().date()
    max_date = df.index.max().date()

    # Ajouter une slider pour choisir la date de début d'affichage
    start_date = st.slider(
    "📅 Choisissez la date de début d'affichage",
    min_value=min_date,
    max_value=max_date,
    value=min_date,
    format="YYYY-MM-DD"
    )

    # Filtrer les données pour le graphique
    start_date = pd.to_datetime(start_date)
    df_filtered = df[df.index >= start_date]

    # --- Récupérer le taux de change USD -> EUR via yfinance ---
    usd_eur = yf.Ticker('EURUSD=X')
    taux_de_change_usd_eur = usd_eur.history(period='1d')['Close'].iloc[-1]

     # --- Convertir toutes les colonnes numériques en EUR ---
    df['Close'] = df['Close'] * taux_de_change_usd_eur

    # --- Calcul des variations ---
    latest_date = df.index.max()
    close_latest = df.loc[latest_date, "Close"]

    variations = {
        "1 jour": latest_date - timedelta(days=1),
        "1 semaine": latest_date - timedelta(weeks=1),
        "1 mois": latest_date - pd.DateOffset(months=1),
        "3 mois": latest_date - pd.DateOffset(months=3),
        "6 mois": latest_date - pd.DateOffset(months=6),
        "1 an": latest_date - pd.DateOffset(years=1),
        "3 an": latest_date - pd.DateOffset(years=3)
    }

    variation_table = []

    for label, past_date in variations.items():
        past_df = df[df.index <= past_date]
        if not past_df.empty:
            past_close = past_df["Close"].iloc[-1]
            variation_pct = ((close_latest - past_close) / past_close) * 100
            variation_table.append((label, variation_pct))

    variation_df = pd.DataFrame(variation_table, columns=["Période", "Var"])

    # --- Formater avec flèches et couleurs HTML ---
    def format_variation_html(pct):
        color = "green" if pct > 0 else "red"
        return f'<span style="color:{color}; font-weight:bold"> {pct:+.2f}%</span>'

    variation_df["Var"] = variation_df["Var"].apply(format_variation_html)

    # Transposer en supprimant toute trace de l'index/colonne "Période"
    variation_df = variation_df.set_index("Période").T
    variation_df.index = ["Variation (%)"]  # Renomme l’unique ligne
    variation_df.columns.name = None  # Supprime "Période" comme nom de colonne

    # --- Affichage Streamlit ---
    # st.markdown("<h3>📈 Suivi de l'ETF Obligations US LT</h3>", unsafe_allow_html=True)
    st.subheader("📈 Suivi de l'ETF Obligations US LT")

    # Affichage du graphique
    fig, ax = plt.subplots()
    df_filtered["Close"].plot(ax=ax, title=f"Cours de clôture de l'ETF {ticker} depuis {start_date.date()}")
    st.pyplot(fig)

    # Affichage du Tableau de variation
    st.subheader("Variation du cours par durée")
    st.write(
        variation_df.to_html(escape=False, index=False),
        unsafe_allow_html=True
    )
