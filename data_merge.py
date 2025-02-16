from meteostat import Hourly,Point
import pandas as pd
import numpy as np
from datetime import datetime
import csv

start = datetime(2023, 1, 1)
end = datetime(2024, 10, 31)

airports = {
"ATL" : Point(33.749, -84.388),
"DFW" : Point(32.7831, -96.8067),
"DEN" : Point(39.8667, -104.6667),
"LAX" : Point(34.0522, -118.2437),
"ORD" : Point(41.9833, -87.9167),
"JFK" : Point(40.7143, -74.006),
"MCO" : Point(28.4167, -81),
"LAS" : Point(36.1167, -115.2667),
"CLT" : Point(35.214, -80.9431),
"MIA" : Point(25.7833, -80.3167),
}

hourly_dict = {
    "time":"Date",
    "temp":"Temperature",
    "dwpt":"Dew Point",
    "rhum":"Humidity",
    "prcp":"Precipitation",
    "snow":"Snow",
    "wdir":"Wind Direction",
    "wspd":"Average Wind Speed",
    "wpgt":"Peak Wind Speed",
    "pres":"Air Pressure",
    "tsun":"Total Sun Hours",
    "coco":"Weather Condition Code",
}

flight_col_dictionary = {
    "FL_DATE" : "Flight Date",
    "OP_UNIQUE_CARRIER" : "Carrier ID",
    "ORIGIN":"Origin Airport",
    "ORIGIN_CITY_NAME": "Origin City",
    "DEST":"Destination Airport",
    "CRS_DEP_TIME":"CRS Scheduled departure time",
    "DEP_DELAY_NEW":"Departure Delay",
    "CARRIER_DELAY":"Carrier Delay",
    "WEATHER_DELAY":"Weather Delay",
    "NAS_DELAY":"National Air System Delay",
    "SECURITY_DELAY":"Security Delay",
    "LATE_AIRCRAFT_DELAY":"Late Aircraft Delay",
}

airports_top10 = ["ATL", "DFW", "DEN", "LAX", "ORD", "JFK", "MCO", "LAS", "CLT", "MIA"]

#Pull Meteostat data and save raw data to .csv
for airport, coordinates in airports.items():
    airport_data = Hourly(coordinates, start, end)
    weather_data = airport_data.fetch()
    print(airport, "saved to weather_datasets")
    weather_data.to_csv(f"weather_data/{airport}_weather_data.csv")

#read the weather data .csv's and save into a dictionary
weather_datasets = {}
for airport in list(airports.keys()):
    weather_data = pd.read_csv(f"weather_data/{airport}_weather_data.csv")
    weather_data = weather_data.reset_index(drop = True)
    weather_data = weather_data.rename(columns = hourly_dict)
    weather_data["Date"] = pd.to_datetime(weather_data["Date"], format = "%Y-%m-%d %H:%M:%S") 
    weather_datasets[airport] = weather_data

#Read raw flight data, concatonate, and filter on top 10 airports 
df_appended = []
for m in [23,24]:
    for n in range(1, 10):  
        if (m==24) and (n>10):
            pass
        else:
            df = pd.read_csv(f"flight_data/Departures {n}-{m}.csv")
            df_appended.append(df)
departure_data = pd.concat(df_appended, ignore_index=True)
departure_data_10 = departure_data[departure_data["ORIGIN"].isin(airports_top10)]

#rename
departure_data_10 = departure_data_10.rename(columns = flight_col_dictionary)

#standardise date time
departure_data_10["CRS Scheduled departure time"] = departure_data_10["CRS Scheduled departure time"].astype(str).str.zfill(4)
departure_data_10["Hour"] = departure_data_10["CRS Scheduled departure time"].str[:2]
departure_data_10["Minute"] = departure_data_10["CRS Scheduled departure time"].str[2:]
departure_data_10["Date"] = pd.to_datetime(departure_data_10["Flight Date"].astype(str) + " " + departure_data_10["Hour"] + ":" + departure_data_10["Minute"])
departure_data_10 = departure_data_10.drop(columns = ["Hour", "Minute", "CRS Scheduled departure time", "Flight Date"])

#rearrange columns and round date time
departure_data_10_1 = pd.concat([departure_data_10.iloc[:, -1:], departure_data_10.iloc[:, :-1]],axis=1)
departure_data_10_1["Date"] = departure_data_10_1["Date"].dt.round("H")  

#merge datasets on date, store in a list and concatonate
large = []
for i in airports_top10:
    sliced = departure_data_10_1[departure_data_10_1["Origin Airport"] == i]
    wd = weather_datasets[i]
    merger = pd.merge(sliced, wd, left_on = "Date", right_on = "Date", how="left")
    large.append(merger)


final_merged_data = pd.concat(large, ignore_index=True)

#save merged dataset to .csv
final_merged_data.to_csv("final_merged_data.csv", index=False)
