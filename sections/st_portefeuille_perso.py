import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from bq_utils_streamlit import get_bigquery_client

def run():
    # 📌 Titre
    st.subheader("📈 Portefeuille personnalisé : croisement des ETF")

    # 🔌 Connexion à BigQuery
    client = get_bigquery_client()

    # 🧠 Chargement des données
    @st.cache_data
    def charger_donnees():
        project_id = "etf-monitoring"
        dataset_id = "etf_data"

        # DTLA + conversion USD -> EUR
        df_dtla = client.query(f"SELECT Date, Close FROM `{project_id}.{dataset_id}.dtla_l`").to_dataframe()
        df_fx = client.query(f"SELECT Date, Close FROM `{project_id}.{dataset_id}.eur_usd_parity`").to_dataframe()
        df_dtla["Date"] = pd.to_datetime(df_dtla["Date"])
        df_fx["Date"] = pd.to_datetime(df_fx["Date"])
        df_fx.rename(columns={"Close": "FX"}, inplace=True)
        df_dtla = pd.merge(df_dtla, df_fx, on="Date", how="inner")
        df_dtla["Close"] = df_dtla["Close"] / df_dtla["FX"]
        df_dtla = df_dtla[["Date", "Close"]].set_index("Date")

        # R1VL + conversion USD -> EUR
        df_r1vl = client.query(f"SELECT Date, Close FROM `{project_id}.{dataset_id}.r1vl_lse`").to_dataframe()
        df_fx = client.query(f"SELECT Date, Close FROM `{project_id}.{dataset_id}.eur_usd_parity`").to_dataframe()
        df_r1vl["Date"] = pd.to_datetime(df_r1vl["Date"])
        df_fx["Date"] = pd.to_datetime(df_fx["Date"])
        df_fx.rename(columns={"Close": "FX"}, inplace=True)
        df_r1vl = pd.merge(df_r1vl, df_fx, on="Date", how="inner")
        df_r1vl["Close"] = df_r1vl["Close"] / df_r1vl["FX"]
        df_r1vl = df_r1vl[["Date", "Close"]].set_index("Date")

        # Autres ETF
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

    # 🔗 Fusion
    df_all = pd.concat([
        df_dtla.rename(columns={"Close": "Oblig. US LT"}),
        df_xd9u.rename(columns={"Close": "MSCI USA"}),
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

    # 📅 Dates valides (élimine les jours avec variation nulle)
    df_diff = df_all.diff().dropna()
    valid_dates = df_diff[(df_diff != 0).all(axis=1)].index
    date_labels = [d.strftime("%Y-%m-%d") for d in valid_dates]
    date_mapping = dict(zip(date_labels, valid_dates))

    # 📍 Sélection de la date base 100
    selected_label_base = st.select_slider(
        "📅 Choisissez la date d’origine base 100 pour comparaison :",
        options=date_labels,
        value=date_labels[0]
    )
    date_base = date_mapping[selected_label_base]

    # 📈 Rebase
    df_base100 = df_all / df_all.loc[date_base] * 100
    df_base100 = df_base100[df_base100.index >= date_base]

    # 📊 Sélection des ETF
    etf_options = list(df_base100.columns)
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

    # 🔀 Données filtrées + mix
    df_selected = df_base100[etf_selection].copy()
    df_selected["Mix valorisé"] = df_selected.mean(axis=1)

    # 📉 Graphe
    fig, ax = plt.subplots(figsize=(12, 6))
    for col in df_selected.columns:
        style = {"label": col}
        if col == "Mix valorisé":
            style.update({"color": "black", "linewidth": 2, "linestyle": "--"})
        ax.plot(df_selected.index, df_selected[col], **style)
    ax.set_title(f"Comparaison des ETFs (Base 100 au {date_base.date()})")
    ax.set_xlabel("Date")
    ax.set_ylabel("Performance")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    # 🟢 Fonction de coloration
    def color_variation(val):
        try:
            val_float = float(val.strip('%'))
            return f'color: {"green" if val_float > 0 else "red"}'
        except:
            return None

    # 🧮 Calculs variation + CAGR
    duration_days = (df_base100.index[-1] - date_base).days
    n_years = duration_days / 365.25
    variation_pct = (df_selected.iloc[-1] / df_selected.loc[date_base] - 1) * 100
    cagr_pct = {
        col: ((df_selected[col].iloc[-1] / df_selected.loc[date_base, col]) ** (1 / n_years) - 1) * 100
        for col in df_selected.columns
    }

    # 📋 Tableau récapitulatif
    variation_df = pd.DataFrame({
        "Variation (%)": variation_pct,
        "Variation Annualisée (%)": pd.Series(cagr_pct)
    })
    variation_df_formatted = variation_df.applymap(lambda x: f"{x:.2f}%" if pd.notnull(x) else "-")
    variation_df_styled = variation_df_formatted.style.applymap(color_variation)

    st.subheader(f"📈 Variation depuis la date d'origine sélectionnée ({date_base.date()}) sur {duration_days} jours")
    st.dataframe(variation_df_styled)

