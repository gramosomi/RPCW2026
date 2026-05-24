#!/usr/bin/env python3
"""
Testa heurísticas de classificação de items e blocos.
Mostra contagens e exemplos por classe inferida.
NÃO gera nada — só imprime para validação humana.
"""
import json
from pathlib import Path
from collections import Counter, defaultdict

DATA_DIR = Path(__file__).parent.parent / "data" / "1.21.11"


def load(f):
    return json.load(open(DATA_DIR / f, encoding="utf-8"))


# ==============================================================
# CLASSIFICAÇÃO DE ITEMS
# ==============================================================

def classify_item(item):
    """Versão melhorada com spawn eggs, discs, dyes, etc."""
    name = item["name"]
    ench = set(item.get("enchantCategories") or [])
    
    # === Equipamento combativo ===
    if "head_armor" in ench:
        return ("Helmet", infer_tier(item, name))
    if "leg_armor" in ench:
        return ("Leggings", infer_tier(item, name))
    if "foot_armor" in ench:
        return ("Boots", infer_tier(item, name))
    if "armor" in ench and "equippable" in ench:
        if name == "elytra":
            return ("Elytra", None)
        if "wolf_armor" in name:
            return ("WolfArmor", infer_tier(item, name))
        return ("Chestplate", infer_tier(item, name))
    
    if "bow" in ench: return ("Bow", None)
    if "crossbow" in ench: return ("Crossbow", None)
    if "trident" in ench: return ("Trident", None)
    if "mace" in ench: return ("Mace", None)
    
    if name.endswith("_sword"):   return ("Sword", infer_tier(item, name))
    if name.endswith("_pickaxe"): return ("Pickaxe", infer_tier(item, name))
    if name.endswith("_axe"):     return ("Axe", infer_tier(item, name))
    if name.endswith("_shovel"):  return ("Shovel", infer_tier(item, name))
    if name.endswith("_hoe"):     return ("Hoe", infer_tier(item, name))
    
    if name == "shears": return ("Shears", None)
    if name == "fishing_rod": return ("FishingRod", None)
    if name == "flint_and_steel": return ("FlintAndSteel", None)
    if name in ("carrot_on_a_stick", "warped_fungus_on_a_stick"):
        return ("SpecialTool", None)
    if name == "shield": return ("Shield", None)
    
    # === Projéteis ===
    if name == "arrow" or name.endswith("_arrow"):
        return ("Projectile", None)
    if name == "snowball" or name == "ender_pearl" or name == "egg":
        return ("Projectile", None)
    if name in ("firework_rocket", "wind_charge"):
        return ("Projectile", None)
    
    # === Containers ===
    if name.endswith("_bucket") or name == "bucket":
        return ("Bucket", None)
    
    # === Spawn eggs ===
    if name.endswith("_spawn_egg"):
        return ("SpawnEgg", None)
    
    # === Music discs ===
    if name.startswith("music_disc_") or name == "disc_fragment_5":
        return ("MusicDisc", None)
    
    # === Dyes ===
    if name.endswith("_dye") or name == "ink_sac" or name == "bone_meal" or name == "cocoa_beans" or name == "lapis_lazuli":
        return ("Dye", None)
    
    # === Potions ===
    if name in ("potion", "splash_potion", "lingering_potion"):
        return ("Potion", None)
    if name in ("glass_bottle", "experience_bottle", "honey_bottle"):
        return ("Bottle", None)
    
    # === Vehicles ===
    if "minecart" in name:
        return ("Minecart", None)
    if name.endswith("_boat") or name.endswith("_chest_boat") or name == "boat":
        return ("Boat", None)
    
    # === Horse/mob equipment ===
    if name == "saddle" or name.endswith("_harness"):
        return ("MobEquipment", None)
    if "horse_armor" in name:
        return ("MobEquipment", infer_tier(item, name))
    
    # === Banners (tecnicamente blocks, mas no items.json) ===
    if name.endswith("_banner"):
        return ("Banner", None)
    
    # === Books ===
    if name in ("book", "written_book", "writable_book", "enchanted_book",
                "knowledge_book", "recipe_book"):
        return ("Book", None)
    if name == "name_tag":
        return ("Utility", None)
    
    # === Food (vamos identificar via foods.json no script real) ===
    # por agora, stub
    
    # === Ingredientes / materiais ===
    if not ench:
        if name.endswith("_ingot"):
            return ("Ingot", None)
        if name in ("diamond", "emerald", "amethyst_shard", "quartz",
                    "nether_star", "echo_shard", "prismarine_crystals"):
            return ("Gem", None)
        if name in ("stick", "string", "leather", "feather", "bone", "gunpowder",
                    "flint", "clay_ball", "brick", "nether_brick", "prismarine_shard",
                    "blaze_rod", "blaze_powder", "magma_cream", "ghast_tear",
                    "nether_wart", "glowstone_dust", "redstone", "slime_ball",
                    "rabbit_hide", "rabbit_foot", "phantom_membrane", "shulker_shell",
                    "chorus_fruit", "popped_chorus_fruit", "turtle_scute", "armadillo_scute",
                    "heart_of_the_sea", "copper_nugget", "iron_nugget", "gold_nugget",
                    "netherite_scrap", "raw_iron", "raw_copper", "raw_gold",
                    "ender_eye", "fire_charge"):
            return ("Material", None)
    
    # === Blocos colocáveis (ficam marcados para merge) ===
    return ("PlaceableBlockCandidate", None)  # será merged com Block no gerador


