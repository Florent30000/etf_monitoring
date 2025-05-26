import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from bq_utils_streamlit import get_bigquery_client

def run():
    st.subheader("📈 Portefeuille Harry Browne : croisement des ETF")

    client = get_bigquery_client()

    @st.cache_data
    def charger_donnees():
        project_id = "etf-monitoring"
        dataset_id = "etf_data"

        query_dtla = f"SELECT Date, Close FROM {project_id}.{dataset_id}.dtla_l"
        df_dtla = client.query(query_dtla).to_dataframe()
        df_dtla["Date"] = pd.to_datetime(df_dtla["Date"])

        query_fx = f"SELECT Date, Close FROM {project_id}.{dataset_id}.eur_usd_parity"
        df_fx = client.query(query_fx).to_dataframe()
        df_fx.rename(columns={"Close": "FX"}, inplace=True)
        df_fx["Date"] = pd.to_datetime(df_fx["Date"])

        df_dtla = pd.merge(df_dtla, df_fx, on="Date", how="inner")
        df_dtla["Close"] = df_dtla["Close"] / df_dtla["FX"]
        df_dtla = df_dtla[["Date", "Close"]].set_index("Date")

        def charger_etf(nom_table):
            query = f"SELECT Date, Close FROM {project_id}.{dataset_id}.{nom_table}"
            df = client.query(query).to_dataframe()
            df["Date"] = pd.to_datetime(df["Date"])
            return df.set_index("Date")

        df_xd9u = charger_etf("xd9u_xetra")
        df_xgdu = charger_etf("xgdu_xetra")
        df_zpr1 = charger_etf("zpr1_xetra")

        return df_dtla, df_xd9u, df_xgdu, df_zpr1

    df_dtla, df_xd9u, df_xgdu, df_zpr1 = charger_donnees()

    df_all = pd.concat([
        df_dtla.rename(columns={"Close": "Oblig. US LT (€)"}),
        df_xd9u.rename(columns={"Close": "MSCI USA"}),
        df_xgdu.rename(columns={"Close": "Or physique"}),
        df_zpr1.rename(columns={"Close": "Oblig. US CT"})
    ], axis=1)

    # Sélection des ETFs
    etf_selection = st.multiselect(
        "🔍 Sélectionnez les ETFs à afficher :",
        options=[col for col in df_all.columns],
        default=df_all.columns[:4].tolist()
    )

    if len(etf_selection) < 2:
        st.error("Veuillez sélectionner au minimum 2 ETFs.")
        return

    df_selection = df_all[etf_selection].dropna()

    # Calcul des dates valides sans valeurs nulles ni diff nulles
    df_diff = df_selection.diff().dropna()
    valid_dates = df_diff[(df_diff != 0).all(axis=1)].index

    if valid_dates.empty:
        st.error("Aucune date valide disponible pour les ETFs sélectionnés.")
        return

    date_labels = [d.strftime("%Y-%m-%d") for d in valid_dates]
    date_mapping = dict(zip(date_labels, valid_dates))

    selected_label_base = st.select_slider(
        "📅 Choisissez la date d’origine base 100 pour comparaison :",
        options=date_labels,
        key="slider_hb_base100"
    )

    date_base = date_mapping[selected_label_base]

    # Base 100 et ajout de la valorisation moyenne
    df_base100 = df_selection / df_selection.loc[date_base] * 100
    df_base100["Valorisation HB"] = df_base100.mean(axis=1)

    df_base100 = df_base100[df_base100.index >= date_base]

    # Calculs de variation
    duration_days = (df_base100.index[-1] - date_base).days
    n_years = duration_days / 365.25

    variation = (df_base100.iloc[-1] / df_base100.loc[date_base] - 1) * 100
    annualized_variation = {
        col: ((df_base100[col].iloc[-1] / df_base100.loc[date_base, col]) ** (1 / n_years) - 1) * 100
        for col in df_base100.columns
    }

    variation_df = pd.DataFrame({
        'Variation (%)': variation,
        'Variation Annualisée (%)': annualized_variation
    })

    # Graphique
    fig = go.Figure()

    for col in df_base100.columns:
        fig.add_trace(go.Scatter(
            x=df_base100.index,
            y=df_base100[col],
            mode="lines",
            name=col,
            line=dict(color="black", width=2, dash="dash") if col == "Valorisation HB" else {}
        ))

    fig.update_layout(
        title=f"Comparaison des ETFs (Base 100 au {date_base.date()})",
        xaxis_title="Date",
        yaxis_title="Prix (€)",
        template="plotly_white",
        legend=dict(title="ETF", orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
        height=600,
        dragmode=False
    )

    st.plotly_chart(fig, use_container_width=True)

    # Mise en forme tableau variation
    def color_variation(val):
        color = 'green' if val > 0 else 'red'
        return f'color: {color}'

    st.subheader(f"📈 Variation depuis la date d'origine sélectionnée ({date_base.date()}) sur {duration_days} jours")

    variation_df_styled = variation_df.style.applymap(color_variation)
    variation_df_styled = variation_df_styled.format({
        'Variation (%)': '{:.2f}%',
        'Variation Annualisée (%)': '{:.2f}%'
    })

    st.dataframe(variation_df_styled)