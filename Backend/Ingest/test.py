import requests

import csv

from dotenv import load_dotenv
import os

load_dotenv()
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")


r = requests.get(
    "https://newsapi.org/v2/everything",
    params={
        "q":"health",
        "language": "en",
        "pageSize": 5,
        "apiKey": NEWSAPI_KEY
    },
    timeout=30,
)

data = r.json()
print(data)