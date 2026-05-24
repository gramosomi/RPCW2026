import subprocess
import sys
from pathlib import Path

from rdflib import Graph
from rdflib.namespace import RDF, OWL

ROOT = Path(__file__).resolve().parents[1]
EXPORTER_RUNNER = ROOT / "scripts" / "exporter" / "run_all.py"
CLASSES_TTL = ROOT / "ontology" / "classes.ttl"
DATA_DIR = ROOT / "scripts" / "ontology"
OUTPUT_TTL = ROOT / "ontology" / "minecraft.ttl"


def main():
    print("1. Running exporters...")
    subprocess.run([sys.executable, str(EXPORTER_RUNNER)], check=True)

    print("2. Building final ontology...")
    graph = Graph()

    graph.parse(CLASSES_TTL, format="turtle")

    for ttl_file in sorted(DATA_DIR.glob("data_*.ttl")):
        print(f"   Loading {ttl_file.name}")
        graph.parse(ttl_file, format="turtle")

    print("3. Serializing ontology...")
    graph.serialize(destination=OUTPUT_TTL, format="turtle")

    print("4. Validating generated TTL...")
    validation_graph = Graph()
    validation_graph.parse(OUTPUT_TTL, format="turtle")

    classes = set(validation_graph.subjects(RDF.type, OWL.Class))
    object_properties = set(validation_graph.subjects(RDF.type, OWL.ObjectProperty))
    data_properties = set(validation_graph.subjects(RDF.type, OWL.DatatypeProperty))

    print()
    print(f"Generated: {OUTPUT_TTL}")
    print(f"Triples: {len(validation_graph)}")
    print(f"Classes: {len(classes)}")
    print(f"Object properties: {len(object_properties)}")
    print(f"Data properties: {len(data_properties)}")


if __name__ == "__main__":
    main()