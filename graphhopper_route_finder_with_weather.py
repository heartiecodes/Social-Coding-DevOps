import requests
import folium
from tabulate import tabulate
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# --- CONFIGURATION ---
GRAPH_API_KEY = "c3945919-0050-4ab3-a9dd-cfb12550840f"
WEATHER_API_KEY = "87cb9d15f966cafb9f2b21bb196354d5"  # OpenWeatherMap API key

BASE_ROUTE_URL = "https://graphhopper.com/api/1/route"
GEOCODE_URL = "https://graphhopper.com/api/1/geocode"
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

# --- FUNCTIONS ---

def geocode_location(location):
    """Convert location name into latitude and longitude using GraphHopper Geocoding API."""
    try:
        response = requests.get(GEOCODE_URL, params={"q": location, "key": GRAPH_API_KEY})
        response.raise_for_status()
        data = response.json()
        hits = data.get("hits", [])
        if not hits:
            print(Fore.RED + f"❌ Could not find location: {location}")
            return None
        point = hits[0]["point"]
        return point["lat"], point["lng"]
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"Error in geocoding '{location}': {e}")
        return None


def get_weather(coords):
    """Fetch current weather info using OpenWeatherMap API."""
    lat, lon = coords
    try:
        response = requests.get(WEATHER_URL, params={
            "lat": lat,
            "lon": lon,
            "appid": WEATHER_API_KEY,
            "units": "metric"
        })
        response.raise_for_status()
        data = response.json()
        weather = data["weather"][0]["description"].capitalize()
        temp = data["main"]["temp"]
        wind = data["wind"]["speed"]
        return f"{weather}, 🌡 {temp}°C, 💨 {wind} m/s"
    except requests.exceptions.RequestException as e:
        print(Fore.YELLOW + f"⚠️ Weather fetch error: {e}")
        return "Weather data unavailable"


def get_route(start_coords, end_coords, vehicle):
    """Retrieve route information between two coordinate points."""
    params = {
        "point": [f"{start_coords[0]},{start_coords[1]}", f"{end_coords[0]},{end_coords[1]}"],
        "vehicle": vehicle,
        "locale": "en",
        "points_encoded": "false",
        "calc_points": "true",
        "key": GRAPH_API_KEY
    }

    try:
        response = requests.get(BASE_ROUTE_URL, params=params)
        response.raise_for_status()
        data = response.json()
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
    """Convert meters to kilometers or miles."""
    if unit == "mi":
        return distance_m / 1609.34, "miles"
    return distance_m / 1000, "km"


def convert_time(ms):
    """Convert milliseconds to hours and minutes."""
    minutes = ms / (1000 * 60)
    hours = int(minutes // 60)
    mins = int(minutes % 60)
    return f"{hours}h {mins}m" if hours else f"{mins} minutes"


def create_map(start_coords, end_coords, route_points, start_label, end_label, start_weather, end_weather, vehicle):
    """Generate an interactive map using Folium with weather info."""
    midpoint = [(start_coords[0] + end_coords[0]) / 2, (start_coords[1] + end_coords[1]) / 2]
    m = folium.Map(location=midpoint, zoom_start=6, control_scale=True)

    # Add start and end markers with weather info
    folium.Marker(
        start_coords,
        popup=f"<b>Start:</b> {start_label}<br><b>Weather:</b> {start_weather}",
        icon=folium.Icon(color="green", icon="play")
    ).add_to(m)

    folium.Marker(
        end_coords,
        popup=f"<b>End:</b> {end_label}<br><b>Weather:</b> {end_weather}",
        icon=folium.Icon(color="red", icon="flag")
    ).add_to(m)

    # Add route polyline
    folium.PolyLine(
        locations=[(lat, lon) for lon, lat in route_points],
        color="blue",
        weight=5,
        opacity=0.8,
        tooltip=f"Route for {vehicle.capitalize()}"
    ).add_to(m)

    m.save("route_map.html")
    print(Fore.GREEN + "🗺️  Map with weather info created successfully! Open 'route_map.html' to view your route.\n")


# --- MAIN PROGRAM ---

def main():
    print(Fore.CYAN + Style.BRIGHT + "\n🌍 === International Route & Weather Finder === 🌍\n")

    # User Inputs
    start = input(Fore.YELLOW + "Enter start location (e.g., Tokyo, Japan): ")
    end = input(Fore.YELLOW + "Enter destination (e.g., Osaka, Japan): ")

    # Vehicle selection
    print(Fore.CYAN + "\nChoose your mode of transportation:")
    print(Fore.MAGENTA + "1. Car\n2. Motorcycle\n3. Foot")
    vehicle_choice = input(Fore.YELLOW + "Enter choice (1/2/3): ").strip()
    vehicle_map = {"1": "car", "2": "motorcycle", "3": "foot"}
    vehicle = vehicle_map.get(vehicle_choice, "car")

    # Unit selection
    unit_choice = input(Fore.YELLOW + "Choose unit system (km/mi): ").lower().strip()
    if unit_choice not in ["km", "mi"]:
        print(Fore.RED + "Invalid choice. Defaulting to kilometers.")
        unit_choice = "km"

    print(Fore.MAGENTA + "\n🔎 Getting coordinates...\n")
    start_coords = geocode_location(start)
    end_coords = geocode_location(end)
    if not start_coords or not end_coords:
        print(Fore.RED + "❌ Could not retrieve valid coordinates. Exiting.")
        return

    # Fetch weather for both points
    print(Fore.CYAN + "\n🌦 Fetching weather information...\n")
    start_weather = get_weather(start_coords)
    end_weather = get_weather(end_coords)

    # Fetch route
    print(Fore.MAGENTA + "\n🛣️ Fetching route data, please wait...\n")
    route = get_route(start_coords, end_coords, vehicle)
    if not route:
        return

    # Convert and display data
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

    # Step-by-Step Directions
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

    # Create map with weather popups
    create_map(start_coords, end_coords, route["points"], start, end, start_weather, end_weather, vehicle)

    # Save summary to file
    save = input(Fore.YELLOW + "\n💾 Save route summary to file? (y/n): ").lower()
    if save == "y":
        with open("route_summary.txt", "w", encoding="utf-8") as f:
            f.write(tabulate(table, headers=["Property", "Value"], tablefmt="grid"))
        print(Fore.GREEN + "✅ Route summary saved as 'route_summary.txt'.")

    print(Fore.CYAN + "\n🌟 Thank you for using the International Route & Weather Finder! 🌟\n")


if __name__ == "__main__":
    main()
