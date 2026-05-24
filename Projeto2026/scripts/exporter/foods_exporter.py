from rdflib import Graph, Literal
from rdflib.namespace import RDF, XSD

from common import MC, EXPORT_DIR, load_dataset


def export_foods():
    g = Graph()
    g.bind("", MC)

    data = load_dataset("foods.json")

    for food in data:
        uri = MC[food["name"]]
        display_name = food.get("displayName", "")

        g.add((uri, RDF.type, MC.Food))

        if display_name.startswith("Cooked"):
            g.add((uri, RDF.type, MC.CookedFood))
        elif display_name.startswith("Raw"):
            g.add((uri, RDF.type, MC.RawFood))

        g.add((uri, MC.itemID, Literal(food["id"], datatype=XSD.integer)))
        g.add((uri, MC.hasName, Literal(food["name"], datatype=XSD.string)))
        g.add((uri, MC.hasDisplayName, Literal(food["displayName"], datatype=XSD.string)))

        if "stackSize" in food:
            g.add((uri, MC.stackSize, Literal(food["stackSize"], datatype=XSD.integer)))

        if "foodPoints" in food:
            g.add((uri, MC.foodPoints, Literal(food["foodPoints"], datatype=XSD.float)))

        if "saturation" in food:
            g.add((uri, MC.saturation, Literal(food["saturation"], datatype=XSD.float)))

        if "saturationRatio" in food:
            g.add((uri, MC.saturationRatio, Literal(food["saturationRatio"], datatype=XSD.float)))

        if "effectiveQuality" in food:
            g.add((uri, MC.effectiveQuality, Literal(food["effectiveQuality"], datatype=XSD.float)))

    output_path = EXPORT_DIR / "data_foods.ttl"
    g.serialize(output_path, format="turtle")

    print(f"Exported {len(data)} foods to {output_path}")


if __name__ == "__main__":
    export_foods()