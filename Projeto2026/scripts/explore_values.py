#!/usr/bin/env python3
"""Explora valores de campos categóricos para planear classificação."""
import json
from pathlib import Path
from collections import Counter

DATA_DIR = Path(__file__).parent.parent / "data" / "1.21.11"


def load(f):
    return json.load(open(DATA_DIR / f, encoding="utf-8"))


def show_counter(title, counter, top=None):
    print(f"\n--- {title} ---")
    items = counter.most_common(top) if top else counter.most_common()
    for value, count in items:
        print(f"  {count:4d}  {value}")


# --- ENTITIES ---
entities = load("entities.json")
show_counter("entities.json :: type", Counter(e["type"] for e in entities))
show_counter("entities.json :: category", Counter(e["category"] for e in entities))

# Cruzar type × category
print("\n--- entities.json :: type × category ---")
for t in sorted({e["type"] for e in entities}):
    cats = Counter(e["category"] for e in entities if e["type"] == t)
    print(f"  type={t!r}:")
    for c, n in cats.most_common():
        print(f"      {n:3d}  category={c!r}")

# Listar todos os mobs (type != 'other' costuma indicar entidade viva)
print("\n--- Entities que parecem mobs (type != 'other') ---")
mobs = [e for e in entities if e["type"] != "other"]
print(f"Total: {len(mobs)}")
for m in mobs[:30]:
    print(f"  {m['name']:30s}  type={m['type']:12s}  category={m['category']}")

# --- BLOCKS ---
blocks = load("blocks.json")
show_counter("blocks.json :: material (top 20)",
             Counter(b["material"] for b in blocks), top=20)
show_counter("blocks.json :: boundingBox",
             Counter(b["boundingBox"] for b in blocks))

# Blocos com drops não vazios
blocks_with_drops = [b for b in blocks if b["drops"]]
print(f"\nBlocos com drops definidos: {len(blocks_with_drops)}/{len(blocks)}")
print("Exemplo de bloco com drops:")
for b in blocks_with_drops[:3]:
    print(f"  {b['name']}: drops={b['drops']}, harvestTools={b.get('harvestTools')}")

# --- BIOMES ---
biomes = load("biomes.json")
show_counter("biomes.json :: dimension", Counter(b["dimension"] for b in biomes))
show_counter("biomes.json :: category", Counter(b["category"] for b in biomes))

# --- ENCHANTMENTS ---
enchs = load("enchantments.json")
show_counter("enchantments.json :: category", Counter(e["category"] for e in enchs))

# Exemplos com exclude não vazio (incompatibilidades)
print("\n--- Enchantments com exclude (incompatibilidades) ---")
for e in enchs:
    if e["exclude"]:
        print(f"  {e['name']:25s}  exclude={e['exclude']}")

# --- EFFECTS ---
effects = load("effects.json")
show_counter("effects.json :: type", Counter(e["type"] for e in effects))

# --- ITEMS com maxDurability ---
items = load("items.json")
dur = [i for i in items if "maxDurability" in i]
print(f"\n--- Items com maxDurability: {len(dur)} ---")
print("Primeiros 20:")
for i in dur[:20]:
    print(f"  {i['name']:30s}  dur={i['maxDurability']:5d}  "
          f"repairWith={i.get('repairWith')}  enchCat={i.get('enchantCategories')}")

# Items com enchantCategories (arma/armadura/ferramenta)
ench_items = [i for i in items if "enchantCategories" in i]
print(f"\n--- Items com enchantCategories: {len(ench_items)} ---")
all_cats = Counter()
for i in ench_items:
    for c in i["enchantCategories"]:
        all_cats[c] += 1
show_counter("enchantCategories agregadas", all_cats)

# --- RECIPES: estrutura ---
recipes = load("recipes.json")
print(f"\n--- Recipes: {len(recipes)} results ---")
# Conta shaped vs shapeless
shaped = shapeless = 0
for rid, rlist in recipes.items():
    for r in rlist:
        if "inShape" in r:
            shaped += 1
        elif "ingredients" in r:
            shapeless += 1
print(f"  Shaped:    {shaped}")
print(f"  Shapeless: {shapeless}")

# Uma receita shapeless de exemplo
for rid, rlist in recipes.items():
    for r in rlist:
        if "ingredients" in r:
            print(f"\nExemplo shapeless (result id {rid}):")
            print(json.dumps(r, indent=2))
            break
    else:
        continue
    break