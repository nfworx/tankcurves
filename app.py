import pandas as pd
import streamlit as st

from calculation import calculate_filling_curve
from drawing.tank_preview import draw_tank_preview
from drawing.head_preview import draw_head_dimensions_preview
from models import HEAD_TYPES, VESSEL_TYPES, TankInput, get_head_parameters
from validation import validate_filling_curve

ANALYTICAL_REFERENCE_HEADS = {
    "Flat Head",
    "Hemispherical Head",
    "Elliptical Head 2:1",
}

st.set_page_config(
    page_title="Tank-Curves",
    layout="wide",
)

st.markdown("""
<style>
.block-container {
    padding-top: 0.8rem;
    padding-bottom: 0.8rem;
    max-width: 1550px;
}

.main-title {
    font-size: 0.8rem;
    line-height: 1.0;
    margin-bottom: 0.25rem;
}
            
.section-title {
    font-size: 1.45rem;
    font-weight: 700;
    line-height: 1.1;
    margin-top: 0.2rem;
    margin-bottom: 0.55rem;
}

h2, h3 {
    margin-top: 0.25rem !important;
    margin-bottom: 0.45rem !important;
}

/* Sidebar top spacing */
section[data-testid="stSidebar"] > div {
    padding-top: 0rem;
}

/* Sidebar compact layout */
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    gap: 0.45rem;
}

/* Sidebar headers */
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    margin-top: 0rem !important;
    margin-bottom: 0.35rem !important;
}

/* Input labels tighter */
section[data-testid="stSidebar"] label {
    margin-bottom: 0rem !important;
}

/* Compact metrics */
section[data-testid="stSidebar"] [data-testid="stMetric"] {
    padding: 0.25rem 0.45rem;
    border-radius: 0.45rem;
}

section[data-testid="stSidebar"] [data-testid="stMetricValue"] {
    font-size: 1.25rem;
}

section[data-testid="stSidebar"] [data-testid="stMetricLabel"] {
    font-size: 0.75rem;
}

.formula-card {
    background-color: #173653;
    border-radius: 0.5rem;
    padding: 1.15rem 1.25rem;
    min-height: 205px;
    color: #2aa8ff;
    font-size: 0.95rem;
    line-height: 1.65;
}

.formula-card strong {
    color: #2aa8ff;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""<h1 class="main-title">TankCurves</h1>""", unsafe_allow_html=True)


horizontal_index = VESSEL_TYPES.index("Horizontal Tank") if "Horizontal Tank" in VESSEL_TYPES else 0

with st.sidebar:
    st.header("Input parameters")

    vessel_type = st.selectbox(
        "Vessel type",
        VESSEL_TYPES,
        index=horizontal_index,
    )

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

    calculate_button = st.button(
        "Calculate",
        type="primary",
        use_container_width=True,
    )


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


def get_formula_box(head_type: str) -> str:
    if head_type == "Torospherical Head (DIN 28011)":
        return """
        **DIN 28011**

        r₁ = dₐ  
        r₂ = 0.1 · dₐ  
        h = 0.1935 · dₐ − 0.455 · s
        """

    if head_type == "Torospherical Head (DIN 28013)":
        return """
        **DIN 28013**

        r₁ = 0.8 · dₐ  
        r₂ = 0.154 · dₐ  
        h = 0.255 · dₐ − 0.635 · s
        """

    if head_type == "Elliptical Head 2:1":
        return """
        **Elliptical Head 2:1**

        r₁ ≈ 0.9 · dᵢ  
        r₂ ≈ 0.17 · dᵢ  
        h = dᵢ / 4
        """

    if head_type == "Hemispherical Head":
        return """
        **Hemispherical Head**

        h = dᵢ / 2  

        Head shape is a hemisphere.
        """

    if head_type == "Flat Head":
        return """
        **Flat Head**

        h = 0  

        Idealized flat end plate.
        """

    return ""


def render_formula_card(markdown_text: str) -> None:
    html = markdown_text.strip()
    html = html.replace("**", "")
    html = html.replace("\n", "<br>")

    st.markdown(
        f"""
        <div class="formula-card">
            {html}
        </div>
        """,
        unsafe_allow_html=True,
    )


geometry_data = {
    "Vessel type": vessel_type,
    "Head type": head_type,
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


st.dataframe(
    pd.DataFrame([geometry_data]),
    width="stretch",
    hide_index=True,
)


col_vessel, col_head, col_formula = st.columns(3)

with col_vessel:
    st.markdown('<div class="section-title">Vessel preview</div>', unsafe_allow_html=True)
    st.pyplot(fig_tank, width="stretch")

with col_head:
    st.markdown('<div class="section-title">Head preview</div>', unsafe_allow_html=True)
    st.pyplot(fig_head, width="stretch")

with col_formula:
    st.markdown('<div class="section-title">Head formula</div>', unsafe_allow_html=True)
    render_formula_card(get_formula_box(head_type))


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

        is_analytical_reference = head_type in ANALYTICAL_REFERENCE_HEADS

        verification_label = (
            "Analytical Reference"
            if is_analytical_reference
            else "Engineering Reference"
        )

        if head_type == "Flat Head":
            verification_help = (
                "Analytical reference for a cylindrical vessel with flat heads:\n\n"
                "V = π · R² · Lᵢ"
            )

        elif head_type == "Hemispherical Head":
            verification_help = (
                "Analytical reference for a cylindrical vessel with two hemispherical heads:\n\n"
                "V = π · R² · (Lᵢ − 2R) + 4/3 · π · R³"
            )

        elif head_type == "Elliptical Head 2:1":
            verification_help = (
                "Analytical reference for a cylindrical vessel with two 2:1 elliptical heads:\n\n"
                "V = π · R² · (Lᵢ − 2h) + 2 · (2/3 · π · R² · h)"
            )

        elif head_type == "Torospherical Head (DIN 28011)":
            verification_help = (
                "Engineering reference for a cylindrical vessel with to torospherical heads according to DIN 28011:\n\n"
                "V ≈ π · R² · (Lᵢ − 2h) + 2 · 0.1 · (Dₐ − 2s)³"
            )

        elif head_type == "Torospherical Head (DIN 28013)":
            verification_help = (
                "Engineering reference for a cylindrical vessel with to torospherical heads according to DIN 28013:\n\n"
                "V ≈ π · R² · (Lᵢ − 2h) + 2 · 0.1298 · (Dₐ − 2s)³"
            )

        else:
            verification_help = (
                "Reference volume used for comparison with the numerically calculated volume."
            )

        with st.sidebar:
            # st.divider()
            st.subheader("Results")
            st.metric(
                "Calculated Volume",
                f"{validation['numerical_volume_m3']:.5f} m³",
                help="Volume calculated numerically from the generated filling curve.",
            )
            st.metric(
                verification_label,
                f"{validation['reference_volume_m3']:.5f} m³",
                help=verification_help,
            )
            st.metric(
                "Difference",
                f"{validation['deviation_percent']:.4f} %",
                help="Relative difference between calculated volume and reference volume.",
            )

        header_left, header_right = st.columns([1.35, 1])

        with header_left:
            st.markdown("### Filling curve")

        col_plot, col_table = st.columns([1.35, 1])

        with col_plot:
            st.line_chart(df.set_index("Level (cm)"), height=300)

        with col_table:
            st.dataframe(
                df,
                width="stretch",
                height=300,
            )

    except Exception as error:
        st.error(f"Calculation failed: {error}")

else:
    st.info("Enter vessel parameters in the sidebar and click Calculate.")