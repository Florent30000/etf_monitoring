import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import timedelta
from bq_utils_streamlit import get_bigquery_client

def run():
    # --- Connexion BigQuery ---
    project_id = "etf-monitoring"
    dataset_id = "etf_data"
    table_name = "xxsc_xetra"
    full_table_id = f"{project_id}.{dataset_id}.{table_name}"

    client = get_bigquery_client()

    # --- Définir le ticker comme le nom de la table ---
    ticker = table_name.upper().replace("_", ".")

    # --- Lecture des données depuis BigQuery ---
    query = f"SELECT Date, Close FROM `{full_table_id}`"
    df = client.query(query).to_dataframe()
    df["Date"] = pd.to_datetime(df["Date"])
    df.set_index("Date", inplace=True)
    df.sort_index(inplace=True)

    # --- Affichage Streamlit ---
    st.subheader("📈 Suivi de l'ETF MSCI Europe Small Cap")

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

    # --- Calcul des variations ---
    latest_date = df.index.max()
    close_latest = df.loc[latest_date, "Close"]

    variations = {
        "1 jour": latest_date - timedelta(days=1),
        "1 sem.": latest_date - timedelta(weeks=1),
        "1 mois": latest_date - pd.DateOffset(months=1),
        "3 mois": latest_date - pd.DateOffset(months=3),
        "6 mois": latest_date - pd.DateOffset(months=6),
        "1 ans": latest_date - pd.DateOffset(years=1),
        "3 ans": latest_date - pd.DateOffset(years=3),
        "5 ans": latest_date - pd.DateOffset(years=5)
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

    # Affichage du graphique
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_filtered.index, y=df_filtered["Close"], mode='lines', name='Close'))

    fig.update_layout(
        title=f"Cours de clôture de l'ETF {ticker} depuis {start_date.date()}",
        xaxis_title="Date",
        yaxis_title="Prix (€)",
        template="plotly_white",
        hovermode="x unified",
        dragmode=False
    )

    st.plotly_chart(fig, use_container_width=True)

    # Affichage de Tableau de variation
    st.subheader("Variation du cours")

    # Découper le tableau en 2 moitiés
    first_half = variation_df.iloc[:, :4]
    second_half = variation_df.iloc[:, 4:]

    # Affichage vertical
    st.write(first_half.to_html(escape=False, index=False), unsafe_allow_html=True)
    st.write(second_half.to_html(escape=False, index=False), unsafe_allow_html=True)
