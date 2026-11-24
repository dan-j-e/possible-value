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


STAT_LABELS = {"pts": "Points", "ast": "Assists", "reb": "Rebounds", "stl": "Steals", "blk": "Blocks",
               "stk": "Stocks (steals + blocks)"}
UP, DOWN = SERIES[0], SERIES[7]  # blue = rose, red = fell


def short_name(name):
    """"Shai Gilgeous-Alexander" -> "S. Gilgeous-Alexander"."""
    first, _, rest = name.partition(" ")
    return f"{first[0]}. {rest}" if rest else name


def rank_panel(ax, season_rows, stat, n=10, decimals=1):
    """Top n per game (left) and per possible game (right), with each left player's move in between."""
    pg, ppg = f"{stat}_pg", f"{stat}_ppg"
    df = season_rows.copy()
    df["pg_rank"] = df[pg].rank(ascending=False, method="min")
    df["ppg_rank"] = df[ppg].rank(ascending=False, method="min")
    left = df.sort_values([pg, ppg], ascending=False).head(n)
    right = df.sort_values([ppg, pg], ascending=False).head(n)

    ax.set_axis_off()
    ax.set_xlim(0, 1); ax.set_ylim(n + 0.6, -0.9)
    ax.text(0.0, -0.4, "Per game", fontsize=9, fontweight="bold", color=INK_2)
    ax.text(0.60, -0.4, "Per possible game", fontsize=9, fontweight="bold", color=INK_2)
    for i, (_, r) in enumerate(left.iterrows(), start=1):
        ax.text(0.0, i, f"{int(r.pg_rank)}. {short_name(r.player_name)}", fontsize=8.5, va="center")
        ax.text(0.425, i, f"{r[pg]:.{decimals}f}", fontsize=8.5, va="center", ha="right", color=INK_2)
        new = int(r.ppg_rank)
        if r.ppg_rank < r.pg_rank:
            glyph, colour = "↗", UP
        elif r.ppg_rank > r.pg_rank:
            glyph, colour = "↘", DOWN
        else:
            glyph, colour = "=", MUTED
        ax.text(0.46, i, glyph, fontsize=11, va="center", ha="center", color=colour, fontweight="bold")
        ax.text(0.485, i, str(new), fontsize=8.5, va="center", color=colour, fontweight="bold")
    for i, (_, r) in enumerate(right.iterrows(), start=1):
        ax.text(0.60, i, f"{int(r.ppg_rank)}. {short_name(r.player_name)}", fontsize=8.5, va="center")
        ax.text(1.0, i, f"{r[ppg]:.{decimals}f}", fontsize=8.5, va="center", ha="right", color=INK_2)


def rank_grid(ps, seasons, stats, in_progress=None, title=None):
    """One row per season, one panel per stat."""
    fig, axes = plt.subplots(len(seasons), len(stats), figsize=(6.6 * len(stats), 3.1 * len(seasons)),
                             squeeze=False, gridspec_kw={"wspace": 0.12, "hspace": 0.25})
    for i, season in enumerate(seasons):
        rows = ps[ps.season == season]
        for j, stat in enumerate(stats):
            rank_panel(axes[i, j], rows, stat, decimals=2 if stat in ("stl", "blk") else 1)
            if i == 0:
                axes[i, j].set_title(STAT_LABELS[stat], fontsize=14, pad=14)
        label = season + ("\n(so far)" if season == in_progress else "")
        axes[i, 0].text(-0.08, 0.5, label, transform=axes[i, 0].transAxes, rotation=90, ha="center", va="center",
                        fontsize=13, fontweight="bold")
    if title:
        top = axes[0, 0].get_position().y1
        fig.suptitle(title, x=0.11, y=top + 0.95 / fig.get_figheight(), ha="left", va="bottom", fontsize=18, fontweight="bold")
        fig.text(0.11, top + 0.62 / fig.get_figheight(), va="bottom", s="Left: top 10 per game played. Right: top 10 per possible game. Middle: where each "
                 "left-hand player ranks per possible game (blue ↗ rose, red ↘ fell). Whole league, no minimum games.",
                 ha="left", fontsize=11, color=MUTED)
    return fig
