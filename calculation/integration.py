import math

import numpy as np

from calculation.constants import DX_DEFAULT, DZ_DEFAULT, MM3_TO_M3
from calculation.radius_profiles import calculate_radius_profile


def trapezoid_integral(y, x):
    if hasattr(np, "trapezoid"):
        return np.trapezoid(y, x)

    return np.trapz(y, x)


def calculate_vertical(da, s, head_type, r1, r2, h2, L):
    dx = DX_DEFAULT

    x_values, radii = calculate_radius_profile(
        da, s, head_type, r1, r2, h2, L, dx
    )

    areas = math.pi * radii**2
    segment_volumes = 0.5 * (areas[:-1] + areas[1:]) * dx
    cumulative_volumes = np.cumsum(segment_volumes) * MM3_TO_M3

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

    area = trapezoid_integral(heights, x_values)

    return float(area)


def calculate_horizontal(da, s, head_type, r1, r2, h2, L):
    dx = DX_DEFAULT
    dz = DZ_DEFAULT

    volume_m3 = 0.0
    result = []

    R = da / 2 - s

    z_values = np.arange(-R, R + dz, dz)

    x_values, radii = calculate_radius_profile(
        da, s, head_type, r1, r2, h2, L, dx
    )

    radii_squared = radii**2

    for idx, z in enumerate(z_values):
        z_squared = z**2

        inside = radii_squared >= z_squared

        heights = np.zeros_like(radii)
        heights[inside] = 2 * np.sqrt(radii_squared[inside] - z_squared)

        area = trapezoid_integral(heights, x_values)

        volume_m3 += area * dz * MM3_TO_M3

        level = z + R

        if idx % 10 == 0:
            result.append((level / 10, float(volume_m3)))

    return result