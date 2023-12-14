## Description

The purpose of this exercise was to:
1) Create a script that will retrieve the forecasts for any 3 locations and for a period of 7 days.
2) Store the retrieved data in a relational database.
3) Create an API that uses the retrieved data and provide endpoints for the following:
   1) List the latest forecast for each location for every day.
   2) List the average the_temp of the last 3 forecasts for each location for every day.
   3) Get the top n locations based on each available metric where n is a parameter given to the API call.
   

## Instructions

1) Install the required packages.
```
pip install -r requirements.txt
```

2) Create the database and the tables. For the purpose of the specific task, PostgreSQL database was used.
```
psql -U <username> -d <database> -a -f db_schema.sql
```

3) Add the locations in the database table
```
py insertLocationsDb.py
```

4) Run the created API.
```
py api.py
```

5) Once the API is up and running, you are able to send any requests available. More specifically, the available endpoints are:
     1) '/latest_forecast' : To list the latest forecast for each location for every day.
     2) '/average_temperature' : To list the average temperature of the last 3 forecasts for each location for every day.
     3) 'top_locations?top_n=<N>' : To get the top N locations based on each available metric. N parameter can be passed by the user.
  
