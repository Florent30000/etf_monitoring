import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from bq_utils_streamlit import get_bigquery_client

def run():
    st.subheader("📈 Suivi de l'ETF Obligations US LT (en EUR)")

    client = get_bigquery_client()

    # --- Connexion à BigQuery ---
    project_id = "etf-monitoring"
    dataset_id = "etf_data"
    etf_table = "dtla_l"
    fx_table = "eur_usd_parity"
    full_etf_table = f"{project_id}.{dataset_id}.{etf_table}"
    full_fx_table = f"{project_id}.{dataset_id}.{fx_table}"

    # --- Récupérer les données de l’ETF et du taux de change ---
    query = f"""
        SELECT
            etf.Date,
            etf.Close AS Close_USD,
            fx.Close AS EURUSD_Close,
            etf.Close * (1/fx.Close) AS Close_EUR
        FROM `{full_etf_table}` etf
        JOIN `{full_fx_table}` fx
        ON etf.Date = fx.Date
        ORDER BY etf.Date
    """
    # df = pd.read_gbq(query, project_id=project_id)
    df = client.query(query).to_dataframe()
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    df.sort_index(inplace=True)

    # --- Slider de sélection de date ---
    min_date = df.index.min().date()
    max_date = df.index.max().date()

    start_date = st.slider(
        "📅 Choisissez la date de début d'affichage",
        min_value=min_date,
        max_value=max_date,
        value=min_date,
        format="YYYY-MM-DD"
    )

    start_date = pd.to_datetime(start_date)
    df_filtered = df[df.index >= start_date]

    # --- Calcul des variations ---
    latest_date = df.index.max()
    close_latest = df.loc[latest_date, "Close_EUR"]

    variations = {
        "1 jour": latest_date - timedelta(days=1),
        "1 sem.": latest_date - timedelta(weeks=1),
        "1 mois": latest_date - pd.DateOffset(months=1),
        "3 mois": latest_date - pd.DateOffset(months=3),
        "6 mois": latest_date - pd.DateOffset(months=6),
        "1 an": latest_date - pd.DateOffset(years=1),
        "3 ans": latest_date - pd.DateOffset(years=3),
        "5 ans": latest_date - pd.DateOffset(years=5)
    }

    variation_table = []

    for label, past_date in variations.items():
        past_df = df[df.index <= past_date]
        if not past_df.empty:
            past_close = past_df["Close_EUR"].iloc[-1]
            variation_pct = ((close_latest - past_close) / past_close) * 100
            variation_table.append((label, variation_pct))

    variation_df = pd.DataFrame(variation_table, columns=["Période", "Var"])

    def format_variation_html(pct):
        color = "green" if pct > 0 else "red"
        return f'<span style="color:{color}; font-weight:bold"> {pct:+.2f}%</span>'

    variation_df["Var"] = variation_df["Var"].apply(format_variation_html)
    variation_df = variation_df.set_index("Période").T
    variation_df.index = ["Variation (%)"]
    variation_df.columns.name = None

    # --- Affichage Streamlit ---
    fig, ax = plt.subplots()
    df_filtered["Close_EUR"].plot(ax=ax, title=f"Cours de l'ETF DTLA en EUR depuis {start_date.date()}")
    st.pyplot(fig)

    st.subheader("Variation du cours (en EUR)")

    # Découper le tableau en 2 moitiés
    first_half = variation_df.iloc[:, :4]
    second_half = variation_df.iloc[:, 4:]

    # Affichage vertical
    st.write(first_half.to_html(escape=False, index=False), unsafe_allow_html=True)
    st.write(second_half.to_html(escape=False, index=False), unsafe_allow_html=True)


