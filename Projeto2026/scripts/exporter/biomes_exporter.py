from rdflib import Graph, Literal
from rdflib.namespace import RDF, XSD

from common import MC, EXPORT_DIR, load_dataset


def export_biomes():
    g = Graph()
    g.bind("", MC)

    data = load_dataset("biomes.json")

    for b in data:
        uri = MC[b["name"]]

        g.add((uri, RDF.type, MC.Biome))

        dimension = b.get("dimension", "").lower()

        if dimension == "overworld":
            g.add((uri, RDF.type, MC.OverworldBiome))
        elif dimension == "nether":
            g.add((uri, RDF.type, MC.NetherBiome))
        elif dimension == "end":
            g.add((uri, RDF.type, MC.EndBiome))

        g.add((uri, MC.biomeID, Literal(b["id"], datatype=XSD.integer)))
        g.add((uri, MC.hasName, Literal(b["name"], datatype=XSD.string)))
        g.add((uri, MC.hasDisplayName, Literal(b["displayName"], datatype=XSD.string)))

        if "category" in b:
            g.add((uri, MC.biomeCategory, Literal(b["category"], datatype=XSD.string)))

        if "temperature" in b:
            g.add((uri, MC.temperature, Literal(b["temperature"], datatype=XSD.float)))

        if "has_precipitation" in b:
            g.add((uri, MC.hasPrecipitation, Literal(b["has_precipitation"], datatype=XSD.boolean)))

    output_path = EXPORT_DIR / "data_biomes.ttl"
    g.serialize(output_path, format="turtle")

    print(f"Exported {len(data)} biomes to {output_path}")


if __name__ == "__main__":
    export_biomes()