import os
import requests
import pandas as pd
from dotenv import load_dotenv

# --- Charger les variables d’environnement ---
load_dotenv()
api_key = os.getenv("EOD_API_KEY")
if not api_key:
    raise ValueError("Clé API EOD manquante")

# Ticker et configuration
symbol = "XD9U.XETRA"  # Format requis : TICKER.EXCHANGE
start_date = "2000-01-01"
end_date = "2024-12-31"

# --- URL de l'API ---
url = f"https://eodhistoricaldata.com/api/eod/{symbol}?from={start_date}&to={end_date}&api_token={api_key}&period=d&fmt=csv"

# --- Requête & chargement dans pandas ---
response = requests.get(url)

if response.status_code == 200:
    from io import StringIO
    df = pd.read_csv(StringIO(response.text))
    print(df.head())
else:
    print("❌ Erreur lors de la requête :", response.status_code)
    print(response.text)
