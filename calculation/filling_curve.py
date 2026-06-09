from models import TankInput, get_head_parameters

from calculation.integration import calculate_horizontal, calculate_vertical


def calculate_filling_curve(tank: TankInput, level_step_mm: float = 10.0) -> list[tuple[float, float]]:
    head = get_head_parameters(
        tank.head_type,
        tank.outer_diameter_mm,
        tank.wall_thickness_mm,
    )

    inner_length = tank.length_mm - 2 * tank.wall_thickness_mm

    if inner_length <= 0:
        raise ValueError("Inner length must be greater than zero.")

    if tank.outer_diameter_mm - 2 * tank.wall_thickness_mm <= 0:
        raise ValueError("Inner diameter must be greater than zero.")

    if tank.vessel_type == "Vertical Tank":
        return calculate_vertical(
            tank.outer_diameter_mm,
            tank.wall_thickness_mm,
            tank.head_type,
            head.r1_mm,
            head.r2_mm,
            head.h2_mm,
            inner_length,
            level_step_mm,
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
            level_step_mm,
        )

    raise ValueError(f"Unsupported vessel type: {tank.vessel_type}")