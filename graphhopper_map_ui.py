# --- IMPORTS ---
import requests                      # Handles HTTP requests to the GraphHopper API
import folium                        # Used to create interactive route maps
from tabulate import tabulate         # For formatted terminal table display
from colorama import Fore, Style, init  # Adds colors and styles to terminal text output

# --- INITIALIZATION ---
init(autoreset=True)  # Automatically resets color after each print call to avoid color bleeding


# --- CONFIGURATION CONSTANTS ---
API_KEY = "c3945919-0050-4ab3-a9dd-cfb12550840f"            # GraphHopper API key
BASE_ROUTE_URL = "https://graphhopper.com/api/1/route"      # API endpoint for route data
GEOCODE_URL = "https://graphhopper.com/api/1/geocode"       # API endpoint for converting place names to coordinates


# --- FUNCTIONS ---

def geocode_location(location):
    """
    Convert a location name into its geographical coordinates (latitude, longitude)
    using the GraphHopper Geocoding API.

    Args:
        location (str): The name of the place (e.g., "Manila, Philippines").

    Returns:
        tuple or None: Returns (latitude, longitude) if successful, otherwise None.
    """
    try:
        # Send a GET request with the location name and API key
        response = requests.get(GEOCODE_URL, params={"q": location, "key": API_KEY})
        response.raise_for_status()  # Raises an exception if an HTTP error occurs
        data = response.json()

        # Extract the geocoding results
        hits = data.get("hits", [])
        if not hits:
            print(Fore.RED + f"❌ Could not find location: {location}")
            return None

        # Get the first match’s coordinates
        point = hits[0]["point"]
        return point["lat"], point["lng"]

    except requests.exceptions.RequestException as e:
        # Handle connection or response errors
        print(Fore.RED + f"Error in geocoding '{location}': {e}")
        return None


