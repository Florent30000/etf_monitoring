# bq_utils.py

import streamlit as st
import json
from google.oauth2 import service_account
from google.cloud import bigquery

@st.cache_resource
def get_bigquery_client():
    service_account_info = st.secrets["GOOGLE_CREDENTIALS"]
    credentials = service_account.Credentials.from_service_account_info(service_account_info)
    client = bigquery.Client(credentials=credentials, project=credentials.project_id)
    return client
