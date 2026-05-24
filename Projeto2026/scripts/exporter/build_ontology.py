import os
from rdflib import Graph, Namespace, RDFS

# Import the functions from your separate exporter files
from enchantments_exporter import export_enchantments as add_enchantments
from effects_exporter import export_effects as add_effects
from item_exporter import export_items as add_items
from foods_exporter import export_foods as  add_foods
from blocks_exporter import  export_blocks as add_blocks
from entities_exporter import export_entities as add_entities
from biomes_exporter import  export_biomes as add_biomes
from recipies_exporter import export_recipes as add_recipes

MC = Namespace("http://rpcw.di.uminho.pt/2026/minecraft/")

def build_master_file():
    print("="*50)
    print("⛏️ Building Master Minecraft Ontology File")
    print("="*50)

    # 1. Create the ONE master graph and bind namespaces
    g = Graph()
    g.bind("", MC)
    g.bind("rdfs", RDFS)

    data_directory = '../../data/1.21.11'

    print("Loading existing minecraft.ttl schema...")
    g.parse('../../ontology/classes.ttl', format='turtle')

    # 2. Pass the master graph to each separated script
    print("\n▶ Processing Enchantments...")
    add_enchantments(g, data_directory)

    print("\n▶ Processing Effects...")
    add_effects(g, data_directory)

    print("\n▶ Processing Items...")
    add_items(g, data_directory)

    print("\n▶ Processing Foods...")
    add_foods(g, data_directory)

    print("\n▶ Processing Blocks...")
    add_blocks(g, data_directory)

    print("\n▶ Processing Entities...")
    add_entities(g, data_directory)

    print("\n▶ Processing Biomes...")
    add_biomes(g, data_directory)

    print("\n▶ Processing Recipes...")
    add_recipes(g, data_directory)

    # 3. Save the final, massive graph to a single file
    output_file = '../ontology/populated_data_master.ttl'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    print("\n" + "="*50)
    print(f"Serializing {len(g)} total triples...")
    g.serialize(destination=output_file, format='turtle')
    print(f"✅ Success! All individuals saved to: {output_file}")
    print("="*50)

if __name__ == "__main__":
    build_master_file()