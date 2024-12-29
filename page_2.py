from datetime import datetime, timedelta
import os
import pandas as pd
import plotly.express as px
import pytz
import streamlit as st
import json

TARGET_FILE = "daily_target.json"


def app():
    st.markdown("### 📊 Jessie Analytics 🌸👶")
    df = read_files()
    daily_target = load_target()

    # Date range filter
    timezone = pytz.timezone("Europe/Amsterdam")
    start_date = st.date_input(
        "Start date", datetime.now(timezone).date() - timedelta(days=7)
    )
    end_date = st.date_input("End date", datetime.now(timezone).date())

    if start_date > end_date:
        st.error("Error: End date must fall after start date.")
        return  # Filter data based on the selected date range
    mask = (df["Date"] >= start_date) & (df["Date"] <= end_date)
    df_filtered = df.loc[mask]

    st.subheader("Most recent activities")
    last_events = df_filtered.sort_values(by="Date-Time").groupby("Activity").tail(1)
    st.dataframe(last_events)

    st.subheader("🍼 Activity Over Time")
    # Plot Activity Count Over Time by Activity
    fig_activity, fig_amount = create_daily_plots(df_filtered, daily_target)
    st.plotly_chart(fig_activity)
    st.plotly_chart(fig_amount)
    st.write("### Raw Data 📋")
    st.dataframe(df)


def read_files(datadir: str = "data") -> pd.DataFrame:
    """Read log files and collect in a dataframe"""
    # Check if any CSV files exist
    csv_files = [f for f in os.listdir("data") if f.endswith(".csv")]

    if len(csv_files) == 0:
        st.write(
            "No data available yet. Please log some activities in the Data Entry page. 🍼👶"
        )

    else:
        st.write(f"Found {len(csv_files)} log files")

    # Combine all CSV files into a single DataFrame
    df_list = []
    for file in csv_files:
        df = pd.read_csv(f"{datadir}/{file}")
        df_list.append(df)

    df = pd.concat(df_list, ignore_index=True)
    # Convert 'Date-Time' column to datetime
    df["Date-Time"] = pd.to_datetime(df["Date-Time"], format="%Y-%m-%d %H:%M:%S")
    df["Date"] = df["Date-Time"].dt.date
    df = df.sort_values(by="Date-Time", ascending=False).reset_index(drop=True)
    return df


def load_target():
    if os.path.exists(TARGET_FILE):
        with open(TARGET_FILE, "r") as file:
            return json.load(file).get(
                "daily_milk_target", 600
            )  # Default to 600 if not set
    return 600


def create_daily_plots(df_filtered, daily_target):
    """Generate daily plots for activity counts and consumption"""
    activity_count = (
        df_filtered.groupby(["Date", "Activity"]).size().reset_index(name="Count")
    )
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
    amount_consumed = df_filtered.groupby("Date")["Amount Consumed"].sum().reset_index()
    fig_amount = px.bar(
        amount_consumed,
        x="Date",
        y="Amount Consumed",
        title="Amount Consumed Over Time",
    )
    fig_amount.update_layout(xaxis_tickformat="%Y-%m-%d")
    fig_amount.add_shape(
        type="line",
        x0=df_filtered["Date"].min(),
        x1=df_filtered["Date"].max(),
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
    return fig_activity, fig_amount
