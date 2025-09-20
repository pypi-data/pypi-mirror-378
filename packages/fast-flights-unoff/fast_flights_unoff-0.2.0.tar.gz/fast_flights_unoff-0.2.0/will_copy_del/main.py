import json
from fast_flights_unoff import FlightData, Passengers, get_flights

# Load parameters from config.json
with open("config.json", "r") as f:
    config = json.load(f)

# Query using config.json values
result = get_flights(
    flight_data=[
        FlightData(
            date=config["date"],
            from_airport=config["from_airport"],
            to_airport=config["to_airport"],
        )
    ],
    trip=config["trip"],
    seat=config["seat"],
    passengers=Passengers(
        adults=config["passengers"]["adults"],
        children=config["passengers"]["children"],
        infants_in_seat=config["passengers"]["infants_in_seat"],
        infants_on_lap=config["passengers"]["infants_on_lap"],
    ),
    fetch_mode=config["fetch_mode"],
)

# Convert result into structured JSON
flights_data = []
for flight in result.flights:
    flights_data.append({
        "airline": flight.name,
        "flight_code": flight.flight_code,
        "departure": flight.departure,
        "arrival": flight.arrival,
        "duration": flight.duration,
        "stops": flight.stops,
        "price": flight.price,
        "is_best": flight.is_best,
        "arrival_time_ahead": getattr(flight, "arrival_time_ahead", None),
        "delay": getattr(flight, "delay", None),
    })

# Save to JSON file
with open("flights.json", "w", encoding="utf-8") as f:
    json.dump(flights_data, f, indent=4, ensure_ascii=False)

print(f"Saved {len(flights_data)} flights to flights.json")
