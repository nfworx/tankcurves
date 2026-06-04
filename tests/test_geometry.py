import pytest

from calculation.geometry import calculate_geometry_points


@pytest.mark.parametrize(
    "da, s, r1, r2, h2, L",
    [
        (2000.0, 5.0, 2000.0, 200.0, 384.725, 5000.0),  # DIN 28011
        (2000.0, 5.0, 1600.0, 308.0, 506.825, 5000.0),  # DIN 28013
    ],
)
def test_geometry_points_are_ordered(da, s, r1, r2, h2, L):
    x1, x2, x3, x4 = calculate_geometry_points(da, s, r1, r2, h2, L)

    assert 0 <= x1 <= x2 <= x3 <= x4 <= L


@pytest.mark.parametrize(
    "da, s, r1, r2, h2, L",
    [
        (2000.0, 5.0, 2000.0, 200.0, 384.725, 5000.0),
        (2000.0, 5.0, 1600.0, 308.0, 506.825, 5000.0),
    ],
)
def test_geometry_points_lie_inside_head_regions(da, s, r1, r2, h2, L):
    x1, x2, x3, x4 = calculate_geometry_points(da, s, r1, r2, h2, L)

    assert 0 <= x1 <= h2
    assert 0 <= x2 <= h2
    assert L - h2 <= x3 <= L
    assert L - h2 <= x4 <= L


@pytest.mark.parametrize(
    "da, s, r1, r2, h2, L",
    [
        (2000.0, 5.0, 2000.0, 200.0, 384.725, 5000.0),
        (2000.0, 5.0, 1600.0, 308.0, 506.825, 5000.0),
    ],
)

def test_geometry_points_are_symmetric(da, s, r1, r2, h2, L):
    x1, x2, x3, x4 = calculate_geometry_points(da, s, r1, r2, h2, L)

    assert x3 == pytest.approx(L - x2)
    assert x4 == pytest.approx(L - x1)