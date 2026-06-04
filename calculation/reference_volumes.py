import math

from calculation import calculate_filling_curve
from models import TankInput, get_head_parameters


def calculate_inner_volume_m3(
    da,
    s,
    head_type,
    r1,
    r2,
    h2,
    L,
):
    R = da / 2 - s
    inner_length = L - 2 * s

    if head_type == "Flat Head":
        return math.pi * R**2 * inner_length * 1e-9

    if head_type == "Hemispherical Head":
        cylinder_length = max(inner_length - 2 * R, 0)
        cylinder_volume = math.pi * R**2 * cylinder_length
        heads_volume = 4 / 3 * math.pi * R**3

        return (cylinder_volume + heads_volume) * 1e-9

    if head_type == "Elliptical Head 2:1":
        cylinder_length = max(inner_length - 2 * h2, 0)
        cylinder_volume = math.pi * R**2 * cylinder_length
        heads_volume = 4 / 3 * math.pi * R**2 * h2

        return (cylinder_volume + heads_volume) * 1e-9

    if head_type == "Torospherical Head (DIN 28011)":
        cylinder_length = max(inner_length - 2 * h2, 0)
        cylinder_volume = math.pi * R**2 * cylinder_length
        head_volume = 0.10 * (da - 2 * s) ** 3

        return (cylinder_volume + 2 * head_volume) * 1e-9

    if head_type == "Torospherical Head (DIN 28013)":
        cylinder_length = max(inner_length - 2 * h2, 0)
        cylinder_volume = math.pi * R**2 * cylinder_length
        head_volume = 0.1298 * (da - 2 * s) ** 3

        return (cylinder_volume + 2 * head_volume) * 1e-9

    raise ValueError(f"Unsupported head type: {head_type}")


def validate_filling_curve(tank: TankInput):
    head = get_head_parameters(
        tank.head_type,
        tank.outer_diameter_mm,
        tank.wall_thickness_mm,
    )

    filling_curve = calculate_filling_curve(tank)
    numerical_volume = filling_curve[-1][1]

    reference_volume = calculate_inner_volume_m3(
        da=tank.outer_diameter_mm,
        s=tank.wall_thickness_mm,
        head_type=tank.head_type,
        r1=head.r1_mm,
        r2=head.r2_mm,
        h2=head.h2_mm,
        L=tank.length_mm,
    )

    deviation_m3 = numerical_volume - reference_volume
    deviation_percent = deviation_m3 / reference_volume * 100 if reference_volume > 0 else 0

    return {
        "numerical_volume_m3": numerical_volume,
        "reference_volume_m3": reference_volume,
        "deviation_m3": deviation_m3,
        "deviation_percent": deviation_percent,
    }