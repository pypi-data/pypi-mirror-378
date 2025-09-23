from typing import Optional, Tuple

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import numpy as np

from runkmc.results import SimulationResult


def plot_monomer_conversion(result: SimulationResult, ax: Optional[Axes] = None):
    """Plot monomer conversion over time from simulation result."""

    if ax is None:
        fig, ax = plt.subplots(figsize=(3.5, 3.5), dpi=300)

    state = result.results

    for monomer_name, monomer_conv in state.unit_convs.items():
        ax.plot(state.kmc_time, monomer_conv, label=monomer_name)

    ax.set_xlabel("KMC Time")
    ax.set_ylabel("Monomer Conversion")
    ax.legend(frameon=False)

    plt.tight_layout()

    return ax


def plot_monomer_counts(result: SimulationResult, ax: Optional[Axes] = None):
    """Plot monomer counts over time from simulation result."""

    if ax is None:
        fig, ax = plt.subplots(figsize=(3.5, 3.5), dpi=300)

    state = result.results
    for monomer_name, monomer_count in state.unit_counts.items():
        ax.plot(state.kmc_time, monomer_count, label=monomer_name)

    ax.set_xlabel("KMC Time")
    ax.set_ylabel("Monomer Count")
    ax.legend(frameon=False)

    plt.tight_layout()
    return ax