def infer_tier(item, name):
    """Infere o tier a partir de repairWith ou do nome."""
    repair = item.get("repairWith") or []
    
    if any("netherite" in r for r in repair) or "netherite" in name:
        return "Netherite"
    if any("diamond" in r for r in repair) or name.startswith("diamond_"):
        return "Diamond"
    if any("gold" in r for r in repair) or name.startswith("gold") or name.startswith("golden_"):
        return "Gold"
    if any("iron" in r for r in repair) or name.startswith("iron_"):
        return "Iron"
    if any("copper" in r for r in repair) or name.startswith("copper_"):
        return "Copper"
    if any("planks" in r for r in repair) or name.startswith("wooden_"):
        return "Wood"
    if any(r in ("cobblestone", "cobbled_deepslate", "blackstone") for r in repair) or name.startswith("stone_"):
        return "Stone"
    if name.startswith("leather_"):
        return "Leather"
    if name.startswith("chainmail_"):
        return "Chainmail"
    if name == "turtle_helmet":
        return "Turtle"
    return None


# ==============================================================
# CLASSIFICAÇÃO DE BLOCOS
# ==============================================================

def classify_block(block):
    """Classe inferida a partir do material e nome."""
    name = block["name"]
    material = block.get("material", "default")
    
    if name in ("air", "cave_air", "void_air"):
        return "Air"  # vamos excluir do export
    
    if name.endswith("_ore") or name == "ancient_debris":
        return "Ore"
    if "log" in name or name.endswith("_stem") or name.endswith("_hyphae"):
        return "Log"
    if name.endswith("_planks"):
        return "Planks"
    if name.endswith("_leaves"):
        return "Leaves"
    if name.endswith("_sapling"):
        return "Sapling"
    if name.endswith("_sign"):
        return "Sign"
    if name.endswith("_door"):
        return "Door"
    if name.endswith("_bed"):
        return "Bed"
    if name in ("water", "lava"):
        return "FluidBlock"
    if name in ("sand", "red_sand", "gravel", "suspicious_sand", "suspicious_gravel", "anvil", "chipped_anvil", "damaged_anvil"):
        return "GravityBlock"
    if name in ("crafting_table", "furnace", "blast_furnace", "smoker", "brewing_stand",
                "enchanting_table", "anvil", "beacon", "loom", "cartography_table",
                "fletching_table", "smithing_table", "stonecutter", "grindstone"):
        return "FunctionalBlock"
    if name in ("torch", "wall_torch", "glowstone", "sea_lantern", "jack_o_lantern",
                "shroomlight", "end_rod", "beacon", "redstone_torch", "lantern", "soul_lantern",
                "soul_torch", "campfire", "soul_campfire"):
        return "LightSource"
    if name.endswith("_slab"):
        return "Slab"
    if name.endswith("_stairs"):
        return "Stairs"
    if name.endswith("_wall"):
        return "Wall"
    if name.endswith("_fence") or name.endswith("_fence_gate"):
        return "Fence"
    if "glass" in name:
        return "GlassBlock"
    if material.startswith("mineable/"):
        return "NaturalBlock"
    if material == "wool":
        return "Wool"
    if material == "plant" or "mineable/axe;plant" in material or material == "gourd;mineable/axe":
        return "Plant"
    if material == "leaves;mineable/hoe":
        return "Leaves"
    
    return "GenericBlock"

