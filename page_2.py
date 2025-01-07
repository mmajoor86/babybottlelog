import json
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import pytz
import requests
import streamlit as st
from dateutil import relativedelta

from constants import DOB_FILE, RECOMMENDATION_FILE, TARGET_FILE


def app():
    st.markdown("### 📊 Jessie Analytics 🌸👶")
    df = read_files()

    st.subheader("What's happening today?")
    dob = load_dob()
    bday_message = generate_bday_message(dob)
    st.write(bday_message)

    weather_messages = generate_weather_message()
    st.write("**Het weer in Utrecht:**")
    if len(weather_messages) > 1:
        st.write(weather_messages[0])
        st.write(weather_messages[1])
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(weather_messages[2])
        with col2:
            st.image(r"images/" + (f"{weather_messages[-1]}") + ".png")
    else:
        st.write(weather_messages[0])

    # Date range filter
    st.subheader("Select date range for analytics:")
    timezone = pytz.timezone("Europe/Amsterdam")
    start_date = st.date_input(
        "Start date", datetime.now(timezone).date() - timedelta(days=7)
    )
    end_date = st.date_input("End date", datetime.now(timezone).date())

    if start_date > end_date:
        st.error("Error: End date must fall after start date.")
        return
    # Filter data based on the selected date range
    mask = (df["Date"] >= start_date) & (df["Date"] <= end_date)
    df_filtered = df.loc[mask]

    daily_target = calculate_daily_target(df)

    st.subheader("Most recent activities")
    last_events = (
        df_filtered.sort_values(by="Date-Time")
        .groupby("Activity")
        .tail(1)
        .drop("Date", axis=1)
    )
    st.dataframe(last_events)

    st.subheader("🍼 Activity Over Time")
    # Generate Plots
    fig_weight, fig_length, fig_activity, fig_amount = create_daily_plots(
        df_filtered, daily_target
    )
    st.plotly_chart(fig_activity)
    st.plotly_chart(fig_amount)
    st.plotly_chart(fig_weight)
    st.plotly_chart(fig_length)
    st.write("### Raw Data 📋")
    st.dataframe(df)


# Calculate daily_target
def calculate_daily_target(df_filtered):
    df_weight = (
        df_filtered[df_filtered["Activity"] == "⚖️ Weight"]
        .sort_values(by="Date-Time", ascending=False)
        .reset_index(drop=True)
    ).dropna(subset="Weight")
    try :
        last_weight = df_weight["Weight"][0]
        recommended_amount_ml_per_kg = load_recommended_amount_ml_per_kg()
        if last_weight != 0 and recommended_amount_ml_per_kg != 0:
            daily_target = last_weight * recommended_amount_ml_per_kg
        else:
            daily_target = load_target()
    except:
        daily_target = load_target()
    return daily_target


def read_files(datadir: str = "data") -> pd.DataFrame:
    """Ingest History CSV File"""
    df = pd.read_csv(f"{datadir}/history.csv")
    # Convert 'Date-Time' column to datetime
    df["Date-Time"] = pd.to_datetime(df["Date-Time"], format="%Y-%m-%d %H:%M:%S")
    df["Date"] = df["Date-Time"].dt.date
    df = df.sort_values(by="Date-Time", ascending=False).reset_index(drop=True)
    return df


def load_target() -> int:
    with open(TARGET_FILE, "r") as file:
        return json.load(file).get("daily_milk_target")


def load_recommended_amount_ml_per_kg() -> int:
    with open(RECOMMENDATION_FILE, "r") as file:
        return json.load(file).get("recommended_amount_ml_per_kg")


def load_dob() -> str:
    with open(DOB_FILE, "r") as file:
        return json.load(file).get("date_of_birth")


