import yfinance as yf
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import os

# --- Paramètres de l'ETF ---
ticker = "DTLA.L"
default_start_date = "2000-01-01"
table_name = ticker.lower().replace(".", "_")

# --- Paramètres BigQuery ---
project_id = "etf-monitoring"
dataset_id = "etf_data"
full_table_id = f"{project_id}.{dataset_id}.{table_name}"

# --- Authentification ---
client = bigquery.Client()

# --- Étape 1 : vérifier la dernière date dans la table ---
query = f"SELECT MAX(Date) as max_date FROM `{full_table_id}`"
try:
    query_job = client.query(query)
    result = query_job.result()
    last_date_in_db = next(result).max_date

    if last_date_in_db is not None:
        start_date = pd.to_datetime(last_date_in_db) + pd.Timedelta(days=1)
        print(f"Dernière date en base : {last_date_in_db}. Nouvelle date de début : {start_date.date()}")
    else:
        start_date = pd.to_datetime(default_start_date)
        print(f"La table est vide. On démarre à partir de : {start_date.date()}")
except Exception as e:
    print(f"La table '{full_table_id}' n'existe pas encore ou erreur de requête. Création à partir de {default_start_date}")
    start_date = pd.to_datetime(default_start_date)

# --- Étape 2 : télécharger les nouvelles données ---
print(f"Téléchargement des données à partir du {start_date.date()} pour l'ETF {ticker}...")
data = yf.download(ticker, start=start_date)

# --- Étape 3 : insérer les données dans BigQuery ---
if not data.empty:
    data.reset_index(inplace=True)
    data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]

    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_APPEND",
        schema=[bigquery.SchemaField("Date", "DATE")],
        autodetect=True,
    )
    job = client.load_table_from_dataframe(data, full_table_id, job_config=job_config)
    job.result()
    print(f"✅ {len(data)} lignes ajoutées à la table '{full_table_id}' dans BigQuery")
else:
    print("❌ Aucune nouvelle donnée à insérer.")
