import os
import psycopg2
from dataRetrieval import locations

DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_NAME = os.getenv('DB_NAME')

conn = None  # Initialize the connection variable outside the try block

try:
    conn = psycopg2.connect(
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host="localhost",
        port="5433"
    )
    cursor = conn.cursor()

    for location_name, location_coords in locations.items():
        # Split the location string into latitude and longitude
        latitude, longitude = map(float, location_coords.split(','))

        # Check if the location already exists
        cursor.execute("SELECT COUNT(id) FROM locations WHERE latitude = %s AND longitude = %s", (latitude, longitude))
        location_exists = cursor.fetchone()[0] > 0

        if not location_exists:
            # Insert the location into the table
            cursor.execute("INSERT INTO locations (name, latitude, longitude) VALUES (%s, %s, %s)",
                           (location_name, latitude, longitude))
            print(f"Location {location_name} inserted successfully!")
        else:
            print(f"Location {location_name} already exists.")

    conn.commit()

except (Exception, psycopg2.Error) as error:
    print(f"Error inserting locations: {error}")

finally:
    if conn:
        conn.close()
