import pandas as pd
import streamlit as st

from calculation import calculate_filling_curve
from drawing.tank_preview import draw_tank_preview
from drawing.head_preview import draw_head_dimensions_preview
from models import HEAD_TYPES, VESSEL_TYPES, TankInput, get_head_parameters
from validation import validate_filling_curve


st.set_page_config(
    page_title="Filling Curve Calculator",
    layout="wide",
)

st.markdown("""
<style>
.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
}

h1 {
    font-size: 2.3rem !important;
    line-height: 1.15 !important;
    margin-bottom: 0.3rem !important;
}

[data-testid="stCaptionContainer"] {
    margin-bottom: 1.2rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<h1>Filling Curve Calculator</h1>
""", unsafe_allow_html=True)

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
head_height_mm = head.h2_mm


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


# -------------------------------------------------
# Top preview section
# -------------------------------------------------

col_tank, col_head = st.columns(2)

with col_tank:
    st.subheader("Vessel preview")
    st.pyplot(fig_tank, width="content")

with col_head:
    st.subheader("Head preview")
    st.pyplot(fig_head, width="content")


# -------------------------------------------------
# Geometry data section
# -------------------------------------------------

st.subheader("Geometry data")

geometry_data = {
    "dₐ": f"{outer_diameter_mm:.1f} mm",
    "dᵢ": f"{inner_diameter_mm:.1f} mm",
    "s": f"{wall_thickness_mm:.1f} mm",
    "L": f"{length_mm:.1f} mm",
    "Inner length": f"{inner_length_mm:.1f} mm",
    "h": f"{head_height_mm:.1f} mm",
}

if head.r1_mm is not None:
    geometry_data["r₁"] = f"{head.r1_mm:.1f} mm"

if head.r2_mm is not None:
    geometry_data["r₂"] = f"{head.r2_mm:.1f} mm"

col_geometry, col_formula = st.columns([2.8, 0.75])

with col_geometry:
    type_col_1, type_col_2 = st.columns(2)

    with type_col_1:
        st.markdown(f"""
        **Vessel type**  
        {vessel_type}
        """)

    with type_col_2:
        st.markdown(f"""
        **Head type**  
        {head_type}
        """)

    st.dataframe(
        pd.DataFrame([geometry_data]),
        width="stretch",
        hide_index=True,
    )

with col_formula:
    if head_type == "Torospherical Head (DIN 28011)":
        st.info("""
        **DIN 28011**

        r₁ = dₐ  
        r₂ = 0.1 · dₐ  
        h = 0.1935 · dₐ − 0.455 · s
        """)

    elif head_type == "Torospherical Head (DIN 28013)":
        st.info("""
        **DIN 28013**

        r₁ = 0.8 · dₐ  
        r₂ = 0.154 · dₐ  
        h = 0.255 · dₐ − 0.635 · s
        """)

    elif head_type == "Elliptical Head 2:1":
        st.info("""
        **Elliptical Head 2:1**

        r₁ ≈ 0.9 · dᵢ  
        r₂ ≈ 0.17 · dᵢ  
        h = dᵢ / 4  

        """)

    elif head_type == "Hemispherical Head":
        st.info("""
        **Hemispherical Head**

        h = dᵢ / 2  

        Head shape is a hemisphere.
        """)

    elif head_type == "Flat Head":
        st.info("""
        **Flat Head**

        h = 0  

        Idealized flat end plate.
        """)


# -------------------------------------------------
# Calculation section
# -------------------------------------------------

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

        col_plot, col_table = st.columns([1.25, 1])

        with col_plot:
            st.line_chart(df.set_index("Level (cm)"))

            v1, v2, v3 = st.columns(3)
            v1.metric("Numerical", f"{validation['numerical_volume_m3']:.5f} m³")
            v2.metric("Reference", f"{validation['reference_volume_m3']:.5f} m³")
            v3.metric("Deviation", f"{validation['deviation_percent']:.4f} %")

        with col_table:
            st.dataframe(
                df,
                width="stretch",
                height=360,
            )

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