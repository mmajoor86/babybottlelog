import json

import pandas as pd
import streamlit as st

from constants import RECOMMENDATION_FILE, TARGET_FILE
from utils import load_recommended_amount_ml_per_kg, load_target


def save_target(target):
    with open(TARGET_FILE, "w") as file:
        json.dump({"daily_milk_target": target}, file)


def save_target_recommended_amount(target):
    with open(RECOMMENDATION_FILE, "w") as file:
        json.dump({"recommended_amount_ml_per_kg": target}, file)


def app():
    st.markdown("### 🚀 Admin Centre")

    # Load the current target
    current_target = load_target()

    # Load recommended amount ml per kg
    recommended_amount_ml_per_kg = load_recommended_amount_ml_per_kg()

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

    # Input for recommended amount of milk in ml per kg
    recommended_amount_per_kg = st.number_input(
        label="Recommended amount of milk per kg (ml)",
        min_value=100,
        step=50,
        value=recommended_amount_ml_per_kg,
    )

    # Button to confirm the change
    if st.button("Set Recommended amount of milk per kg (ml)"):
        save_target_recommended_amount(recommended_amount_per_kg)
        st.success(
            f"Recommended amount of milk per kg (ml) set to: {recommended_amount_per_kg} ml"
        )
        st.rerun()  # Reload

    # Display the current target
    st.write(
        f"Current recommended amount of milk per kg: {recommended_amount_per_kg} ml"
    )

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
