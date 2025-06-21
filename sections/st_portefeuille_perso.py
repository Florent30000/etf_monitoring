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

    etf_options = list(df_all.columns)
    default_selection = ["MSCI World Large cap", "Physical Gold", "Physical Bitcoin"
                        ]
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

