#!/usr/bin/env python3
"""
Quick two-column plotting script with metadata handling.

Usage:
    python plot_intensity.py file1.txt [file2.txt ...]
    python plot_intensity.py --diff file1.txt file2.txt
    python plot_intensity.py --waterfall file1.txt [file2.txt ...]

Behavior:
    - Skips metadata lines at the top
    - Looks for a line beginning with "#L" for x/y column labels
    - Assumes two numeric columns for plotting
    - Can:
        * Plot multiple files together
        * Plot a vertical waterfall stack of multiple files
        * Plot the difference between two files
"""

import sys
import re
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from bg_mpl_stylesheets.styles import all_styles

plt.style.use(all_styles["bg-style"])


def find_labels_and_data_start(lines):
    """Find the label line (#L ...) and the first numeric data line index."""
    label_line = ""
    data_start_idx = None

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Look for #L label line
        if stripped.startswith("#L"):
            label_line = stripped[2:].strip()  # remove "#L"

        # Detect start of numeric data
        parts = re.split(r"[,\s]+", stripped)
        if not parts or parts == ['']:
            continue
        try:
            [float(p) for p in parts]
            data_start_idx = i
            break
        except ValueError:
            continue

    if data_start_idx is None:
        raise ValueError("No numeric data found in file.")
    return label_line, data_start_idx


def load_data(filename):
    """Load two-column numeric data and labels from a file."""
    lines = filename.read_text().splitlines()
    label_line, start_idx = find_labels_and_data_start(lines)

    # Extract x/y labels
    labels = re.split(r"[,\s]+", label_line)
    xlabel = labels[0] if len(labels) >= 1 else "X"
    ylabel = labels[1] if len(labels) >= 2 else "Y"

    # Load numeric data
    try:
        data = np.loadtxt(lines[start_idx:], delimiter=None)
    except Exception as e:
        raise ValueError(f"{filename}: error reading numeric data: {e}")

    if data.ndim == 1 or data.shape[1] < 2:
        raise ValueError(f"{filename}: file must have at least two numeric columns.")

    return data[:, 0], data[:, 1], xlabel, ylabel


def show_legend_outside():
    """Show legend outside the right side of the plot."""
    plt.legend(
        loc="upper left",
        bbox_to_anchor=(1.02, 1.0),
        borderaxespad=0,
        frameon=False,
    )
    # plt.tight_layout(rect=[0, 0, 0.8, 1])  # leave room on right for legend


def plot_multiple(files):
    """Plot multiple files on one figure."""
    plt.figure(figsize=(7, 4))  # slightly wider to fit legend
    xlabel, ylabel = "X", "Y"

    for f in files:
        path = Path(f)
        if not path.exists():
            print(f"Error: file not found -> {path}")
            continue

        try:
            x, y, xlabel, ylabel = load_data(path)
        except Exception as e:
            print(f"Error reading {path}: {e}")
            continue

        plt.plot(x, y, label=path.name, alpha=.7)

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    show_legend_outside()
    plt.grid(True, ls="--", alpha=0.6)
    plt.show()


def plot_waterfall(files, scale_factor=.1):
    """
    Plot multiple files in a vertical waterfall format.

    Each dataset is vertically offset by (ymax - ymin) * scale_factor
    relative to the previous one.
    """
    plt.figure(figsize=(7, 4))
    xlabel, ylabel = "X", "Y"

    data_list = []
    for f in files:
        path = Path(f)
        if not path.exists():
            print(f"Error: file not found -> {path}")
            continue
        try:
            x, y, xlabel, ylabel = load_data(path)
            data_list.append((path.name, x, y))
        except Exception as e:
            print(f"Error reading {path}: {e}")
            continue

    if not data_list:
        print("No valid data to plot.")
        return

    offset = 0.0
    for name, x, y in data_list:
        if ".dofr" in name:
            y = y * 1 / 8
            label_name = name.split(".dofr")[0]
        elif "LTS_HME_PCM_AFF_" in name:
            subname = name.split("_2025")[0]
            label_name = subname.replace("LTS_HME_PCM_AFF_", "Long_term_storage_")
        elif "Paracetamol" in name:
            label_name = "crystalline paracetamol"
        else:
            label_name = name.split("_2025")[0]

        y_range = np.nanmax(y) - np.nanmin(y)
        plt.plot(x, y + offset, lw=1.5, label=label_name)
        offset += y_range * scale_factor

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    show_legend_outside()
    plt.grid(True, ls="--", alpha=0.6)
    plt.show()


def plot_difference(file1, file2):
    """Plot the difference between two files (y1 - y2)."""
    path1, path2 = Path(file1), Path(file2)
    if not path1.exists() or not path2.exists():
        print("Error: one or both files not found.")
        sys.exit(1)

    x1, y1, xlabel, ylabel = load_data(path1)
    x2, y2, _, _ = load_data(path2)

    if not np.allclose(x1, x2):
        y2_interp = np.interp(x1, x2, y2)
    else:
        y2_interp = y2

    y_diff = y1 - y2_interp

    plt.figure(figsize=(7, 4))
    plt.plot(x1, y_diff, '-', lw=1.5, label=f"{path1.name} - {path2.name}", alpha=.7)
    plt.xlabel(xlabel)
    plt.ylabel(f"Δ{ylabel}")
    show_legend_outside()
    plt.grid(True, ls="--", alpha=0.6)
    plt.show()


def main():
    args = sys.argv[1:]
    if not args:
        print("Usage:")
        print("  python plot_intensity.py file1.txt [file2.txt ...]")
        print("  python plot_intensity.py --diff file1.txt file2.txt")
        print("  python plot_intensity.py --waterfall file1.txt [file2.txt ...]")
        sys.exit(1)

    if args[0] == "--diff":
        if len(args) != 3:
            print("Error: --diff requires exactly two filenames.")
            sys.exit(1)
        plot_difference(args[1], args[2])

    elif args[0] == "--waterfall":
        if len(args) < 2:
            print("Error: --waterfall requires at least one filename.")
            sys.exit(1)
        plot_waterfall(args[1:])

    else:
        plot_multiple(args)


if __name__ == "__main__":
    main()
