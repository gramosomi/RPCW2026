import csv
import json
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, OWL

g = Graph()
g.parse("medical.ttl", format="turtle")

MED = Namespace("http://www.example.org/disease-ontology#")
g.bind("", MED)

def clean_uri(text):
    cleaned = text.strip().replace('"', '')
    
    cleaned = cleaned.title()
    
    return cleaned.replace(" ", "_")

with open('Disease_Syntoms.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader) # Ignorar cabeçalho
    for row in reader:
        disease_name = clean_uri(row[0])
        disease_uri = MED[disease_name]
        
        g.add((disease_uri, RDF.type, MED.Disease))
        
        for symptom in row[1:]:
            if symptom.strip():
                symptom_uri = MED[clean_uri(symptom)]
                g.add((symptom_uri, RDF.type, MED.Symptom))
                g.add((disease_uri, MED.hasSymptom, symptom_uri))

g.add((MED.description, RDF.type, OWL.DatatypeProperty))

with open('Disease_Description.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        disease_uri = MED[clean_uri(row[0])]
        description = row[1].strip()
        g.add((disease_uri, MED.description, Literal(description)))

g.serialize(destination="med_doencas.ttl", format="turtle")

with open('Disease_Treatment.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        disease_uri = MED[clean_uri(row[0])]
        
        for treatment in row[1:]:
            if treatment.strip():
                treatment_uri = MED[clean_uri(treatment)]
                g.add((treatment_uri, RDF.type, MED.Treatment))
                g.add((disease_uri, MED.hasTreatment, treatment_uri))

g.serialize(destination="med_tratamentos.ttl", format="turtle")

with open('doentes.json', 'r', encoding='utf-8') as f:
    doentes = json.load(f)
    
    for i, doente in enumerate(doentes):
        patient_uri = MED[f"Patient_{i+1}"]
        g.add((patient_uri, RDF.type, MED.Patient))
        
        g.add((patient_uri, MED.name, Literal(doente['nome'])))
        
        for symptom in doente['sintomas']:
            symptom_uri = MED[clean_uri(symptom)]
            g.add((patient_uri, MED.exhibitsSymptom, symptom_uri))

g.serialize(destination="med_doentes.ttl", format="turtle")