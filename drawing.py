# drawing.py

import matplotlib.pyplot as plt
import numpy as np

from calculation import calculate_geometry_points, radius_at_x
from models import get_head_parameters

def draw_tank_preview(
    vessel_type: str,
    head_type: str,
    outer_diameter_mm: float,
    wall_thickness_mm: float,
    length_mm: float,
):
    da = outer_diameter_mm
    s = wall_thickness_mm
    L = length_mm

    head = get_head_parameters(head_type, da, s)

    r1 = head.r1_mm
    r2 = head.r2_mm
    h2 = head.h2_mm

    x1, x2, x3, x4 = calculate_geometry_points(da, s, r1, r2, h2, L)

    x = np.unique(
        np.concatenate(
            [
                np.linspace(0, x1, 180),
                np.linspace(x1, x2, 180),
                np.linspace(x2, x3, 400),
                np.linspace(x3, x4, 180),
                np.linspace(x4, L, 180),
            ]
        )
    )

    r = np.array([radius_at_x(xi, da, s, r1, r2, h2, L) for xi in x])

    fig, ax = plt.subplots(figsize=(12, 4))

    line_color = "#003366"
    dim_color = "black"
    helper_color = "gray"

    # Tank contour
    ax.plot(x, r, color=line_color, linewidth=2.8)
    ax.plot(x, -r, color=line_color, linewidth=2.8)

    # Centerlines
    ax.axhline(0, color=dim_color, linestyle="--", linewidth=0.8, alpha=0.55)
    ax.axvline(L / 2, color=dim_color, linestyle="--", linewidth=0.8, alpha=0.55)

    # Helper lines for cylinder radius
    inner_radius = da / 2 - s
    ax.hlines(
        [inner_radius, -inner_radius],
        xmin=0,
        xmax=L,
        colors=helper_color,
        linewidth=0.8,
        alpha=0.35,
    )

    # Dimension: length
    y_dim = -da * 0.72
    ax.annotate(
        "",
        xy=(0, y_dim),
        xytext=(L, y_dim),
        arrowprops=dict(arrowstyle="<->", color=dim_color, linewidth=0.9),
    )
    ax.text(L / 2, y_dim - da * 0.07, f"L = {L:.0f} mm", ha="center", va="top")

    # Dimension: outer diameter
    x_dim = -L * 0.06
    ax.annotate(
        "",
        xy=(x_dim, -da / 2),
        xytext=(x_dim, da / 2),
        arrowprops=dict(arrowstyle="<->", color=dim_color, linewidth=0.9),
    )
    ax.text(
        x_dim - L * 0.015,
        0,
        f"dₐ = {da:.0f} mm",
        rotation=90,
        ha="center",
        va="center",
    )

    # Dimension: inner diameter
    x_dim_inner = L * 1.045
    ax.annotate(
        "",
        xy=(x_dim_inner, -inner_radius),
        xytext=(x_dim_inner, inner_radius),
        arrowprops=dict(arrowstyle="<->", color=dim_color, linewidth=0.9),
    )
    ax.text(
        x_dim_inner + L * 0.015,
        0,
        f"dᵢ = {2 * inner_radius:.0f} mm",
        rotation=90,
        ha="center",
        va="center",
    )

    # Head depth left/right
    h2_inner = h2 - s
    y_head = da * 0.63

    ax.annotate(
        "",
        xy=(0, y_head),
        xytext=(h2_inner, y_head),
        arrowprops=dict(arrowstyle="<->", color=dim_color, linewidth=0.9),
    )
    ax.text(h2_inner / 2, y_head + da * 0.06, f"h₂ = {h2_inner:.0f} mm", ha="center")

    ax.annotate(
        "",
        xy=(L - h2_inner, y_head),
        xytext=(L, y_head),
        arrowprops=dict(arrowstyle="<->", color=dim_color, linewidth=0.9),
    )
    ax.text(
        L - h2_inner / 2,
        y_head + da * 0.06,
        f"h₂ = {h2_inner:.0f} mm",
        ha="center",
    )

    # Wall thickness label
    ax.text(L / 2, da * 0.56, f"s = {s:.1f} mm", ha="center")

    # Radius labels
    ax.text(h2_inner * 0.7, da * 0.22, f"r₂ = {r2:.0f} mm", ha="center")
    ax.text(h2_inner * 0.9, -da * 0.30, f"r₁ = {r1:.0f} mm", ha="center")

    ax.text(L - h2_inner * 0.7, da * 0.22, f"r₂ = {r2:.0f} mm", ha="center")
    ax.text(L - h2_inner * 0.9, -da * 0.30, f"r₁ = {r1:.0f} mm", ha="center")

    ax.set_title(f"{vessel_type} – {head_type}", fontsize=11)

    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")

    ax.set_xlim(-L * 0.12, L * 1.12)
    ax.set_ylim(-da * 0.85, da * 0.85)

    fig.tight_layout()
    return fig