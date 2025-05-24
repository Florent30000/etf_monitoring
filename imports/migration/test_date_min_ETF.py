import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("EOD_API_KEY")

ticker = "SXR8.XETRA"
api_key = os.getenv("EOD_API_KEY")
url = (
    f"https://eodhistoricaldata.com/api/eod/{ticker}"
    f"?from=1990-01-01&to=2023-12-31"
    f"&api_token={api_key}&period=d&fmt=csv"
)

response = requests.get(url)
print(response.text[:1000])  # affiche un extrait
