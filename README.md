# TankCurves

Engineering tool for generating filling curves of horizontal and vertical storage tanks with different vessel head geometries.

TankCurves calculates the relationship between liquid level and contained volume and provides graphical visualization, tabular results, and export capabilities.

![TankCurves Screenshot](docs/images/tankcurves-demo.png)

---

## Features

* Horizontal and vertical vessels
* Multiple head geometries

  * Flat heads
  * Torispherical heads (DIN 28011)
  * Additional geometries can be added easily
* Numerical filling curve calculation
* Interactive Streamlit web application
* Vessel geometry preview
* Head geometry visualization
* Filling curve plotting
* CSV export of level-volume tables
* Validation against reference vessel volumes

---

## Example

For a horizontal vessel with:

| Parameter      | Value                          |
| -------------- | ------------------------------ |
| Outer Diameter | 2000 mm                        |
| Wall Thickness | 5 mm                           |
| Length         | 5000 mm                        |
| Head Type      | Torispherical Head (DIN 28011) |

TankCurves calculates:

* Total vessel volume
* Filling curve
* Level-volume lookup table
* Numerical deviation from reference volume

---

## Installation

Clone the repository:

```bash
git clone https://github.com/nfworx/tankcurves.git
cd tankcurves
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Run the Streamlit App

```bash
streamlit run app.py
```

The application will open in your browser.

---

## Project Structure

```text
tankcurves/
│
├── calculation/        # Filling curve calculations
├── drawing/            # Geometry visualizations
├── models.py           # Data models
├── validation.py       # Reference volume validation
├── app.py              # Streamlit application
└── requirements.txt
```

---

## Calculation Workflow

1. Define vessel geometry
2. Generate internal dimensions
3. Calculate cross-sectional liquid area
4. Integrate vessel volume along the vessel length
5. Generate level-volume table
6. Plot filling curve
7. Validate against reference volume

---

## Validation

Calculated vessel volumes are compared against reference values.

The resulting deviation is displayed to verify numerical accuracy.

Example:

| Numerical   | Reference   | Deviation |
| ----------- | ----------- | --------- |
| 14.68548 m³ | 14.70311 m³ | -0.1199 % |

---

## Future Improvements

* Excel export
* PDF reports
* Plotly visualizations
* Additional head geometries
* Unit conversion support
* Automated test suite
* Python package distribution

---

## License

MIT License
