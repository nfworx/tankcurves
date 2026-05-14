#tank_preview.py
import matplotlib.pyplot as plt
import numpy as np

from calculation import calculate_geometry_points, radius_at_x
from models import get_head_parameters

from drawing.utilities import (
    fit_equal_view,
    get_wall_linewidth,
)


TOROSPHERICAL_HEADS = {
    "Torospherical Head (DIN 28011)",
    "Torospherical Head (DIN 28013)",
}


def draw_tank_preview(
    vessel_type,
    head_type,
    outer_diameter_mm,
    wall_thickness_mm,
    length_mm,
):
    da = outer_diameter_mm
    s = wall_thickness_mm
    L = length_mm

    head = get_head_parameters(head_type, da, s)

    r1 = head.r1_mm
    r2 = head.r2_mm
    h2 = head.h2_mm

    inner_radius = da / 2 - s

    wall_lw = get_wall_linewidth(s, da)

    # -------------------------------------------------
    # Generate geometry points
    # -------------------------------------------------

    if head_type in TOROSPHERICAL_HEADS:
        x1, x2, x3, x4 = calculate_geometry_points(
            da,
            s,
            r1,
            r2,
            h2,
            L,
        )

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
        [
            radius_at_x(
                xi,
                da,
                s,
                head_type,
                r1,
                r2,
                h2,
                L,
            )
            for xi in x
        ]
    )

    # -------------------------------------------------
    # Figure setup
    # -------------------------------------------------

    fig, ax = plt.subplots(
        figsize=(5.8, 2.8),
        dpi=110,
    )

    line_color = "#003366"
    helper_color = "gray"

    dim_arrow = dict(
        arrowstyle="<->",
        color="black",
        linewidth=0.9,
        mutation_scale=12,
    )

    # =================================================
    # VERTICAL TANK
    # =================================================

    if vessel_type == "Vertical Tank":

        # shell
        ax.plot(
            r,
            x,
            color=line_color,
            linewidth=wall_lw,
        )

        ax.plot(
            -r,
            x,
            color=line_color,
            linewidth=wall_lw,
        )

        if head_type == "Flat Head":
            ax.hlines(
                [0, L],
                xmin=-inner_radius,
                xmax=inner_radius,
                colors=line_color,
                linewidth=wall_lw,
            )

        # centerline
        ax.axvline(
            0,
            color=helper_color,
            linestyle="--",
            linewidth=0.8,
            alpha=0.55,
        )

        # helper lines
        ax.hlines(
            [0, L],
            xmin=-inner_radius * 1.9,
            xmax=inner_radius * 1.9,
            colors=helper_color,
            linestyles="--",
            linewidth=0.8,
            alpha=0.45,
        )

        # ---------------------------------------------
        # L dimension
        # ---------------------------------------------

        x_dim = inner_radius * 2.2

        ax.annotate(
            "",
            xy=(x_dim, 0),
            xytext=(x_dim, L),
            arrowprops=dim_arrow,
        )

        ax.text(
            x_dim + da * 0.04,
            L / 2,
            "L",
            rotation=90,
            va="center",
        )

        # ---------------------------------------------
        # d_a dimension
        # ---------------------------------------------

        y_da = -da * 0.65

        ax.annotate(
            "",
            xy=(-da / 2, y_da),
            xytext=(da / 2, y_da),
            arrowprops=dim_arrow,
        )

        ax.text(
            0,
            y_da - da * 0.05,
            "dₐ",
            ha="center",
            va="top",
        )

        # vertical helper lines
        ax.vlines(
            [-da / 2, da / 2],
            ymin=y_da,
            ymax=0,
            colors=helper_color,
            linestyles="--",
            linewidth=0.8,
            alpha=0.45,
        )

        fit_equal_view(
            ax,
            xmin=-inner_radius * 2.6,
            xmax=inner_radius * 2.6,
            ymin=-da * 0.85,
            ymax=L,
            pad=0.06,
        )

    # =================================================
    # HORIZONTAL TANK
    # =================================================

    else:

        # shell
        ax.plot(
            x,
            r,
            color=line_color,
            linewidth=wall_lw,
        )

        ax.plot(
            x,
            -r,
            color=line_color,
            linewidth=wall_lw,
        )

        if head_type == "Flat Head":
            ax.vlines(
                [0, L],
                ymin=-inner_radius,
                ymax=inner_radius,
                colors=line_color,
                linewidth=wall_lw,
            )

        # centerline
        ax.axhline(
            0,
            color=helper_color,
            linestyle="--",
            linewidth=0.8,
            alpha=0.55,
        )

        # helper lines
        ax.vlines(
            [0, L],
            ymin=-inner_radius * 1.5,
            ymax=inner_radius * 1.5,
            colors=helper_color,
            linestyles="--",
            linewidth=0.8,
            alpha=0.45,
        )

        # ---------------------------------------------
        # L dimension
        # ---------------------------------------------

        y_dim = inner_radius * 1.7

        ax.annotate(
            "",
            xy=(0, y_dim),
            xytext=(L, y_dim),
            arrowprops=dim_arrow,
        )

        ax.text(
            L / 2,
            y_dim + da * 0.05,
            "L",
            ha="center",
        )

        # ---------------------------------------------
        # d_a dimension
        # ---------------------------------------------

        x_da = -da * 0.75

        ax.annotate(
            "",
            xy=(x_da, -da / 2),
            xytext=(x_da, da / 2),
            arrowprops=dim_arrow,
        )

        ax.text(
            x_da - da * 0.05,
            0,
            "dₐ",
            rotation=90,
            va="center",
            ha="right",
        )

        # horizontal helper lines
        ax.hlines(
            [-da / 2, da / 2],
            xmin=x_da,
            xmax=0,
            colors=helper_color,
            linestyles="--",
            linewidth=0.8,
            alpha=0.45,
        )

        fit_equal_view(
            ax,
            xmin=x_da - da * 0.10,
            xmax=L,
            ymin=-inner_radius * 2.1,
            ymax=inner_radius * 2.1,
            pad=0.06,
        )

    ax.axis("off")

    fig.tight_layout(pad=0.05)

    return fig