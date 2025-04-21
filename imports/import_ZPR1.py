import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine
import os
import sqlite3

# --- Paramètres de l'ETF ---
ticker = "ZPR1.DE"
default_start_date = "2000-01-01"  # Si la table est vide ou n'existe pas

# --- Configuration du nom de table et du chemin de la base ---
table_name = ticker.lower().replace(".", "_")  # Nom SQL-friendly
os.makedirs("data", exist_ok=True)  # Créer le dossier s’il n’existe pas
db_path = os.path.join("data", "etf_data.db")

# --- Connexion à SQLite ---
engine = create_engine(f"sqlite:///{db_path}")
conn = sqlite3.connect(db_path)

# --- Étape 1 : vérifier la dernière date dans la base ---
query = f"SELECT MAX(Date) FROM {table_name}"
try:
    result = pd.read_sql_query(query, conn)
    last_date_in_db = result.iloc[0, 0]  # Récupère la valeur unique de la requête

    if last_date_in_db is not None:
        # Convertit en datetime et ajoute un jour pour éviter les doublons
        start_date = pd.to_datetime(last_date_in_db) + pd.Timedelta(days=1)
        print(f"Dernière date en base : {last_date_in_db}. Nouvelle date de début : {start_date.date()}")
    else:
        # Si la table existe mais est vide
        start_date = pd.to_datetime(default_start_date)
        print(f"La table est vide. On démarre à partir de : {start_date.date()}")

except Exception as e:
    # Si la table n'existe pas encore
    print(f"La table '{table_name}' n'existe pas encore. Création à partir de {default_start_date}")
    start_date = pd.to_datetime(default_start_date)

# --- Étape 2 : télécharger les nouvelles données ---
print(f"Téléchargement des données à partir du {start_date.date()} pour l'ETF {ticker}...")
data = yf.download(ticker, start=start_date)

# --- Étape 3 : insérer les données dans la base ---
if not data.empty:
    data.reset_index(inplace=True)  # Fait de "Date" une colonne

    # Nettoyage des noms de colonnes pour éviter le texte indésirable
    data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]

    # Vérifier le type de la colonne Date
    print(f"Type de la colonne Date avant insertion : {data['Date'].dtype}")

    data.to_sql(table_name, con=engine, if_exists="append", index=False)
    print(f"✅ {len(data)} lignes ajoutées à la table '{table_name}' dans {db_path}")
else:
    print("❌ Aucune nouvelle donnée à insérer.")
