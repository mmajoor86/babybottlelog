import json

import streamlit as st

from utils import (TARGET_FILE, download_file_from_blob, load_target,
                   upload_dataframe_to_blob)


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

    # Load the data
    df = download_file_from_blob()

    # Display the data editor s
    st.markdown("### Data Editor")
    edited_df = st.data_editor(df, num_rows="dynamic")
    # Save button
    if st.button("Save Changes"):
        upload_dataframe_to_blob(edited_df)
        st.success("Changes saved successfully!")
