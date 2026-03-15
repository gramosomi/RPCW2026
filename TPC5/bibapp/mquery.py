from SPARQLWrapper import SPARQLWrapper, JSON

GRAPHDB_ENDPOINT = "http://localhost:7200/repositories/biblioteca_temporal"

def execute_query(query):
    sparql = SPARQLWrapper(GRAPHDB_ENDPOINT)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    try:
        return sparql.query().convert()
    except Exception as e:
        print(f"Error executing query: {e}")
        return None