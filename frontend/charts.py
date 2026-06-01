from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def calculate_stats(df: pd.DataFrame) -> dict[str, Any]:
    return {
        "count": len(df),
        "avg_completion": float(np.mean(df["global_percent"])),
        "median_completion": float(np.median(df["global_percent"])),
        "hardest": df.nsmallest(1, "global_percent").iloc[0],
        "easiest": df.nlargest(1, "global_percent").iloc[0],
    }


def plot_achievement_chart(
    df: pd.DataFrame,
    player_df: pd.DataFrame | None = None,
) -> plt.Figure:
    top_hard = df.nsmallest(20, "global_percent")

    unlocked_names: set[str] = set()
    if player_df is not None:
        unlocked_names = set(
            player_df.loc[player_df["achieved"], "name"]
        )

    color_values = np.linspace(0.1, 0.9, len(top_hard))
    colors = [plt.cm.RdYlGn(v) for v in color_values]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(top_hard["display_name"], top_hard["global_percent"], color=colors)

    labels = []
    for bar, name in zip(bars, top_hard["name"]):
        if name in unlocked_names:
            bar.set_edgecolor("#1f77b4")
            bar.set_linewidth(2.5)
            labels.append("★")
        else:
            labels.append("")

    ax.set_xlabel("Global completion (%)")
    title = "De 20 sværeste achievements"
    if unlocked_names:
        title += "  (★ = du har denne)"
    ax.set_title(title)
    ax.invert_yaxis()
    ax.bar_label(bars, labels=labels, padding=3, fontsize=10)
    plt.tight_layout()
    return fig
