import os
import psycopg2
from dataRetrieval import locations, weather_data

DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_NAME = os.getenv('DB_NAME')

def insert_weather_data(data, location_id, cursor):
    try:
        # Create a dictionary to store data for a specific date
        date_data = {}

        for entry in data:
            for item in entry['data']:
                parameter = item['parameter']
                coordinates = item['coordinates'][0]
                lat = coordinates['lat']
                lon = coordinates['lon']

                for date_value in coordinates['dates']:
                    date = date_value['date']
                    value = date_value['value']

                    if date not in date_data:
                        date_data[date] = {
                            'location_id': location_id,
                            'date': date,
                        }

                    # Map parameters to field names
                    parameter_to_field = {
                        'wind_speed_10m:ms': 'wind_speed',
                        'wind_dir_10m:d': 'wind_direction',
                        'wind_gusts_10m_1h:ms': 'wind_gusts_1h',
                        'wind_gusts_10m_24h:ms': 'wind_gusts_24h',
                        't_2m:C': 'temperature',
                        't_max_2m_24h:C': 'max_temperature',
                        't_min_2m_24h:C': 'min_temperature',
                        'msl_pressure:hPa': 'pressure',
                        'precip_1h:mm': 'precipitation_1h',
                        'precip_24h:mm': 'precipitation_24h'
                    }

                    if parameter in parameter_to_field:
                        field_name = parameter_to_field[parameter]
                        date_data[date][field_name] = value

        # Insert data into the database
        # Loop through date_data and execute the insert/update query for each date
        for date, values in date_data.items():
            cursor.execute(
                """
                INSERT INTO weather_data (location_id, timestamp, wind_speed, wind_direction, wind_gusts_1h, wind_gusts_24h, 
                temperature, max_temperature, min_temperature, pressure, precipitation_1h, precipitation_24h)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (location_id, timestamp) DO UPDATE SET
                wind_speed = EXCLUDED.wind_speed,
                wind_direction = EXCLUDED.wind_direction,
                wind_gusts_1h = EXCLUDED.wind_gusts_1h,
                wind_gusts_24h = EXCLUDED.wind_gusts_24h,
                temperature = EXCLUDED.temperature,
                max_temperature = EXCLUDED.max_temperature,
                min_temperature = EXCLUDED.min_temperature,
                pressure = EXCLUDED.pressure,
                precipitation_1h = EXCLUDED.precipitation_1h,
                precipitation_24h = EXCLUDED.precipitation_24h;
                """,
                (
                    values['location_id'], values['date'], values['wind_speed'], values['wind_direction'],
                    values['wind_gusts_1h'], values['wind_gusts_24h'], values['temperature'], values['max_temperature'],
                    values['min_temperature'], values['pressure'], values['precipitation_1h'],
                    values['precipitation_24h']
                )
            )

    except (Exception, psycopg2.Error) as error:
        print(f"Error inserting weather data: {error}")


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
        latitude, longitude = map(float, location_coords.split(','))
        location_id = None

        # Check if the location already exists in the database
        cursor.execute("SELECT id FROM locations WHERE latitude = %s AND longitude = %s", (latitude, longitude))
        result = cursor.fetchone()

        if result:
            location_id = result[0]

        if weather_data:
            insert_weather_data(weather_data, location_id, cursor)

    conn.commit()
    print(f"Weather data inserted successfully!")

except (Exception, psycopg2.Error) as error:
    print(f"Error connecting to the database: {error}")

finally:
    if conn:
        conn.close()
