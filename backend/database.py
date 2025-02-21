##############################################
### Step 3: Set Up the Database Connection ###
##############################################

# import snowflake.connector
# from config import (
#     SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_PASSWORD,
#     SNOWFLAKE_DATABASE, SNOWFLAKE_SCHEMA, SNOWFLAKE_WAREHOUSE
# )
#
# # Function to create a database connection
# def get_snowflake_connection():
#     conn = snowflake.connector.connect(
#         user=SNOWFLAKE_USER,
#         password=SNOWFLAKE_PASSWORD,
#         account=SNOWFLAKE_ACCOUNT,
#         warehouse=SNOWFLAKE_WAREHOUSE,
#         database=SNOWFLAKE_DATABASE,
#         schema=SNOWFLAKE_SCHEMA
#     )
#     return conn
#######################################################
### Step 7: Configure Snowflake Database Connection ###
#######################################################
import os
import snowflake.connector
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Snowflake credentials from .env file
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE")
SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")

def get_snowflake_connection():
    """Establish and return a Snowflake database connection."""
    try:
        conn = snowflake.connector.connect(
            user=SNOWFLAKE_USER,
            password=SNOWFLAKE_PASSWORD,
            account=SNOWFLAKE_ACCOUNT,
            database=SNOWFLAKE_DATABASE,
            schema=SNOWFLAKE_SCHEMA,
            warehouse=SNOWFLAKE_WAREHOUSE
        )
        return conn
    except Exception as e:
        print(f"Error connecting to Snowflake: {e}")
        return None

def create_users_table():
    """Create the 'users' table if it does not exist."""
    conn = get_snowflake_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER AUTOINCREMENT PRIMARY KEY,
                    username STRING UNIQUE NOT NULL,
                    email STRING UNIQUE NOT NULL,
                    hashed_password STRING NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            conn.commit()
            cur.close()
            print("✅ Users table is ready.")
        except Exception as e:
            print(f"Error creating users table: {e}")
        finally:
            conn.close()

# Run this function when starting the backend to ensure the table exists
create_users_table()
