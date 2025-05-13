import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from bq_utils_streamlit import get_bigquery_client

def run():
    # Titre
    st.subheader("📈 Portefeuille Harry Brown : croisement des ETF")

    client = get_bigquery_client()

    # Chargement des données
    @st.cache_data
    def charger_donnees():
        project_id = "etf-monitoring"
        dataset_id = "etf_data"

        # Charger DTLA
        query_dtla = f"SELECT Date, Close FROM `{project_id}.{dataset_id}.dtla_l`"
        df_dtla = client.query(query_dtla).to_dataframe()
        df_dtla["Date"] = pd.to_datetime(df_dtla["Date"])

        # Charger taux de change USD -> EUR
        query_fx = f"SELECT Date, Close FROM `{project_id}.{dataset_id}.eur_usd_parity`"
        df_fx = client.query(query_fx).to_dataframe()
        df_fx.rename(columns={"Close": "FX"}, inplace=True)
        df_fx["Date"] = pd.to_datetime(df_fx["Date"])

        # Conversion en EUR via jointure
        df_dtla = pd.merge(df_dtla, df_fx, on="Date", how="inner")
        df_dtla["Close"] = df_dtla["Close"] / df_dtla["FX"]
        df_dtla = df_dtla[["Date", "Close"]].set_index("Date")

        # Charger les autres ETF
        def charger_etf(nom_table):
            query = f"SELECT Date, Close FROM `{project_id}.{dataset_id}.{nom_table}`"
            df = client.query(query).to_dataframe()
            df["Date"] = pd.to_datetime(df["Date"])
            return df.set_index("Date")

        df_xd9u = charger_etf("xd9u_xetra")
        df_xgdu = charger_etf("xgdu_xetra")
        df_zpr1 = charger_etf("zpr1_xetra")

        return df_dtla, df_xd9u, df_xgdu, df_zpr1

    df_dtla, df_xd9u, df_xgdu, df_zpr1 = charger_donnees()

    # Création d’un DataFrame combiné
    df_all = pd.concat([
        df_dtla.rename(columns={"Close": "Oblig. US LT"}),
        df_xd9u.rename(columns={"Close": "Actions US"}),
        df_xgdu.rename(columns={"Close": "Or physique"}),
        df_zpr1.rename(columns={"Close": "Oblig. US CT"})
    ], axis=1)

    # Filtrage des données valides (communes et non nulles)
    df_all.dropna(inplace=True)
    df_diff = df_all.diff().dropna()
    valid_dates = df_diff[(df_diff != 0).all(axis=1)].index

    # Conversion des dates en labels affichables
    date_labels = [d.strftime("%Y-%m-%d") for d in valid_dates]
    date_mapping = dict(zip(date_labels, valid_dates))

    # 🔹 Slider : Date base 100
    selected_label_base = st.select_slider(
        "📅 Choisissez la date d’origine base 100 pour comparaison :",
        options=date_labels,
        value=date_labels[0]
    )
    date_base = date_mapping[selected_label_base]

    # Rebase à 100
    df_base100 = df_all / df_all.loc[date_base] * 100
    df_base100["Moyenne"] = df_base100.mean(axis=1)

    # Utiliser la date de base 100 comme date de début
    df_base100 = df_base100[df_base100.index >= date_base]

    # Sélectionner plusieurs ETFs (au moins 2, au maximum tous)
    etf_selection = st.multiselect(
        "🔍 Sélectionnez les ETFs à afficher :",
        options=[col for col in df_base100.columns if col != "Moyenne"],
        default=df_base100.columns[:4].tolist()
    )

    # Vérifier qu'il y a au moins 2 ETFs sélectionnés
    if len(etf_selection) < 2:
        st.error("Veuillez sélectionner au minimum 2 ETFs.")
    else:
        # Filtrer les données selon la sélection
        df_selected = df_base100[etf_selection]
        
        # Calculer la moyenne des ETFs sélectionnés
        df_selected["Moyenne"] = df_selected.mean(axis=1)

        # Affichage du graphique avec les ETFs sélectionnés et la moyenne
        fig, ax = plt.subplots(figsize=(12, 6))
        for col in df_base100.columns:
            if col == "Moyenne":
                ax.plot(df_base100.index, df_base100[col], label=col, color="black", linewidth=2, linestyle="--")
            elif col in etf_selection:
                ax.plot(df_base100.index, df_base100[col], label=col)

            
        ax.set_title(f"Comparaison des ETFs (Base 100 au {pd.to_datetime(date_base).date()})")
        ax.set_xlabel("Date")
        ax.set_ylabel("Performance")
        ax.legend()
        ax.grid(True)

        st.pyplot(fig)

    # Fonction pour colorer la police de texte en fonction de la variation
    def color_variation(val):
        color = 'green' if val > 0 else 'red'  # Vert si positif, rouge si négatif
        return f'color: {color}'  # Change la couleur de la police de texte

    # Calcul de la durée en jours
    duration_days = (df_base100.index[-1] - pd.to_datetime(date_base)).days

    # Calcul de la variation en pourcentage par rapport à la base 100
    variation = (df_base100.iloc[-1] / df_base100.loc[pd.to_datetime(date_base)] - 1) * 100

    # Calcul du nombre d'années
    n_years = duration_days / 365.25

    # Calcul de la variation annualisée (CAGR) pour chaque ETF et la moyenne
    annualized_variation = {}
    for col in df_base100.columns:
        initial_value = df_base100.loc[pd.to_datetime(date_base), col]
        final_value = df_base100[col].iloc[-1]
        cagr = (final_value / initial_value) ** (1 / n_years) - 1
        annualized_variation[col] = cagr

    # Création du DataFrame des variations avec le taux annualisé
    variation_df = pd.DataFrame({
        'Variation (%)': variation,  # Variation en pourcentage
        'Variation Annualisée (%)': [annualized_variation[col] * 100 for col in variation.index]  # Taux annualisé en %
    }, index=variation.index)

    # Mise à jour du titre avec les informations de date et durée
    st.subheader(f"📈 Variation depuis la date d'origine sélectionnée ({date_base.date()}) sur {duration_days} jours")

    # Appliquer le formatage en pourcentage sur les valeurs avant la mise en couleur
    variation_df_formatted = variation_df.applymap(lambda x: f"{x:.2f}%")

    # Appliquer la coloration sur les valeurs numériques
    variation_df_styled = variation_df.style.applymap(color_variation)

    # Affichage du tableau des variations avec mise en couleur de la police
    st.dataframe(variation_df_styled.format({'Variation (%)': '{:.2f}%', 'Variation Annualisée (%)': '{:.2f}%'}))