from rdflib import Graph, Literal
from rdflib.namespace import RDF, XSD

from common import MC, EXPORT_DIR, load_dataset
from classifiers import classify_entity


def export_entities():
    g = Graph()
    g.bind("", MC)

    data = load_dataset("entities.json")

    for e in data:
        uri = MC[e["name"]]

        specific_class = classify_entity(e)

        # Tipo genérico
        g.add((uri, RDF.type, MC.Entity))

        # Tipo específico
        g.add((uri, RDF.type, MC[specific_class]))

        # Classes superiores úteis para navegação sem depender totalmente do reasoner
        if specific_class in {"HostileMob", "PassiveMob", "Animal", "AmbientMob", "NeutralMob", "BossMob", "TameableMob"}:
            g.add((uri, RDF.type, MC.Mob))

        if specific_class == "Animal":
            g.add((uri, RDF.type, MC.PassiveMob))

        if specific_class == "ProjectileEntity":
            g.add((uri, RDF.type, MC.ProjectileEntity))

        g.add((uri, MC.entityID, Literal(e["id"], datatype=XSD.integer)))
        g.add((uri, MC.hasName, Literal(e["name"], datatype=XSD.string)))
        g.add((uri, MC.hasDisplayName, Literal(e["displayName"], datatype=XSD.string)))

        if "width" in e:
            g.add((uri, MC.entityWidth, Literal(e["width"], datatype=XSD.float)))

        if "height" in e:
            g.add((uri, MC.entityHeight, Literal(e["height"], datatype=XSD.float)))

    output_path = EXPORT_DIR / "data_entities.ttl"
    g.serialize(output_path, format="turtle")

    print(f"Exported {len(data)} entities to {output_path}")


if __name__ == "__main__":
    export_entities()