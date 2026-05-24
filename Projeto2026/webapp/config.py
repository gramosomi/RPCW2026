GRAPHDB_ENDPOINT = "http://localhost:7200/repositories/minecraft"
GRAPHDB_UPDATE_ENDPOINT = "http://localhost:7200/repositories/minecraft/statements"

ONTOLOGY_NS = "http://rpcw.di.uminho.pt/2026/minecraft/"

PREFIXES = f"""
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX mc: <{ONTOLOGY_NS}>
"""

