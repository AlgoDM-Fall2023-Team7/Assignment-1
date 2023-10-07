import streamlit as st
import os  # Add this import
from sqlalchemy import create_engine
from snowflake.sqlalchemy import URL
from dotenv import load_dotenv
import pandas as pd
from queries import queries  # Import the queries dictionary

load_dotenv()  # Load environment variables from .env

# Define a function to execute SQL queries
def execute_query(engine, sql_query):
    with engine.connect() as conn:
        result_df = pd.read_sql_query(sql_query, conn)
    return result_df

# Define a function to dispose of the engine and close the connection
def close_connection(engine):
    if engine is not None:  # Check if engine is created
        engine.dispose()

# Define a function to render the query input form
def render_query_input(query_name, query_info):
    query_sql = query_info["sql"]
    query_description = query_info["description"]
    query_explanation = query_info["explanation"]
    placeholders = query_info["placeholders"]
    
    st.sidebar.markdown(f"#### {query_description}")
    st.sidebar.markdown("Substitution Parameters:")
    
    # Create a dictionary to store parameter values
    params = {}
    
    # Loop through placeholders and create input elements dynamically
    for placeholder, param_info in placeholders.items():
        param_label = param_info["label"]
        param_type = param_info["type"]
        
        if param_type == "slider":
            # Use a slider for the year parameter
            selected_option = st.sidebar.slider(param_label, int(param_info["min"]), int(param_info["max"]))
        else:
            # Use a dropdown for other parameters
            param_options = param_info["options"]
            selected_option = st.sidebar.selectbox(param_label, param_options)
        
        params[placeholder] = selected_option

    # Create a button to execute the query
    if all(params.values()) and st.sidebar.button("Execute Query", key="execute_query_button"):
        sql_query = query_sql.format(**params)
        if sql_query:
            # Display the query explanation
            st.markdown(f"**Query Explanation:** {query_explanation}")
            result_df = execute_query(engine, sql_query)
            st.table(result_df)
    elif not all(params.values()):
        st.sidebar.warning("Please fill in all substitution parameters.")
    else:
        st.sidebar.warning("Please fill in all substitution parameters before executing the query.")

# Create a Snowflake URL using the snowflake.sqlalchemy module
engine = create_engine(
    f'snowflake://{os.getenv("SNOWFLAKE_USER")}:{os.getenv("SNOWFLAKE_PASSWORD")}@{os.getenv("SNOWFLAKE_ACCOUNT_IDENTIFIER")}/?warehouse={os.getenv("SNOWFLAKE_WAREHOUSE")}&database={os.getenv("SNOWFLAKE_DATABASE")}&schema={os.getenv("SNOWFLAKE_SCHEMA")}'
)

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


