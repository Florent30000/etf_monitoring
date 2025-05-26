import streamlit as st
import pandas as pd
from bq_utils_streamlit import get_bigquery_client
import plotly.graph_objects as go

def run():
    st.subheader("📈 Portefeuille personnalisé : croisement des ETF")

    client = get_bigquery_client()

    @st.cache_data
    def charger_donnees():
        project_id = "etf-monitoring"
        dataset_id = "etf_data"

        df_dtla = client.query(f"SELECT Date, Close FROM `{project_id}.{dataset_id}.dtla_l`").to_dataframe()
        df_fx = client.query(f"SELECT Date, Close FROM `{project_id}.{dataset_id}.eur_usd_parity`").to_dataframe()
        df_dtla["Date"] = pd.to_datetime(df_dtla["Date"])
        df_fx["Date"] = pd.to_datetime(df_fx["Date"])
        df_fx.rename(columns={"Close": "FX"}, inplace=True)
        df_dtla = pd.merge(df_dtla, df_fx, on="Date", how="inner")
        df_dtla["Close"] = df_dtla["Close"] / df_dtla["FX"]
        df_dtla = df_dtla[["Date", "Close"]].set_index("Date")

        df_r1vl = client.query(f"SELECT Date, Close FROM `{project_id}.{dataset_id}.r1vl_lse`").to_dataframe()
        df_fx = client.query(f"SELECT Date, Close FROM `{project_id}.{dataset_id}.eur_usd_parity`").to_dataframe()
        df_r1vl["Date"] = pd.to_datetime(df_r1vl["Date"])
        df_fx["Date"] = pd.to_datetime(df_fx["Date"])
        df_fx.rename(columns={"Close": "FX"}, inplace=True)
        df_r1vl = pd.merge(df_r1vl, df_fx, on="Date", how="inner")
        df_r1vl["Close"] = df_r1vl["Close"] / df_r1vl["FX"]
        df_r1vl = df_r1vl[["Date", "Close"]].set_index("Date")

        def charger_etf(nom_table):
            df = client.query(f"SELECT Date, Close FROM `{project_id}.{dataset_id}.{nom_table}`").to_dataframe()
            df["Date"] = pd.to_datetime(df["Date"])
            return df.set_index("Date")

        return (
            df_dtla,
            df_r1vl,
            charger_etf("xd9u_xetra"),
            charger_etf("xgdu_xetra"),
            charger_etf("zpr1_xetra"),
            charger_etf("xdew_xetra"),
            charger_etf("rtwo_as"),
            charger_etf("xmld_xetra"),
            charger_etf("sxr8_xetra"),
            charger_etf("nukl_xetra"),
            charger_etf("xdw0_xetra"),
            charger_etf("delg_xetra")
        )

    (df_dtla, df_r1vl, df_xd9u, df_xgdu, df_zpr1, df_xdew, df_rtwo, 
     df_xmld, df_sxr8, df_nukl, df_xdw0, df_delg) = charger_donnees()

    df_all = pd.concat([
        df_dtla.rename(columns={"Close": "Oblig. US LT (€)"}),
        df_xd9u.rename(columns={"Close": "MSCI USA"}),
        df_xgdu.rename(columns={"Close": "Or physique"}),
        df_zpr1.rename(columns={"Close": "Oblig. US CT"}),
        df_r1vl.rename(columns={"Close": "Largest 1000 US CAP (€)"}),
        df_xdew.rename(columns={"Close": "SP500 Equal weight"}),
        df_rtwo.rename(columns={"Close": "Small cap US"}),
        df_xmld.rename(columns={"Close": "Intelligence Artificielle"}),
        df_sxr8.rename(columns={"Close": "SP500"}),
        df_nukl.rename(columns={"Close": "Nucléaire Monde"}),
        df_xdw0.rename(columns={"Close": "Fossiles Monde"}),
        df_delg.rename(columns={"Close": "Renouvellable Monde"})
    ], axis=1)

    etf_options = list(df_all.columns)
    default_selection = ["MSCI USA", "Or physique", "SP500 Equal weight",
                        "Intelligence Artificielle", "Nucléaire Monde"]
    etf_selection = st.multiselect(
        "🔍 Sélectionnez les ETFs à afficher :",
        options=etf_options,
        default=default_selection
    )

    if len(etf_selection) < 2:
        st.error("Veuillez sélectionner au minimum 2 ETFs.")
        return

    df_selection = df_all[etf_selection].copy()
    df_selection = df_selection.dropna(how="any")

    # Vérification si aucune date n’est commune aux ETFs sélectionnés
    if df_selection.empty:
        st.error("Aucune date commune entre les ETFs sélectionnés. Veuillez modifier votre sélection.")
        return

    # Création des options de date pour le select_slider
    valid_dates = df_selection.index
    date_labels = [d.strftime("%Y-%m-%d") for d in valid_dates]

    selected_label_base = st.select_slider(
        "📅 Choisissez la date d’origine base 100 pour comparaison :",
        options=date_labels,
        key="slider_base100"
    )

    # Conversion en datetime
    date_base = pd.to_datetime(selected_label_base)

    # Création du DataFrame base 100 à partir de la date sélectionnée
    df_base100 = df_selection[df_selection.index >= date_base]
    df_base100 = df_base100 / df_base100.loc[date_base] * 100

    df_selected = df_base100[etf_selection].copy()
    df_selected["Mix valorisé"] = df_selected.mean(axis=1)

    fig = go.Figure()
    for col in df_selected.columns:
        fig.add_trace(go.Scatter(
            x=df_selected.index,
            y=df_selected[col],
            mode="lines",
            name=col,
            line=dict(color="black", width=2, dash="dash") if col == "Mix valorisé" else None
        ))

    fig.update_layout(
        title=f"Comparaison des ETFs (Base 100 au {date_base.date()})",
        xaxis_title="Date",
        yaxis_title="Prix (€)",
        dragmode=False,
        template="plotly_white",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.4,
            xanchor="center",
            x=0.5,
            bordercolor="gray",
            borderwidth=0.5,
        ),
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

    def color_variation(val):
        try:
            val_float = float(val.strip('%'))
            return f'color: {"green" if val_float > 0 else "red"}'
        except:
            return None

    duration_days = (df_base100.index[-1] - date_base).days
    n_years = duration_days / 365.25
    variation_pct = (df_selected.iloc[-1] / df_selected.loc[date_base] - 1) * 100
    cagr_pct = {
        col: ((df_selected[col].iloc[-1] / df_selected.loc[date_base, col]) ** (1 / n_years) - 1) * 100
        for col in df_selected.columns
    }

    variation_df = pd.DataFrame({
        "Variation (%)": variation_pct,
        "Variation Annualisée (%)": pd.Series(cagr_pct)
    })
    variation_df_formatted = variation_df.applymap(lambda x: f"{x:.2f}%" if pd.notnull(x) else "-")
    variation_df_styled = variation_df_formatted.style.applymap(color_variation)

    st.subheader(f"📈 Variation depuis la date d'origine sélectionnée ({date_base.date()}) sur {duration_days} jours")
    st.dataframe(variation_df_styled)

