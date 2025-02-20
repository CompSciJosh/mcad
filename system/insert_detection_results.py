# Insert detection results into Snowflake from algorithm 6
import snowflake.connector
import json
from datetime import datetime

# Connect to Snowflake
conn = snowflake.connector.connect(
    user="YOUR_USER",
    password="YOUR_PASSWORD",
    account="YOUR_ACCOUNT"
)
cur = conn.cursor()

def insert_crater_results(results):
    image_id = results["image_id"]
    detected_craters = json.dumps(results["detected_craters"])  # Convert list to JSON string
    crater_count = results["crater_count"]
    processing_time = results["processing_time"]
    detection_timestamp = results["detection_timestamp"]

    query = f"""
    INSERT INTO crater_detection_results (image_id, detected_craters, crater_count, processing_time, detection_timestamp)
    VALUES (%s, %s, %s, %s, %s)
    """
    cur.execute(query, (image_id, detected_craters, crater_count, processing_time, detection_timestamp))
    conn.commit()

# Example insertion
sample_results = {
    "image_id": "001/image_0.png",
    "detected_craters": [{"center": (150, 200), "radius": 30, "confidence": 0.9}],
    "crater_count": 1,
    "processing_time": 0.8,
    "detection_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}

insert_crater_results(sample_results)
