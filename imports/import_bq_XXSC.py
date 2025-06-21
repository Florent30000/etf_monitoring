import os
import pandas as pd
import requests
from datetime import datetime
from io import StringIO
from dotenv import load_dotenv
from google.cloud import bigquery
from bq_utils_import import get_bigquery_client

# --- Charger les variables d’environnement ---
load_dotenv()
api_key = os.getenv("EOD_API_KEY")
if not api_key:
    raise ValueError("Clé API EOD manquante")

# --- Paramètres de l'ETF ---
ticker = "xxsc.XETRA"  # format EOD
table_name = ticker.lower().replace(".", "_")
bq_project = "etf-monitoring"
bq_dataset = "etf_data"
bq_table = f"{bq_project}.{bq_dataset}.{table_name}"
default_start_date = pd.to_datetime("2000-01-01")

# --- Initialiser le client BigQuery ---
client = get_bigquery_client()

# --- Vérifier la dernière date en base ---
query = f"""
    SELECT MAX(Date) as max_date
    FROM `{bq_table}`
"""
try:
    query_job = client.query(query)
    result = query_job.result()
    last_date_in_db = next(result).max_date

    if last_date_in_db:
        start_date = pd.to_datetime(last_date_in_db) + pd.Timedelta(days=1)
        print(f"Dernière date en base : {last_date_in_db}. Nouvelle date de début : {start_date.date()}")
    else:
        start_date = default_start_date
        print(f"La table est vide. Démarrage à partir de : {start_date.date()}")

except Exception as e:
    print(f"La table '{bq_table}' n'existe pas encore ou erreur : {e}")
    start_date = default_start_date

# --- Télécharger les données depuis EOD Historical Data ---
print(f"Téléchargement des données EOD pour {ticker}...")

url = (
    f"https://eodhistoricaldata.com/api/eod/{ticker}"
    f"?from={start_date.date()}"
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

# Supprimer les lignes invalides qui ne contiennent pas une vraie date
df = df[df["Date"].str.match(r"^\d{4}-\d{2}-\d{2}$", na=False)].copy()

# Conversion après nettoyage
df["Date"] = pd.to_datetime(df["Date"])

df = df[df["Date"] >= start_date]
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
    print("❌ Aucune nouvelle donnée à insérer.")
