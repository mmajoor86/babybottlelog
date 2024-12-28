import streamlit as st
import pandas as pd
import pytz
from datetime import datetime


def app():
    st.title("🍼 Baby Jessie’s Bottle Logger")
    st.markdown("### Log feedings and diaper changes for baby Jessie! 🌸👶")

    # Define the timezone for Amsterdam
    timezone = pytz.timezone("Europe/Amsterdam")
    # Get the current date and time in the Amsterdam timezone and remove microseconds
    current_time_amsterdam = datetime.now(timezone).replace(microsecond=0)
    # Record Date and Time
    date = st.date_input("📅 Date", current_time_amsterdam.date())
    time = st.time_input("⏰ Time", value=current_time_amsterdam)
    date_time = datetime.combine(date, time)
    st.write(date_time)

    # Record Activity
    activity = st.selectbox("Activity", ["🍼 Drink", "👶 Diaper", "💩 Poopy Diaper"])

    # Record Amount (optional)
    amount = st.number_input(
        "Amount Consumed (ml)",
        min_value=0,
        max_value=200,
        step=10,
        format="%d",
        value=0,
    )

    # Submit button
    if st.button("Submit"):
        st.write(f"Date-Time: {date_time}")
        st.write(f"Activity: {activity}")
        st.write(
            f"Amount Consumed: {amount} ml" if amount > 0 else "Amount Consumed: N/A"
        )
        store_data_csv(date_time, activity, amount)
        st.markdown("### Updated Data 📊")


def store_data_csv(date_time: datetime, activity: str, amount: int) -> pd.DataFrame:
    formatted_date_time = date_time.strftime("%Y-%m-%d_%H-%M-%S")
    """Store the input data as a csv file"""
    data = {
        "Date-Time": [date_time],
        "Activity": [activity],
        "Amount Consumed": [amount if amount > 0 else None],
    }
    df = pd.DataFrame(data)
    df.to_csv(f"data/{formatted_date_time}.csv", index=False)
    return df
