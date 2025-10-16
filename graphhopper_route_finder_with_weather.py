import requests
import folium
from tabulate import tabulate
from colorama import Fore, Style, init

# Initialize colorama to automatically reset color styles after each print
init(autoreset=True)

# --- CONFIGURATION SECTION ---
# API keys for GraphHopper (routing & geocoding) and OpenWeatherMap (weather data)
GRAPH_API_KEY = "c3945919-0050-4ab3-a9dd-cfb12550840f"
WEATHER_API_KEY = "87cb9d15f966cafb9f2b21bb196354d5"

# Base URLs for each API service
BASE_ROUTE_URL = "https://graphhopper.com/api/1/route"
GEOCODE_URL = "https://graphhopper.com/api/1/geocode"
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


# --- FUNCTION DEFINITIONS ---

def geocode_location(location):
    """Convert a location name into its latitude and longitude using GraphHopper Geocoding API."""
    try:
        # Send GET request to the GraphHopper Geocoding API
        response = requests.get(GEOCODE_URL, params={"q": location, "key": GRAPH_API_KEY})
        response.raise_for_status()
        data = response.json()
        
        # Extract the first matching location ("hit")
        hits = data.get("hits", [])
        if not hits:
            print(Fore.RED + f"❌ Could not find location: {location}")
            return None
        
        # Return coordinates (latitude, longitude)
        point = hits[0]["point"]
        return point["lat"], point["lng"]
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"Error in geocoding '{location}': {e}")
        return None


def get_weather(coords):
    """Retrieve current weather data for given coordinates using OpenWeatherMap API."""
    lat, lon = coords
    try:
        # Send GET request to OpenWeatherMap API
        response = requests.get(WEATHER_URL, params={
            "lat": lat,
            "lon": lon,
            "appid": WEATHER_API_KEY,
            "units": "metric"
        })
        response.raise_for_status()
        data = response.json()

        # Extract weather details
        weather = data["weather"][0]["description"].capitalize()
        temp = data["main"]["temp"]
        wind = data["wind"]["speed"]

        # Return formatted weather string
        return f"{weather}, 🌡 {temp}°C, 💨 {wind} m/s"
    except requests.exceptions.RequestException as e:
        print(Fore.YELLOW + f"⚠️ Weather fetch error: {e}")
        return "Weather data unavailable"


def get_route(start_coords, end_coords, vehicle):
    """Retrieve route information between two coordinates using GraphHopper Routing API."""
    params = {
        "point": [f"{start_coords[0]},{start_coords[1]}", f"{end_coords[0]},{end_coords[1]}"],
        "vehicle": vehicle,           # travel mode: car, motorcycle, or foot
        "locale": "en",               # response language
        "points_encoded": "false",    # ensure coordinates are in readable format
        "calc_points": "true",
        "key": GRAPH_API_KEY
    }

    try:
        response = requests.get(BASE_ROUTE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        # Extract route data such as distance, duration, path, and step-by-step instructions
        path = data["paths"][0]
        return {
            "distance": path["distance"],
            "time": path["time"],
            "points": path["points"]["coordinates"],
            "instructions": path.get("instructions", [])
        }
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"Error fetching route: {e}")
        return None


def convert_distance(distance_m, unit):
    """Convert distance in meters to kilometers or miles based on chosen unit."""
    if unit == "mi":
        return distance_m / 1609.34, "miles"  # meters to miles
    return distance_m / 1000, "km"            # meters to kilometers


