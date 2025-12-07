# bq_utils_import.py
# fournit une fonction get_bigquery_client() 
# qui permet de créer automatiquement un client 
# BigQuery en utilisant la meilleure méthode 
# d’authentification disponible selon l’environnement 
# (GitHub Actions, variable d’environnement locale 
# ou authentification gcloud).
# cette fonction est appelée dans tous les scripts
# d'import dans GCP des données

import os
import json
from google.cloud import bigquery
from google.auth.exceptions import DefaultCredentialsError
from google.oauth2 import service_account

def get_bigquery_client():
    try:
        # 1. GitHub Actions ou exécution automatisée avec variable JSON
        if "GOOGLE_APPLICATION_CREDENTIALS_JSON" in os.environ:
            creds_info = json.loads(os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"])
            credentials = service_account.Credentials.from_service_account_info(creds_info)
            return bigquery.Client(credentials=credentials, project=credentials.project_id)

        # 2. Local avec variable d’environnement vers un fichier .json
        elif "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
            return bigquery.Client()

        # 3. Local avec `gcloud auth application-default login`
        else:
            return bigquery.Client()

    except DefaultCredentialsError as e:
        raise RuntimeError(
            "Impossible de trouver les identifiants GCP. "
            "Configurez GOOGLE_APPLICATION_CREDENTIALS ou GOOGLE_APPLICATION_CREDENTIALS_JSON."
        ) from e
