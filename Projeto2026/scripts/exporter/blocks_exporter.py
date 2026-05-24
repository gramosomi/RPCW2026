from rdflib import Graph, Literal
from rdflib.namespace import RDF, XSD

from common import MC, EXPORT_DIR, load_dataset
from classifiers import classify_block


def export_blocks():
    g = Graph()
    g.bind("", MC)

    blocks = load_dataset("blocks.json")
    items = load_dataset("items.json")

    item_id_to_uri = {i["id"]: MC[i["name"]] for i in items}

    for b in blocks:
        block_name = b["name"]
        uri = MC[block_name]

        g.add((uri, RDF.type, MC.Block))

        specific_class = classify_block(b)

        if specific_class:
            g.add((uri, RDF.type, MC[specific_class]))

        if specific_class == "GravityBlock":
            g.add((uri, MC.affectedByGravity, Literal(True, datatype=XSD.boolean)))

        if b.get("emitLight", 0) > 0:
            g.add((uri, RDF.type, MC.LightSource))

        g.add((uri, MC.blockID, Literal(b["id"], datatype=XSD.integer)))
        g.add((uri, MC.hasName, Literal(block_name, datatype=XSD.string)))
        g.add((uri, MC.hasDisplayName, Literal(b["displayName"], datatype=XSD.string)))
        g.add((uri, MC.hardness, Literal(b.get("hardness", 0.0), datatype=XSD.float)))
        g.add((uri, MC.blastResistance, Literal(b.get("resistance", 0.0), datatype=XSD.float)))

        if "stackSize" in b:
            g.add((uri, MC.stackSize, Literal(b["stackSize"], datatype=XSD.integer)))

        if "diggable" in b:
            g.add((uri, MC.isDiggable, Literal(b["diggable"], datatype=XSD.boolean)))

        if "transparent" in b:
            g.add((uri, MC.isTransparent, Literal(b["transparent"], datatype=XSD.boolean)))

        if "emitLight" in b:
            g.add((uri, MC.emitLight, Literal(b["emitLight"], datatype=XSD.integer)))

        if "filterLight" in b:
            g.add((uri, MC.filterLight, Literal(b["filterLight"], datatype=XSD.integer)))

        if "boundingBox" in b:
            g.add((uri, MC.boundingBox, Literal(b["boundingBox"], datatype=XSD.string)))

        if "material" in b:
            g.add((uri, MC.materialCategory, Literal(b["material"], datatype=XSD.string)))

        if "minStateId" in b:
            g.add((uri, MC.minStateId, Literal(b["minStateId"], datatype=XSD.integer)))

        if "maxStateId" in b:
            g.add((uri, MC.maxStateId, Literal(b["maxStateId"], datatype=XSD.integer)))

        if "defaultState" in b:
            g.add((uri, MC.defaultStateId, Literal(b["defaultState"], datatype=XSD.integer)))

        if "states" in b:
            for state in b["states"]:
                state_uri = MC[f"{block_name}_state_{state['name']}"]

                g.add((state_uri, RDF.type, MC.BlockState))
                g.add((state_uri, MC.hasName, Literal(state["name"], datatype=XSD.string)))
                g.add((state_uri, MC.BlockStateType, Literal(state["type"], datatype=XSD.string)))

                if "num_values" in state:
                    g.add((state_uri, MC.BlockStateNumValues, Literal(state["num_values"], datatype=XSD.integer)))

                g.add((uri, MC.hasBlockState, state_uri))

        for drop_id in b.get("drops", []):
            if drop_id in item_id_to_uri:
                drop_uri = item_id_to_uri[drop_id]
                g.add((uri, MC.minedDrops, drop_uri))
                g.add((drop_uri, MC.minedFrom, uri))

        for tool_id_str in b.get("harvestTools", {}).keys():
            tool_id = int(tool_id_str)

            if tool_id in item_id_to_uri:
                tool_uri = item_id_to_uri[tool_id]
                g.add((uri, MC.minedWith, tool_uri))
                g.add((tool_uri, MC.canMine, uri))

    output_path = EXPORT_DIR / "data_blocks.ttl"
    g.serialize(output_path, format="turtle")

    print(f"Exported {len(blocks)} blocks with their states to {output_path}")


if __name__ == "__main__":
    export_blocks()