DROP DATABASE IF EXISTS meteo;

CREATE DATABASE meteo
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'English_United States.1252'
    LC_CTYPE = 'English_United States.1252'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;
	
CREATE TABLE IF NOT EXISTS locations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    latitude DECIMAL,
    longitude DECIMAL
);

CREATE TABLE IF NOT EXISTS weather_data (
    id SERIAL PRIMARY KEY,
    location_id INT,
    timestamp TIMESTAMP NOT NULL,
    wind_speed REAL,
    wind_direction REAL,
    wind_gusts_1h REAL,
    wind_gusts_24h REAL,
    temperature REAL,
    max_temperature REAL,
    min_temperature REAL,
    pressure REAL,
    precipitation_1h REAL,
    precipitation_24h REAL,
    FOREIGN KEY (location_id) REFERENCES locations (id),
    CONSTRAINT unique_location_timestamp UNIQUE (location_id, timestamp)
);