def simulate_merge():
    """Simula a Opção C: merge de items com blocks."""
    items = load("items.json")
    blocks = load("blocks.json")
    
    block_names = {b["name"] for b in blocks}
    item_names = {i["name"] for i in items}
    
    both = item_names & block_names
    only_item = item_names - block_names
    only_block = block_names - item_names
    
    print("\n" + "=" * 70)
    print("ANÁLISE DE MERGE ITEMS↔BLOCKS (Opção C)")
    print("=" * 70)
    print(f"Só em items.json (items 'puros'):       {len(only_item)}")
    print(f"Só em blocks.json (blocos não-coletáveis): {len(only_block)}")
    print(f"Em ambos (PlaceableBlock):               {len(both)}")
    print(f"Total indivíduos únicos:                 {len(item_names | block_names)}")
    
    print(f"\n=== Amostra de items 'puros' (não-blocos) ===")
    for n in sorted(only_item)[:40]:
        print(f"  - {n}")
    print(f"  ... total {len(only_item)}")
    
    print(f"\n=== Amostra de blocos não-coletáveis (só no mundo) ===")
    for n in sorted(only_block)[:20]:
        print(f"  - {n}")
    print(f"  ... total {len(only_block)}")


# ==============================================================
# MAIN
# ==============================================================

def main():
    items = load("items.json")
    blocks = load("blocks.json")
    
    # --- ITEMS ---
    print("=" * 70)
    print("CLASSIFICAÇÃO DE ITEMS")
    print("=" * 70)
    
    by_class = defaultdict(list)
    tier_counter = Counter()
    
    for item in items:
        cls, tier = classify_item(item)
        by_class[cls].append(item["name"])
        if tier:
            tier_counter[tier] += 1
    
    print(f"\nTotal items: {len(items)}")
    print(f"\nDistribuição por classe:")
    for cls, names in sorted(by_class.items(), key=lambda x: -len(x[1])):
        print(f"  {cls:25s}  {len(names):5d}")
    
    print(f"\nDistribuição por tier (só items tipados):")
    for tier, count in tier_counter.most_common():
        print(f"  {tier:15s}  {count}")
    
    # Mostrar exemplos de cada classe (exceto as grandes)
    print("\n\n=== EXEMPLOS POR CLASSE ===")
    for cls, names in sorted(by_class.items()):
        if cls in ("GenericItem", "UnclassifiedItem"):
            continue
        print(f"\n[{cls}] ({len(names)} items)")
        for n in names[:12]:
            print(f"  - {n}")
        if len(names) > 12:
            print(f"  ... +{len(names)-12} mais")
    
    # Unclassified: o que nos escapou?
    print(f"\n\n=== ITEMS NÃO CLASSIFICADOS ===")
    print(f"Total: {len(by_class.get('UnclassifiedItem', []))}")
    for n in by_class.get('UnclassifiedItem', [])[:30]:
        print(f"  - {n}")
    if len(by_class.get('UnclassifiedItem', [])) > 30:
        print(f"  ... +{len(by_class['UnclassifiedItem'])-30} mais")
    
    # GenericItem: grande bucket, amostra
    print(f"\n\n=== AMOSTRA DE GenericItem ({len(by_class.get('GenericItem', []))}) ===")
    sample = by_class.get('GenericItem', [])
    for n in sample[:30]:
        print(f"  - {n}")
    if len(sample) > 30:
        print(f"  ... +{len(sample)-30} mais")
    
    # --- BLOCKS ---
    print("\n\n" + "=" * 70)
    print("CLASSIFICAÇÃO DE BLOCOS")
    print("=" * 70)
    
    by_bclass = defaultdict(list)
    for block in blocks:
        cls = classify_block(block)
        by_bclass[cls].append(block["name"])
    
    print(f"\nTotal blocks: {len(blocks)}")
    print(f"\nDistribuição por classe:")
    for cls, names in sorted(by_bclass.items(), key=lambda x: -len(x[1])):
        print(f"  {cls:20s}  {len(names):5d}")
    
    print("\n=== AMOSTRA GenericBlock ===")
    for n in by_bclass.get('GenericBlock', [])[:40]:
        print(f"  - {n}")

    simulate_merge()


if __name__ == "__main__":
    main()