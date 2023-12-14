import os
import psycopg2
import subprocess
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS for the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_NAME = os.getenv('DB_NAME')

def get_connection():
    return psycopg2.connect(
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host="localhost",
        port="5433"
    )


@app.on_event("startup")
def insert_weather_data():
    # Execute the insertWeatherDataDb.py script as a subprocess
    result = subprocess.run(["py", "insertWeatherDataDb.py"], capture_output=True, text=True)
    # Check if the script ran successfully
    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=f"Error running the script: {result.stderr}")


@app.get("/latest_forecast")
def get_latest_forecast():
    try:
        # Retrieve the latest forecast
        conn = get_connection()
        cursor = conn.cursor()

        # SQL query to retrieve the latest forecast for each location for every day and every parameter
        query = """
            SELECT
                l.name as location_name,
                DATE(wd.timestamp) as forecast_date,
                wd.wind_speed,
                wd.wind_direction,
                wd.wind_gusts_1h,
                wd.wind_gusts_24h,
                wd.temperature,
                wd.max_temperature,
                wd.min_temperature,
                wd.pressure,
                wd.precipitation_1h,
                wd.precipitation_24h
            FROM locations as l
            INNER JOIN weather_data as wd
            ON l.id = wd.location_id
            INNER JOIN (
                SELECT
                    location_id,
                    MAX(timestamp) as timestamp
                FROM weather_data
                GROUP BY location_id, DATE(timestamp)
            ) as latest
            ON l.id = latest.location_id
            AND latest.timestamp = wd.timestamp
            ORDER BY l.id, forecast_date
        """
        cursor.execute(query)
        records = cursor.fetchall()

        response = []
        for record in records:
            location_name, forecast_date, *parameters = record
            response.append({
                "location_name": location_name,
                "forecast_date": forecast_date,
                "parameters": {
                    "wind_speed": parameters[0],
                    "wind_direction": parameters[1],
                    "wind_gusts_1h": parameters[2],
                    "wind_gusts_24h": parameters[3],
                    "temperature": parameters[4],
                    "max_temperature": parameters[5],
                    "min_temperature": parameters[6],
                    "pressure": parameters[7],
                    "precipitation_1h": parameters[8],
                    "precipitation_24h": parameters[9]
                }
            })

        return response

    except (Exception, psycopg2.Error) as error:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(error)}")

    finally:
        if conn:
            conn.close()


@app.get("/average_temperature")
def get_average_temperature():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # SQL query to calculate the average temperature of the last N forecasts for every day
        query = """
            WITH ranked_data AS (
              SELECT
                w.location_id,
                l.name AS location_name,
                w.timestamp,
                w.temperature,
                ROW_NUMBER() OVER (PARTITION BY w.location_id, DATE(w.timestamp) ORDER BY w.timestamp DESC) AS rn
              FROM weather_data w
              JOIN locations l ON w.location_id = l.id
            )
            SELECT
              location_name,
              DATE(timestamp) AS day,
              AVG(temperature) AS average_temperature
            FROM ranked_data
            WHERE rn <= 3
            GROUP BY location_name, DATE(timestamp)
            ORDER BY location_name, day;
        """
        cursor.execute(query, ())
        records = cursor.fetchall()

        response = [{"location_name": record[0], "forecast_date": record[1], "average_temperature": record[2]}
                    for record in records]

        conn.close()

        return response

    except (Exception, psycopg2.Error) as error:
        raise HTTPException(status_code=500, detail=f"Error calculating average temperature: {error}")


@app.get("/top_locations")
def get_top_locations(
    top_n: int = Query(..., description="Number of top locations to retrieve")
):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # SQL query to get the N top locations based on the maximum value of the specified parameter
        query = f"""
            WITH ranked_data AS (
              SELECT
                metric,
                location_id,
                l.name AS location_name,
                timestamp,
                value,
                ROW_NUMBER() OVER (PARTITION BY metric ORDER BY value DESC, timestamp DESC) AS rn
              FROM (
                SELECT
                  'wind_speed' AS metric, location_id, timestamp, wind_speed AS value
                FROM weather_data
                UNION ALL
                SELECT
                  'wind_direction' AS metric, location_id, timestamp, wind_direction AS value
                FROM weather_data
                UNION ALL
                SELECT
                  'wind_gusts_1h' AS metric, location_id, timestamp, wind_gusts_1h AS value
                FROM weather_data
                UNION ALL
                SELECT
                  'wind_gusts_24h' AS metric, location_id, timestamp, wind_gusts_24h AS value
                FROM weather_data
                UNION ALL
                SELECT
                  'temperature' AS metric, location_id, timestamp, temperature AS value
                FROM weather_data
                UNION ALL
                SELECT
                  'max_temperature' AS metric, location_id, timestamp, max_temperature AS value
                FROM weather_data
                UNION ALL
                SELECT
                  'min_temperature' AS metric, location_id, timestamp, min_temperature AS value
                FROM weather_data
                UNION ALL
                SELECT
                  'pressure' AS metric, location_id, timestamp, pressure AS value
                FROM weather_data
                UNION ALL
                SELECT
                  'precipitation_1h' AS metric, location_id, timestamp, precipitation_1h AS value
                FROM weather_data
                UNION ALL
                SELECT
                  'precipitation_24h' AS metric, location_id, timestamp, precipitation_24h AS value
                FROM weather_data
              ) combined_data
              JOIN locations l ON combined_data.location_id = l.id
            )
            SELECT
              metric,
              location_name,
              timestamp,
              value
            FROM ranked_data
            WHERE rn <= %s
            ORDER BY metric, rn;
        """
        cursor.execute(query, (top_n,))
        records = cursor.fetchall()

        response = [{"location_name": record[1], "forecast_date": record[2], "metric": record[0], "value": record[3]}
                    for record in records]

        return response

    except (Exception, psycopg2.Error) as error:
        raise HTTPException(status_code=500, detail=f"Error retrieving top locations: {error}")

    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

