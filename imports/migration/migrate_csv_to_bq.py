import os
import pandas as pd
from google.cloud import bigquery
from dotenv import load_dotenv

# --- Charger les variables d’environnement ---
load_dotenv()

# --- Paramètres ---
csv_path = "data/parite_EUR-USD.csv"
bq_project = "etf-monitoring"
bq_dataset = "etf_data"
table_name = "eur_usd_parity"
bq_table = f"{bq_project}.{bq_dataset}.{table_name}"

# --- Lire le fichier CSV avec séparateur ";" ---
df = pd.read_csv(csv_path, sep=";")

print(f"Colonnes détectées dans le CSV : {df.columns.tolist()}")

if "Date" in df.columns and "Close" in df.columns:
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)
    df["Close"] = df["Close"].str.replace(",", ".").astype(float)
    df.sort_values("Date", inplace=True)
else:
    raise ValueError("Colonnes 'Date' ou 'Close' introuvables dans le fichier CSV.")

# --- Connexion BigQuery ---
client = bigquery.Client()

# --- Configuration du job ---
job_config = bigquery.LoadJobConfig(
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    schema=[
        bigquery.SchemaField("Date", "DATE"),
        bigquery.SchemaField("Close", "FLOAT"),
    ],
)

# --- Envoi vers BigQuery ---
print(f"Envoi de {len(df)} lignes vers {bq_table}...")
job = client.load_table_from_dataframe(df[["Date", "Close"]], bq_table, job_config=job_config)
job.result()

print(f"✅ Table '{bq_table}' créée/mise à jour avec succès.")

