
import streamlit as st
from datetime import datetime

# ==========================================
# SMART AGRICULTURE AND CROP DISEASE SYSTEM
# ==========================================

st.set_page_config(
    page_title="Smart Agriculture System",
    page_icon="🌱",
    layout="wide"
)

# ==========================================
# CROP INFORMATION
# ==========================================

CROPS = {
    "Rice": {
        "n": (60, 120),
        "p": (30, 60),
        "k": (30, 60),
        "ph": (5.5, 7.0),
        "temp": (20, 35),
        "rain": (100, 250)
    },
    "Wheat": {
        "n": (80, 150),
        "p": (30, 60),
        "k": (30, 60),
        "ph": (6.0, 7.5),
        "temp": (15, 25),
        "rain": (30, 100)
    },
    "Maize": {
        "n": (80, 150),
        "p": (40, 80),
        "k": (40, 80),
        "ph": (5.5, 7.5),
        "temp": (18, 32),
        "rain": (50, 150)
    },
    "Cotton": {
        "n": (60, 120),
        "p": (30, 60),
        "k": (30, 60),
        "ph": (5.5, 8.0),
        "temp": (21, 35),
        "rain": (50, 120)
    },
    "Tomato": {
        "n": (60, 120),
        "p": (40, 80),
        "k": (60, 120),
        "ph": (5.5, 7.0),
        "temp": (18, 30),
        "rain": (40, 100)
    },
    "Potato": {
        "n": (60, 120),
        "p": (50, 100),
        "k": (80, 150),
        "ph": (5.0, 6.5),
        "temp": (15, 25),
        "rain": (50, 100)
    }
}

# ==========================================
# DISEASE KNOWLEDGE BASE
# ==========================================

DISEASES = {
    "Rice": {
        "Brown spots on leaves": (
            "Possible Brown Spot",
            "Look for oval brown lesions with yellow halos."
        ),
        "Diamond-shaped lesions": (
            "Possible Rice Blast",
            "Look for spindle-shaped lesions on leaves."
        ),
        "Water-soaked leaf lesions": (
            "Possible Bacterial Leaf Blight",
            "Check for yellowing and drying from leaf tips."
        )
    },
    "Tomato": {
        "Yellow leaves with brown spots": (
            "Possible Early Blight",
            "Look for concentric rings on older leaves."
        ),
        "White powder on leaves": (
            "Possible Powdery Mildew",
            "Look for white powder-like growth."
        ),
        "Dark water-soaked patches": (
            "Possible Late Blight",
            "Look for rapidly spreading dark lesions."
        )
    },
    "Potato": {
        "Dark patches on leaves": (
            "Possible Late Blight",
            "Look for water-soaked dark lesions and white growth underneath."
        ),
        "Brown concentric leaf spots": (
            "Possible Early Blight",
            "Look for target-like rings on leaves."
        ),
        "Yellowing and wilting": (
            "Possible Wilt Disease",
            "Check roots and stems for discoloration."
        )
    },
    "Wheat": {
        "Orange or brown pustules": (
            "Possible Rust Disease",
            "Look for powdery orange or brown pustules."
        ),
        "White powder on leaves": (
            "Possible Powdery Mildew",
            "Look for white fungal growth on leaf surfaces."
        ),
        "Dark spots on leaves": (
            "Possible Leaf Blotch",
            "Inspect for irregular dark lesions."
        )
    },
    "Cotton": {
        "Angular water-soaked spots": (
            "Possible Bacterial Blight",
            "Look for angular lesions and vein discoloration."
        ),
        "Yellowing and leaf curling": (
            "Possible Leaf Curl Disease",
            "Check for curling, thickened veins and stunted growth."
        )
    },
    "Maize": {
        "Long grey or brown leaf lesions": (
            "Possible Leaf Blight",
            "Look for elongated lesions along leaf surfaces."
        ),
        "Small orange-brown pustules": (
            "Possible Common Rust",
            "Look for raised rust-colored pustules."
        )
    }
}

# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.title("🌾 Smart Agriculture")
page = st.sidebar.radio(
    "Choose Module",
    [
        "Dashboard",
        "Crop Recommendation",
        "Disease Checker",
        "Soil Monitoring",
        "Smart Irrigation",
        "Fertilizer Advice"
    ]
)

st.sidebar.divider()
st.sidebar.caption("Educational agriculture prototype")

# ==========================================
# MAIN HEADER
# ==========================================

