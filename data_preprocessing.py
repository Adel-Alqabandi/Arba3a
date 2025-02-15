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

# Encode text values by converting to integer IDs
encoders = {}  # Dictionary to store encoders
for col in ["Carrier ID", "Origin Airport", "Origin City", "Destination Airport"]:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    encoders[col] = le  # Store the encoder

# Saving encoders to disk in case it's required later
import pickle
with open('encoders.pkl', 'wb') as file:
    pickle.dump(encoders, file)

# Standardising integers values
# Initialize the scaler
min_max_scaler = MinMaxScaler()

# Scale the columns to range [0, 1]
int_col = ["Departure Delay", "Carrier Delay", "National Air System Delay", "Security Delay", 
            "Late Aircraft Delay", "Temperature", "Dew Point", "Humidity", 
            "Precipitation", "Snow", "Wind Direction", "Average Wind Speed",
            "Peak Wind Speed", "Air Pressure", "Total Sun Hours", "Weather Condition Code"]

df[int_col] = min_max_scaler.fit_transform(df[int_col])

# Saving data to csv
df.to_csv("preprocessed_data.csv")