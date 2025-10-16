import requests
from tabulate import tabulate
from colorama import Fore, Style, init


init(autoreset=True)


API_KEY = "c3945919-0050-4ab3-a9dd-cfb12550840f"
BASE_ROUTE_URL = "https://graphhopper.com/api/1/route"
GEOCODE_URL = "https://graphhopper.com/api/1/geocode"



def geocode_location(location):
    """Convert location name into latitude and longitude using GraphHopper Geocoding API."""
    try:
        response = requests.get(GEOCODE_URL, params={"q": location, "key": API_KEY})
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


def get_route(start_coords, end_coords):
    """Retrieve route information between two coordinate points."""
    params = {
        "point": [f"{start_coords[0]},{start_coords[1]}", f"{end_coords[0]},{end_coords[1]}"],
        "vehicle": "car",
        "locale": "en",
        "calc_points": "true",
        "key": API_KEY
    }

    try:
        response = requests.get(BASE_ROUTE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        path = data["paths"][0]
        return {
            "distance": path["distance"],
            "time": path["time"],
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
    """Convert milliseconds to minutes."""
    return round(ms / (1000 * 60), 1)




def main():
    print(Fore.CYAN + Style.BRIGHT + "\n🌍 === GraphHopper Enhanced Route Finder === 🌍\n")

    
    start = input(Fore.YELLOW + "Enter start location (e.g., Batangas, Philippines): ")
    end = input(Fore.YELLOW + "Enter destination (e.g., Manila, Philippines): ")
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

    print(Fore.MAGENTA + "\n🛣️ Fetching route data, please wait...\n")
    route = get_route(start_coords, end_coords)
    if not route:
        return

    
    distance_value, unit_label = convert_distance(route["distance"], unit_choice)
    duration_min = convert_time(route["time"])

    
    print(Fore.GREEN + Style.BRIGHT + "\n🚗 === ROUTE SUMMARY ===\n")
    table = [
        ["Start Location", start],
        ["Destination", end],
        ["Total Distance", f"{distance_value:.2f} {unit_label}"],
        ["Estimated Time", f"{duration_min} minutes"]
    ]
    print(tabulate(table, headers=["Property", "Value"], tablefmt="fancy_grid"))

 
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

    
    save = input(Fore.YELLOW + "\n💾 Save route summary to file? (y/n): ").lower()
    if save == "y":
        with open("route_summary.txt", "w", encoding="utf-8") as f:
            f.write(tabulate(table, headers=["Property", "Value"], tablefmt="grid"))
        print(Fore.GREEN + "✅ Route summary saved as 'route_summary.txt'.")

    print(Fore.CYAN + "\n🌟 Thank you for using GraphHopper Enhanced Route Finder! 🌟\n")


if __name__ == "__main__":
    main()