def convert_time(ms):
    """Convert duration from milliseconds to hours and minutes format."""
    minutes = ms / (1000 * 60)
    hours = int(minutes // 60)
    mins = int(minutes % 60)
    return f"{hours}h {mins}m" if hours else f"{mins} minutes"


def create_map(start_coords, end_coords, route_points, start_label, end_label, start_weather, end_weather, vehicle):
    """Generate and save an interactive route map using Folium with weather info at start and end points."""
    # Compute midpoint to center the map
    midpoint = [(start_coords[0] + end_coords[0]) / 2, (start_coords[1] + end_coords[1]) / 2]
    m = folium.Map(location=midpoint, zoom_start=6, control_scale=True)

    # Add marker for the starting point
    folium.Marker(
        start_coords,
        popup=f"<b>Start:</b> {start_label}<br><b>Weather:</b> {start_weather}",
        icon=folium.Icon(color="green", icon="play")
    ).add_to(m)

    # Add marker for the destination point
    folium.Marker(
        end_coords,
        popup=f"<b>End:</b> {end_label}<br><b>Weather:</b> {end_weather}",
        icon=folium.Icon(color="red", icon="flag")
    ).add_to(m)

    # Draw the route line connecting start and end coordinates
    folium.PolyLine(
        locations=[(lat, lon) for lon, lat in route_points],
        color="blue",
        weight=5,
        opacity=0.8,
        tooltip=f"Route for {vehicle.capitalize()}"
    ).add_to(m)

    # Save the map as an HTML file
    m.save("route_map.html")
    print(Fore.GREEN + "🗺️  Map with weather info created successfully! Open 'route_map.html' to view your route.\n")


# --- MAIN EXECUTION FLOW ---

def main():
    print(Fore.CYAN + Style.BRIGHT + "\n🌍 === International Route & Weather Finder === 🌍\n")

    # --- Step 1: User Input for locations ---
    start = input(Fore.YELLOW + "Enter start location (e.g., Tokyo, Japan): ")
    end = input(Fore.YELLOW + "Enter destination (e.g., Osaka, Japan): ")

    # --- Step 2: Choose mode of transport ---
    print(Fore.CYAN + "\nChoose your mode of transportation:")
    print(Fore.MAGENTA + "1. Car\n2. Motorcycle\n3. Foot")
    vehicle_choice = input(Fore.YELLOW + "Enter choice (1/2/3): ").strip()
    vehicle_map = {"1": "car", "2": "motorcycle", "3": "foot"}
    vehicle = vehicle_map.get(vehicle_choice, "car")  # default to car

    # --- Step 3: Choose unit system ---
    unit_choice = input(Fore.YELLOW + "Choose unit system (km/mi): ").lower().strip()
    if unit_choice not in ["km", "mi"]:
        print(Fore.RED + "Invalid choice. Defaulting to kilometers.")
        unit_choice = "km"

    # --- Step 4: Convert locations to coordinates ---
    print(Fore.MAGENTA + "\n🔎 Getting coordinates...\n")
    start_coords = geocode_location(start)
    end_coords = geocode_location(end)
    if not start_coords or not end_coords:
        print(Fore.RED + "❌ Could not retrieve valid coordinates. Exiting.")
        return

    # --- Step 5: Fetch weather data for both points ---
    print(Fore.CYAN + "\n🌦 Fetching weather information...\n")
    start_weather = get_weather(start_coords)
    end_weather = get_weather(end_coords)

    # --- Step 6: Fetch route information ---
    print(Fore.MAGENTA + "\n🛣️ Fetching route data, please wait...\n")
    route = get_route(start_coords, end_coords, vehicle)
    if not route:
        return

    # --- Step 7: Display summarized route info ---
    distance_value, unit_label = convert_distance(route["distance"], unit_choice)
    duration = convert_time(route["time"])

    print(Fore.GREEN + Style.BRIGHT + "\n🚗 === ROUTE SUMMARY ===\n")
    table = [
        ["Start Location", start],
        ["Destination", end],
        ["Vehicle Type", vehicle.capitalize()],
        ["Total Distance", f"{distance_value:.2f} {unit_label}"],
        ["Estimated Time", duration],
        ["Start Weather", start_weather],
        ["End Weather", end_weather]
    ]
    print(tabulate(table, headers=["Property", "Value"], tablefmt="fancy_grid"))

    # --- Step 8: Optional detailed step-by-step directions ---
    show_steps = input(Fore.CYAN + "\nWould you like to see step-by-step directions? (y/n): ").lower()
    if show_steps == "y":
        print(Fore.BLUE + Style.BRIGHT + "\n🧭 === Step-by-Step Directions ===\n")
        steps = []
        for step in route["instructions"]:
            text = step["text"]
            dist = step["distance"]
            dist_val, dist_unit = convert_distance(dist, unit_choice)
            steps.append([text, f"{dist_val:.2f} {dist_unit}"])
        print(tabulate(steps, headers=["Instruction", "Distance"], tablefmt="grid"))

    # --- Step 9: Create map visualization with weather info ---
    create_map(start_coords, end_coords, route["points"], start, end, start_weather, end_weather, vehicle)

    # --- Step 10: Optional summary file export ---
    save = input(Fore.YELLOW + "\n💾 Save route summary to file? (y/n): ").lower()
    if save == "y":
        with open("route_summary.txt", "w", encoding="utf-8") as f:
            f.write(tabulate(table, headers=["Property", "Value"], tablefmt="grid"))
        print(Fore.GREEN + "✅ Route summary saved as 'route_summary.txt'.")

    print(Fore.CYAN + "\n🌟 Thank you for using the International Route & Weather Finder! 🌟\n")


# Run the main program
if __name__ == "__main__":
    main()
