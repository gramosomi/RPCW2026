from rdflib import Graph, Literal
from rdflib.namespace import RDF, XSD

from common import MC, EXPORT_DIR, load_manual


def export_manual_data():
    g = Graph()
    g.bind("", MC)

    for tier in load_manual("material_tiers.json"):
        uri = MC[tier["name"]]
        g.add((uri, RDF.type, MC.MaterialTier))
        g.add((uri, MC.hasName, Literal(tier["name"], datatype=XSD.string)))
        g.add((uri, MC.tierOrder, Literal(tier["order"], datatype=XSD.integer)))

    for row in load_manual("block_mining.json"):
        block = MC[row["block"]]
        tier = MC[row["requiresMinTier"]]
        g.add((block, MC.requiresMinTier, tier))

    for row in load_manual("mob_drops.json"):
        mob = MC[row["mob"]]
        for item_name in row.get("drops", []):
            item = MC[item_name]
            g.add((mob, MC.drops, item))
            g.add((item, MC.droppedBy, mob))

    for row in load_manual("mob_spawns.json"):
        mob = MC[row["mob"]]
        for biome_name in row.get("biomes", []):
            biome = MC[biome_name]
            g.add((mob, MC.spawnsIn, biome))
            g.add((biome, MC.hasSpawn, mob))

    for row in load_manual("dimensions.json"):
        dim = MC[row["name"]]
        g.add((dim, RDF.type, MC.Dimension))
        g.add((dim, MC.hasName, Literal(row["name"], datatype=XSD.string)))
        g.add((dim, MC.hasDisplayName, Literal(row["displayName"], datatype=XSD.string)))

    for row in load_manual("structures.json"):
        structure = MC[row["name"]]
        structure_type = row.get("type", "Structure")

        g.add((structure, RDF.type, MC.Structure))
        g.add((structure, RDF.type, MC[structure_type]))
        g.add((structure, MC.hasName, Literal(row["name"], datatype=XSD.string)))

        for biome_name in row.get("biomes", []):
            biome = MC[biome_name]
            g.add((structure, MC.generatesIn, biome))
            g.add((biome, MC.hasStructure, structure))

    for row in load_manual("portals.json"):
        dimension = MC[row["dimension"]]
        for item_name in row.get("required", []):
            item = MC[item_name]
            g.add((dimension, MC.requiredToEnter, item))
            g.add((item, MC.opensAccess, dimension))

    for row in load_manual("mob_properties.json"):
        mob = MC[row["mob"]]

        if "isBurnableInSunlight" in row:
            g.add((mob, MC.isBurnableInSunlight, Literal(row["isBurnableInSunlight"], datatype=XSD.boolean)))

        if "isImmuneToFire" in row:
            g.add((mob, MC.isImmuneToFire, Literal(row["isImmuneToFire"], datatype=XSD.boolean)))

    for row in load_manual("block_properties.json"):
        block = MC[row["block"]]

        if row.get("affectedByGravity") is True:
            g.add((block, RDF.type, MC.GravityBlock))
            g.add((block, MC.affectedByGravity, Literal(True, datatype=XSD.boolean)))

    output = EXPORT_DIR / "data_manual.ttl"
    g.serialize(output, format="turtle")
    print(f"Exported manual data to {output}")


if __name__ == "__main__":
    export_manual_data()