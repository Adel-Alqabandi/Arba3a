import socket
import threading
import json
import pickle
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import load_model
from datetime import datetime

# Initialising host address and port
HOST = "127.0.0.1" # Local host
PORT = 65432

# Loading in AI model, encoders, and scalers
model = load_model("model_files/model.keras")  # Keras model

with open("model_files/encoders.pkl", "rb") as f:
    encoders = pickle.load(f)

with open("model_files/scalers.pkl", "rb") as f:
    scalers = pickle.load(f)

# Columns used in AI model
predictor_cols = [
    "Origin Airport", "Destination Airport", "Carrier ID",
    "Month", "Day", "Hour", "Temperature", "Average Wind Speed", "Humidity", "Precipitation"
]

# Delay mapping for the AI output
delay_mapping = {
    0: "On Time",
    1: "Very Slight Delay (15 min)",
    2: "Minor Delay (30 min)",
    3: "Moderate Delay (60 min)",
    4: "Severe Delay (120 min)",
    5: "Extreme Delay (240 min)"
}

# Load airline name to code conversion file
airline_df = pd.read_csv("flight_data/airline_code_conversion.csv")
# Build a dictionary mapping airline name to airline code
airline_dict = dict(zip(airline_df["Description"], airline_df["Code"]))

# Function to process inputs and run AI
def preprocess_and_predict(flight_info):

    # Get month, day, and hour from user input
    dt = datetime.strptime(flight_info["date_time"], "%Y-%m-%d %H:%M")
    month, day, hour = dt.month, dt.day, dt.hour

    # Get the airline code from the CSV conversion file
    airline_name = flight_info["airline_name"]
    if airline_name not in airline_dict:
        raise ValueError(f"Airline name '{airline_name}' not found in airline_code_conversion.csv")
    carrier_id = airline_dict[airline_name]

    # Convert rain description into precipitation values
    precipitation_map = {
    "no rain": 0.0,
    "very light rain": 0.5,
    "light rain": 5.5,
    "moderate rain": 20.5,
    "heavy rain": 50.5,
    "very heavy rain": 110.5,
    "extremely heay rain": 151
    }
    rain = flight_info["rain"].lower()
    if rain not in precipitation_map:
        raise ValueError(f"Rain description '{rain}' not found.")
    precipitation = precipitation_map.get(rain, None)

    # Create dictionary of the input values
    raw_inputs = {
        "Origin Airport": flight_info["origin_airport"].strip().upper(),
        "Destination Airport": flight_info["destination_airport"].strip().upper(),
        "Carrier ID": carrier_id.strip().upper(),
        "Month": float(month),
        "Day": float(day),
        "Hour": float(hour),
        "Temperature": float(flight_info["temperature"]),
        "Average Wind Speed": float(flight_info["wind_speed"]),
        "Humidity": float(flight_info["humidity"]),
        "Precipitation": float(precipitation)
    }

    # Encode categorical columns and scale numeric columns
    processed = []
    for col in ["Origin Airport", "Destination Airport", "Carrier ID"]:
        encoder = encoders.get(col)
        if encoder is None:
            raise ValueError(f"No label encoder found for column '{col}'")
        encoded_val = encoder.transform([raw_inputs[col]])[0]
        processed.append(encoded_val)

    for col in ["Month", "Day", "Hour", "Temperature", "Average Wind Speed", "Humidity", "Precipitation"]:
        scaler = scalers.get(col)
        if scaler is None:
            raise ValueError(f"No scaler found for column '{col}'")
        scaled_val = scaler.transform(np.array([[raw_inputs[col]]]))[0][0]
        processed.append(scaled_val)

    X_input = np.array(processed).reshape(1, -1)

    # Predict using the AI model
    prediction_prob = model.predict(X_input)
    predicted_class = np.argmax(prediction_prob, axis=1)[0]
    predicted_category = delay_mapping.get(predicted_class, "Unknown")
    return predicted_category

# Function to return replies based on user input
def process_conversation(message):

    message_lower = message.lower().strip()
    if any(greet in message_lower for greet in ["hi", "hello", "hey"]):
        return "Hello! How may I assist you?"
    elif "delay" in message_lower and "flight" in message_lower:
        return "Please enter flight details to check delay status."
    elif "help" in message_lower:
        return "I can help you check flight delay status. Please enter your flight details when prompted."
    elif "thank" in message_lower:
        return "You're welcome!"
    else:
        return "I'm not sure I understand. Could you please rephrase?"

# Function to determine if user input is flight details or not (True/False)
def is_flight_detail_message(msg_dict):
    required_keys = {"origin_airport", "destination_airport", "airline_name", "date_time", 
                     "temperature", "wind_speed", "humidity", "rain"}
    return required_keys.issubset(set(msg_dict.keys()))

# Function to run commands based on conversation
def handle_client(conn, addr):
    print(f"[CONNECTED] {addr} joined.")
    
    # Send initial greeting
    welcome_msg = "Welcome to the Flight Delay Chatbot! This is Oracle. How may I assist you?"
    conn.send(welcome_msg.encode())
    
    # Enter conversation loop
    while True:
        try:
            data = conn.recv(4096).decode()
            if not data:
                continue  # If empty, continue waiting for data
            if data.lower().strip() == "exit":
                conn.send("Goodbye!".encode())
                break

            # Try to process message as JSON
            try:
                message_dict = json.loads(data)
                # Check if message_dict contains flight details
                if is_flight_detail_message(message_dict):
                    print(f"[REQUEST] From {addr}: {message_dict}")
                    try:
                        prediction = preprocess_and_predict(message_dict)
                        response = f"Predicted Flight Delay Category: {prediction}"
                    except Exception as e:
                        response = f"Error in prediction: {str(e)}"
                else:
                    # If valid JSON but not flight details, process it as conversation
                    response = process_conversation(data)
            except json.JSONDecodeError:
                # If not a JSON, then process as plain text conversation
                print(f"[CHAT] From {addr}: {data}")
                response = process_conversation(data)
            
            conn.send(response.encode())
        except Exception as e:
            print(f"[ERROR] {addr} encountered an error: {e}")
            break

    conn.close()
    print(f"[DISCONNECTED] {addr} left.")

# Main server operation
def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen(5)
        print(f"[LISTENING] Server running on {HOST}:{PORT}")

        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

if __name__ == "__main__":
    main()
