#!/usr/bin/env python3

import csv
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
TEMPLATE_DIRECTORY = SCRIPT_DIRECTORY.parent.parent
INPUT_FILE = (Path(sys.argv[1]) if len(sys.argv) > 1 else
              TEMPLATE_DIRECTORY / "waitKernel_results.txt")
OUTPUT_DIRECTORY = Path(sys.argv[2]) if len(sys.argv) > 2 else INPUT_FILE.parent
OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)

# Lettura dei tempi medi, gia espressi in microsecondi.
with open(INPUT_FILE, newline="", encoding="utf-8") as file:
    measurements = list(csv.DictReader(file))
if not measurements:
    raise RuntimeError("Il file non contiene misure")

clocks = [int(row["clocks"]) for row in measurements]
times = [float(row["time_us"]) for row in measurements]
baseline = float(measurements[0]["baseline_us"])
threshold = float(measurements[0]["threshold_us"])
crossings = [i for i, time in enumerate(times) if time >= threshold]
if not crossings:
    raise ValueError("La soglia del raddoppio non e stata raggiunta")
crossing = crossings[0]

figure, axis = plt.subplots(figsize=(9, 4.5), layout="constrained")
axis.plot(clocks, times, color="#2563eb", marker=".", markersize=4,
          label="Measured mean time")
axis.axhline(baseline, color="#64748b", linestyle=":",
             label=f"Baseline: {baseline:.3f} us")
axis.axhline(threshold, color="#dc2626", linestyle="--",
             label=f"Doubling threshold: {threshold:.3f} us")
axis.scatter([clocks[crossing]], [times[crossing]], color="#dc2626", zorder=4)
axis.annotate(f"{clocks[crossing]} cycles", (clocks[crossing], times[crossing]),
              xytext=(-85, -30), textcoords="offset points",
              arrowprops={"arrowstyle": "->", "color": "#dc2626"})
axis.set_xlabel("Requested busy-wait duration (GPU clock cycles)")
axis.set_ylabel("Mean time per launch (us)")
axis.set_title("Break-even kernel startup time")
axis.grid(alpha=0.2)
axis.legend(loc="upper left")
for extension in ["png", "svg"]:
    figure.savefig(OUTPUT_DIRECTORY / f"break_even.{extension}", dpi=220)
plt.close(figure)
print(f"Misure lette: {len(measurements)}; primo superamento: {clocks[crossing]} cicli")
