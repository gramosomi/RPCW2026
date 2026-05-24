#!/usr/bin/env python3
"""Exploração inicial dos dados PrismarineJS para a 1.21.11."""
import json
from pathlib import Path
from collections import Counter

DATA_DIR = Path(__file__).parent.parent / "data" / "1.21.11"

FILES = [
    "blocks.json",
    "items.json",
    "entities.json",
    "biomes.json",
    "foods.json",
    "enchantments.json",
    "recipes.json",
    "effects.json",
    "materials.json",
    "attributes.json",
]


def load(filename):
    path = DATA_DIR / filename
    if not path.exists():
        print(f"  [AVISO] {filename} não encontrado em {DATA_DIR}")
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def describe(name, data):
    print("\n" + "=" * 70)
    print(f"FICHEIRO: {name}")
    print("=" * 70)

    if data is None:
        return

    if isinstance(data, list):
        print(f"Tipo: lista com {len(data)} entradas")
        if not data:
            return
        sample = data[0]
    elif isinstance(data, dict):
        print(f"Tipo: dict com {len(data)} chaves")
        first_key = next(iter(data))
        print(f"Primeira chave: {first_key!r}")
        sample = data[first_key]
    else:
        print(f"Tipo inesperado: {type(data)}")
        return

    if isinstance(sample, dict):
        print(f"\nCampos na primeira entrada:")
        for k, v in sample.items():
            tipo = type(v).__name__
            preview = str(v)
            if len(preview) > 60:
                preview = preview[:60] + "..."
            print(f"  - {k:25s} ({tipo:8s}) = {preview}")

    if isinstance(data, list) and isinstance(sample, dict):
        field_count = Counter()
        for entry in data:
            if isinstance(entry, dict):
                for k in entry.keys():
                    field_count[k] += 1
        total = len(data)
        print(f"\nFrequência de campos (em {total} entradas):")
        for field, count in field_count.most_common():
            pct = 100 * count / total
            marker = " " if count == total else "*"
            print(f"  {marker} {field:25s} {count:5d}/{total}  ({pct:5.1f}%)")
        print("  (* = campo opcional)")

    print(f"\nExemplo completo da primeira entrada (truncado a 800 chars):")
    print(json.dumps(sample, indent=2, ensure_ascii=False)[:800])


def main():
    print(f"Diretório de dados: {DATA_DIR}")
    print(f"\nFicheiros presentes:")
    for f in sorted(DATA_DIR.iterdir()):
        size_kb = f.stat().st_size / 1024
        print(f"  {f.name:35s}  {size_kb:>8.1f} KB")

    for filename in FILES:
        data = load(filename)
        describe(filename, data)


if __name__ == "__main__":
    main()