def get_route(start_coords, end_coords):
    """
    Retrieve the driving route information between two coordinates from GraphHopper.

    Args:
        start_coords (tuple): Start coordinates (latitude, longitude).
        end_coords (tuple): End coordinates (latitude, longitude).

    Returns:
        dict or None: Contains total distance, time, list of coordinates, and driving instructions.
    """
    # Define parameters for route request
    params = {
        "point": [f"{start_coords[0]},{start_coords[1]}", f"{end_coords[0]},{end_coords[1]}"],
        "vehicle": "car",              # Specifies transportation mode
        "locale": "en",                # Language for the directions
        "points_encoded": "false",     # Returns decoded coordinates (needed for Folium)
        "calc_points": "true",         # Enables coordinate calculation for route line
        "key": API_KEY                 # API key for authentication
    }

    try:
        # Send the API request and handle response
        response = requests.get(BASE_ROUTE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        # Parse route path data
        path = data["paths"][0]
        return {
            "distance": path["distance"],                # Distance in meters
            "time": path["time"],                        # Time in milliseconds
            "points": path["points"]["coordinates"],     # List of coordinates for map plotting
            "instructions": path.get("instructions", []) # Step-by-step navigation
        }

    except requests.exceptions.RequestException as e:
        # Handle network or API issues
        print(Fore.RED + f"Error fetching route: {e}")
        return None


def convert_distance(distance_m, unit):
    """
    Convert a distance in meters to either kilometers or miles.

    Args:
        distance_m (float): Distance in meters.
        unit (str): Measurement system ('km' or 'mi').

    Returns:
        tuple: (converted_distance, unit_label)
    """
    if unit == "mi":
        return distance_m / 1609.34, "miles"  # 1 mile = 1609.34 meters
    return distance_m / 1000, "km"            # Default conversion to kilometers


def convert_time(ms):
    """
    Convert a time duration from milliseconds to minutes.

    Args:
        ms (int): Duration in milliseconds.

    Returns:
        float: Duration in minutes (rounded to one decimal place).
    """
    return round(ms / (1000 * 60), 1)


def create_map(start_coords, end_coords, route_points, start_label, end_label):
    """
    Generate an interactive HTML map showing the route between two points using Folium.

    Args:
        start_coords (tuple): Starting coordinates (latitude, longitude).
        end_coords (tuple): Destination coordinates (latitude, longitude).
        route_points (list): List of (longitude, latitude) pairs forming the route.
        start_label (str): Name/label for start location.
        end_label (str): Name/label for destination.

    Returns:
        None: Creates and saves an HTML file named 'route_map.html'.
    """
    # Calculate the midpoint between start and end to center the map
    midpoint = [(start_coords[0] + end_coords[0]) / 2, (start_coords[1] + end_coords[1]) / 2]
    m = folium.Map(location=midpoint, zoom_start=9)

    # Add start and end markers
    folium.Marker(
        start_coords,
        popup=f"Start: {start_label}",
        icon=folium.Icon(color="green")
    ).add_to(m)
    folium.Marker(
        end_coords,
        popup=f"End: {end_label}",
        icon=folium.Icon(color="red")
    ).add_to(m)

    # Draw the route as a blue polyline on the map
    folium.PolyLine(
        locations=[(lat, lon) for lon, lat in route_points],  # Reverse order for Folium (lat, lon)
        color="blue",
        weight=5,
        opacity=0.8
    ).add_to(m)

    # Save the interactive map to an HTML file
    m.save("route_map.html")
    print(Fore.GREEN + "🗺️  Map created successfully! Open 'route_map.html' to view your route.\n")


# --- MAIN PROGRAM EXECUTION ---

def main():
    """
    Main function: runs the full route-finding workflow.
    Prompts user for input, fetches data from GraphHopper, and displays results.
    """
    print(Fore.CYAN + Style.BRIGHT + "\n🌍 === GraphHopper Enhanced Route Finder with Map UI === 🌍\n")

    # --- User Input Section ---
    start = input(Fore.YELLOW + "Enter start location (e.g., Batangas, Philippines): ")
    end = input(Fore.YELLOW + "Enter destination (e.g., Manila, Philippines): ")
    unit_choice = input(Fore.YELLOW + "Choose unit system (km/mi): ").lower().strip()

    # Validate distance unit input
    if unit_choice not in ["km", "mi"]:
        print(Fore.RED + "Invalid choice. Defaulting to kilometers.")
        unit_choice = "km"

    # --- Geocoding Step ---
    print(Fore.MAGENTA + "\n🔎 Getting coordinates...\n")
    start_coords = geocode_location(start)
    end_coords = geocode_location(end)

    if not start_coords or not end_coords:
        print(Fore.RED + "❌ Could not retrieve valid coordinates. Exiting.")
        return

    # --- Route Retrieval Step ---
    print(Fore.MAGENTA + "\n🛣️ Fetching route data, please wait...\n")
    route = get_route(start_coords, end_coords)
    if not route:
        return

    # --- Data Conversion for Readable Output ---
    distance_value, unit_label = convert_distance(route["distance"], unit_choice)
    duration_min = convert_time(route["time"])

    # --- Display Route Summary ---
    print(Fore.GREEN + Style.BRIGHT + "\n🚗 === ROUTE SUMMARY ===\n")
    table = [
        ["Start Location", start],
        ["Destination", end],
        ["Total Distance", f"{distance_value:.2f} {unit_label}"],
        ["Estimated Time", f"{duration_min} minutes"]
    ]
    print(tabulate(table, headers=["Property", "Value"], tablefmt="fancy_grid"))

    # --- Optional: Step-by-Step Driving Instructions ---
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

    # --- Generate and Save Interactive Map ---
    create_map(start_coords, end_coords, route["points"], start, end)

    # --- Optional: Save Route Summary to File ---
    save = input(Fore.YELLOW + "\n💾 Save route summary to file? (y/n): ").lower()
    if save == "y":
        with open("route_summary.txt", "w", encoding="utf-8") as f:
            f.write(tabulate(table, headers=["Property", "Value"], tablefmt="grid"))
        print(Fore.GREEN + "✅ Route summary saved as 'route_summary.txt'.")

    print(Fore.CYAN + "\n🌟 Thank you for using GraphHopper Enhanced Route Finder with Map UI! 🌟\n")


# --- ENTRY POINT CHECK ---
if __name__ == "__main__":
    main()
