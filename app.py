import pandas as pd
import streamlit as st

from calculation import calculate_filling_curve
from models import HEAD_TYPES, VESSEL_TYPES, TankInput
from drawing import draw_tank_preview

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


st.subheader("Vessel preview")

fig = draw_tank_preview(
    vessel_type=vessel_type,
    head_type=head_type,
    outer_diameter_mm=outer_diameter_mm,
    wall_thickness_mm=wall_thickness_mm,
    length_mm=length_mm,
)

st.pyplot(fig)


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

        df = pd.DataFrame(result, columns=["Level (cm)", "Volume (m³)"])

        st.subheader("Filling curve")
        st.line_chart(df.set_index("Level (cm)"))

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