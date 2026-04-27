"""
Airport Finder - Find the closest airport to a given location.
Supports user input and CSV file input.
"""

import math
import csv
import sys
from typing import Tuple, List, Dict, Optional

# Sample airport database (IATA code, name, latitude, longitude)
AIRPORTS = [
    {"code": "JFK", "name": "John F. Kennedy International Airport", "lat": 40.6413, "lon": -73.7781},
    {"code": "LAX", "name": "Los Angeles International Airport", "lat": 33.9425, "lon": -118.4081},
    {"code": "ORD", "name": "O'Hare International Airport", "lat": 41.9742, "lon": -87.9073},
    {"code": "DFW", "name": "Dallas/Fort Worth International Airport", "lat": 32.8998, "lon": -97.0403},
    {"code": "DEN", "name": "Denver International Airport", "lat": 39.8561, "lon": -104.6737},
    {"code": "SFO", "name": "San Francisco International Airport", "lat": 37.6213, "lon": -122.3790},
    {"code": "SEA", "name": "Seattle-Tacoma International Airport", "lat": 47.4502, "lon": -122.3088},
    {"code": "ATL", "name": "Hartsfield-Jackson Atlanta International Airport", "lat": 33.6407, "lon": -84.4277},
    {"code": "BOS", "name": "Boston Logan International Airport", "lat": 42.3656, "lon": -71.0096},
    {"code": "MIA", "name": "Miami International Airport", "lat": 25.7959, "lon": -80.2870},
    {"code": "LHR", "name": "London Heathrow Airport", "lat": 51.4700, "lon": -0.4543},
    {"code": "CDG", "name": "Paris Charles de Gaulle Airport", "lat": 49.0097, "lon": 2.5479},
    {"code": "NRT", "name": "Tokyo Narita International Airport", "lat": 35.7720, "lon": 140.3929},
    {"code": "SYD", "name": "Sydney Kingsford Smith Airport", "lat": -33.9399, "lon": 151.1753},
    {"code": "DXB", "name": "Dubai International Airport", "lat": 25.2532, "lon": 55.3657},
]


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on Earth using the Haversine formula.
    
    Args:
        lat1: Latitude of point 1 in degrees
        lon1: Longitude of point 1 in degrees
        lat2: Latitude of point 2 in degrees
        lon2: Longitude of point 2 in degrees
    
    Returns:
        Distance in kilometers
    """
    # Earth's radius in kilometers
    R = 6371.0
    
    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return distance


def find_closest_airport(lat: float, lon: float, airports: List[Dict] = None) -> Tuple[Dict, float]:
    """
    Find the closest airport to a given location.
    
    Args:
        lat: Latitude of the location
        lon: Longitude of the location
        airports: Optional list of airports to search (defaults to AIRPORTS)
    
    Returns:
        Tuple of (airport dict, distance in km)
    """
    if airports is None:
        airports = AIRPORTS
    
    if not airports:
        raise ValueError("Airport list cannot be empty")
    
    closest_airport = None
    min_distance = float('inf')
    
    for airport in airports:
        distance = haversine_distance(lat, lon, airport["lat"], airport["lon"])
        if distance < min_distance:
            min_distance = distance
            closest_airport = airport
    
    return closest_airport, min_distance


def process_csv_file(filepath: str) -> List[Dict]:
    """
    Process a CSV file containing locations and find closest airports.
    
    CSV format expected: name,latitude,longitude
    
    Args:
        filepath: Path to the CSV file
    
    Returns:
        List of results with location info and closest airport
    """
    results = []
    
    with open(filepath, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            try:
                name = row.get('name', 'Unknown')
                lat = float(row['latitude'])
                lon = float(row['longitude'])
                
                airport, distance = find_closest_airport(lat, lon)
                
                results.append({
                    "location_name": name,
                    "latitude": lat,
                    "longitude": lon,
                    "closest_airport": airport,
                    "distance_km": round(distance, 2)
                })
            except (KeyError, ValueError) as e:
                print(f"Warning: Skipping invalid row: {row}. Error: {e}")
    
    return results


def get_user_input() -> Tuple[float, float]:
    """
    Get latitude and longitude from user input.
    
    Returns:
        Tuple of (latitude, longitude)
    """
    while True:
        try:
            lat_input = input("Enter latitude (-90 to 90): ").strip()
            lat = float(lat_input)
            if not -90 <= lat <= 90:
                print("Latitude must be between -90 and 90")
                continue
            
            lon_input = input("Enter longitude (-180 to 180): ").strip()
            lon = float(lon_input)
            if not -180 <= lon <= 180:
                print("Longitude must be between -180 and 180")
                continue
            
            return lat, lon
        except ValueError:
            print("Please enter valid numeric values")


def main():
    """Main function to run the airport finder."""
    print("=" * 60)
    print("AIRPORT FINDER - Find the closest airport to your location")
    print("=" * 60)
    
    print("\nOptions:")
    print("1. Enter location manually")
    print("2. Load locations from CSV file")
    
    choice = input("\nSelect option (1 or 2): ").strip()
    
    if choice == "1":
        lat, lon = get_user_input()
        airport, distance = find_closest_airport(lat, lon)
        
        print("\n" + "-" * 40)
        print("RESULT:")
        print(f"Your location: ({lat}, {lon})")
        print(f"Closest airport: {airport['name']}")
        print(f"Airport code: {airport['code']}")
        print(f"Airport location: ({airport['lat']}, {airport['lon']})")
        print(f"Distance: {distance:.2f} km")
        print("-" * 40)
        
    elif choice == "2":
        filepath = input("Enter CSV file path: ").strip()
        
        try:
            results = process_csv_file(filepath)
            
            print("\n" + "-" * 60)
            print("RESULTS:")
            print("-" * 60)
            
            for result in results:
                print(f"\nLocation: {result['location_name']} ({result['latitude']}, {result['longitude']})")
                print(f"  Closest airport: {result['closest_airport']['name']} ({result['closest_airport']['code']})")
                print(f"  Distance: {result['distance_km']} km")
                
        except FileNotFoundError:
            print(f"Error: File '{filepath}' not found")
        except Exception as e:
            print(f"Error processing file: {e}")
    else:
        print("Invalid option selected")
        sys.exit(1)


if __name__ == "__main__":
    main()
