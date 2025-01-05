import json
import os

import pandas as pd
import streamlit as st

# Path to the JSON file to store the daily milk target
TARGET_FILE = "daily_target.json"


def load_target():
    if os.path.exists(TARGET_FILE):
        with open(TARGET_FILE, "r") as file:
            return json.load(file).get(
                "daily_milk_target", 600
            )  # Default to 600 if not set
    return 600


def save_target(target):
    with open(TARGET_FILE, "w") as file:
        json.dump({"daily_milk_target": target}, file)


def app():
    st.markdown("### 🚀 Admin Centre")

    # Load the current target
    current_target = load_target()

    # Input for Daily Milk Target
    daily_target = st.number_input(
        label="Daily Milk Target (ml)", min_value=600, step=50, value=current_target
    )

    # Button to confirm the change
    if st.button("Set Daily Target"):
        save_target(daily_target)
        st.success(f"Daily Milk Target set to: {daily_target} ml")
        st.rerun()  # Reload
    # Display the current target
    st.write(f"Current Daily Milk Target: {daily_target} ml")

    # Path to the data file
    data_file = "data/history.csv"
    # Load the data
    df = pd.read_csv(data_file)

    # Display the data editor s
    st.markdown("### Data Editor")
    edited_df = st.data_editor(df, num_rows="dynamic")
    # Save button
    if st.button("Save Changes"):
        edited_df.to_csv(data_file, index=False)
        st.success("Changes saved successfully!")
