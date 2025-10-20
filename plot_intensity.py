#!/usr/bin/env python3
"""
Quick two-column plotting script with metadata handling.

Usage:
    python plot_intensity.py datafile.txt

Behavior:
    - Skips metadata lines at the top
    - Uses the last non-numeric line before numeric data as x/y labels
    - Assumes two numeric columns for plotting
"""

import sys
import re
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def find_data_start(lines):
    """Find index where numeric data begins, and extract labels."""
    for i, line in enumerate(lines):
        # Split line and check if it's all numbers
        parts = re.split(r"[,\s]+", line.strip())
        if not parts or parts == ['']:
            continue
        try:
            [float(p) for p in parts]  # test conversion
        except ValueError:
            continue  # non-numeric line
        # The line before this one should be labels
        label_line = lines[i - 1] if i > 0 else ""
        return i, label_line.strip()
    raise ValueError("No numeric data found in file.")

def main():
    if len(sys.argv) != 2:
        print("Usage: python plot_intensity.py <filename>")
        sys.exit(1)

    filename = Path(sys.argv[1])
    if not filename.exists():
        print(f"Error: file not found -> {filename}")
        sys.exit(1)

    lines = filename.read_text().splitlines()
    try:
        start_idx, label_line = find_data_start(lines)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Try to get labels (default to generic ones)
    labels = re.split(r"[,\s]+", label_line)
    xlabel = labels[0] if len(labels) >= 1 else "X"
    ylabel = labels[1] if len(labels) >= 2 else "Y"

    # Load numeric data from the detected start line
    try:
        data = np.loadtxt(lines[start_idx:], delimiter=None)
    except Exception as e:
        print(f"Error reading numeric data: {e}")
        sys.exit(1)

    if data.ndim == 1 or data.shape[1] < 2:
        print("Error: file must have at least two numeric columns.")
        sys.exit(1)

    x, y = data[:, 0], data[:, 1]

    # Plot
    plt.figure(figsize=(6, 4))
    plt.plot(x, y, '-', lw=1.5)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(filename.name)
    plt.grid(True, ls="--", alpha=0.6)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
