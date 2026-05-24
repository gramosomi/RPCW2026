from rdflib import Graph, Literal
from rdflib.namespace import RDF, XSD

from common import MC, EXPORT_DIR, load_dataset
from classifiers import classify_item


def export_items():
    g = Graph()
    g.bind("", MC)

    items = load_dataset("items.json")
    enchantments = load_dataset("enchantments.json")

    ench_by_cat = {}

    for enchantment in enchantments:
        category = enchantment.get("category")

        if category:
            ench_by_cat.setdefault(category, []).append(MC[enchantment["name"]])

    for item in items:
        uri = MC[item["name"]]

        g.add((uri, RDF.type, MC.Item))

        specific_class, tier = classify_item(item)

        if specific_class:
            g.add((uri, RDF.type, MC[specific_class]))

        if tier:
            g.add((uri, MC.madeOfMaterial, MC[tier]))

        categories = item.get("enchantCategories", [])

        if "weapon" in categories or "melee_weapon" in categories or "sharp_weapon" in categories:
            g.add((uri, RDF.type, MC.Weapon))

        if "mining" in categories:
            g.add((uri, RDF.type, MC.Tool))

        if "armor" in categories or "head_armor" in categories or "leg_armor" in categories or "foot_armor" in categories:
            g.add((uri, RDF.type, MC.Armor))

        g.add((uri, MC.itemID, Literal(item["id"], datatype=XSD.integer)))
        g.add((uri, MC.hasName, Literal(item["name"], datatype=XSD.string)))
        g.add((uri, MC.hasDisplayName, Literal(item["displayName"], datatype=XSD.string)))

        if "stackSize" in item:
            g.add((uri, MC.stackSize, Literal(item["stackSize"], datatype=XSD.integer)))

        if "maxDurability" in item:
            g.add((uri, MC.maxDurability, Literal(item["maxDurability"], datatype=XSD.integer)))

        for category in categories:
            for enchantment_uri in ench_by_cat.get(category, []):
                g.add((uri, MC.canBeEnchantedWith, enchantment_uri))
                g.add((enchantment_uri, MC.applicableTo, uri))

    output_path = EXPORT_DIR / "data_items.ttl"
    g.serialize(output_path, format="turtle")

    print(f"Exported {len(items)} items to {output_path}")


if __name__ == "__main__":
    export_items()