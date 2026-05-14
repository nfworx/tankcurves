import math

import numpy as np

from models import TankInput, get_head_parameters


def calculate_filling_curve(tank: TankInput) -> list[tuple[float, float]]:
    head = get_head_parameters(
        tank.head_type,
        tank.outer_diameter_mm,
        tank.wall_thickness_mm,
    )

    inner_length = tank.length_mm - 2 * tank.wall_thickness_mm

    if tank.vessel_type == "Vertical Tank":
        return calculate_vertical(
            tank.outer_diameter_mm,
            tank.wall_thickness_mm,
            tank.head_type,
            head.r1_mm,
            head.r2_mm,
            head.h2_mm,
            inner_length,
        )

    if tank.vessel_type == "Horizontal Tank":
        return calculate_horizontal(
            tank.outer_diameter_mm,
            tank.wall_thickness_mm,
            tank.head_type,
            head.r1_mm,
            head.r2_mm,
            head.h2_mm,
            inner_length,
        )

    raise ValueError(f"Unsupported vessel type: {tank.vessel_type}")


def calculate_geometry_points(da, s, r1, r2, h2, L):
    R = da / 2 - s

    c1x = r1
    c1y = 0.0

    c2x = h2
    c2y = R - r2

    dx = c2x - c1x
    dy = c2y - c1y

    d = math.hypot(dx, dy)

    if d == 0:
        raise ValueError("Invalid torospherical head geometry.")

    x1 = c1x + r1 * dx / d
    x2 = h2

    x3 = L - h2
    x4 = L - x1

    return x1, x2, x3, x4


def radius_at_x(x, da, s, head_type, r1, r2, h2, L):
    if head_type in (
        "Torospherical Head (DIN 28011)",
        "Torospherical Head (DIN 28013)",
    ):
        return radius_torospherical_at_x(x, da, s, r1, r2, h2, L)

    if head_type == "Elliptical Head 2:1":
        return radius_elliptical_2to1_at_x(x, da, s, h2, L)

    if head_type == "Hemispherical Head":
        return radius_hemispherical_at_x(x, da, s, L)

    if head_type == "Flat Head":
        return radius_flat_at_x(x, da, s, L)

    raise ValueError(f"Unsupported head type: {head_type}")


def radius_torospherical_at_x(x, da, s, r1, r2, h2, L):
    R = da / 2 - s

    x1, x2, x3, x4 = calculate_geometry_points(da, s, r1, r2, h2, L)

    if 0 <= x < x1:
        return math.sqrt(max(r1**2 - (x - r1) ** 2, 0))

    if x1 <= x < x2:
        c2x = h2
        c2y = R - r2
        return c2y + math.sqrt(max(r2**2 - (x - c2x) ** 2, 0))

    if x2 <= x < x3:
        return R

    if x3 <= x < x4:
        c2x = L - h2
        c2y = R - r2
        return c2y + math.sqrt(max(r2**2 - (x - c2x) ** 2, 0))

    if x4 <= x <= L:
        return math.sqrt(max(r1**2 - (x - (L - r1)) ** 2, 0))

    return 0


def radius_elliptical_2to1_at_x(x, da, s, h2, L):
    R = da / 2 - s

    if h2 <= 0:
        return 0

    if 0 <= x <= h2:
        return R * math.sqrt(max(1 - ((x - h2) / h2) ** 2, 0))

    if h2 < x < L - h2:
        return R

    if L - h2 <= x <= L:
        return R * math.sqrt(max(1 - ((x - (L - h2)) / h2) ** 2, 0))

    return 0


def radius_hemispherical_at_x(x, da, s, L):
    R = da / 2 - s

    if 0 <= x <= R:
        return math.sqrt(max(R**2 - (x - R) ** 2, 0))

    if R < x < L - R:
        return R

    if L - R <= x <= L:
        return math.sqrt(max(R**2 - (x - (L - R)) ** 2, 0))

    return 0


def radius_flat_at_x(x, da, s, L):
    R = da / 2 - s

    if 0 <= x <= L:
        return R

    return 0


# -------------------------------------------------
# New internal helper
# Keeps public function names unchanged
# -------------------------------------------------

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
    radii[mask] = np.sqrt(
        np.maximum(r1**2 - (x_values[mask] - r1) ** 2, 0)
    )

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
    radii[mask] = np.sqrt(
        np.maximum(R**2 - (x_values[mask] - R) ** 2, 0)
    )

    mask = (x_values > R) & (x_values < L - R)
    radii[mask] = R

    mask = (x_values >= L - R) & (x_values <= L)
    radii[mask] = np.sqrt(
        np.maximum(R**2 - (x_values[mask] - (L - R)) ** 2, 0)
    )

    return radii


def calculate_vertical(da, s, head_type, r1, r2, h2, L):
    dx = 1.0

    x_values, radii = calculate_radius_profile(
        da, s, head_type, r1, r2, h2, L, dx
    )

    areas = math.pi * radii**2
    segment_volumes = 0.5 * (areas[:-1] + areas[1:]) * dx
    cumulative_volumes = np.cumsum(segment_volumes) * 1e-9

    result = []

    for i in range(0, len(cumulative_volumes), 10):
        level_cm = x_values[i] / 10
        volume_m3 = float(cumulative_volumes[i])
        result.append((level_cm, volume_m3))

    return result


def cross_section(z, xmin, xmax, dx, da, s, head_type, r1, r2, h2, L):
    x_values, radii = calculate_radius_profile(
        da, s, head_type, r1, r2, h2, L, dx
    )

    radii_squared = radii**2
    z_squared = z**2

    inside = radii_squared >= z_squared

    heights = np.zeros_like(radii)
    heights[inside] = 2 * np.sqrt(radii_squared[inside] - z_squared)

    area = np.trapz(heights, x_values)

    return float(area)


def calculate_horizontal(da, s, head_type, r1, r2, h2, L):
    dx = 1.0
    dz = 1.0

    volume_m3 = 0
    result = []

    x_min = 0
    x_max = L

    R = da / 2 - s
    z_min = int(-R)
    z_max = int(R)

    x_values, radii = calculate_radius_profile(
        da, s, head_type, r1, r2, h2, L, dx
    )

    radii_squared = radii**2

    for idx, z in enumerate(range(z_min, z_max + 1, int(dz))):
        z_squared = z**2

        inside = radii_squared >= z_squared

        heights = np.zeros_like(radii)
        heights[inside] = 2 * np.sqrt(radii_squared[inside] - z_squared)

        area = np.trapz(heights, x_values)

        volume_m3 += area * dz * 1e-9

        level = z + R

        if idx % 10 == 0:
            result.append((level / 10, float(volume_m3)))

    return result