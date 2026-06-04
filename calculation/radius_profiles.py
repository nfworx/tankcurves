import numpy as np

from calculation.geometry import calculate_geometry_points


def calculate_radius_profile(da, s, head_type, r1, r2, h2, L, dx=1.0):
    x_values = np.arange(0.0, L + dx, dx)
    R = da / 2 - s

    if head_type in (
        "Torospherical Head (DIN 28011)",
        "Torospherical Head (DIN 28013)",
    ):
        radii = calculate_torospherical_radius_profile(
            x_values, da, s, r1, r2, h2, L
        )

    elif head_type == "Elliptical Head 2:1":
        radii = calculate_elliptical_2to1_radius_profile(
            x_values, da, s, h2, L
        )

    elif head_type == "Hemispherical Head":
        radii = calculate_hemispherical_radius_profile(
            x_values, da, s, L
        )

    elif head_type == "Flat Head":
        radii = np.full_like(x_values, R, dtype=float)

    else:
        raise ValueError(f"Unsupported head type: {head_type}")

    radii = np.clip(radii, 0.0, R)

    return x_values, radii


def calculate_torospherical_radius_profile(x_values, da, s, r1, r2, h2, L):
    R = da / 2 - s
    radii = np.zeros_like(x_values, dtype=float)

    x1, x2, x3, x4 = calculate_geometry_points(da, s, r1, r2, h2, L)

    mask = (x_values >= 0) & (x_values < x1)
    radii[mask] = np.sqrt(np.maximum(r1**2 - (x_values[mask] - r1) ** 2, 0))

    c2x = h2
    c2y = R - r2
    mask = (x_values >= x1) & (x_values < x2)
    radii[mask] = c2y + np.sqrt(
        np.maximum(r2**2 - (x_values[mask] - c2x) ** 2, 0)
    )

    mask = (x_values >= x2) & (x_values < L - h2)
    radii[mask] = R

    c2x = L - h2
    mask = (x_values >= L - h2) & (x_values < x4)
    radii[mask] = c2y + np.sqrt(
        np.maximum(r2**2 - (x_values[mask] - c2x) ** 2, 0)
    )

    mask = (x_values >= x4) & (x_values <= L)
    radii[mask] = np.sqrt(
        np.maximum(r1**2 - (x_values[mask] - (L - r1)) ** 2, 0)
    )

    return radii


def calculate_elliptical_2to1_radius_profile(x_values, da, s, h2, L):
    R = da / 2 - s
    radii = np.zeros_like(x_values, dtype=float)

    if h2 <= 0:
        return radii

    mask = (x_values >= 0) & (x_values <= h2)
    radii[mask] = R * np.sqrt(
        np.maximum(1 - ((x_values[mask] - h2) / h2) ** 2, 0)
    )

    mask = (x_values > h2) & (x_values < L - h2)
    radii[mask] = R

    mask = (x_values >= L - h2) & (x_values <= L)
    radii[mask] = R * np.sqrt(
        np.maximum(1 - ((x_values[mask] - (L - h2)) / h2) ** 2, 0)
    )

    return radii


def calculate_hemispherical_radius_profile(x_values, da, s, L):
    R = da / 2 - s
    radii = np.zeros_like(x_values, dtype=float)

    mask = (x_values >= 0) & (x_values <= R)
    radii[mask] = np.sqrt(np.maximum(R**2 - (x_values[mask] - R) ** 2, 0))

    mask = (x_values > R) & (x_values < L - R)
    radii[mask] = R

    mask = (x_values >= L - R) & (x_values <= L)
    radii[mask] = np.sqrt(
        np.maximum(R**2 - (x_values[mask] - (L - R)) ** 2, 0)
    )

    return radii