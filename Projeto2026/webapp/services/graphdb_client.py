import requests
from config import GRAPHDB_ENDPOINT, GRAPHDB_UPDATE_ENDPOINT

def run_select(query: str):
    response = requests.post(
        GRAPHDB_ENDPOINT,
        data={"query": query},
        headers={"Accept": "application/sparql-results+json"},
        timeout=30
    )
    response.raise_for_status()
    return response.json()

def run_update(update_query: str):
    response = requests.post(
        GRAPHDB_UPDATE_ENDPOINT,
        data=update_query,
        headers={"Content-Type": "application/sparql-update"},
        timeout=30
    )
    response.raise_for_status()
    return True

def run_ask(query: str):
    response = requests.post(
        GRAPHDB_ENDPOINT,
        data={"query": query},
        headers={"Accept": "application/sparql-results+json"},
        timeout=30
    )
    response.raise_for_status()
    return response.json().get("boolean", False)