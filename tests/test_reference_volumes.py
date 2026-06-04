import math

import pytest

from calculation.reference_volumes import calculate_inner_volume_m3


def test_flat_head_volume_equals_cylinder_formula():
    da = 2000.0
    s = 5.0
    L = 5000.0

    R = da / 2 - s
    inner_length = L - 2 * s

    expected = math.pi * R**2 * inner_length * 1e-9

    actual = calculate_inner_volume_m3(
        da=da,
        s=s,
        head_type="Flat Head",
        r1=None,
        r2=None,
        h2=0.0,
        L=L,
    )

    assert actual == pytest.approx(expected, rel=1e-12)


def test_hemispherical_head_volume_equals_analytical_solution():
    da = 2000.0
    s = 5.0
    L = 5000.0

    R = da / 2 - s
    inner_length = L - 2 * s
    cylinder_length = inner_length - 2 * R

    expected = (
        math.pi * R**2 * cylinder_length
        + (4 / 3) * math.pi * R**3
    ) * 1e-9

    actual = calculate_inner_volume_m3(
        da=da,
        s=s,
        head_type="Hemispherical Head",
        r1=None,
        r2=None,
        h2=R,
        L=L,
    )

    assert actual == pytest.approx(expected, rel=1e-12)


def test_elliptical_head_volume_equals_analytical_solution():
    da = 2000.0
    s = 5.0
    L = 5000.0

    R = da / 2 - s
    h = (da - 2 * s) / 4

    inner_length = L - 2 * s
    cylinder_length = inner_length - 2 * h

    expected = (
        math.pi * R**2 * cylinder_length
        + (4 / 3) * math.pi * R**2 * h
    ) * 1e-9

    actual = calculate_inner_volume_m3(
        da=da,
        s=s,
        head_type="Elliptical Head 2:1",
        r1=None,
        r2=None,
        h2=h,
        L=L,
    )

    assert actual == pytest.approx(expected, rel=1e-12)


def test_din28011_volume_equals_engineering_reference_formula():
    da = 2000.0
    s = 5.0
    L = 5000.0

    R = da / 2 - s
    h = 0.1935 * da - 0.455 * s

    inner_length = L - 2 * s
    cylinder_length = inner_length - 2 * h

    expected = (
        math.pi * R**2 * cylinder_length
        + 2 * 0.10 * (da - 2 * s) ** 3
    ) * 1e-9

    actual = calculate_inner_volume_m3(
        da=da,
        s=s,
        head_type="Torospherical Head (DIN 28011)",
        r1=da,
        r2=0.1 * da,
        h2=h,
        L=L,
    )

    assert actual == pytest.approx(expected, rel=1e-12)


def test_din28013_volume_equals_engineering_reference_formula():
    da = 2000.0
    s = 5.0
    L = 5000.0

    R = da / 2 - s
    h = 0.255 * da - 0.635 * s

    inner_length = L - 2 * s
    cylinder_length = inner_length - 2 * h

    expected = (
        math.pi * R**2 * cylinder_length
        + 2 * 0.1298 * (da - 2 * s) ** 3
    ) * 1e-9

    actual = calculate_inner_volume_m3(
        da=da,
        s=s,
        head_type="Torospherical Head (DIN 28013)",
        r1=0.8 * da,
        r2=0.154 * da,
        h2=h,
        L=L,
    )

    assert actual == pytest.approx(expected, rel=1e-12)