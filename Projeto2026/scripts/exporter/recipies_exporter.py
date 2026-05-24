from rdflib import Graph, Literal
from rdflib.namespace import RDF, XSD

from common import MC, EXPORT_DIR, load_dataset


def export_recipes():
    g = Graph()
    g.bind("", MC)

    recipes_data = load_dataset("recipes.json")
    items = load_dataset("items.json")

    item_id_to_uri = {i["id"]: MC[i["name"]] for i in items}

    count = 0

    for result_item_id_str, recipe_list in recipes_data.items():
        result_item_id = int(result_item_id_str)

        if result_item_id not in item_id_to_uri:
            continue

        result_uri = item_id_to_uri[result_item_id]

        for idx, recipe in enumerate(recipe_list):
            count += 1

            recipe_uri = MC[f"recipe_{result_item_id}_{idx}"]

            g.add((recipe_uri, RDF.type, MC.Recipe))
            g.add((recipe_uri, MC.produces, result_uri))
            g.add((result_uri, MC.craftedBy, recipe_uri))

            output_quantity = recipe.get("result", {}).get("count", 1)
            g.add((recipe_uri, MC.outputQuantity, Literal(output_quantity, datatype=XSD.integer)))

            if "inShape" in recipe:
                g.add((recipe_uri, RDF.type, MC.CraftingRecipe))
                g.add((recipe_uri, RDF.type, MC.ShapedRecipe))

                for row_idx, row in enumerate(recipe["inShape"]):
                    for col_idx, item_id in enumerate(row):
                        if item_id is not None and item_id in item_id_to_uri:
                            item_uri = item_id_to_uri[item_id]

                            g.add((recipe_uri, MC.hasIngredient, item_uri))
                            g.add((item_uri, MC.usedIn, recipe_uri))

                            slot_uri = MC[f"recipe_{result_item_id}_{idx}_slot_{row_idx}_{col_idx}"]

                            g.add((slot_uri, RDF.type, MC.RecipeSlot))
                            g.add((slot_uri, MC.slotRow, Literal(row_idx, datatype=XSD.integer)))
                            g.add((slot_uri, MC.slotColumn, Literal(col_idx, datatype=XSD.integer)))
                            g.add((slot_uri, MC.slotItem, item_uri))

                            g.add((recipe_uri, MC.hasSlot, slot_uri))

            elif "ingredients" in recipe:
                g.add((recipe_uri, RDF.type, MC.CraftingRecipe))
                g.add((recipe_uri, RDF.type, MC.ShapelessRecipe))

                for ingredient_idx, item_id in enumerate(recipe["ingredients"]):
                    if item_id is not None and item_id in item_id_to_uri:
                        item_uri = item_id_to_uri[item_id]

                        g.add((recipe_uri, MC.hasIngredient, item_uri))
                        g.add((item_uri, MC.usedIn, recipe_uri))

                        slot_uri = MC[f"recipe_{result_item_id}_{idx}_slot_0_{ingredient_idx}"]

                        g.add((slot_uri, RDF.type, MC.RecipeSlot))
                        g.add((slot_uri, MC.slotRow, Literal(0, datatype=XSD.integer)))
                        g.add((slot_uri, MC.slotColumn, Literal(ingredient_idx, datatype=XSD.integer)))
                        g.add((slot_uri, MC.slotItem, item_uri))

                        g.add((recipe_uri, MC.hasSlot, slot_uri))

    output_path = EXPORT_DIR / "data_recipes.ttl"
    g.serialize(output_path, format="turtle")

    print(f"Exported {count} recipes to {output_path}")


if __name__ == "__main__":
    export_recipes()