import streamlit as st
import os  # Add this import
from sqlalchemy import create_engine
from snowflake.sqlalchemy import URL
from dotenv import load_dotenv
import pandas as pd
from queries import queries  # Import the queries dictionary

load_dotenv()  # Load environment variables from .env

# Define a function to dispose of the engine and close the connection
def close_connection(engine):
    if engine is not None:  # Check if engine is created
        engine.dispose()

# Set the title of the app
st.sidebar.markdown("<h1 style='text-align: center;'>FlakeQuery</h1>", unsafe_allow_html=True)

# Create a colored horizontal rule using HTML and CSS
st.sidebar.markdown("<hr style='border: 2px solid gray;'>", unsafe_allow_html=True)

# Background-color of the sidebar
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        background-color: #FAF5E9;
    }
</style>
""", unsafe_allow_html=True)


# Create a Snowflake URL using the snowflake.sqlalchemy module
engine = create_engine(
    f'snowflake://{os.getenv("SNOWFLAKE_USER")}:{os.getenv("SNOWFLAKE_PASSWORD")}@{os.getenv("SNOWFLAKE_ACCOUNT_IDENTIFIER")}/?warehouse={os.getenv("SNOWFLAKE_WAREHOUSE")}&database={os.getenv("SNOWFLAKE_DATABASE")}&schema={os.getenv("SNOWFLAKE_SCHEMA")}'
)


