# --- IMPORTS ---
import requests                     # For making HTTP requests to the GraphHopper API
from tabulate import tabulate        # For formatting and displaying tables in the console
from colorama import Fore, Style, init  # For adding colored text output in the terminal

# --- INITIALIZE COLORAMA ---
init(autoreset=True)  # Automatically reset colors after each print statement

# --- CONFIGURATION ---
API_KEY = "c3945919-0050-4ab3-a9dd-cfb12550840f"  # GraphHopper API key
BASE_ROUTE_URL = "https://graphhopper.com/api/1/route"  # Base URL for routing API
GEOCODE_URL = "https://graphhopper.com/api/1/geocode"   # Base URL for geocoding API

# --- FUNCTIONS ---

def geocode_location(location):
    """
    Converts a textual location (e.g., 'Manila, Philippines')
    into geographical coordinates (latitude, longitude)
    using the GraphHopper Geocoding API.
    """
    try:
        # Send a GET request with location query and API key
        response = requests.get(GEOCODE_URL, params={"q": location, "key": API_KEY})
        response.raise_for_status()  # Raise an error if request failed
        data = response.json()

        # Extract geocoding results ('hits' list)
        hits = data.get("hits", [])
        if not hits:
            print(Fore.RED + f"❌ Could not find location: {location}")
            return None

        # Take the first result and return its coordinates
        point = hits[0]["point"]
        return point["lat"], point["lng"]

    except requests.exceptions.RequestException as e:
        # Handle network or API errors
        print(Fore.RED + f"Error in geocoding '{location}': {e}")
        return None


def get_route(start_coords, end_coords, unit="km"):
    """
    Fetches route information (distance, time, and directions)
    between two sets of coordinates using the GraphHopper Routing API.
    """
    params = {
        "point": [
            f"{start_coords[0]},{start_coords[1]}",
            f"{end_coords[0]},{end_coords[1]}"
        ],
        "vehicle": "car",         # Transport mode (car, bike, foot, etc.)
        "locale": "en",           # Language for directions
        "calc_points": "true",    # Whether to include route points in response
        "key": API_KEY            # API key for authentication
    }

    try:
        # Send request to the GraphHopper routing API
        response = requests.get(BASE_ROUTE_URL, params=params)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"Error fetching route: {e}")
        return None

    try:
        # Extract path information from the API response
        path = data["paths"][0]
        return {
            "distance": path["distance"],          # Distance in meters
            "time": path["time"],                  # Duration in milliseconds
            "instructions": path.get("instructions", [])  # Step-by-step directions
        }
    except (KeyError, IndexError):
        print(Fore.RED + "Invalid API response format.")
        return None


def convert_distance(distance_m, unit):
    """
    Converts distance from meters to kilometers or miles.
    Returns the converted value and unit label.
    """
    if unit == "mi":
        return distance_m / 1609.34, "miles"  # Convert meters to miles
    return distance_m / 1000, "km"            # Convert meters to kilometers


def convert_time(ms):
    """
    Converts time from milliseconds to minutes (rounded to 1 decimal place).
    """
    return round(ms / (1000 * 60), 1)


# --- MAIN PROGRAM ---

def main():
    """Main function: handles user input, API calls, and displaying results."""
    print(Fore.CYAN + "\n=== GraphHopper Route Finder ===\n")

    # --- USER INPUT ---
    start = input("Enter start location (e.g., Batangas, Philippines): ")
    end = input("Enter destination (e.g., Manila, Philippines): ")
    unit_choice = input("Choose unit system (km/mi): ").lower().strip()

    # Validate unit choice
    if unit_choice not in ["km", "mi"]:
        print(Fore.YELLOW + "Invalid choice. Defaulting to kilometers.")
        unit_choice = "km"

    print(Fore.MAGENTA + "\nFetching coordinates...\n")

    # Get coordinates for start and end locations
    start_coords = geocode_location(start)
    end_coords = geocode_location(end)

    # Stop if any location could not be found
    if not start_coords or not end_coords:
        print(Fore.RED + "❌ Could not retrieve valid coordinates. Exiting.")
        return

    print(Fore.MAGENTA + "\nFetching route data, please wait...\n")

    # Get routing data from API
    route = get_route(start_coords, end_coords, unit_choice)
    if not route:
        return

    # --- CONVERT AND DISPLAY SUMMARY ---
    distance_value, unit_label = convert_distance(route["distance"], unit_choice)
    duration_min = convert_time(route["time"])

    print(Fore.GREEN + "=== Route Summary ===")
    table = [
        ["Start", start],
        ["End", end],
        ["Distance", f"{distance_value:.2f} {unit_label}"],
        ["Estimated Time", f"{duration_min} minutes"]
    ]
    print(tabulate(table, headers=["Property", "Value"], tablefmt="fancy_grid"))

    # --- OPTIONAL: STEP-BY-STEP DIRECTIONS ---
    show_steps = input("\nShow step-by-step directions? (y/n): ").lower()
    if show_steps == "y":
        print(Fore.CYAN + "\n=== Directions ===")
        steps = []
        for step in route["instructions"]:
            text = step["text"]  # Instruction text
            dist = step["distance"]
            dist_val, dist_unit = convert_distance(dist, unit_choice)
            steps.append([text, f"{dist_val:.2f} {dist_unit}"])
        print(tabulate(steps, headers=["Instruction", "Distance"], tablefmt="grid"))

    print(Fore.CYAN + "\n=== Thank you for using GraphHopper Route Finder! ===\n")


# --- RUN PROGRAM ---
if __name__ == "__main__":
    main()
