# Joshua Jackson
# Senior Design Spring '25: Multiscale Crater Analysis and Detection (MCAD)
# February 13, 2025

######################################################################
###################### Snowflake Connection Test #####################
############## Check your phone for connection request  ##############
############################ due to MFA ##############################
######################################################################

import snowflake.connector

try:
    conn = snowflake.connector.connect(
        user="your_username",
        password="your_password",
        account="your_account"
    )
    # conn.close()
    cur = conn.cursor()

    cur.execute("SELECT CURRENT_VERSION()")
    version = cur.fetchone()
    print("Connected successfully!")
    print(f"Connected to Snowflake, version: {version[0]}")

    cur.close()
    conn.close()
except Exception as e:
    print(f"Connection failed: {e}")

#############################################
########## Update Version of Above ##########
#############################################

# import snowflake.connector
#
# conn = snowflake.connector.connect(
#     user="your_username",
#     password="your_password",
#     account="your_account",
#     warehouse="your_warehouse",
#     database="MCAD",
#     schema="MCAD_DATA"
# )
#
# cur = conn.cursor()
#
# cur.execute("SELECT CURRENT_VERSION()")
# version = cur.fetchone()
# print(f"Connected to Snowflake, version: {version[0]}")
#
# cur.close()
# conn.close()
