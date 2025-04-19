import streamlit as st
import yfinance as yf
import pandas as pd

# Exemple de téléchargement de données (tu peux adapter selon ton code Jupyter)
ticker = "XD9U.MI"
data = yf.download(ticker, start="2022-01-01")

# Affichage de données dans Streamlit
st.title('Analyse des données ETF')
st.write(f"### Données de l'ETF {ticker}")
st.write(data)

# Affichage d'un graphique simple
st.line_chart(data['Close'])