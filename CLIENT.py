import socket
import json

# Initialise server host address and port
HOST = "16.171.254.190" # Public IPv4 address of the AWS instance
PORT = 65432

# Function that promts user for flights details and returns as JSON
def prompt_flight_details():
    origin_airport = input("Origin Airport (e.g., JFK): ")
    destination_airport = input("Destination Airport (e.g., LAX): ")
    airline_name = input("Airline Name (e.g., United Air Lines Inc.): ")
    date_time = input("Date & Time (YYYY-MM-DD HH:MM): ")
    temperature = input("Temperature (Celcius): ")
    wind_speed = input("Average Wind Speed (km/h): ")
    humidity = input("Humidity (percentage): ")
    rain = input("Rain Description (e.g., Light rain): ")

    data = {
        "origin_airport": origin_airport,
        "destination_airport": destination_airport,
        "airline_name": airline_name,
        "date_time": date_time,
        "temperature": temperature,
        "wind_speed": wind_speed,
        "humidity": humidity,
        "rain": rain
    }
    return json.dumps(data)

# Main function that sends and receives data from server
def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((HOST, PORT))
        
        # Receive and print initial greeting from server
        welcome = client.recv(4096).decode()
        print(f"\n[CHATBOT]: {welcome}")

        # Conversation loop
        while True:
            user_input = input("\n[USER]: ")
            if user_input.lower().strip() == "exit":
                client.send("exit".encode())
                break

            # Send user's message to the server
            client.send(user_input.encode())
            
            # Receive the server's response
            response = client.recv(4096).decode()
            print(f"\n[CHATBOT]: {response}")
            
            # Check if the response instructs to enter flight details
            if "enter flight details" in response.lower():
                # Prompt user for flight details and send as JSON
                flight_details_json = prompt_flight_details()
                client.send(flight_details_json.encode())
                
                # Receive and display prediction result
                prediction_response = client.recv(4096).decode()
                print(f"\n[CHATBOT]: {prediction_response}")
                
                # Ask if the user wants to continue the conversation
                cont = input("\n[CHATBOT]: Would you like to continue the conversation? (yes/no): ")
                if cont.lower().strip() != "yes":
                    client.send("exit".encode())
                    break
            # Otherwise, continue conversation with the server

    print("\n[CHATBOT]: Goodbye!")

if __name__ == "__main__":
    main()
