#!/usr/bin/env python3

import csv
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
TEMPLATE_DIRECTORY = SCRIPT_DIRECTORY.parent.parent
INPUT_FILE = Path(sys.argv[1]) if len(sys.argv) > 1 else TEMPLATE_DIRECTORY / "pcie_results.csv"
OUTPUT_DIRECTORY = Path(sys.argv[2]) if len(sys.argv) > 2 else INPUT_FILE.parent
OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)

with open(INPUT_FILE, newline="", encoding="utf-8") as file:
    measurements = list(csv.DictReader(file))
if not measurements:
    raise RuntimeError("Il file non contiene misure")

sizes = sorted({int(row["bytes"]) for row in measurements})
conditions = [("pageable", "H2D", "#2563eb"), ("pageable", "D2H", "#06b6d4"),
              ("pinned", "H2D", "#dc2626"), ("pinned", "D2H", "#e88d10")]
figure, axis = plt.subplots(figsize=(10, 5), layout="constrained")
for memory, direction, color in conditions:
    rows = sorted([row for row in measurements
                   if row["memory"] == memory and row["direction"] == direction],
                  key=lambda row: int(row["bytes"]))
    if [int(row["bytes"]) for row in rows] != sizes:
        raise ValueError(f"Dimensioni mancanti o duplicate: {memory} {direction}")
    axis.plot(sizes, [float(row["gbps"]) for row in rows], marker="o", markersize=4,
              color=color, label=f"{memory.capitalize()} {direction}")

labels = []
for size in sizes:
    if size >= 1024**3:
        labels.append(f"{size // 1024**3} GiB")
    elif size >= 1024**2:
        labels.append(f"{size // 1024**2} MiB")
    else:
        labels.append(f"{size // 1024} KiB")
axis.set_xscale("log", base=4)
axis.set_xticks(sizes, labels, rotation=35, ha="right")
axis.axhline(15.8, color="#64748b", linestyle="--", label="PCIe 3.0 x16 reference")
axis.set_ylim(0, 16.5)
axis.set_xlabel("Transfer size (logarithmic scale)")
axis.set_ylabel("Effective bandwidth (GB/s)")
axis.set_title("PCIe data transfers: pageable versus pinned memory")
axis.grid(alpha=0.2)
axis.legend(loc="upper left", fontsize=9)
for extension in ["png", "svg"]:
    figure.savefig(OUTPUT_DIRECTORY / f"pcie_graph.{extension}", dpi=220)
plt.close(figure)
print(f"Misure lette: {len(measurements)}; grafici salvati in: {OUTPUT_DIRECTORY}")
