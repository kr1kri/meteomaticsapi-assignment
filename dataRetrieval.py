import os
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta

USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')

BASE_URL = f"https://api.meteomatics.com/"

CURR_DT = (datetime.now() + timedelta(minutes=59 - datetime.now().minute, seconds=60-datetime.now().second)).strftime("%Y-%m-%dT%H:%M:%S")
END_DT = (datetime.now() + timedelta(days=7, minutes=59 - datetime.now().minute, seconds=60-datetime.now().second)).strftime("%Y-%m-%dT%H:%M:%S")

DELTA = "T1H"

locations = {
    "Athens": "37.983810,23.727539",
    "Thessaloniki": "40.629269,22.947412",
    "Patras": "38.246639,21.734573"
}

parameters = [
    "wind_speed_10m:ms",        # wind speed
    "wind_dir_10m:d",           # wind direction
    "wind_gusts_10m_1h:ms",     # wind gusts previous hour
    "wind_gusts_10m_24h:ms",    # wind gusts previous 24h
    "t_2m:C",                   # temperature
    "t_max_2m_24h:C",           # max temperature
    "t_min_2m_24h:C",           # min temperature
    "msl_pressure:hPa",         # pressure
    "precip_1h:mm",             # precipitation past hour
    "precip_24h:mm"             # precipitation past 24h
]

params = ','.join(parameters)

weather_data = []

for location_name, location_coords in locations.items():

    latitude, longitude = map(float, location_coords.split(','))

    url = f"{BASE_URL}{CURR_DT}Z--{END_DT}Z:P{DELTA}/{params}/{latitude},{longitude}/json?model=mix"
    response = requests.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD))

    if response.status_code == 200:
        try:
            data = response.json()
            print(f"Data retrieved successfully for {location_name}.")
            weather_data.append(data)
        except requests.exceptions.JSONDecodeError:
            print(f"JSON decoding error. The response content is not valid JSON.")
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
