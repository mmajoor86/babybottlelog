from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import pytz
import streamlit as st
from dateutil import relativedelta

from utils import download_file_from_blob, load_dob, load_target


def app():
    st.markdown("### 📊 Jessie Analytics 🌸👶")
    df = read_files()
    daily_target = load_target()
    dob = load_dob()
    bday_message = generate_bday_message(dob)
    st.write(bday_message)
    # Date range filter
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


def read_files() -> pd.DataFrame:
    """Ingest History CSV File"""
    df = download_file_from_blob()
    # Convert 'Date-Time' column to datetime
    df["Date-Time"] = pd.to_datetime(df["Date-Time"], format="%Y-%m-%d %H:%M:%S")
    df["Date"] = df["Date-Time"].dt.date
    df = df.sort_values(by="Date-Time", ascending=False).reset_index(drop=True)
    return df


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
        df_weight,
        x="Date",
        y="Weight",
        color="Activity",
        markers=True,
        title="Weight In kg Over Time",
        labels={"Date": "Date", "Weight": "Weight"},
    )

    fig_weight.update_layout(xaxis_tickformat="%Y-%m-%d")

    fig_length = px.line(
        df_length,
        x="Date",
        y="Length",
        color="Activity",
        markers=True,
        title="Length in cm Over Time",
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
