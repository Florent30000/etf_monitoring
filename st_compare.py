import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import numpy as np

# Titre
st.title("Comparaison des 4 ETFs (base 100 avec moyenne)")

# Connexion à la base
db_path = "data/etf_data.db"
conn = sqlite3.connect(db_path)

# Chargement des données
@st.cache_data
def charger_donnees():
    df_dtla = pd.read_sql("SELECT Date, Close FROM dtla_l", conn, parse_dates=["Date"]).set_index("Date")
    df_xd9u = pd.read_sql("SELECT Date, Close FROM xd9u_mi", conn, parse_dates=["Date"]).set_index("Date")
    df_xgdu = pd.read_sql("SELECT Date, Close FROM xgdu_mi", conn, parse_dates=["Date"]).set_index("Date")
    df_zpr1 = pd.read_sql("SELECT Date, Close FROM zpr1_de", conn, parse_dates=["Date"]).set_index("Date")
    return df_dtla, df_xd9u, df_xgdu, df_zpr1

df_dtla, df_xd9u, df_xgdu, df_zpr1 = charger_donnees()

# Création d’un DataFrame combiné
df_all = pd.concat([
    df_dtla.rename(columns={"Close": "DTLA"}),
    df_xd9u.rename(columns={"Close": "XD9U"}),
    df_xgdu.rename(columns={"Close": "XGDU"}),
    df_zpr1.rename(columns={"Close": "ZPR1"})
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
    "📅 Choisissez la date d’origine (base 100) :",
    options=date_labels,
    value=date_labels[0]
)
date_base = date_mapping[selected_label_base]

# 🔄 Nouvel affichage : slider de début d'affichage
all_dates = df_all.index
date_labels_all = [d.strftime("%Y-%m-%d") for d in all_dates]
date_mapping_all = dict(zip(date_labels_all, all_dates))

selected_start_label = st.select_slider(
    "📆 Choisissez la date de début d’affichage du graphique :",
    options=date_labels_all,
    value=date_labels_all[0]
)
date_start = date_mapping_all[selected_start_label]

# Rebase à 100
df_base100 = df_all / df_all.loc[date_base] * 100
df_base100["Moyenne"] = df_base100.mean(axis=1)

# Filtrage à partir de la date d'affichage
df_base100 = df_base100[df_base100.index >= date_start]

# Sélectionner plusieurs ETFs (au moins 2, au maximum tous)
etf_selection = st.multiselect(
    "🔍 Sélectionnez les ETFs à afficher :",
    options=[col for col in df_base100.columns if col != "Moyenne"],
    default=df_base100.columns[:2].tolist()
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