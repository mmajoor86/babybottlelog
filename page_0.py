import json

import streamlit as st

from utils import (
    load_recommended_amount_ml_per_kg,
    read_files_from_blob,
    upload_dataframe_to_blob,
    save_target_recommended_amount,
)


def app():
    st.markdown("### 🚀 Admin Centre")

    # Load recommended amount ml per kg
    recommended_amount_ml_per_kg = load_recommended_amount_ml_per_kg()

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
    # Load the data
    df = read_files_from_blob()

    # Display the data editor s
    st.markdown("### Data Editor")
    edited_df = st.data_editor(df, num_rows="dynamic")
    # Save button
    if st.button("Save Changes"):
        upload_dataframe_to_blob(edited_df, blob_name="history.csv")
        st.success("#### Changes uploaded to Azure successfully 📊")
