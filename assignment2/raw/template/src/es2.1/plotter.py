#!/usr/bin/env python3

import math
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

plt.rcParams.update({"font.size": 15, "axes.titlesize": 17,
                     "figure.titlesize": 18})

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
TEMPLATE_DIRECTORY = SCRIPT_DIRECTORY.parent.parent
INPUT_FILE = (Path(sys.argv[1]) if len(sys.argv) > 1 else
              TEMPLATE_DIRECTORY / "results/es2.1/nullKernelAsyncVarious.txt")
OUTPUT_DIRECTORY = Path(sys.argv[2]) if len(sys.argv) > 2 else INPUT_FILE.parent
OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)


def is_number(value):
    """Controlla se una stringa rappresenta un numero."""
    try:
        return math.isfinite(float(value))
    except ValueError:
        return False


# Lettura dei tempi asincroni e sincroni, espressi in secondi.
measurements = []
with open(INPUT_FILE, "r", encoding="utf-8") as file:
    for line in file:
        fields = line.split()
        if len(fields) != 4 or not all(is_number(field) for field in fields):
            continue
        num_blocks = int(fields[0])
        threads_per_block = int(fields[1])
        async_seconds = float(fields[2])
        sync_seconds = float(fields[3])
        if async_seconds <= 0 or sync_seconds <= 0:
            raise ValueError("I tempi devono essere positivi")
        measurements.append((num_blocks, threads_per_block,
                             async_seconds, sync_seconds))

if not measurements:
    raise RuntimeError("Non sono stati trovati dati numerici con quattro colonne")

block_values = sorted({measurement[0] for measurement in measurements})
thread_values = sorted({measurement[1] for measurement in measurements})
block_index = {value: index for index, value in enumerate(block_values)}
thread_index = {value: index for index, value in enumerate(thread_values)}

if len({row[:2] for row in measurements}) != len(measurements):
    raise ValueError("Sono presenti configurazioni duplicate")
if len(measurements) != len(block_values) * len(thread_values):
    raise ValueError("Mancano alcune configurazioni della griglia")

# Creazione delle due matrici e conversione in microsecondi.
async_matrix = [[math.nan for _ in thread_values] for _ in block_values]
sync_matrix = [[math.nan for _ in thread_values] for _ in block_values]
for num_blocks, threads_per_block, async_seconds, sync_seconds in measurements:
    row = block_index[num_blocks]
    column = thread_index[threads_per_block]
    async_matrix[row][column] = async_seconds * 1_000_000
    sync_matrix[row][column] = sync_seconds * 1_000_000

# Stessa scala dei colori, senza tagliare i valori estremi.
color_max = math.ceil(max(max(row) for row in async_matrix + sync_matrix) / 5) * 5
figure, axes = plt.subplots(1, 2, figsize=(13, 6.5), layout="constrained")
for axis, matrix, title in zip(axes, [async_matrix, sync_matrix],
                               ["Asynchronous launches", "Synchronous launches"]):
    image = axis.imshow(matrix, aspect="auto", origin="lower",
                        interpolation="nearest", cmap="viridis",
                        vmin=0, vmax=color_max)
    axis.set_xticks(range(len(thread_values)), thread_values, rotation=60)
    axis.set_yticks(range(len(block_values)), block_values)
    axis.set_xlabel("Threads per block")
    axis.set_ylabel("Number of blocks")
    axis.set_title(title)
figure.colorbar(image, ax=axes, label="Mean time per launch (us)", shrink=0.85)
figure.suptitle("Empty kernel: mean launch and completion time")
for extension in ["png", "svg"]:
    figure.savefig(OUTPUT_DIRECTORY / f"launch_heatmaps.{extension}", dpi=220)
plt.close(figure)

print(f"Misure lette: {len(measurements)}")
print(f"Griglia: {len(block_values)} x {len(thread_values)}")
print(f"Grafici salvati in: {OUTPUT_DIRECTORY}")
