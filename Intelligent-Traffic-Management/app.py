
import streamlit as st
import random
from datetime import datetime

st.set_page_config(
    page_title="Intelligent Traffic Management",
    page_icon="🚦",
    layout="wide"
)

st.title("🚦 Intelligent Traffic Management System")
st.write("Smart traffic monitoring and signal management dashboard")

st.sidebar.header("Traffic Controls")
mode = st.sidebar.selectbox(
    "Select Signal Mode",
    ["Automatic", "Manual"]
)

cycle_time = st.sidebar.slider(
    "Total Signal Cycle (seconds)",
    60, 240, 120
)

st.subheader("Enter Vehicle Count for Each Road")

roads = ["North Road", "South Road", "East Road", "West Road"]
vehicles = {}

columns = st.columns(4)

for i, road in enumerate(roads):
    with columns[i]:
        vehicles[road] = st.number_input(
            road,
            min_value=0,
            max_value=200,
            value=[45, 30, 70, 20][i],
            step=1
        )

emergency = st.selectbox(
    "Emergency Vehicle Road",
    ["None"] + roads
)

if st.button("🚦 Calculate Traffic Signals", type="primary"):
    total = sum(vehicles.values())

    if total == 0:
        st.warning("Please enter at least one vehicle.")
    else:
        green_times = {}

        if mode == "Automatic":
            remaining = cycle_time - 40
            for road in roads:
                green_times[road] = max(
                    10,
                    int(remaining * vehicles[road] / total)
                )
        else:
            st.info(
                "Manual mode: Use Automatic mode for calculated "
                "signal timings in this demonstration."
            )
            for road in roads:
                green_times[road] = 30

        if emergency != "None":
            green_times[emergency] = max(
                green_times[emergency], 60
            )

        st.success("Traffic signals calculated successfully!")

        st.subheader("Traffic Dashboard")

        metric_columns = st.columns(4)

        for i, road in enumerate(roads):
            with metric_columns[i]:
                st.metric(
                    road,
                    f"{vehicles[road]} vehicles",
                    f"{green_times[road]} sec green"
                )

        st.subheader("Traffic Density")

        for road in roads:
            count = vehicles[road]

            if count < 30:
                density = "Low 🟢"
            elif count < 70:
                density = "Medium 🟡"
            else:
                density = "High 🔴"

            st.write(f"**{road}:** {density}")
            st.progress(count / 200)

        st.subheader("Traffic Signal Status")

        for road in roads:
            st.write(
                f"🚦 **{road}** — "
                f"🟢 Green: {green_times[road]} seconds"
            )

        if emergency != "None":
            st.warning(
                f"Emergency priority enabled for {emergency}"
            )

        st.caption(
            "Last updated: " + datetime.now().strftime(
                "%d-%m-%Y %H:%M:%S"
            )
        )

st.divider()
st.caption(
    "Educational simulation only. Not connected to real traffic lights."
)
