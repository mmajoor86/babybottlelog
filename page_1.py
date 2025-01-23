from datetime import datetime

import numpy as np
import pytz
import streamlit as st

from constants import ACTIVITIES
from utils import store_df_to_blob


def app():
    st.markdown("### Log feedings and diaper changes for baby Jessie! 🌸👶")

    # Define the timezone for Amsterdam
    timezone = pytz.timezone("Europe/Amsterdam")
    # Get the current date and time in the Amsterdam timezone and remove microseconds
    current_time_amsterdam = datetime.now(timezone).replace(microsecond=0)
    # Record Date and Time
    date = st.date_input("📅 Date", current_time_amsterdam.date())
    time = st.time_input("⏰ Time", value=current_time_amsterdam)
    date_time = datetime.combine(date, time)

    # Record Activity
    activity = activity = st.selectbox("Activity", options=ACTIVITIES)
    amount = np.nan
    weight = np.nan
    length = np.nan
    # Record Amount (optional)
    if activity == "🍼 Drink":
        amount = st.number_input(
            "Amount Consumed (ml)",
            min_value=0,
            max_value=200,
            step=10,
            format="%d",
            value=0,
        )

    # Record Weight (optional)
    if activity == "⚖️ Weight":
        weight = st.number_input("Weight (kg)", step=0.1, format="%.2f")

    # Record Length (optional)
    if activity == "📏 Length":
        length = st.number_input("Length (cm)", step=0.1, format="%.2f")

    # Submit button
    if st.button("Submit"):
        numbers = [i for i in [amount, weight, length] if ~np.isnan(i)]
        if len(numbers) > 0:
            st.write(f"#### Recorded: {activity} of {numbers[0]} on {date_time}")
        else:
            st.write(f"#### Recorded: {activity} on {date_time}")

        store_df_to_blob(date_time, activity, amount, weight, length)
        st.markdown("#### Data uploaded to Azure successfully 📊")
