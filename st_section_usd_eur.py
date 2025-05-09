import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from bq_utils import get_bigquery_client

client = get_bigquery_client()

def run():
    # --- Connexion BigQuery ---
    project_id = "etf-monitoring"
    dataset_id = "etf_data"
    table_name = "eur_usd_parity"
    full_table_id = f"{project_id}.{dataset_id}.{table_name}"

    # --- Lecture des données depuis BigQuery ---
    query = f"SELECT Date, Close FROM `{full_table_id}`"
    df = client.query(query).to_dataframe()
    df["Date"] = pd.to_datetime(df["Date"])
    df.set_index("Date", inplace=True)
    df.sort_index(inplace=True)

    # --- Inverser EUR/USD -> USD/EUR ---
    df["Close"] = 1 / df["Close"]

    # --- Affichage Streamlit ---
    st.subheader("💱 Suivi de la parité USD/EUR")

    # Définir la plage de dates disponibles
    min_date = df.index.min().date()
    max_date = df.index.max().date()

    # Slider de date de début
    start_date = st.slider(
        "📅 Choisissez la date de début d'affichage",
        min_value=min_date,
        max_value=max_date,
        value=min_date,
        format="YYYY-MM-DD"
    )

    # Filtrer les données
    start_date = pd.to_datetime(start_date)
    df_filtered = df[df.index >= start_date]

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
        "3 ans": latest_date - pd.DateOffset(years=3),
    }

    variation_table = []

    for label, past_date in variations.items():
        past_df = df[df.index <= past_date]
        if not past_df.empty:
            past_close = past_df["Close"].iloc[-1]
            variation_pct = ((close_latest - past_close) / past_close) * 100
            variation_table.append((label, variation_pct))

    variation_df = pd.DataFrame(variation_table, columns=["Période", "Var"])

    # --- Format HTML (flèches couleurs) ---
    def format_variation_html(pct):
        color = "green" if pct > 0 else "red"
        return f'<span style="color:{color}; font-weight:bold"> {pct:+.2f}%</span>'

    variation_df["Var"] = variation_df["Var"].apply(format_variation_html)
    variation_df = variation_df.set_index("Période").T
    variation_df.index = ["Variation (%)"]
    variation_df.columns.name = None

    # --- Affichage graphique ---
    fig, ax = plt.subplots()
    df_filtered["Close"].plot(ax=ax, title=f"Parité USD/EUR depuis le {start_date.date()}")
    ax.set_ylabel("Taux de change")
    st.pyplot(fig)

    # --- Tableau de variation ---
    st.subheader("Variation du taux de change")
    st.write(variation_df.to_html(escape=False, index=False), unsafe_allow_html=True)
