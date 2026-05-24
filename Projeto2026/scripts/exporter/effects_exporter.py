from rdflib import Graph, Literal
from rdflib.namespace import RDF, XSD

from common import MC, EXPORT_DIR, load_dataset


def export_effects():
    g = Graph()
    g.bind("", MC)

    data = load_dataset("effects.json")

    for e in data:
        effect_name = e["name"].replace(" ", "_")
        uri = MC[effect_name]

        g.add((uri, RDF.type, MC.Effect))

        if e["type"] == "good":
            g.add((uri, RDF.type, MC.BeneficialEffect))
        elif e["type"] == "bad":
            g.add((uri, RDF.type, MC.HarmfulEffect))

        g.add((uri, MC.effectID, Literal(e["id"], datatype=XSD.integer)))
        g.add((uri, MC.hasName, Literal(e["name"], datatype=XSD.string)))
        g.add((uri, MC.hasDisplayName, Literal(e["displayName"], datatype=XSD.string)))
        g.add((uri, MC.effectType, Literal(e["type"], datatype=XSD.string)))

    output_path = EXPORT_DIR / "data_effects.ttl"
    g.serialize(output_path, format="turtle")

    print(f"Exported {len(data)} effects to {output_path}")


if __name__ == "__main__":
    export_effects()