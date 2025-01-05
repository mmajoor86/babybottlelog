import json
from io import StringIO

import pandas as pd
import streamlit as st
from azure.storage.blob import BlobServiceClient

TARGET_FILE = r"data/daily_target.json"
DOB_FILE = r"data/dob.json"


def load_target() -> int:
    with open(TARGET_FILE, "r") as file:
        return json.load(file).get("daily_milk_target")


def load_dob() -> str:
    with open(DOB_FILE, "r") as file:
        return json.load(file).get("date_of_birth")


def download_file_from_blob(container_name="prod", blob_name="history.csv"):
    blob_service_client = BlobServiceClient.from_connection_string(
        st.secrets["connection_string"]
    )
    blob_client = blob_service_client.get_blob_client(
        container=container_name, blob=blob_name
    )
    blob_data = blob_client.download_blob().readall()
    df = pd.read_csv(StringIO(blob_data.decode("utf-8")))
    return df


def upload_dataframe_to_blob(df, container_name="prod", blob_name="history.csv"):
    blob_service_client = BlobServiceClient.from_connection_string(
        st.secrets["connection_string"]
    )
    blob_client = blob_service_client.get_blob_client(
        container=container_name, blob=blob_name
    )
    csv_string = df.to_csv(index=False)
    blob_client.upload_blob(csv_string, overwrite=True)
