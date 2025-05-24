import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
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
        df_dtla.rename(columns={"Close": "Oblig. US LT"}),
        df_xd9u.rename(columns={"Close": "Actions US"}),
        df_xgdu.rename(columns={"Close": "Or physique"}),
        df_zpr1.rename(columns={"Close": "Oblig. US CT"}),
        df_r1vl.rename(columns={"Close": "Largest 1000 US CAP"}),
        df_xdew.rename(columns={"Close": "SP500 Equal weight"}),
        df_rtwo.rename(columns={"Close": "Small cap US"}),
        df_xmld.rename(columns={"Close": "Intelligence Artificielle"}),
        df_sxr8.rename(columns={"Close": "SP500"}),
        df_nukl.rename(columns={"Close": "Nucléaire Monde"}),
        df_xdw0.rename(columns={"Close": "Fossiles Monde"}),
        df_delg.rename(columns={"Close": "Renouvellable Monde"})
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
        if len(variation_series) < 3:
            st.warning(f"❗ Pas assez d'ETF avec historique suffisant pour afficher un podium : {titre}")
            if excluded_etfs.get(periode):
                st.info("⏳ Les ETF suivants n’ont pas suffisamment d’historique et sont exclus du podium :")
                for etf in excluded_etfs[periode]:
                    st.write(f"• {etf}")
            return

        fig, ax = plt.subplots()
        couleurs = ["#C0C0C0", "#FFD700", "#CD7F32"]  # argent, or, bronze

        variation_series = variation_series.sort_values(ascending=False)
        valeurs = [variation_series.iloc[1], variation_series.iloc[0], variation_series.iloc[2]]
        noms = [variation_series.index[1], variation_series.index[0], variation_series.index[2]]

        positions = [0, 1, 2]
        bars = ax.bar(positions, valeurs, color=couleurs)

        ax.set_title(titre)
        ax.set_ylabel("Variation (%)")
        ax.set_xticks(positions)
        ax.set_xticklabels(noms)

        ymax = max(valeurs) * 1.25
        ymin = min(0, min(valeurs) * 1.25)
        ax.set_ylim(ymin, ymax)

        for i, bar in enumerate(bars):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + 0.5,
                    f"{height:.2f}%", ha='center', va='bottom')

        st.pyplot(fig)

    # Calculs et affichages
    variation_3m = calc_variation(df_all[valid_etfs["3 mois"]], periods["3 mois"])
    top3_3m = variation_3m.sort_values(ascending=False).head(3)
    afficher_podium(top3_3m, "Top 3 ETF à 3 mois")

    variation_1y = calc_variation(df_all[valid_etfs["1 an"]], periods["1 an"])
    top3_1y = variation_1y.sort_values(ascending=False).head(3)
    afficher_podium(top3_1y, "Top 3 ETF à 1 an")

    variation_3y = calc_variation(df_all[valid_etfs["3 ans"]], periods["3 ans"])
    top3_3y = variation_3y.sort_values(ascending=False).head(3)
    afficher_podium(top3_3y, "Top 3 ETF à 3 ans")

















