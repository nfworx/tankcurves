import numpy as np
import pytest

from calculation.radius_profiles import calculate_radius_profile


@pytest.mark.parametrize(
    "head_type",
    [
        "Flat Head",
        "Hemispherical Head",
        "Elliptical Head 2:1",
        "Torospherical Head (DIN 28011)",
        "Torospherical Head (DIN 28013)",
    ],
)
def test_radius_profile_contains_no_negative_values(head_type):
    da = 2000.0
    s = 5.0
    L = 5000.0
    R = da / 2 - s

    if head_type == "Torospherical Head (DIN 28011)":
        r1 = da
        r2 = 0.1 * da
        h2 = 0.1935 * da - 0.455 * s
    elif head_type == "Torospherical Head (DIN 28013)":
        r1 = 0.8 * da
        r2 = 0.154 * da
        h2 = 0.255 * da - 0.635 * s
    elif head_type == "Elliptical Head 2:1":
        r1 = None
        r2 = None
        h2 = (da - 2 * s) / 4
    elif head_type == "Hemispherical Head":
        r1 = None
        r2 = None
        h2 = R
    else:
        r1 = None
        r2 = None
        h2 = 0.0

    _, radii = calculate_radius_profile(
        da=da,
        s=s,
        head_type=head_type,
        r1=r1,
        r2=r2,
        h2=h2,
        L=L,
    )

    assert np.all(radii >= 0)


@pytest.mark.parametrize(
    "head_type",
    [
        "Flat Head",
        "Hemispherical Head",
        "Elliptical Head 2:1",
        "Torospherical Head (DIN 28011)",
        "Torospherical Head (DIN 28013)",
    ],
)
def test_radius_profile_never_exceeds_inner_radius(head_type):
    da = 2000.0
    s = 5.0
    L = 5000.0
    R = da / 2 - s

    if head_type == "Torospherical Head (DIN 28011)":
        r1 = da
        r2 = 0.1 * da
        h2 = 0.1935 * da - 0.455 * s
    elif head_type == "Torospherical Head (DIN 28013)":
        r1 = 0.8 * da
        r2 = 0.154 * da
        h2 = 0.255 * da - 0.635 * s
    elif head_type == "Elliptical Head 2:1":
        r1 = None
        r2 = None
        h2 = (da - 2 * s) / 4
    elif head_type == "Hemispherical Head":
        r1 = None
        r2 = None
        h2 = R
    else:
        r1 = None
        r2 = None
        h2 = 0.0

    _, radii = calculate_radius_profile(
        da=da,
        s=s,
        head_type=head_type,
        r1=r1,
        r2=r2,
        h2=h2,
        L=L,
    )

    assert np.all(radii <= R)


def test_flat_head_radius_profile_is_constant():
    da = 2000.0
    s = 5.0
    L = 5000.0
    R = da / 2 - s

    _, radii = calculate_radius_profile(
        da=da,
        s=s,
        head_type="Flat Head",
        r1=None,
        r2=None,
        h2=0.0,
        L=L,
    )

    assert np.all(radii == pytest.approx(R))