#models.py

from dataclasses import dataclass


VESSEL_TYPES = ["Vertical Tank", "Horizontal Tank"]

HEAD_TYPES = [
    "Torospherical Head (DIN 28011)",
    "Torospherical Head (DIN 28013)",
]


@dataclass
class TankInput:
    vessel_type: str
    head_type: str
    outer_diameter_mm: float
    wall_thickness_mm: float
    length_mm: float


@dataclass
class HeadParameters:
    r1_mm: float
    r2_mm: float
    h2_mm: float


def get_head_parameters(head_type: str, da: float, s: float) -> HeadParameters:
    if head_type == "Torospherical Head (DIN 28011)":
        return HeadParameters(
            r1_mm=1.0 * da,
            r2_mm=0.1 * da,
            h2_mm=0.1935 * da + 0.455 * s,
        )

    if head_type == "Torospherical Head (DIN 28013)":
        return HeadParameters(
            r1_mm=0.8 * da,
            r2_mm=0.154 * da,
            h2_mm=0.255 * da + 0.635 * s,
        )

    raise ValueError(f"Unsupported head type: {head_type}")