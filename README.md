# GraphHopper Enhanced Route Finder with Map UI

This Python project is an interactive route-finding tool that integrates the [GraphHopper API](https://www.graphhopper.com/) to calculate routes between two locations.  
It provides step-by-step directions, distance and duration summaries, real-time weather information, and an interactive map visualization powered by Folium.

---

## Features

- **Geocoding Integration** – Converts location names (e.g., "Batangas, Philippines") into coordinates using the GraphHopper Geocoding API.  
- **Route Calculation** – Computes optimal driving routes and provides travel distance and estimated time.  
- **Unit Conversion** – Displays results in kilometers or miles.  
- **Interactive CLI** – Colorized console interface using `colorama` for better readability.  
- **Formatted Output** – Tabulated results and clear step-by-step navigation instructions.  
- **Map Visualization** – Automatically generates an interactive HTML map (`route_map.html`) showing your route and markers for start and end points.  
- **File Saving Option** – Exports your route summary to `route_summary.txt`.  
- **Weather Integration (NEW)** – Fetches and displays current weather conditions (temperature, humidity, and description) for both the start and destination locations using the [OpenWeather API](https://openweathermap.org/api).  

---

## How It Works

1. The user inputs a start and destination location.  
2. The script uses the GraphHopper Geocoding API to retrieve latitude and longitude.  
3. The GraphHopper Routing API retrieves the optimal path, distance, and travel time.  
4. The OpenWeather API fetches real-time weather information for both locations.  
5. The program displays:
   - A formatted summary of distance, duration, and weather data  
   - Optional turn-by-turn navigation directions  
   - A generated `route_map.html` file with an interactive map visualization  

---

## Requirements

- Python 3.8+
- Install dependencies using:
```bash
pip install -r requirements.txt
