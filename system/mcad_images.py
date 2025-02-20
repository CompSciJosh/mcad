import os
import snowflake.connector

# Connect to Snowflake using environment variables
conn = snowflake.connector.connect(
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    warehouse="mcad_warehouse",
    database="MCAD",
    schema="mcad_data"
)
cur = conn.cursor()

# Define the path where PNG images are stored
data_folder = "/Users/joshuajackson/Downloads/mcad_moon_data"

# Iterate through all folders and insert PNG images
for root, _, files in os.walk(data_folder):
    subfolder_name = os.path.basename(root)  # Extract folder name (e.g., "001")

    for file in files:
        if file.lower().endswith(".png"):
            png_path = os.path.join(root, file)
            png_file_name = f"{subfolder_name}/{file}"  # Match format in `moon_crater_data`

            try:
                # Read PNG as binary data
                with open(png_path, "rb") as f:
                    png_binary = f.read()

                # SQL Insert Statement
                sql_query = """
                    INSERT INTO MCAD.MCAD_DATA.MOON_CRATER_IMAGES ("PNG File", "Image_Data")
                    VALUES (%s, %s)
                """

                # Execute Insert
                cur.execute(sql_query, (png_file_name, png_binary))

            except Exception as e:
                print(f"Error inserting {png_file_name}: {e}")

# Commit and Close Connection
conn.commit()
cur.close()
conn.close()

print("🫵🏾👍🏾 PNG images successfully uploaded to Snowflake! 🚀")
