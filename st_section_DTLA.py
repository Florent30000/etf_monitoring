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

    variation_df = pd.DataFrame(variation_table, columns=["Période", ticker])

    # --- Formater avec flèches et couleurs HTML ---
    def format_variation_html(pct):
        color = "green" if pct > 0 else "red"
        return f'<span style="color:{color}; font-weight:bold"> {pct:+.2f}%</span>'

    variation_df[ticker] = variation_df[ticker].apply(format_variation_html)

    # --- Affichage Streamlit ---
    st.title("📈 Suivi de l'ETF Obligations US LT")

    # Diviser l'espace en deux colonnes
    col1, col2 = st.columns([2, 1])  # La première colonne sera plus large (2/3), la deuxième plus étroite (1/3)

    # Courbe dans la première colonne
    with col1:
        fig, ax = plt.subplots()
        df["Close"].plot(ax=ax, title=f"Cours de clôture de l'ETF {ticker}")
        st.pyplot(fig)

    # Tableau de variation dans la deuxième colonne
    with col2:
        st.subheader("Variation du cours")
        st.write(
            variation_df.to_html(escape=False, index=False),
            unsafe_allow_html=True
        )
