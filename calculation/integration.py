import math

import numpy as np

from calculation.constants import DX_DEFAULT, DZ_DEFAULT, MM3_TO_M3
from calculation.radius_profiles import calculate_radius_profile


def trapezoid_integral(y, x):
    if hasattr(np, "trapezoid"):
        return np.trapezoid(y, x)

    return np.trapz(y, x)

def interpolate_result(levels_mm, volumes_m3, level_step_mm):
    max_level_mm = levels_mm[-1]

    target_levels_mm = np.arange(
        0.0,
        max_level_mm + level_step_mm,
        level_step_mm,
    )

    target_levels_mm = target_levels_mm[target_levels_mm <= max_level_mm]

    target_volumes_m3 = np.interp(
        target_levels_mm,
        levels_mm,
        volumes_m3,
    )

    return [
        (float(level_mm), float(volume_m3))
        for level_mm, volume_m3 in zip(target_levels_mm, target_volumes_m3)
    ]

def calculate_vertical(da, s, head_type, r1, r2, h2, L, level_step_mm=10.0):
    dx = DX_DEFAULT

    x_values, radii = calculate_radius_profile(
        da, s, head_type, r1, r2, h2, L, dx
    )

    areas = math.pi * radii**2
    segment_volumes = 0.5 * (areas[:-1] + areas[1:]) * dx
    cumulative_volumes = np.cumsum(segment_volumes) * MM3_TO_M3

    levels_mm = x_values[1:]
    volumes_m3 = cumulative_volumes

    return interpolate_result(levels_mm, volumes_m3, level_step_mm)


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


def calculate_horizontal(da, s, head_type, r1, r2, h2, L, level_step_mm=10.0):
    dx = DX_DEFAULT
    dz = DZ_DEFAULT

    R = da / 2 - s

    z_values = np.arange(-R, R + dz, dz)

    x_values, radii = calculate_radius_profile(
        da, s, head_type, r1, r2, h2, L, dx
    )

    radii_squared = radii**2

    levels_mm = []
    volumes_m3 = []

    volume_m3 = 0.0

    for z in z_values:
        z_squared = z**2

        inside = radii_squared >= z_squared

        heights = np.zeros_like(radii)
        heights[inside] = 2 * np.sqrt(radii_squared[inside] - z_squared)

        area = trapezoid_integral(heights, x_values)

        volume_m3 += area * dz * MM3_TO_M3

        level_mm = z + R

        levels_mm.append(level_mm)
        volumes_m3.append(volume_m3)

    levels_mm = np.array(levels_mm)
    volumes_m3 = np.array(volumes_m3)

    return interpolate_result(levels_mm, volumes_m3, level_step_mm)