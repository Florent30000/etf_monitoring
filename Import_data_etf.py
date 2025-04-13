import yfinance as yf
import os


# Fonction pour télécharger les données d'un ETF
def download_etf_data(ticker, start_date, output_file):
    print(f"Téléchargement des données de l'ETF {ticker}...")

    # Récupérer les données historiques de l'ETF
    data = yf.download(ticker, start=start_date)

    # Vérifier si des données ont été récupérées
    if not data.empty:
        # Trouver la dernière date disponible
        last_date = data.index[-1]  # La dernière ligne de l'index est la date la plus récente
        print(f"Date la plus récente disponible : {last_date.strftime('%Y-%m-%d')}")

        # Enregistrer les données dans un fichier CSV
        data.to_csv(output_file)
        print(f"Les données ont été enregistrées dans {output_file}")

        return last_date  # Retourne la dernière date pour l'utiliser si nécessaire
    else:
        print("Aucune donnée disponible pour cet ETF.")
        return None


# Paramètres de l'ETF et du fichier
ticker = "XD9U.MI"  # Ticker avec suffixe .MI
start_date = "2000-01-01"  # Date de début
output_file = "xd9u_historical.csv"  # Fichier de sortie

# Vérifier si le fichier existe déjà
if os.path.exists(output_file):
    print(f"Le fichier {output_file} existe déjà. Il sera écrasé.")

# Télécharger les données et obtenir la dernière date disponible
last_date = download_etf_data(ticker, start_date, output_file)

# Optionnel : Si tu veux faire quelque chose avec la dernière date (par exemple l'afficher)
if last_date:
    print(f"La date la plus récente des données est : {last_date.strftime('%Y-%m-%d')}")

