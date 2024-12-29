from datetime import datetime, timedelta
import os
import pandas as pd
import plotly.express as px
import pytz
import streamlit as st


def app():
    st.markdown("### 📊 Visualizing baby Jessie's logged data! 🌸👶")
    df = read_files()

    # Date range filter
    timezone = pytz.timezone("Europe/Amsterdam")
    start_date = st.date_input('Start date', datetime.now(timezone).date()- timedelta(days=7))
    end_date = st.date_input('End date', datetime.now(timezone).date())

    if start_date > end_date:
        st.error("Error: End date must fall after start date.")
        return  # Filter data based on the selected date range
    mask = (df["Date"] >= start_date) & (df["Date"] <= end_date)
    df_filtered = df.loc[mask]
    st.subheader("🍼 Activity Over Time")

    # Plot Activity Count Over Time by Activity
    fig_activity, fig_amount = create_daily_plots(df_filtered)
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


def create_daily_plots(df_filtered):
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
        return fig_activity, fig_amount