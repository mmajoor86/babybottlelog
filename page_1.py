import streamlit as st
import pandas as pd
import numpy as np
import pytz
from datetime import datetime


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
    activity = st.selectbox(
        "Activity",
        ["🍼 Drink", "👶 Diaper", "💩 Poopy Diaper", "⚖️ Weight", "📏 Length"],
    )
    amount = np.nan
    weigth = np.nan
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
        length = st.number_input("Length (cm)", step=1, format="%d")

    # Submit button
    if st.button("Submit"):
        st.write(f"Date-Time: {date_time}")
        st.write(f"Activity: {activity}")
        st.write(
            f"Amount Consumed: {amount} ml" if amount > 0 else "Amount Consumed: N/A"
        )
        st.write(f"Weight: {weight} kg" if weight > 0 else "Weight: N/A")
        st.write(f"Length: {length} kg" if length > 0 else "Length: N/A")
        store_data_csv(date_time, activity, amount, weight, length)
        st.markdown("### Updated Data 📊")


def store_data_csv(
    date_time: datetime, activity: str, amount: int, weight: float, length: int
) -> pd.DataFrame:
    """Append the data to the history csv file."""
    df_hist = pd.read_csv("data/history.csv")
    df_hist["Date-Time"] = pd.to_datetime(
        df_hist["Date-Time"], format="%Y-%m-%d %H:%M:%S"
    )
    data = {
        "Date-Time": [date_time],
        "Activity": [activity],
        "Amount Consumed": [amount if amount > 0 else None],
        "Weight": [weight if weight > 0 else None],
        "Length": [length if length > 0 else None],
    }
    df = pd.concat([df_hist, pd.DataFrame(data)]).sort_values(
        by="Date-Time", ascending=False
    )
    df.to_csv("data/history.csv", index=False)
    return df
