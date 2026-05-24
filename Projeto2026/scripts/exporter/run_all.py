import subprocess
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

EXPORTERS = [
    "enchantments_exporter.py",
    "effects_exporter.py",
    "item_exporter.py",
    "foods_exporter.py",
    "blocks_exporter.py",
    "entities_exporter.py",
    "biomes_exporter.py",
    "recipies_exporter.py",
    "manual_exporter.py",
]


def run_all():
    print("=" * 50)
    print("Starting Minecraft Ontology Export Process")
    print("=" * 50)

    start_time = time.time()
    successful_runs = 0

    for script in EXPORTERS:
        script_path = SCRIPT_DIR / script

        if not script_path.exists():
            print(f"Skipping missing exporter: {script}")
            continue

        print(f"\nExecuting: {script}")

        subprocess.run(
            [sys.executable, str(script_path)],
            check=True,
            cwd=SCRIPT_DIR,
        )

        successful_runs += 1

    elapsed_time = time.time() - start_time

    print("\n" + "=" * 50)
    print(f"Finished {successful_runs} exporters in {elapsed_time:.2f}s")
    print("=" * 50)


if __name__ == "__main__":
    run_all()