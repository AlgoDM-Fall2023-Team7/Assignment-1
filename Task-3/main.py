import streamlit as st
import os  # Add this import
from sqlalchemy import create_engine
from snowflake.sqlalchemy import URL
from dotenv import load_dotenv
import pandas as pd
from queries import queries  # Import the queries dictionary

load_dotenv()  # Load environment variables from .env


# Set the title of the app
st.sidebar.markdown("<h1 style='text-align: center;'>FlakeQuery</h1>", unsafe_allow_html=True)
