import pickle
import csv
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import MinMaxScaler

df = pd.read_csv("final_merged_data.csv")

# Replace all NaN values with 0
df.fillna(0, inplace=True)

# Seperate datetime column into multiple columns (should consider leaving year out as we're predicting future dates)
df["Date"] = pd.to_datetime(df["Date"])
df["Year"] = df["Date"].dt.year
df["Month"] = df["Date"].dt.month
df["Day"] = df["Date"].dt.day
df["Hour"] = df["Date"].dt.hour
df = df.drop("Date", axis=1)

# Encode text values by converting to integer IDs (will be used in embedding encoding layer in ml model)
encoders = {}  # Dictionary to store encoders
for col in ["Carrier ID", "Origin Airport", "Origin City", "Destination Airport"]:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    encoders[col] = le  # Store the encoder

# Saving encoders to disk to encode user inputs later
with open("encoders.pkl", "wb") as file:
    pickle.dump(encoders, file)

# Standardising integers values to range [0, 1]
int_col = ["Departure Delay", "Carrier Delay", "National Air System Delay", "Security Delay", 
            "Late Aircraft Delay", "Temperature", "Dew Point", "Humidity", 
            "Precipitation", "Snow", "Wind Direction", "Average Wind Speed",
            "Peak Wind Speed", "Air Pressure", "Total Sun Hours", "Weather Condition Code",
            "Year", "Month", "Day", "Hour"]

# Creating seperate scalers for each column. This is because we might decide to remove columns from ai input later on
scalers = {}
for i in int_col:
    scaler = MinMaxScaler()
    df[i] = scaler.fit_transform(df[[i]])
    scalers[i] = scaler

# Saving scalers
with open("scalers.pkl", "wb") as file:
    pickle.dump(scalers, file)

# Saving data to csv
df.to_csv("preprocessed_data.csv", index=False)