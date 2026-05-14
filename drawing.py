# drawing.py

import matplotlib.pyplot as plt
import numpy as np

from calculation import calculate_geometry_points, radius_at_x
from models import get_head_parameters


TOROSPHERICAL_HEADS = {
    "Torospherical Head (DIN 28011)",
    "Torospherical Head (DIN 28013)",
}


def fit_equal_view(ax, xmin, xmax, ymin, ymax, pad=0.08):
    width = xmax - xmin
    height = ymax - ymin

    cx = (xmin + xmax) / 2
    cy = (ymin + ymax) / 2

    fig = ax.figure
    fig_w, fig_h = fig.get_size_inches()
    fig_ratio = fig_w / fig_h

    data_width = width * (1 + pad)
    data_height = height * (1 + pad)

    if data_height == 0:
        data_height = 1

    data_ratio = data_width / data_height

    if data_ratio > fig_ratio:
        final_width = data_width
        final_height = data_width / fig_ratio
    else:
        final_height = data_height
        final_width = data_height * fig_ratio

    ax.set_xlim(cx - final_width / 2, cx + final_width / 2)
    ax.set_ylim(cy - final_height / 2, cy + final_height / 2)
    ax.set_aspect("equal", adjustable="box")


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

    inner_radius = da / 2 - s

    if head_type in TOROSPHERICAL_HEADS:
        x1, x2, x3, x4 = calculate_geometry_points(da, s, r1, r2, h2, L)

        x = np.unique(
            np.concatenate(
                [
                    np.linspace(0, x1, 120),
                    np.linspace(x1, x2, 120),
                    np.linspace(x2, x3, 240),
                    np.linspace(x3, x4, 120),
                    np.linspace(x4, L, 120),
                ]
            )
        )
    else:
        x = np.linspace(0, L, 600)

    r = np.array(
        [radius_at_x(xi, da, s, head_type, r1, r2, h2, L) for xi in x]
    )

    fig, ax = plt.subplots(figsize=(4.8, 2.0), dpi=110)

    line_color = "#003366"
    centerline_color = "gray"
    helper_color = "lightgray"
    lw = 1.8

    if vessel_type == "Vertical Tank":
        ax.plot(r, x, color=line_color, linewidth=lw)
        ax.plot(-r, x, color=line_color, linewidth=lw)

        if head_type == "Flat Head":
            ax.hlines(
                [0, L],
                xmin=-inner_radius,
                xmax=inner_radius,
                color=line_color,
                linewidth=lw,
            )

        ax.axvline(0, color=centerline_color, linestyle="--", linewidth=0.7, alpha=0.55)
        ax.axhline(L / 2, color=centerline_color, linestyle="--", linewidth=0.7, alpha=0.55)

        ax.vlines(
            [-inner_radius, inner_radius],
            ymin=0,
            ymax=L,
            colors=helper_color,
            linewidth=0.7,
            alpha=0.45,
        )

        fit_equal_view(
            ax,
            xmin=-inner_radius,
            xmax=inner_radius,
            ymin=0,
            ymax=L,
            pad=0.12,
        )

    else:
        ax.plot(x, r, color=line_color, linewidth=lw)
        ax.plot(x, -r, color=line_color, linewidth=lw)

        if head_type == "Flat Head":
            ax.vlines(
                [0, L],
                ymin=-inner_radius,
                ymax=inner_radius,
                color=line_color,
                linewidth=lw,
            )

        ax.axhline(0, color=centerline_color, linestyle="--", linewidth=0.7, alpha=0.55)
        ax.axvline(L / 2, color=centerline_color, linestyle="--", linewidth=0.7, alpha=0.55)

        ax.hlines(
            [-inner_radius, inner_radius],
            xmin=0,
            xmax=L,
            colors=helper_color,
            linewidth=0.7,
            alpha=0.45,
        )

        fit_equal_view(
            ax,
            xmin=0,
            xmax=L,
            ymin=-inner_radius,
            ymax=inner_radius,
            pad=0.12,
        )

    ax.axis("off")
    fig.tight_layout(pad=0.05)
    return fig


