#app.py
import pandas as pd
import streamlit as st

from calculation import calculate_filling_curve
from drawing import draw_tank_preview, draw_head_dimensions_preview
from models import HEAD_TYPES, VESSEL_TYPES, TankInput, get_head_parameters
from validation import validate_filling_curve


st.set_page_config(
    page_title="Filling Curve Calculator",
    layout="wide",
)

st.title("Filling Curve Calculator")
st.caption("Numerical filling curve calculator for rotationally symmetric vessels")


with st.sidebar:
    st.header("Input parameters")

    vessel_type = st.selectbox("Vessel type", VESSEL_TYPES)
    head_type = st.selectbox("Head type", HEAD_TYPES)

    outer_diameter_mm = st.number_input(
        "Outer diameter (mm)",
        min_value=1.0,
        value=2000.0,
        step=100.0,
    )

    wall_thickness_mm = st.number_input(
        "Wall thickness (mm)",
        min_value=0.0,
        value=5.0,
        step=1.0,
    )

    length_mm = st.number_input(
        "Length (mm)",
        min_value=1.0,
        value=5000.0,
        step=100.0,
    )

    calculate_button = st.button("Calculate", type="primary")


head = get_head_parameters(
    head_type,
    outer_diameter_mm,
    wall_thickness_mm,
)

inner_diameter_mm = outer_diameter_mm - 2 * wall_thickness_mm
inner_length_mm = length_mm - 2 * wall_thickness_mm

h1_mm = 3.5 * wall_thickness_mm
h2_mm = head.h2_mm
h3_mm = h1_mm + h2_mm

fig_tank = draw_tank_preview(
    vessel_type=vessel_type,
    head_type=head_type,
    outer_diameter_mm=outer_diameter_mm,
    wall_thickness_mm=wall_thickness_mm,
    length_mm=length_mm,
)

fig_head = draw_head_dimensions_preview(
    head_type=head_type,
    outer_diameter_mm=outer_diameter_mm,
    wall_thickness_mm=wall_thickness_mm,
)


col_preview, col_geometry = st.columns([1.35, 1])

with col_preview:
    st.subheader("Vessel preview")
    st.pyplot(fig_tank, use_container_width=False)

with col_geometry:
    st.subheader("Geometry")

    g1, g2 = st.columns(2)

    with g1:
        st.markdown(f"""
        **Vessel type**  
        {vessel_type}

        **Outer diameter dₐ**  
        {outer_diameter_mm:.1f} mm

        **Wall thickness s**  
        {wall_thickness_mm:.1f} mm

        **Head depth h₂**  
        {h2_mm:.1f} mm
        """)

    with g2:
        st.markdown(f"""
        **Head type**  
        {head_type}

        **Inner diameter dᵢ**  
        {inner_diameter_mm:.1f} mm

        **Outer length L**  
        {length_mm:.1f} mm

        **Inner length**  
        {inner_length_mm:.1f} mm
        """)

        if head.r1_mm is not None and head.r2_mm is not None:
            st.markdown(f"""
            **r₁ / r₂**  
            {head.r1_mm:.1f} / {head.r2_mm:.1f} mm
            """)


st.subheader(f"Head dimensions – {head_type}")

col_head, col_formula = st.columns([1.35, 1])

with col_head:
    st.pyplot(fig_head, use_container_width=False)

    dimension_data = {
        "dₐ": f"{outer_diameter_mm:.1f} mm",
        "dᵢ": f"{inner_diameter_mm:.1f} mm",
        "h₁": f"{h1_mm:.1f} mm",
        "h₂": f"{h2_mm:.1f} mm",
        "h₃": f"{h3_mm:.1f} mm",
        "s": f"{wall_thickness_mm:.1f} mm",
    }

    if head.r1_mm is not None:
        dimension_data["r₁"] = f"{head.r1_mm:.1f} mm"

    if head.r2_mm is not None:
        dimension_data["r₂"] = f"{head.r2_mm:.1f} mm"

    st.dataframe(
        pd.DataFrame([dimension_data]),
        use_container_width=True,
        hide_index=True,
    )

with col_formula:
    if head_type == "Torospherical Head (DIN 28011)":
        st.info("""
        **DIN 28011**

        r₁ = dₐ  
        r₂ = 0.1 · dₐ  
        h₁ = 3.5 · s  
        h₂ = 0.1935 · dₐ − 0.455 · s  
        h₃ = h₁ + h₂  

        All dimensions shown are inner dimensions.
        """)

    elif head_type == "Torospherical Head (DIN 28013)":
        st.info("""
        **DIN 28013**

        r₁ = 0.8 · dₐ  
        r₂ = 0.154 · dₐ  
        h₁ = 3.5 · s  
        h₂ = 0.255 · dₐ − 0.635 · s  
        h₃ = h₁ + h₂  

        All dimensions shown are inner dimensions.
        """)

    elif head_type == "Elliptical Head 2:1":
        st.info("""
        **Elliptical Head 2:1**

        h₂ = dᵢ / 4  
        h₃ = h₁ + h₂  

        Approximation as half ellipsoid.
        """)

    elif head_type == "Hemispherical Head":
        st.info("""
        **Hemispherical Head**

        h₂ = dᵢ / 2  
        h₃ = h₁ + h₂  

        Head shape is a hemisphere.
        """)

    elif head_type == "Flat Head":
        st.info("""
        **Flat Head**

        h₂ = 0  
        h₃ = h₁  

        Idealized flat end plate.
        """)


if calculate_button:
    tank = TankInput(
        vessel_type=vessel_type,
        head_type=head_type,
        outer_diameter_mm=outer_diameter_mm,
        wall_thickness_mm=wall_thickness_mm,
        length_mm=length_mm,
    )

    try:
        with st.spinner("Calculating filling curve..."):
            result = calculate_filling_curve(tank)
            validation = validate_filling_curve(tank)

        df = pd.DataFrame(result, columns=["Level (cm)", "Volume (m³)"])

        st.subheader("Filling curve")
        st.line_chart(df.set_index("Level (cm)"))

        st.subheader("Volume validation")

        col1, col2, col3 = st.columns(3)

        col1.metric("Numerical volume", f"{validation['numerical_volume_m3']:.5f} m³")
        col2.metric("Reference volume", f"{validation['reference_volume_m3']:.5f} m³")
        col3.metric("Deviation", f"{validation['deviation_percent']:.4f} %")

        st.subheader("Result table")
        st.dataframe(df, use_container_width=True)

        csv_data = df.to_csv(index=False, sep=";").encode("utf-8")

        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name="filling_curve.csv",
            mime="text/csv",
        )

    except Exception as error:
        st.error(f"Calculation failed: {error}")

else:
    st.info("Enter vessel parameters in the sidebar and click Calculate.")