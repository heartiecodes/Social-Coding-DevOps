import pytest
from unittest.mock import patch
from graphhopper_route_finder_with_weather import geocode_location, get_weather, get_route, convert_distance, convert_time


# Mock responses
mock_geocode_response = {
    "hits": [{"point": {"lat": 51.5074, "lng": -0.1278}}]  # London coordinates
}

mock_weather_response = {
    "weather": [{"description": "clear sky"}],
    "main": {"temp": 15},
    "wind": {"speed": 5}
}

mock_route_response = {
    "paths": [{
        "distance": 10000,  # 10 km
        "time": 600000,  # 10 minutes
        "points": {"coordinates": [[51.5074, -0.1278], [51.5075, -0.128]]},
        "instructions": [{"text": "Head north", "distance": 100}]
    }]
}

# --- TEST CASES ---

# Test geocode_location function
@patch('requests.get')
def test_geocode_location(mock_get):
    mock_get.return_value.json.return_value = mock_geocode_response

    location = "London"
    coords = geocode_location(location)

    assert coords == (51.5074, -0.1278)  # Check if the coordinates match
    mock_get.assert_called_once_with("https://graphhopper.com/api/1/geocode", params={"q": location, "key": "c3945919-0050-4ab3-a9dd-cfb12550840f"})


# Test get_weather function
@patch('requests.get')
def test_get_weather(mock_get):
    mock_get.return_value.json.return_value = mock_weather_response

    coords = (51.5074, -0.1278)
    weather = get_weather(coords)

    assert weather == "Clear sky, 🌡 15°C, 💨 5 m/s"  # Check the weather format
    mock_get.assert_called_once_with("https://api.openweathermap.org/data/2.5/weather", params={
        "lat": coords[0],
        "lon": coords[1],
        "appid": "87cb9d15f966cafb9f2b21bb196354d5",
        "units": "metric"
    })


# Test get_route function
@patch('requests.get')
def test_get_route(mock_get):
    mock_get.return_value.json.return_value = mock_route_response

    start_coords = (51.5074, -0.1278)
    end_coords = (51.5075, -0.1280)
    vehicle = "car"
    
    route = get_route(start_coords, end_coords, vehicle)

    assert route["distance"] == 10000  # 10 km
    assert route["time"] == 600000  # 10 minutes
    assert len(route["points"]) == 2  # Two points in the route
    mock_get.assert_called_once_with("https://graphhopper.com/api/1/route", params={
        "point": ["51.5074,-0.1278", "51.5075,-0.1280"],
        "vehicle": vehicle,
        "locale": "en",
        "points_encoded": "false",
        "calc_points": "true",
        "key": "c3945919-0050-4ab3-a9dd-cfb12550840f"
    })


# Test convert_distance function
def test_convert_distance():
    distance_km, unit_label = convert_distance(10000, "km")
    distance_miles, _ = convert_distance(10000, "mi")

    assert distance_km == 10  # 10000 meters = 10 km
    assert unit_label == "km"
    assert distance_miles == 6.2137  # 10000 meters = 6.2137 miles


# Test convert_time function
def test_convert_time():
    time_str = convert_time(600000)  # 600000 ms = 10 minutes
    assert time_str == "10 minutes"

    time_str = convert_time(7200000)  # 7200000 ms = 2 hours
    assert time_str == "2h 0m"  # 2 hours


# Optional: Test create_map (Map creation isn't easy to test, but we can check if no errors occur)
@patch('folium.Map')
def test_create_map(mock_map):
    start_coords = (51.5074, -0.1278)
    end_coords = (51.5075, -0.1280)
    route_points = [[51.5074, -0.1278], [51.5075, -0.1280]]
    start_label = "Start"
    end_label = "End"
    start_weather = "Clear sky, 🌡 15°C, 💨 5 m/s"
    end_weather = "Clear sky, 🌡 16°C, 💨 4 m/s"
    vehicle = "car"

    # No assertion needed here, just ensure the method runs without error
    create_map(start_coords, end_coords, route_points, start_label, end_label, start_weather, end_weather, vehicle)
    mock_map.assert_called_once()

