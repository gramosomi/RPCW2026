from rdflib import Graph, Literal
from rdflib.namespace import RDF, XSD

from common import MC, EXPORT_DIR, load_dataset


def enchantment_class_from_category(category):
    if not category:
        return "Enchantment"

    return category.capitalize() + "Enchantment"


def export_enchantments():
    g = Graph()
    g.bind("", MC)

    data = load_dataset("enchantments.json")

    for e in data:
        uri = MC[e["name"]]
        category = e.get("category", "generic")
        specific_class = enchantment_class_from_category(category)

        g.add((uri, RDF.type, MC.Enchantment))
        g.add((uri, RDF.type, MC[specific_class]))

        g.add((uri, MC.enchantmentID, Literal(e["id"], datatype=XSD.integer)))
        g.add((uri, MC.hasName, Literal(e["name"], datatype=XSD.string)))
        g.add((uri, MC.hasDisplayName, Literal(e["displayName"], datatype=XSD.string)))
        g.add((uri, MC.maxLevel, Literal(e["maxLevel"], datatype=XSD.integer)))
        g.add((uri, MC.enchantmentWeight, Literal(e["weight"], datatype=XSD.integer)))
        g.add((uri, MC.isCurse, Literal(e.get("curse", False), datatype=XSD.boolean)))
        g.add((uri, MC.isDiscoverable, Literal(e.get("discoverable", True), datatype=XSD.boolean)))
        g.add((uri, MC.isTradeable, Literal(e.get("tradeable", True), datatype=XSD.boolean)))
        g.add((uri, MC.isTreasureOnly, Literal(e.get("treasureOnly", False), datatype=XSD.boolean)))

        if "minCost" in e:
            g.add((uri, MC.minCostA, Literal(e["minCost"].get("a", 0), datatype=XSD.integer)))
            g.add((uri, MC.minCostB, Literal(e["minCost"].get("b", 0), datatype=XSD.integer)))

        if "maxCost" in e:
            g.add((uri, MC.maxCostA, Literal(e["maxCost"].get("a", 0), datatype=XSD.integer)))
            g.add((uri, MC.maxCostB, Literal(e["maxCost"].get("b", 0), datatype=XSD.integer)))

        for excluded_name in e.get("exclude", []):
            excluded_uri = MC[excluded_name]
            g.add((uri, MC.incompatibleWith, excluded_uri))
            g.add((excluded_uri, MC.incompatibleWith, uri))

    output_path = EXPORT_DIR / "data_enchantments.ttl"
    g.serialize(output_path, format="turtle")

    print(f"Exported {len(data)} enchantments to {output_path}")


if __name__ == "__main__":
    export_enchantments()