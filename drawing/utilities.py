import numpy as np


def fit_equal_view(ax, xmin, xmax, ymin, ymax, pad=0.08):
    width = xmax - xmin
    height = ymax - ymin

    cx = (xmin + xmax) / 2
    cy = (ymin + ymax) / 2

    fig_w, fig_h = ax.figure.get_size_inches()
    fig_ratio = fig_w / fig_h

    data_width = width * (1 + pad)
    data_height = max(height * (1 + pad), 1)

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


def get_wall_linewidth(s, da):
    return min(max(s / da * 180, 1.6), 5.0)


def point_on_curve(radius, y, target_x):
    idx = int(np.argmin(np.abs(radius - target_x)))
    return radius[idx], y[idx]