st.title("🌱 Smart Agriculture & Crop Disease System")
st.write(
    "An agriculture support system for crop selection, "
    "soil monitoring, disease symptom checking and irrigation."
)

# ==========================================
# DASHBOARD
# ==========================================

if page == "Dashboard":

    st.subheader("Agriculture Dashboard")

    c1, c2, c3 = st.columns(3)

    c1.metric("Available Crops", len(CROPS))
    c2.metric("Disease Profiles", sum(
        len(v) for v in DISEASES.values()
    ))
    c3.metric("System Status", "Active")

    st.divider()

    st.subheader("Available Modules")

    modules = [
        ("🌾", "Crop Recommendation",
         "Find suitable crops using soil and climate inputs."),
        ("🔬", "Disease Checker",
         "Check possible crop diseases from observed symptoms."),
        ("🌱", "Soil Monitoring",
         "Review soil pH and nutrient values."),
        ("💧", "Smart Irrigation",
         "Get irrigation suggestions using moisture readings."),
        ("🧪", "Fertilizer Advice",
         "Review nutrient levels and possible deficiencies.")
    ]

    for icon, title, description in modules:
        with st.container(border=True):
            st.markdown(f"### {icon} {title}")
            st.write(description)

    st.info(
        "Select a module from the left sidebar to begin."
    )

# ==========================================
# CROP RECOMMENDATION
# ==========================================

