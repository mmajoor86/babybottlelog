import json
from io import StringIO

import pandas as pd
import streamlit as st
from azure.storage.blob import BlobServiceClient

from constants import DOB_FILE, RECOMMENDATION_FILE, TARGET_FILE


def download_file_from_blob(, blob_name="history.csv"):
    blob_service_client = BlobServiceClient.from_connection_string(
        st.secrets["connection_string"]
    )
    blob_client = blob_service_client.get_blob_client(
        container=st.secrets['env'], blob=blob_name
    )
    blob_data = blob_client.download_blob().readall()
    df = pd.read_csv(StringIO(blob_data.decode("utf-8")))
    return df


def upload_dataframe_to_blob(df, blob_name="history.csv"):
    blob_service_client = BlobServiceClient.from_connection_string(
        st.secrets["connection_string"]
    )
    blob_client = blob_service_client.get_blob_client(
        container=st.secrets['env'], blob=blob_name
    )
    csv_string = df.to_csv(index=False)
    blob_client.upload_blob(csv_string, overwrite=True)


def load_target() -> int:
    with open(TARGET_FILE, "r") as file:
        return json.load(file).get("daily_milk_target")


def load_recommended_amount_ml_per_kg() -> int:
    with open(RECOMMENDATION_FILE, "r") as file:
        return json.load(file).get("recommended_amount_ml_per_kg")


def load_dob() -> str:
    with open(DOB_FILE, "r") as file:
        return json.load(file).get("date_of_birth")
