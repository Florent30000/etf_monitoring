import os
import pandas as pd
from google.cloud import bigquery
from sqlalchemy import create_engine
from dotenv import load_dotenv

# --- Charger les variables d’environnement ---
load_dotenv()

# --- Paramètres ---
sqlite_path = "data/etf_data.db"  # chemin de ta base locale
table_name = "zpr1_de"         # nom de la table dans SQLite
bq_project = "etf-monitoring"     # nom du projet GCP
bq_dataset = "etf_data"           # nom du dataset BigQuery
bq_table = f"{bq_project}.{bq_dataset}.zpr1_xetra"

# --- Connexion SQLite ---
engine = create_engine(f"sqlite:///{sqlite_path}")
df = pd.read_sql_table(table_name, con=engine)

# --- Vérification des colonnes ---
print(f"Colonnes détectées dans SQLite : {df.columns.tolist()}")
if "Date" in df.columns:
    df["Date"] = pd.to_datetime(df["Date"])
    df.sort_values("Date", inplace=True)
else:
    raise ValueError("Colonne 'Date' introuvable dans la table SQLite.")

# --- Connexion BigQuery ---
client = bigquery.Client()

# --- Configuration du job BigQuery ---
job_config = bigquery.LoadJobConfig(
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,  # on écrase la table
    schema=[
        bigquery.SchemaField("Date", "DATE"),
        bigquery.SchemaField("Close", "FLOAT"),
    ],
)

# --- Envoi dans BigQuery ---
print(f"Envoi de {len(df)} lignes vers {bq_table}...")
job = client.load_table_from_dataframe(df[["Date", "Close"]], bq_table, job_config=job_config)
job.result()  # attendre la fin du job

print(f"✅ Table '{bq_table}' mise à jour avec succès.")
