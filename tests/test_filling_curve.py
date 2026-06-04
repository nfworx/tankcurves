import pytest

from calculation import calculate_filling_curve
from models import TankInput
from calculation.reference_volumes import calculate_inner_volume_m3
from models import get_head_parameters


def make_tank(head_type="Flat Head", vessel_type="Horizontal Tank"):
    return TankInput(
        vessel_type=vessel_type,
        head_type=head_type,
        outer_diameter_mm=2000.0,
        wall_thickness_mm=5.0,
        length_mm=5000.0,
    )


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
def test_filling_curve_starts_at_zero_volume(head_type):
    tank = make_tank(head_type=head_type)

    curve = calculate_filling_curve(tank)

    assert curve[0][1] == pytest.approx(0.0, abs=1e-12)


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
def test_filling_curve_contains_no_negative_volumes(head_type):
    tank = make_tank(head_type=head_type)

    curve = calculate_filling_curve(tank)
    volumes = [volume for _, volume in curve]

    assert all(volume >= 0 for volume in volumes)


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

def test_filling_curve_is_monotonic(head_type):
    tank = make_tank(head_type=head_type)

    curve = calculate_filling_curve(tank)
    volumes = [volume for _, volume in curve]

    assert all(
        current <= next_value
        for current, next_value in zip(volumes, volumes[1:])
    )


def test_flat_head_full_volume_matches_reference_volume():
    tank = make_tank(head_type="Flat Head")
    head = get_head_parameters(
        tank.head_type,
        tank.outer_diameter_mm,
        tank.wall_thickness_mm,
    )

    curve = calculate_filling_curve(tank)
    full_volume = curve[-1][1]

    reference_volume = calculate_inner_volume_m3(
        da=tank.outer_diameter_mm,
        s=tank.wall_thickness_mm,
        head_type=tank.head_type,
        r1=head.r1_mm,
        r2=head.r2_mm,
        h2=head.h2_mm,
        L=tank.length_mm,
    )

    assert full_volume == pytest.approx(reference_volume, rel=1e-3)

@pytest.mark.parametrize(
    "height_fraction, expected_volume_fraction",
    [
        (0.25, 0.25),
        (0.50, 0.50),
        (0.75, 0.75),
    ],
)

def test_vertical_flat_head_volume_fraction_equals_height_fraction(
    height_fraction,
    expected_volume_fraction,
):
    tank = TankInput(
        vessel_type="Vertical Tank",
        head_type="Flat Head",
        outer_diameter_mm=2000.0,
        wall_thickness_mm=5.0,
        length_mm=5000.0,
    )

    curve = calculate_filling_curve(tank)

    max_level = curve[-1][0]
    target_level = max_level * height_fraction

    closest_point = min(
        curve,
        key=lambda point: abs(point[0] - target_level),
    )

    volume_at_target_height = closest_point[1]
    total_volume = curve[-1][1]

    assert volume_at_target_height / total_volume == pytest.approx(
        expected_volume_fraction,
        rel=0.01,
    )