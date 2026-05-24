def infer_tier(item, name):
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


def classify_item(item):
    name = item["name"]
    ench = set(item.get("enchantCategories") or [])

    if "head_armor" in ench:
        return "Helmet", infer_tier(item, name)
    if "leg_armor" in ench:
        return "Leggings", infer_tier(item, name)
    if "foot_armor" in ench:
        return "Boots", infer_tier(item, name)
    if "armor" in ench and "equippable" in ench:
        if name == "elytra":
            return "Elytra", None
        if "wolf_armor" in name:
            return "WolfArmor", infer_tier(item, name)
        return "Chestplate", infer_tier(item, name)

    if "bow" in ench:
        return "Bow", None
    if "crossbow" in ench:
        return "Crossbow", None
    if "trident" in ench:
        return "Trident", None
    if "mace" in ench:
        return "Mace", None

    if name.endswith("_sword"):
        return "Sword", infer_tier(item, name)
    if name.endswith("_pickaxe"):
        return "Pickaxe", infer_tier(item, name)
    if name.endswith("_axe"):
        return "Axe", infer_tier(item, name)
    if name.endswith("_shovel"):
        return "Shovel", infer_tier(item, name)
    if name.endswith("_hoe"):
        return "Hoe", infer_tier(item, name)

    if name == "shears":
        return "Shears", None
    if name == "fishing_rod":
        return "FishingRod", None
    if name == "flint_and_steel":
        return "FlintAndSteel", None
    if name in ("carrot_on_a_stick", "warped_fungus_on_a_stick"):
        return "SpecialTool", None
    if name == "shield":
        return "Shield", None

    if name == "arrow" or name.endswith("_arrow"):
        return "Projectile", None
    if name in ("snowball", "ender_pearl", "egg", "firework_rocket", "wind_charge"):
        return "Projectile", None

    if name.endswith("_bucket") or name == "bucket":
        return "Bucket", None

    if name.endswith("_spawn_egg"):
        return "SpawnEgg", None

    if name.startswith("music_disc_") or name == "disc_fragment_5":
        return "MusicDisc", None

    if name.endswith("_dye") or name in ("ink_sac", "bone_meal", "cocoa_beans", "lapis_lazuli"):
        return "Dye", None

    if name in ("potion", "splash_potion", "lingering_potion"):
        return "Potion", None

    if "minecart" in name:
        return "Minecart", None

    if name.endswith("_boat") or name.endswith("_chest_boat") or name == "boat":
        return "Boat", None

    if name == "saddle" or name.endswith("_harness") or "horse_armor" in name:
        return "MobEquipment", infer_tier(item, name)

    if name.endswith("_banner"):
        return "Decoration", None

    if name in ("book", "written_book", "writable_book", "enchanted_book", "knowledge_book", "recipe_book"):
        return "Book", None

    if name.endswith("_ingot"):
        return "Ingot", None

    if name in ("diamond", "emerald", "amethyst_shard", "quartz", "nether_star", "echo_shard", "prismarine_crystals"):
        return "Gem", None

    if name in (
        "stick", "string", "leather", "feather", "bone", "gunpowder", "flint",
        "clay_ball", "brick", "nether_brick", "prismarine_shard", "blaze_rod",
        "blaze_powder", "magma_cream", "ghast_tear", "nether_wart", "glowstone_dust",
        "redstone", "slime_ball", "rabbit_hide", "rabbit_foot", "phantom_membrane",
        "shulker_shell", "chorus_fruit", "popped_chorus_fruit", "turtle_scute",
        "armadillo_scute", "heart_of_the_sea", "copper_nugget", "iron_nugget",
        "gold_nugget", "netherite_scrap", "raw_iron", "raw_copper", "raw_gold",
        "ender_eye", "fire_charge"
    ):
        return "Material", None

    return None, None


def classify_block(block):
    name = block["name"]
    material = block.get("material", "")

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

    if name in (
        "crafting_table", "furnace", "blast_furnace", "smoker", "brewing_stand",
        "enchanting_table", "anvil", "beacon", "loom", "cartography_table",
        "fletching_table", "smithing_table", "stonecutter", "grindstone"
    ):
        return "FunctionalBlock"

    if name in (
        "torch", "wall_torch", "glowstone", "sea_lantern", "jack_o_lantern",
        "shroomlight", "end_rod", "beacon", "redstone_torch", "lantern",
        "soul_lantern", "soul_torch", "campfire", "soul_campfire"
    ):
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

    if material == "plant" or "plant" in material:
        return "Plant"

    return None


def classify_entity(entity):
    name = entity.get("name", "")
    category = entity.get("category", "").lower()
    ent_type = entity.get("type", "").lower()

    hostile_names = {
        "zombie", "skeleton", "creeper", "spider", "cave_spider", "enderman",
        "witch", "slime", "magma_cube", "blaze", "ghast", "drowned", "husk",
        "stray", "warden", "phantom", "pillager", "vindicator", "evoker",
        "ravager", "guardian", "elder_guardian", "shulker", "silverfish"
    }

    passive_names = {
        "cow", "sheep", "pig", "chicken", "rabbit", "horse", "donkey", "mule",
        "cat", "wolf", "fox", "bee", "goat", "camel", "llama", "trader_llama",
        "parrot", "turtle", "frog", "sniffer", "armadillo", "mooshroom"
    }

    ambient_names = {
        "bat", "allay"
    }

    if name in hostile_names or "hostile" in ent_type or "hostile" in category:
        return "HostileMob"

    if name in passive_names or ent_type in {"animal", "passive"} or "passive" in category:
        return "Animal"

    if name in ambient_names or ent_type == "ambient":
        return "AmbientMob"

    if ent_type == "projectile" or "projectile" in category:
        return "ProjectileEntity"

    if ent_type == "mob":
        return "Mob"

    return "Entity"