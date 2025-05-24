import os
import pandas as pd
import requests
from datetime import datetime
from io import StringIO
from dotenv import load_dotenv
from google.cloud import bigquery
import sys
from pathlib import Path

# Ajouter le dossier parent au sys.path
parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

from bq_utils_import import get_bigquery_client

# --- Charger les variables d’environnement ---
load_dotenv()
api_key = os.getenv("EOD_API_KEY")
if not api_key:
    raise ValueError("Clé API EOD manquante")

# --- Paramètres de l'ETF ---
ticker = "SXR8.XETRA"  # format EOD
table_name = ticker.lower().replace(".", "_")
bq_project = "etf-monitoring"
bq_dataset = "etf_data"
bq_table = f"{bq_project}.{bq_dataset}.{table_name}"
earliest_date_to_fetch = pd.to_datetime("1990-01-01")  # ou selon l'historique dispo

# --- Initialiser le client BigQuery ---
client = get_bigquery_client()

# --- Récupérer la date la plus ancienne déjà en base ---
query = f"""
    SELECT MIN(Date) as min_date
    FROM `{bq_table}`
"""
try:
    query_job = client.query(query)
    result = query_job.result()
    first_date_in_db = next(result).min_date

    if first_date_in_db:
        end_date = pd.to_datetime(first_date_in_db) - pd.Timedelta(days=1)
        print(f"Première date en base : {first_date_in_db}. Fin de téléchargement : {end_date.date()}")
    else:
        end_date = pd.to_datetime("today")
        print(f"Aucune donnée existante. Utilisation de la date actuelle : {end_date.date()}")

except Exception as e:
    print(f"Erreur lors de la récupération de la première date ou table inexistante : {e}")
    end_date = pd.to_datetime("today")

# --- Télécharger les données depuis EOD Historical Data ---
print(f"Téléchargement des données EOD pour {ticker} jusqu'à {end_date.date()}...")

url = (
    f"https://eodhistoricaldata.com/api/eod/{ticker}"
    f"?to={end_date.date()}"
    f"&from={earliest_date_to_fetch.date()}"
    f"&api_token={api_key}&period=d&fmt=csv"
)

response = requests.get(url)
if response.status_code != 200 or not response.text.strip():
    print("❌ Erreur API EOD ou aucune donnée reçue")
    print(response.text)
    exit()

# --- Préparer les données ---
df = pd.read_csv(StringIO(response.text))
print("Colonnes reçues :", df.columns)

if "Date" not in df.columns or "Close" not in df.columns:
    print("❌ Colonnes attendues non trouvées dans la réponse API")
    exit()

df = df[["Date", "Close"]].copy()
df = df[df["Date"].str.match(r"^\d{4}-\d{2}-\d{2}$", na=False)].copy()
df["Date"] = pd.to_datetime(df["Date"])

df = df[df["Date"] <= end_date]
df.sort_values("Date", inplace=True)

# --- Écriture dans BigQuery ---
if not df.empty:
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        schema=[
            bigquery.SchemaField("Date", "DATE"),
            bigquery.SchemaField("Close", "FLOAT"),
        ],
    )

    job = client.load_table_from_dataframe(df, bq_table, job_config=job_config)
    job.result()  # attendre la fin

    print(f"✅ {len(df)} lignes insérées dans {bq_table}")
else:
    print("❌ Aucune donnée antérieure à insérer.")