def generate_weather_message():
    with st.spinner("Retrieving weather data..."):
        ### prepare API key and URL
        api_key = st.secrets["api_key"]
        api_url = (
            "http://weerlive.nl/api/weerlive_api_v2.php?key=3f76c74abe&locatie=Utrecht"
        )

        ### invoke API and get the response
        response = requests.get(url=api_url, headers={"X-Api-Key": api_key})
        if response.status_code == requests.codes.ok:
            ### Convert data to JSON format and construct weather message
            data = json.loads(json.dumps(response.json()))
            weather = data["liveweer"][0]
            if "temp" in weather:
                messages = [
                    f"🌡️ **Temperatuur** : {weather['temp']} °C",
                    f"📝 **Omschrijving**: {weather['samenv']}",
                    f"💡 **Korte Samenvatting**: {weather['lkop']}",
                    f"{weather['image']}",
                ]
            else:
                messages = [
                    "Er is helaas iets misgegaan met het ophalen van weer data 😒"
                ]

        else:
            messages = ["Er is helaas iets misgegaan met het ophalen van weer data 😒"]
    return messages


def generate_bday_message(dob: str) -> str:
    timezone = pytz.timezone("Europe/Amsterdam")
    dob = pd.to_datetime(dob, format="%d-%m-%Y").date()
    today = datetime.now(timezone).date()
    r = relativedelta.relativedelta(today, dob)
    ndays = (today - dob).days

    # check if X full years have passed
    year_cond = dob.month == today.month and dob.day == today.day
    calmonth_cond = dob.day == today.day
    if year_cond:
        message = f"🎂HURRAY🎂 Jessie is {today.year-dob.year} year old today 🎁🎁"
    elif calmonth_cond:
        months_difference = (r.years * 12) + r.months
        message = (
            f"🎈HURRAY🎈 Jessie is {months_difference} calender months old today 🎉"
        )
    elif ndays % 28 == 0:
        message = f"🎈HURRAY🎈 Jessie is {ndays/28} months old today 🎉"
    elif ndays % 7 == 0:
        message = f"🎈HURRAY🎈 Jessie is {ndays/7} weeks old today 🥳"
    else:
        message = f"🎈HURRAY🎈 Jessie is {ndays} days old today"
    return message


def create_daily_plots(df_filtered: pd.DataFrame, daily_target: int):
    """Generate daily plots for activity counts and consumption"""

    # DF without weight and length
    df_activities = df_filtered[
        ~df_filtered["Activity"].isin(["⚖️ Weight", "📏 Length"])
    ]

    # DF weight
    df_weight = df_filtered[df_filtered["Activity"].isin(["⚖️ Weight"])]

    # DF length
    df_length = df_filtered[df_filtered["Activity"].isin(["📏 Length"])]

    activity_count = (
        df_activities.groupby(["Date", "Activity"]).size().reset_index(name="Count")
    )

    fig_weight = px.line(
        df_weight.dropna(subset="Weight"),
        x="Date",
        y="Weight",
        color="Activity",
        markers=True,
        title="Weight In kg Over Time",
        labels={"Date": "Date", "Weight": "Weight"},
    )

    fig_weight.update_layout(xaxis_tickformat="%Y-%m-%d")

    fig_length = px.line(
        df_length.dropna(subset="Length"),
        x="Date",
        y="Length",
        color="Activity",
        markers=True,
        title="Length In cm Over Time",
        labels={"Date": "Date", "Length": "Length"},
    )

    fig_length.update_layout(xaxis_tickformat="%Y-%m-%d")

    fig_activity = px.line(
        activity_count,
        x="Date",
        y="Count",
        color="Activity",
        markers=True,
        title="Activity Count Over Time",
        labels={"Date": "Date", "Count": "Activity Count"},
    )

    fig_activity.update_layout(xaxis_tickformat="%Y-%m-%d")
    amount_consumed = (
        df_activities.groupby("Date")["Amount Consumed"].sum().reset_index()
    )
    fig_amount = px.bar(
        amount_consumed,
        x="Date",
        y="Amount Consumed",
        title="Amount Consumed Over Time",
    )
    fig_amount.update_layout(xaxis_tickformat="%Y-%m-%d")
    fig_amount.add_shape(
        type="line",
        x0=df_activities["Date"].min(),
        x1=df_activities["Date"].max(),
        y0=daily_target,
        y1=daily_target,
        line=dict(color="Red", width=3, dash="dash"),
    )
    fig_amount.add_annotation(
        x=amount_consumed["Date"].max(),
        y=daily_target,
        text=f"Daily Target: {daily_target} ml",
        showarrow=False,
        yshift=10,
    )
    return fig_weight, fig_length, fig_activity, fig_amount
