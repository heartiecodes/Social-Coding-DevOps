# ==============================================================================================
# DEVS - GEOTRAVEL
# Gets coordinates for start and destination, calculates routes with distance, - JUSTIN
# time, and optional step-by-step directions, and displays results. - JUSTIN
# Supports kilometers or miles and allows saving summaries to a text file. - JUSTIN
# Provides a clear, interactive terminal experience for route planning. - JUSTIN

# Overall, the application itself has functioning purposes from start to finish. It just - RICCI
# needs a GUI rather than processing through the terminal. - RICCI
# ==============================================================================================



# --- IMPORTS ---
import requests                     # Used to send HTTP requests to the GraphHopper API
from tabulate import tabulate        # Used to display data in formatted tables in the terminal
from colorama import Fore, Style, init  # Used to add colored and styled text outputs for better UX

# --- INITIALIZE COLOR OUTPUT ---
init(autoreset=True)  # Ensures colors reset automatically after each print to avoid color bleeding


# --- CONFIGURATION CONSTANTS ---
API_KEY = "c3945919-0050-4ab3-a9dd-cfb12550840f"           # Your GraphHopper API key for authentication
BASE_ROUTE_URL = "https://graphhopper.com/api/1/route"     # Endpoint for route calculations
GEOCODE_URL = "https://graphhopper.com/api/1/geocode"      # Endpoint for location name to coordinates lookup


# --- FUNCTIONS ---

def geocode_location(location):
    """
    Converts a given location name into geographical coordinates (latitude, longitude)
    using the GraphHopper Geocoding API.

    Args:
        location (str): The name of the place to look up (e.g., "Manila, Philippines").

    Returns:
        tuple or None: Returns (latitude, longitude) if found, otherwise None.
    """
    try:
        # Send GET request with the location query and API key
        response = requests.get(GEOCODE_URL, params={"q": location, "key": API_KEY})
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()

        # Extract results from response
        hits = data.get("hits", [])
        if not hits:
            print(Fore.RED + f"❌ Could not find location: {location}")
            return None

        # Retrieve the coordinates (latitude & longitude) of the first result
        point = hits[0]["point"]
        return point["lat"], point["lng"]

    except requests.exceptions.RequestException as e:
        # Handle network or API request failures
        print(Fore.RED + f"Error in geocoding '{location}': {e}")
        return None


