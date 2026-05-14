import matplotlib.pyplot as plt
import numpy as np

from calculation import calculate_geometry_points, radius_at_x
from models import get_head_parameters
from drawing.utilities import fit_equal_view, get_wall_linewidth


TOROSPHERICAL_HEADS = {
    "Torospherical Head (DIN 28011)",
    "Torospherical Head (DIN 28013)",
}


def draw_radius_marker(
    ax,
    end_x,
    end_y,
    direction_x,
    direction_y,
    label,
    length,
    label_side=1,
):
    direction_length = np.hypot(direction_x, direction_y)

    if direction_length == 0:
        return

    direction_x /= direction_length
    direction_y /= direction_length

    start_x = end_x - direction_x * length
    start_y = end_y - direction_y * length

    ax.annotate(
        "",
        xy=(end_x, end_y),
        xytext=(start_x, start_y),
        arrowprops=dict(
            arrowstyle="->",
            color="black",
            linewidth=0.9,
            mutation_scale=12,
            shrinkA=0,
            shrinkB=0,
        ),
    )

    normal_x = -direction_y
    normal_y = direction_x

    label_x = (start_x + end_x) / 2 + label_side * normal_x * length * 0.22
    label_y = (start_y + end_y) / 2 + label_side * normal_y * length * 0.22

    ax.text(
        label_x,
        label_y,
        label,
        fontsize=10,
        ha="center",
        va="center",
        rotation=np.degrees(np.arctan2(direction_y, direction_x)),
        rotation_mode="anchor",
    )

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
    h = head.h2_mm

    R = da / 2 - s
    straight_section_draw = max(3.5 * s, da * 0.08)

    wall_lw = get_wall_linewidth(s, da)

    fig, ax = plt.subplots(figsize=(5.8, 2.8), dpi=110)

    line_color = "#003366"
    dim_color = "black"
    helper_color = "gray"

    dim_arrow = dict(
        arrowstyle="<->",
        color=dim_color,
        linewidth=0.9,
        mutation_scale=12,
    )

    if h <= 0:
        ax.hlines(0, xmin=-R, xmax=R, color=line_color, linewidth=wall_lw)
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

    depth = np.linspace(0, h, 500)

    radius = np.array(
        [
            radius_at_x(xi, da, s, head_type, r1, r2, h, 2 * h + 1000)
            for xi in depth
        ]
    )

    y = depth - h

    ax.plot(radius, y, color=line_color, linewidth=wall_lw)
    ax.plot(-radius, y, color=line_color, linewidth=wall_lw)

    ax.vlines(
        [-R, R],
        ymin=0,
        ymax=straight_section_draw,
        colors=line_color,
        linewidth=wall_lw,
    )

    x_left_dim = -da * 0.70
    x_right_dim = da * 0.70

    ax.hlines(
        [0, -h],
        xmin=x_left_dim,
        xmax=x_right_dim,
        colors=helper_color,
        linestyles="--",
        linewidth=0.8,
        alpha=0.55,
    )

    ax.axvline(0, color=helper_color, linestyle="--", linewidth=0.8, alpha=0.55)

    x_h = -da * 0.74

    ax.annotate("", xy=(x_h, 0), xytext=(x_h, -h), arrowprops=dim_arrow)
    ax.text(
        x_h - da * 0.025,
        -h / 2,
        "h",
        rotation=90,
        ha="center",
        va="center",
    )

    if head_type in TOROSPHERICAL_HEADS:
        x1, x2, _, _ = calculate_geometry_points(
            da=da,
            s=s,
            r1=r1,
            r2=r2,
            h2=h,
            L=2 * h + 1000,
        )

        # -------------------------------------------------
        # r1 at x1
        # Crown radius: center is on the symmetry axis.
        # Draw from inside toward the inner curve.
        # -------------------------------------------------

        r1_depth = x1 * 0.1
        r1_radius = radius_at_x(
            r1_depth,
            da,
            s,
            head_type,
            r1,
            r2,
            h,
            2 * h + 1000,
        )
        r1_y = r1_depth - h

        r1_center_x = 0.0
        r1_center_y = r1 - h

        r1_dir_x = r1_radius - r1_center_x
        r1_dir_y = r1_y - r1_center_y

        draw_radius_marker(
            ax=ax,
            end_x=r1_radius,
            end_y=r1_y,
            direction_x=r1_dir_x,
            direction_y=r1_dir_y,
            label="r₁",
            length=da * 0.12,
            label_side=-1,
        )

        # -------------------------------------------------
        # r2 at x2
        # Knuckle radius: center is inside the head.
        # x2 is the tangent point to the straight shell.
        # Draw from inside toward the inner curve.
        # -------------------------------------------------

        r2_depth = x1*1.1
        r2_radius = radius_at_x(
            r2_depth,
            da,
            s,
            head_type,
            r1,
            r2,
            h,
            2 * h + 1000,
        )
        r2_y = r2_depth - h

        r2_center_x = R - r2
        r2_center_y = 0.0

        r2_dir_x = r2_radius - r2_center_x
        r2_dir_y = r2_y - r2_center_y

        draw_radius_marker(
            ax=ax,
            end_x=r2_radius,
            end_y=r2_y,
            direction_x=r2_dir_x,
            direction_y=r2_dir_y,
            label="r₂",
            length=da * 0.09,
            label_side=1,
        )

    elif head_type == "Elliptical Head 2:1":
        a = h
        b = R

        # r1 weiter innen / unten auf der großen Ellipse
        r1_depth = h * 0.1
        r1_radius = radius_at_x(r1_depth, da, s, head_type, r1, r2, h, 2 * h + 1000)
        r1_y = r1_depth - h

        r1_dir_x = r1_radius / b**2
        r1_dir_y = r1_y / a**2

        draw_radius_marker(
            ax=ax,
            end_x=r1_radius,
            end_y=r1_y,
            direction_x=r1_dir_x,
            direction_y=r1_dir_y,
            label="r₁",
            length=da * 0.09,
            label_side=1,
        )

        # r2 oben am Rand / kleiner Ersatzradius
        r2_depth = h * 0.8
        r2_radius = radius_at_x(r2_depth, da, s, head_type, r1, r2, h, 2 * h + 1000)
        r2_y = r2_depth - h

        r2_dir_x = r2_radius / b**2
        r2_dir_y = r2_y / a**2

        draw_radius_marker(
            ax=ax,
            end_x=r2_radius,
            end_y=r2_y,
            direction_x=r2_dir_x,
            direction_y=r2_dir_y,
            label="r₂",
            length=da * 0.09,
            label_side=1,
        )

    elif head_type == "Hemispherical Head":
        ax.text(0, -h * 0.55, "hemispherical", ha="center", fontsize=10)

    fit_equal_view(
        ax,
        xmin=-da * 0.82,
        xmax=da * 0.82,
        ymin=-h * 1.12,
        ymax=straight_section_draw + da * 0.10,
        pad=0.02,
    )

    ax.axis("off")
    fig.tight_layout(pad=0.1)
    return fig