"""One chart style for every notebook, and a helper to save figures."""

import matplotlib.pyplot as plt

from xppg.raw import PROJECT_ROOT

FIG_DIR = PROJECT_ROOT / "outputs" / "figures"

# Categorical slots, always used in this order (never cycled)
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
INK, INK_2, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID, AXIS, SURFACE = "#e1e0d9", "#c3c2b7", "#fcfcfb"


def use_style():
    plt.rcParams.update({
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
        "figure.dpi": 110, "savefig.dpi": 200, "savefig.bbox": "tight",
        "font.size": 10, "axes.titlesize": 12, "axes.titleweight": "bold", "axes.titlelocation": "left",
        "axes.labelcolor": INK_2, "text.color": INK, "xtick.color": MUTED, "ytick.color": MUTED,
        "axes.edgecolor": AXIS, "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "axes.grid.axis": "y", "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
        "axes.prop_cycle": plt.cycler(color=SERIES), "legend.frameon": False,
    })


def save(fig, name):
    """Save to outputs/figures/<name>.png and return the path relative to the project."""
    path = FIG_DIR / f"{name}.png"
    fig.savefig(path)
    return path.relative_to(PROJECT_ROOT)
