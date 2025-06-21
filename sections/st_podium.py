import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from bq_utils_streamlit import get_bigquery_client

def run():
    st.subheader("📈 Podium des ETF de l'application par durée d'investissement")

    st.write("""
    Les podiums affichés sont à 3 mois, 1 an et 3 ans.""")

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

        df_xdwi = client.query(f"SELECT Date, Close FROM `{project_id}.{dataset_id}.xdwi_xetra`").to_dataframe()
        df_fx = client.query(f"SELECT Date, Close FROM `{project_id}.{dataset_id}.eur_usd_parity`").to_dataframe()
        df_xdwi["Date"] = pd.to_datetime(df_xdwi["Date"])
        df_fx["Date"] = pd.to_datetime(df_fx["Date"])
        df_fx.rename(columns={"Close": "FX"}, inplace=True)
        df_xdwi = pd.merge(df_xdwi, df_fx, on="Date", how="inner")
        df_xdwi["Close"] = df_xdwi["Close"] / df_xdwi["FX"]
        df_xdwi = df_xdwi[["Date", "Close"]].set_index("Date")

        def charger_etf(nom_table):
            df = client.query(f"SELECT Date, Close FROM `{project_id}.{dataset_id}.{nom_table}`").to_dataframe()
            df["Date"] = pd.to_datetime(df["Date"])
            return df.set_index("Date")

        return (
            df_dtla,
            df_xdwi,
            charger_etf("xgdu_xetra"),
            charger_etf("zpr1_xetra"),
            charger_etf("rtwo_as"),
            charger_etf("sxr8_xetra"),
            charger_etf("eunl_xetra"),
            charger_etf("is3n_xetra"),
            charger_etf("xdwt_xetra"),
            charger_etf("xdwh_xetra"),
            charger_etf("bitc_xetra"),
            charger_etf("eunk_xetra"),
            charger_etf("xxsc_xetra"),
            charger_etf("etlk_xetra"),
            charger_etf("cebl_xetra")
        )

    (df_dtla, df_xdwi, df_xgdu, df_zpr1, df_rtwo,
     df_sxr8, df_eunl, df_is3n, df_xdwt, df_xdwh, df_bitc,
     df_eunk, df_xxsc, df_etlk, df_cebl ) = charger_donnees()

    df_all = pd.concat([
        df_dtla.rename(columns={"Close": "USD T-Bond 20 yrs"}),
        df_xdwi.rename(columns={"Close": "MSCI World Industrials"}),
        df_xgdu.rename(columns={"Close": "Physical Gold"}),
        df_zpr1.rename(columns={"Close": "USD T-Bill 1-3 Month"}),
        df_rtwo.rename(columns={"Close": "Russel 2000 US"}),
        df_sxr8.rename(columns={"Close": "S&P 500"}),
        df_eunl.rename(columns={"Close": "MSCI World Large cap"}),
        df_is3n.rename(columns={"Close": "MSCI World Emerging markets"}),
        df_xdwt.rename(columns={"Close": "MSCI World IT"}),
        df_xdwh.rename(columns={"Close": "MSCI World Health Care"}),
        df_bitc.rename(columns={"Close": "Physical Bitcoin"}),
        df_eunk.rename(columns={"Close": "MSCI Europe Large cap"}),
        df_xxsc.rename(columns={"Close": "MSCI Europe Small Cap"}),
        df_etlk.rename(columns={"Close": "MSCI Asia Large cap"}),
        df_cebl.rename(columns={"Close": "MSCI Asia Emerging markets"})
    ], axis=1)
    df_all.dropna(inplace=True)

    date_fin = df_all.index.max()

    periods = {
        "3 mois": 90,
        "1 an": 365,
        "3 ans": 365*3
    }

    def etf_suffisamment_historique(df, col, days):
        date_debut_min = date_fin - pd.Timedelta(days=days)
        date_min_etf = df[col].dropna().index.min()
        return date_min_etf <= date_debut_min

    valid_etfs = {}
    excluded_etfs = {}

    for label, days in periods.items():
        valid = [col for col in df_all.columns if etf_suffisamment_historique(df_all, col, days)]
        excluded = [col for col in df_all.columns if col not in valid]
        valid_etfs[label] = valid
        excluded_etfs[label] = excluded

    def calc_variation(df, days):
        date_debut = date_fin - pd.Timedelta(days=days)
        pos = df.index.searchsorted(date_debut, side='left')
        if pos == len(df.index):
            pos -= 1
        elif pos > 0 and df.index[pos] > date_debut:
            pos -= 1
        date_debut_reelle = df.index[pos]
        variation = (df.loc[date_fin] / df.loc[date_debut_reelle] - 1) * 100
        return variation

    def afficher_podium(variation_series, titre):
        periode = titre.split("à")[-1].strip()
        #if len(variation_series) < 3:
        #    st.warning(f"❗ Pas assez d'ETF avec historique suffisant pour afficher un podium : {titre}")
        #    if excluded_etfs.get(periode):
        #        st.info("⏳ Les ETF suivants n’ont pas suffisamment d’historique et sont exclus du podium :")
        #        for etf in excluded_etfs[periode]:
        #            st.write(f"• {etf}")
        #    return

        couleurs = ["#C0C0C0", "#FFD700", "#CD7F32"]  # argent, or, bronze
        variation_series = variation_series.sort_values(ascending=False)
        valeurs = [variation_series.iloc[1], variation_series.iloc[0], variation_series.iloc[2]]
        noms = [variation_series.index[1], variation_series.index[0], variation_series.index[2]]

        fig = go.Figure()

        for i, (val, nom, couleur) in enumerate(zip(valeurs, noms, couleurs)):
            fig.add_trace(go.Bar(
                x=[nom],
                y=[val],
                name=nom,
                marker_color=couleur,
                text=f"{val:.2f}%",
                textposition="outside"
            ))

        fig.update_layout(
            title=titre,
            yaxis_title="Variation (%)",
            xaxis_title="ETF",
            showlegend=False,
            height=400,
            template="plotly_white",
            yaxis=dict(range=[min(0, min(valeurs)*1.25), max(valeurs)*1.25]),
            dragmode=False,
            margin=dict(t=60, b=60)
        )

        st.plotly_chart(fig, use_container_width=True)

    # Calculs et affichages
    variation_3m = calc_variation(df_all[valid_etfs["3 mois"]], periods["3 mois"])
    top3_3m = variation_3m.sort_values(ascending=False).head(3)
    afficher_podium(top3_3m, "Top 3 ETF à 3 mois")

    variation_1y = calc_variation(df_all[valid_etfs["1 an"]], periods["1 an"])
    top3_1y = variation_1y.sort_values(ascending=False).head(3)
    afficher_podium(top3_1y, "Top 3 ETF à 1 an")

    #variation_3y = calc_variation(df_all[valid_etfs["3 ans"]], periods["3 ans"])
    #top3_3y = variation_3y.sort_values(ascending=False).head(3)
    #afficher_podium(top3_3y, "Top 3 ETF à 3 ans")

