def get_route(start_coords, end_coords):
    """
    Retrieves route information (distance, time, and step-by-step directions)
    between two geographical coordinates using the GraphHopper Routing API.

    Args:
        start_coords (tuple): Starting point (latitude, longitude)
        end_coords (tuple): Destination point (latitude, longitude)

    Returns:
        dict or None: Contains route 'distance', 'time', and 'instructions' if successful.
    """
    # Parameters to send with the API request
    params = {
        "point": [f"{start_coords[0]},{start_coords[1]}", f"{end_coords[0]},{end_coords[1]}"],
        "vehicle": "car",          # Mode of transport (car, bike, foot, etc.)
        "locale": "en",            # Language of directions
        "calc_points": "true",     # Whether to include geometry/points in response
        "key": API_KEY             # API key for access
    }

    try:
        # Send the route request to GraphHopper
        response = requests.get(BASE_ROUTE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        # Parse route information from the first path in response
        path = data["paths"][0]
        return {
            "distance": path["distance"],                # Distance in meters
            "time": path["time"],                        # Duration in milliseconds
            "instructions": path.get("instructions", []) # Turn-by-turn directions
        }

    except requests.exceptions.RequestException as e:
        # Handle connectivity or server issues
        print(Fore.RED + f"Error fetching route: {e}")
        return None


def convert_distance(distance_m, unit):
    """
    Converts a distance from meters to kilometers or miles.

    Args:
        distance_m (float): Distance in meters.
        unit (str): 'km' for kilometers, 'mi' for miles.

    Returns:
        tuple: (converted_distance, unit_label)
    """
    if unit == "mi":
        return distance_m / 1609.34, "miles"  # Convert meters to miles
    return distance_m / 1000, "km"            # Default conversion to kilometers


def convert_time(ms):
    """
    Converts a time duration from milliseconds to minutes.

    Args:
        ms (int): Time in milliseconds.

    Returns:
        float: Time in minutes, rounded to one decimal place.
    """
    return round(ms / (1000 * 60), 1)


# --- MAIN PROGRAM LOGIC ---

def main():
    """Main entry point for the Enhanced Route Finder app."""
    print(Fore.CYAN + Style.BRIGHT + "\n🌍 === GraphHopper Enhanced Route Finder === 🌍\n")

    # --- USER INPUT SECTION ---
    start = input(Fore.YELLOW + "Enter start location (e.g., Batangas, Philippines): ")
    end = input(Fore.YELLOW + "Enter destination (e.g., Manila, Philippines): ")
    unit_choice = input(Fore.YELLOW + "Choose unit system (km/mi): ").lower().strip()

    # Validate unit system input
    if unit_choice not in ["km", "mi"]:
        print(Fore.RED + "Invalid choice. Defaulting to kilometers.")
        unit_choice = "km"

    print(Fore.MAGENTA + "\n🔎 Getting coordinates...\n")

    # --- GEOCODING LOCATIONS ---
    start_coords = geocode_location(start)
    end_coords = geocode_location(end)

    # Check if valid coordinates were found
    if not start_coords or not end_coords:
        print(Fore.RED + "❌ Could not retrieve valid coordinates. Exiting.")
        return

    print(Fore.MAGENTA + "\n🛣️ Fetching route data, please wait...\n")

    # --- FETCH ROUTE DATA ---
    route = get_route(start_coords, end_coords)
    if not route:
        return

    # --- CONVERT DATA FOR DISPLAY ---
    distance_value, unit_label = convert_distance(route["distance"], unit_choice)
    duration_min = convert_time(route["time"])

    # --- DISPLAY ROUTE SUMMARY ---
    print(Fore.GREEN + Style.BRIGHT + "\n🚗 === ROUTE SUMMARY ===\n")
    table = [
        ["Start Location", start],
        ["Destination", end],
        ["Total Distance", f"{distance_value:.2f} {unit_label}"],
        ["Estimated Time", f"{duration_min} minutes"]
    ]
    print(tabulate(table, headers=["Property", "Value"], tablefmt="fancy_grid"))

    # --- OPTIONAL STEP-BY-STEP DIRECTIONS ---
    show_steps = input(Fore.CYAN + "\nWould you like to see step-by-step directions? (y/n): ").lower()
    if show_steps == "y":
        print(Fore.BLUE + Style.BRIGHT + "\n🧭 === Step-by-Step Directions ===\n")
        steps = []
        for step in route["instructions"]:
            text = step["text"]  # Instruction (e.g., "Turn left onto Main Street")
            dist = step["distance"]
            dist_val, dist_unit = convert_distance(dist, unit_choice)
            steps.append([text, f"{dist_val:.2f} {dist_unit}"])
        print(tabulate(steps, headers=["Instruction", "Distance"], tablefmt="grid"))

    # --- OPTIONAL SAVE FEATURE ---
    save = input(Fore.YELLOW + "\n💾 Save route summary to file? (y/n): ").lower()
    if save == "y":
        # Save the summary table to a text file
        with open("route_summary.txt", "w", encoding="utf-8") as f:
            f.write(tabulate(table, headers=["Property", "Value"], tablefmt="grid"))
        print(Fore.GREEN + "✅ Route summary saved as 'route_summary.txt'.")

    print(Fore.CYAN + "\n🌟 Thank you for using GraphHopper Enhanced Route Finder! 🌟\n")


# --- PROGRAM ENTRY POINT ---
if __name__ == "__main__":
    main()


