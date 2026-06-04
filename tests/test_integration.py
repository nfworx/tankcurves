import math

import pytest

from calculation.integration import (
    calculate_horizontal,
    calculate_vertical,
    cross_section,
    trapezoid_integral,
)


def test_trapezoid_integral_matches_triangle_area():
    x = [0.0, 1.0, 2.0]
    y = [0.0, 1.0, 0.0]

    area = trapezoid_integral(y, x)

    assert area == pytest.approx(1.0)


def test_cross_section_at_center_equals_rectangle_area_for_flat_head():
    da = 2000.0
    s = 5.0
    L = 5000.0
    R = da / 2 - s

    area = cross_section(
        z=0.0,
        xmin=0.0,
        xmax=L,
        dx=1.0,
        da=da,
        s=s,
        head_type="Flat Head",
        r1=None,
        r2=None,
        h2=0.0,
        L=L,
    )

    expected = 2 * R * L

    assert area == pytest.approx(expected)


def test_cross_section_at_outer_radius_is_zero_for_flat_head():
    da = 2000.0
    s = 5.0
    L = 5000.0
    R = da / 2 - s

    area = cross_section(
        z=R,
        xmin=0.0,
        xmax=L,
        dx=1.0,
        da=da,
        s=s,
        head_type="Flat Head",
        r1=None,
        r2=None,
        h2=0.0,
        L=L,
    )

    assert area == pytest.approx(0.0)


def test_cross_section_is_symmetric_around_centerline_for_flat_head():
    da = 2000.0
    s = 5.0
    L = 5000.0

    area_positive = cross_section(
        z=500.0,
        xmin=0.0,
        xmax=L,
        dx=1.0,
        da=da,
        s=s,
        head_type="Flat Head",
        r1=None,
        r2=None,
        h2=0.0,
        L=L,
    )

    area_negative = cross_section(
        z=-500.0,
        xmin=0.0,
        xmax=L,
        dx=1.0,
        da=da,
        s=s,
        head_type="Flat Head",
        r1=None,
        r2=None,
        h2=0.0,
        L=L,
    )

    assert area_positive == pytest.approx(area_negative)


def test_calculate_horizontal_flat_head_full_volume_matches_cylinder_volume():
    da = 2000.0
    s = 5.0
    L = 5000.0
    R = da / 2 - s
    inner_length = L

    curve = calculate_horizontal(
        da=da,
        s=s,
        head_type="Flat Head",
        r1=None,
        r2=None,
        h2=0.0,
        L=L,
    )

    full_volume = curve[-1][1]
    expected = math.pi * R**2 * inner_length * 1e-9

    assert full_volume == pytest.approx(expected, rel=1e-3)


def test_calculate_horizontal_flat_head_half_height_is_half_volume():
    da = 2000.0
    s = 5.0
    L = 5000.0

    curve = calculate_horizontal(
        da=da,
        s=s,
        head_type="Flat Head",
        r1=None,
        r2=None,
        h2=0.0,
        L=L,
    )

    total_volume = curve[-1][1]
    max_level = curve[-1][0]
    target_level = max_level / 2

    closest_point = min(curve, key=lambda point: abs(point[0] - target_level))
    volume_at_half_height = closest_point[1]

    assert volume_at_half_height / total_volume == pytest.approx(0.5, rel=0.01)


def test_calculate_vertical_flat_head_full_volume_matches_cylinder_volume():
    da = 2000.0
    s = 5.0
    L = 5000.0
    R = da / 2 - s

    curve = calculate_vertical(
        da=da,
        s=s,
        head_type="Flat Head",
        r1=None,
        r2=None,
        h2=0.0,
        L=L,
    )

    full_volume = curve[-1][1]
    expected = math.pi * R**2 * L * 1e-9

    assert full_volume == pytest.approx(expected, rel=3e-3)

def test_calculate_vertical_hemispherical_tank_as_sphere_matches_sphere_volume():
    da = 2000.0
    s = 5.0
    R = da / 2 - s
    L = 2 * R

    curve = calculate_vertical(
        da=da,
        s=s,
        head_type="Hemispherical Head",
        r1=None,
        r2=None,
        h2=R,
        L=L,
    )

    full_volume = curve[-1][1]
    expected = (4 / 3) * math.pi * R**3 * 1e-9

    assert full_volume == pytest.approx(expected, rel=3e-3)

def test_calculate_horizontal_hemispherical_tank_as_sphere_matches_sphere_volume():
    da = 2000.0
    s = 5.0
    R = da / 2 - s
    L = 2 * R

    curve = calculate_horizontal(
        da=da,
        s=s,
        head_type="Hemispherical Head",
        r1=None,
        r2=None,
        h2=R,
        L=L,
    )

    full_volume = curve[-1][1]
    expected = (4 / 3) * math.pi * R**3 * 1e-9

    assert full_volume == pytest.approx(expected, rel=3e-3)