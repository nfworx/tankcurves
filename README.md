# Filling Curve Calculator

Numerical filling curve calculator for rotationally symmetric vessels.

The application calculates filling curves for vertical and horizontal tanks with different head geometries using numerical integration methods.

Built with **Python**, **NumPy** and **Streamlit**.

---

## Features

### Vessel Types

- Vertical tanks
- Horizontal tanks

### Supported Head Geometries

- Flat Head
- Hemispherical Head
- Elliptical Head 2:1
- Torospherical Head (DIN 28011)
- Torospherical Head (DIN 28013)

### Functionality

- Numerical filling curve calculation
- Interactive geometry preview
- CSV export
- Validation against analytical reference solutions
- Optimized NumPy-based solver
- Fast vectorized integration

---

## Demo

🌐 Streamlit App:

https://tankcurves.streamlit.app/

---

# Project Structure

```text
filling_curve/
│
├── app.py
├── models.py
├── validation.py
├── requirements.txt
│
├── calculation/
│   ├── __init__.py
│   ├── constants.py
│   ├── filling_curve.py
│   ├── geometry.py
│   ├── profiles.py
│   └── integration.py
│
├── drawing/
│   ├── __init__.py
│   ├── head_preview.py
│   ├── tank_preview.py
│   └── utilities.py
│
└── README.md
```

---

# Numerical Method

The filling curve is generated using numerical integration of rotational cross sections.

## Vertical Tanks

The volume is calculated by integrating circular cross-sectional areas along the vessel axis:

```math
V = \int \pi r(x)^2 \, dx
```

## Horizontal Tanks

The liquid cross section is discretized and integrated numerically over the vessel length and filling height.

The solver uses NumPy vectorization for significantly improved performance compared to pure Python loops.

---

# Supported Head Geometries

## Flat Head

Idealized flat end plate.

## Hemispherical Head

True hemispherical geometry.

## Elliptical Head 2:1

Standard 2:1 elliptical head approximation.

## Torospherical Heads

Implemented according to:

- DIN 28011
- DIN 28013

---

# Performance

The calculation engine was optimized using:

- NumPy vectorization
- Precomputed radius profiles
- Reduced redundant geometry evaluations
- Optimized numerical integration

This significantly improves performance for large tanks and small integration step sizes.

---

# Dependencies

Main dependencies:

- Python 3.12+
- NumPy
- Pandas
- Streamlit
- Matplotlib

---

# Future Improvements

Possible future extensions:

- Plotly-based interactive charts
- Adaptive integration step size
- Tilted vessels
- Nozzle offsets
- Additional DIN/ASME head geometries
- Excel export
- Interactive filling animation
- GPU/Numba acceleration

---

# License

MIT License

---

# Author

Developed by **nfworx**