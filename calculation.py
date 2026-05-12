import math

from models import TankInput, get_head_parameters


def calculate_filling_curve(tank: TankInput) -> list[tuple[float, float]]:
    head = get_head_parameters(
        tank.head_type,
        tank.outer_diameter_mm,
        tank.wall_thickness_mm,
    )

    if tank.vessel_type == "Vertical Tank":
        return calculate_vertical(
            tank.outer_diameter_mm,
            tank.wall_thickness_mm,
            head.r1_mm,
            head.r2_mm,
            head.h2_mm,
            tank.length_mm,
        )

    if tank.vessel_type == "Horizontal Tank":
        return calculate_horizontal(
            tank.outer_diameter_mm,
            tank.wall_thickness_mm,
            head.r1_mm,
            head.r2_mm,
            head.h2_mm,
            tank.length_mm,
        )

    raise ValueError(f"Unsupported vessel type: {tank.vessel_type}")


def calculate_geometry_points(da, s, r1, r2, h2, L):

    # inner cylinder radius
    R = da / 2 - s

    # inner head depth
    h2_inner = h2 - s

    # -----------------------------------
    # circle center of crown radius r1
    # -----------------------------------
    c1x = r1
    c1y = 0.0

    # -----------------------------------
    # circle center of knuckle radius r2
    # -----------------------------------
    c2x = h2_inner
    c2y = R - r2

    # -----------------------------------
    # vector between circle centers
    # -----------------------------------
    dx = c2x - c1x
    dy = c2y - c1y

    d = math.sqrt(dx**2 + dy**2)

    # -----------------------------------
    # tangency point between r1 and r2
    # -----------------------------------
    x1 = c1x + r1 * dx / d

    # tangent point cylinder / knuckle
    x2 = h2_inner

    # mirrored right side
    x3 = L - h2_inner
    x4 = L - x1

    return x1, x2, x3, x4


def radius_at_x(x, da, s, r1, r2, h2, L):
    R = da / 2 - s
    h2_inner = h2 - s

    x1, x2, x3, x4 = calculate_geometry_points(da, s, r1, r2, h2, L)

    if 0 <= x < x1:
        # left crown radius r1
        return math.sqrt(max(r1**2 - (x - r1) ** 2, 0))

    elif x1 <= x < x2:
        # left knuckle radius r2
        c2x = h2_inner
        c2y = R - r2
        return c2y + math.sqrt(max(r2**2 - (x - c2x) ** 2, 0))

    elif x2 <= x < x3:
        # cylindrical shell
        return R

    elif x3 <= x < x4:
        # right knuckle radius r2
        c2x = L - h2_inner
        c2y = R - r2
        return c2y + math.sqrt(max(r2**2 - (x - c2x) ** 2, 0))

    elif x4 <= x <= L:
        # right crown radius r1
        return math.sqrt(max(r1**2 - (x - (L - r1)) ** 2, 0))

    return 0


def calculate_vertical(da, s, r1, r2, h2, L):
    volume_m3 = 0
    result = []

    for i in range(int(L - 2 * s) + 1):
        fx = radius_at_x(i, da, s, r1, r2, h2, L) ** 2
        fx1 = radius_at_x(i + 1, da, s, r1, r2, h2, L) ** 2

        volume_m3 += math.pi * 0.5 * (fx + fx1) * 1e-9

        if i % 10 == 0:
            result.append((i / 10, volume_m3))

    return result


def cross_section(z, xmin, xmax, dx, da, s, r1, r2, h2, L):
    area = 0
    steps = int((xmax - xmin) / dx) + 1

    for i in range(steps):
        x = xmin + i * dx
        radius = radius_at_x(x, da, s, r1, r2, h2, L)

        if z**2 <= radius**2:
            height = 2 * math.sqrt(radius**2 - z**2)
        else:
            height = 0

        area += height * dx

    return area


def calculate_horizontal(da, s, r1, r2, h2, L):
    dx = 1
    dz = 1
    volume_m3 = 0
    result = []

    x_min = 0
    x_max = L - 2 * s

    z_min = int(-1 * (da / 2 - s))
    z_max = int(da / 2 - s)

    for idx, z in enumerate(range(z_min, z_max + 1, dz)):
        area = cross_section(z, x_min, x_max, dx, da, s, r1, r2, h2, L)
        volume_m3 += area * dz * 1e-9

        level = z + (da / 2 - s)

        if idx % 10 == 0:
            result.append((level / 10, volume_m3))

    return result