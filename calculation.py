import math

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

    d = math.sqrt(dx**2 + dy**2)

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


def calculate_vertical(da, s, head_type, r1, r2, h2, L):
    volume_m3 = 0
    result = []

    for i in range(int(L) + 1):
        fx = radius_at_x(i, da, s, head_type, r1, r2, h2, L) ** 2
        fx1 = radius_at_x(i + 1, da, s, head_type, r1, r2, h2, L) ** 2

        volume_m3 += math.pi * 0.5 * (fx + fx1) * 1e-9

        if i % 10 == 0:
            result.append((i / 10, volume_m3))

    return result


def cross_section(z, xmin, xmax, dx, da, s, head_type, r1, r2, h2, L):
    area = 0
    steps = int((xmax - xmin) / dx) + 1

    for i in range(steps):
        x = xmin + i * dx
        radius = radius_at_x(x, da, s, head_type, r1, r2, h2, L)

        if z**2 <= radius**2:
            height = 2 * math.sqrt(radius**2 - z**2)
        else:
            height = 0

        area += height * dx

    return area


def calculate_horizontal(da, s, head_type, r1, r2, h2, L):
    dx = 1
    dz = 1
    volume_m3 = 0
    result = []

    x_min = 0
    x_max = L

    R = da / 2 - s
    z_min = int(-R)
    z_max = int(R)

    for idx, z in enumerate(range(z_min, z_max + 1, dz)):
        area = cross_section(
            z,
            x_min,
            x_max,
            dx,
            da,
            s,
            head_type,
            r1,
            r2,
            h2,
            L,
        )

        volume_m3 += area * dz * 1e-9

        level = z + R

        if idx % 10 == 0:
            result.append((level / 10, volume_m3))

    return result