def draw_head_dimensions_preview(
    head_type: str,
    outer_diameter_mm: float,
    wall_thickness_mm: float,
):
    da = outer_diameter_mm
    s = wall_thickness_mm

    head = get_head_parameters(head_type, da, s)

    r1 = head.r1_mm
    r2 = head.r2_mm
    h2 = head.h2_mm

    R = da / 2 - s
    h1 = 3.5 * s

    if h2 <= 0:
        fig, ax = plt.subplots(figsize=(5.8, 2.4), dpi=110)

        line_color = "#003366"
        dim_color = "black"
        helper_color = "gray"

        ax.hlines(0, xmin=-R, xmax=R, color=line_color, linewidth=2.0)

        y_da = da * 0.08
        ax.annotate(
            "",
            xy=(-da / 2, y_da),
            xytext=(da / 2, y_da),
            arrowprops=dict(arrowstyle="<->", color=dim_color, linewidth=0.9),
        )
        ax.text(0, y_da + da * 0.025, "dₐ", ha="center", va="bottom", fontsize=10)
        ax.text(0, -da * 0.05, "flat head", ha="center", va="top", fontsize=10)

        ax.axvline(0, color=helper_color, linestyle="--", linewidth=0.8, alpha=0.55)

        fit_equal_view(
            ax,
            xmin=-da * 0.65,
            xmax=da * 0.65,
            ymin=-da * 0.16,
            ymax=da * 0.18,
            pad=0.02,
        )

        ax.axis("off")
        fig.tight_layout(pad=0.1)
        return fig

    depth = np.linspace(0, h2, 500)

    radius = np.array(
        [
            radius_at_x(
                xi,
                da,
                s,
                head_type,
                r1,
                r2,
                h2,
                2 * h2 + 1000,
            )
            for xi in depth
        ]
    )

    y = depth - h2

    fig, ax = plt.subplots(figsize=(5.8, 2.4), dpi=110)

    line_color = "#003366"
    dim_color = "black"
    helper_color = "gray"

    ax.plot(radius, y, color=line_color, linewidth=2.0)
    ax.plot(-radius, y, color=line_color, linewidth=2.0)

    ax.hlines(0, xmin=-R, xmax=R, color=helper_color, linewidth=0.8, alpha=0.45)
    ax.axvline(0, color=helper_color, linestyle="--", linewidth=0.8, alpha=0.55)

    y_da = h1 + da * 0.025
    ax.annotate(
        "",
        xy=(-da / 2, y_da),
        xytext=(da / 2, y_da),
        arrowprops=dict(arrowstyle="<->", color=dim_color, linewidth=0.9),
    )
    ax.text(0, y_da + da * 0.018, "dₐ", ha="center", va="bottom", fontsize=10)

    x_h2 = -da * 0.56
    ax.annotate(
        "",
        xy=(x_h2, 0),
        xytext=(x_h2, -h2),
        arrowprops=dict(arrowstyle="<->", color=dim_color, linewidth=0.9),
    )
    ax.text(x_h2 - da * 0.025, -h2 / 2, "h₂", rotation=90, ha="center", va="center")

    x_h1 = -da * 0.63
    ax.annotate(
        "",
        xy=(x_h1, h1),
        xytext=(x_h1, 0),
        arrowprops=dict(arrowstyle="<->", color=dim_color, linewidth=0.9),
    )
    ax.text(x_h1 - da * 0.025, h1 / 2, "h₁", rotation=90, ha="center", va="center")

    x_h3 = da * 0.56
    ax.annotate(
        "",
        xy=(x_h3, h1),
        xytext=(x_h3, -h2),
        arrowprops=dict(arrowstyle="<->", color=dim_color, linewidth=0.9),
    )
    ax.text(x_h3 + da * 0.025, (h1 - h2) / 2, "h₃", rotation=90, ha="center", va="center")

    if head_type in TOROSPHERICAL_HEADS:
        ax.text(-R * 0.82, -h2 * 0.30, "r₂", fontsize=10)
        ax.text(R * 0.20, -h2 * 0.72, "r₁", fontsize=10)
        ax.text(R * 0.60, -h2 * 0.78, "s", fontsize=10)

    elif head_type == "Elliptical Head 2:1":
        ax.text(0, -h2 * 0.55, "2:1 elliptical", ha="center", fontsize=10)

    elif head_type == "Hemispherical Head":
        ax.text(0, -h2 * 0.55, "hemispherical", ha="center", fontsize=10)

    fit_equal_view(
        ax,
        xmin=-da * 0.70,
        xmax=da * 0.70,
        ymin=-h2 * 1.12,
        ymax=h1 + da * 0.10,
        pad=0.02,
    )

    ax.axis("off")
    fig.tight_layout(pad=0.1)
    return fig