elif page == "Crop Recommendation":

    st.header("🌾 Crop Recommendation")

    st.write(
        "Enter your soil and environmental conditions "
        "to find crops that may suit your farm."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        nitrogen = st.number_input(
            "Nitrogen (N)", 0.0, 200.0, 80.0
        )
        phosphorus = st.number_input(
            "Phosphorus (P)", 0.0, 200.0, 45.0
        )

    with col2:
        potassium = st.number_input(
            "Potassium (K)", 0.0, 200.0, 50.0
        )
        ph = st.number_input(
            "Soil pH", 0.0, 14.0, 6.5
        )

    with col3:
        temperature = st.number_input(
            "Temperature (°C)", -10.0, 60.0, 25.0
        )
        rainfall = st.number_input(
            "Rainfall (mm/month)", 0.0, 1000.0, 100.0
        )

    if st.button("Recommend Suitable Crops", type="primary"):

        scores = []

        for crop, values in CROPS.items():

            score = 0

            if values["n"][0] <= nitrogen <= values["n"][1]:
                score += 1

            if values["p"][0] <= phosphorus <= values["p"][1]:
                score += 1

            if values["k"][0] <= potassium <= values["k"][1]:
                score += 1

            if values["ph"][0] <= ph <= values["ph"][1]:
                score += 1

            if values["temp"][0] <= temperature <= values["temp"][1]:
                score += 1

            if values["rain"][0] <= rainfall <= values["rain"][1]:
                score += 1

            scores.append((crop, score))

        scores.sort(key=lambda x: x[1], reverse=True)

        st.success("Crop analysis completed!")

        for crop, score in scores:
            percentage = int(score / 6 * 100)

            st.write(
                f"**{crop} — {percentage}% condition match**"
            )
            st.progress(percentage / 100)

        st.caption(
            "These are rule-based condition matches, not "
            "scientifically validated yield predictions."
        )

# ==========================================
# DISEASE CHECKER
# ==========================================

elif page == "Disease Checker":

    st.header("🔬 Crop Disease Symptom Checker")

    st.write(
        "Upload a leaf photograph and select the symptoms "
        "you can observe."
    )

    crop = st.selectbox(
        "Select Crop",
        list(DISEASES.keys())
    )

    uploaded_image = st.file_uploader(
        "Upload Leaf Image",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_image:
        st.image(
            uploaded_image,
            caption="Uploaded crop leaf",
            use_container_width=True
        )

    symptoms = list(DISEASES[crop].keys())

    selected_symptoms = st.multiselect(
        "Select visible symptoms",
        symptoms
    )

    if st.button("Check Possible Disease", type="primary"):

        if not selected_symptoms:
            st.warning("Please select at least one symptom.")

        else:
            st.subheader("Disease Check Results")

            for symptom in selected_symptoms:

                disease, description = DISEASES[crop][symptom]

                with st.container(border=True):
                    st.warning(f"Possible condition: {disease}")
                    st.write(f"Observed symptom: {symptom}")
                    st.write(f"What to inspect: {description}")

            st.info(
                "This is a symptom-matching tool, not an AI "
                "image classifier. Similar symptoms can have "
                "different causes. Confirm with an agricultural "
                "expert or local KVK before treatment."
            )

# ==========================================
# SOIL MONITORING
# ==========================================

elif page == "Soil Monitoring":

    st.header("🌱 Soil Health Monitoring")

    col1, col2 = st.columns(2)

    with col1:
        soil_ph = st.slider(
            "Soil pH", 0.0, 14.0, 6.5
        )

        soil_moisture = st.slider(
            "Soil Moisture (%)", 0, 100, 45
        )

        soil_temperature = st.slider(
            "Soil Temperature (°C)", 0, 60, 25
        )

    with col2:
        n = st.slider("Nitrogen (N)", 0, 200, 80)
        p = st.slider("Phosphorus (P)", 0, 200, 50)
        k = st.slider("Potassium (K)", 0, 200, 50)

    if st.button("Analyze Soil"):

        st.subheader("Soil Analysis")

        if soil_ph < 5.5:
            st.warning("Soil is acidic.")
        elif soil_ph > 7.5:
            st.warning("Soil is alkaline.")
        else:
            st.success("Soil pH is within a commonly suitable range.")

        if soil_moisture < 30:
            st.warning("Low moisture: check irrigation requirement.")
        elif soil_moisture < 70:
            st.success("Moderate moisture reading.")
        else:
            st.info("High moisture: check for waterlogging.")

        st.write("**Nutrient readings:**")
        st.write(f"Nitrogen: {n}")
        st.write(f"Phosphorus: {p}")
        st.write(f"Potassium: {k}")

        st.caption(
            "NPK interpretation depends on the soil test method, "
            "units and crop. Get a laboratory soil test for "
            "accurate fertilizer planning."
        )

# ==========================================
# SMART IRRIGATION
# ==========================================

elif page == "Smart Irrigation":

    st.header("💧 Smart Irrigation Recommendation")

    moisture = st.slider(
        "Current Soil Moisture (%)",
        0, 100, 35
    )

    crop = st.selectbox(
        "Select Crop",
        list(CROPS.keys())
    )

    temperature = st.slider(
        "Current Temperature (°C)",
        0, 50, 28
    )

    if st.button("Check Irrigation Requirement"):

        st.subheader("Irrigation Result")

        if moisture < 30:
            st.error("Irrigation may be needed soon.")
            st.write(
                "Check the crop's water requirement and soil "
                "before irrigating."
            )

        elif moisture < 60:
            st.warning("Soil moisture is moderate.")
            st.write("Continue monitoring the soil.")

        else:
            st.success("Soil moisture is relatively high.")
            st.write(
                "Avoid unnecessary irrigation and check drainage."
            )

        if temperature > 35:
            st.info(
                "High temperature detected. Monitor moisture "
                "more frequently."
            )

        st.caption(
            "Moisture thresholds are demonstration values. "
            "Actual irrigation depends on soil type, crop stage, "
            "sensor calibration and weather."
        )

# ==========================================
# FERTILIZER ADVICE
# ==========================================

elif page == "Fertilizer Advice":

    st.header("🧪 Fertilizer Recommendation")

    crop = st.selectbox(
        "Select Crop",
        list(CROPS.keys())
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        n = st.number_input(
            "Nitrogen (N)", 0.0, 300.0, 30.0
        )

    with col2:
        p = st.number_input(
            "Phosphorus (P)", 0.0, 300.0, 30.0
        )

    with col3:
        k = st.number_input(
            "Potassium (K)", 0.0, 300.0, 30.0
        )

    if st.button("Analyze Nutrients"):

        requirements = CROPS[crop]

        st.subheader("Nutrient Analysis")

        for nutrient, value in [
            ("Nitrogen", n),
            ("Phosphorus", p),
            ("Potassium", k)
        ]:

            key = nutrient[0].lower()

            minimum = requirements[key][0]
            maximum = requirements[key][1]

            if value < minimum:
                st.warning(
                    f"{nutrient}: Below the example crop range."
                )

            elif value > maximum:
                st.info(
                    f"{nutrient}: Above the example crop range."
                )

            else:
                st.success(
                    f"{nutrient}: Within the example crop range."
                )

        st.write(
            "Use a laboratory soil test and locally recommended "
            "fertilizer schedule before applying fertilizers."
        )

# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "Smart Agriculture & Crop Disease Prediction System | "
    "Educational Prototype"
)

st.caption(
    "Last opened: " +
    datetime.now().strftime("%d-%m-%Y %H:%M:%S")
)
