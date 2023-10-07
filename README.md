## Assignment 1 - Task 1

### Company Evaluation of Best Buy - https://www.bestbuy.com/

#### 1. Product
- Identify and describe the company's product or service.

#### 2. Sales Strategy
- Explain how the company sells its product or service. Is it primarily through e-commerce, physical stores, or other channels?

#### 3. Pricing
- Detail the pricing strategy employed by the company. Is it based on a subscription model, one-time purchase, or something else?

#### 4. Promotions
- Describe the promotions and marketing campaigns the company uses to attract customers.

#### 5. Algorithmic Marketing Services
- Enumerate the algorithmic marketing services utilized by the company. Reference the provided image for guidance.

#### 6. Data Requirements
- Identify the datasets necessary for building and implementing the algorithmic marketing services.
  - Discuss the expected frequency of data changes.
  - Propose how these datasets would be stored.

#### 7. Technology Stack
- After reviewing the company's job/career site (https://www.stitchfix.com/), list the technologies and programmatic services mentioned. Include any relevant findings.

## Assignment 1 - Task 2 

### Marketing Dashboard Prototype - https://shorturl.at/rCG24
#### Design
- Utilize the TPC-DS Dataset from Snowflake to design a marketing dashboard.
- Discuss the use case and functionality of the dashboard.
- Explain the purpose and relevance of the 10 assigned SQL queries in building the dashboard.
  - Categorize each query according to the areas they serve.

## Assignment 1 - Task 3

### Streamlit Application

#### Streamlit-Snowflake Integration

- Develop a Streamlit application that connects to Snowflake using SQLAlchemy.
- The application should allow users to change query substitution parameters from the Streamlit frontend.

## Usage
#### Requirements to Run the App
Before running the Streamlit application, make sure you have the following requirements installed:

- Your Favorite IDE or Text Editor: Use an integrated development environment (IDE) or a text editor of your choice for code editing.

- Python 3.8 - Python 3.11: Ensure that you have Python installed on your system, preferably in the version range from Python 3.8 to Python 3.11.

- Snowflake Account: You need access to a Snowflake account to connect to the Snowflake database.

- PIP: Ensure that PIP, the Python package manager, is installed on your system.

Create a new Python virtual environment and activate it.

Install Streamlit and other required packages.

Before running the Streamlit application, add your Snowflake credentials to a .env file in the project directory. Include the following information:
##### .env file
- SNOWFLAKE_ACCOUNT = your_account_url
- SNOWFLAKE_USER = your_username
- SNOWFLAKE_PASSWORD = your_password
- SNOWFLAKE_ROLE = your_role
- SNOWFLAKE_WAREHOUSE = your_warehouse
- SNOWFLAKE_DATABASE = your_database
- SNOWFLAKE_SCHEMA = your_schema

Once you have set up your environment and configured Snowflake credentials, you can run the Streamlit application using the following command:
streamlit run main.py


## Contributors

- Aishwarya SVS
- Arjun Janardhan
- Sanidhya Mathur
