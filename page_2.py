import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime


def app():
    st.title("📊 Overview Page")
    st.markdown("### Visualizing baby Jessie's logged data! 🌸👶")
    df = read_files()

    # Date range filter
    min_date = df["Date"].min()
    max_date = df["Date"].max()
    start_date = st.date_input("Start date", min_date)
    end_date = st.date_input("End date", max_date)
    if start_date > end_date:
        st.error("Error: End date must fall after start date.")
        return  # Filter data based on the selected date range
    mask = (df["Date"] >= start_date) & (df["Date"] <= end_date)
    df_filtered = df.loc[mask]
    st.subheader("🍼 Activity Over Time")

    # Plot Activity Count Over Time using Plotly
    activity_count = (
        df_filtered.groupby(["Date", "Activity"]).size().reset_index(name="Count")
    )
    fig_activity = px.bar(
        activity_count,
        x="Date",
        y="Count",
        color="Activity",
        barmode="stack",
        title="Activity Count Over Time",
        labels={"Date": "Date", "Count": "Activity Count"},
    )
    fig_activity.update_layout(xaxis_tickformat="%Y-%m-%d")
    st.plotly_chart(fig_activity)

    st.subheader("💧 Amount Consumed Over Time")

    # Plot Amount Consumed Over Time using Plotly
    if "Amount Consumed" in df.columns:
        amount_consumed = (
            df_filtered.groupby("Date")["Amount Consumed"].sum().reset_index()
        )
        fig_amount = px.bar(
            amount_consumed,
            x="Date",
            y="Amount Consumed",
            title="Amount Consumed Over Time",
        )
        fig_amount.update_layout(xaxis_tickformat="%Y-%m-%d")
        st.plotly_chart(fig_amount)
    else:
        st.write("No data on amount consumed yet.")

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
    return df
