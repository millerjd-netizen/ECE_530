"""
Unit tests for Airport Finder module.
"""

import unittest
import os
import tempfile
import csv
from airport_finder import (
    haversine_distance,
    find_closest_airport,
    process_csv_file,
    AIRPORTS
)


class TestHaversineDistance(unittest.TestCase):
    """Test cases for the haversine_distance function."""
    
    def test_same_location(self):
        """Distance between same point should be 0."""
        distance = haversine_distance(40.7128, -74.0060, 40.7128, -74.0060)
        self.assertEqual(distance, 0)
    
    def test_known_distance_nyc_to_la(self):
        """Test distance between NYC and LA (approximately 3944 km)."""
        # NYC coordinates
        nyc_lat, nyc_lon = 40.7128, -74.0060
        # LA coordinates
        la_lat, la_lon = 34.0522, -118.2437
        
        distance = haversine_distance(nyc_lat, nyc_lon, la_lat, la_lon)
        
        # Should be approximately 3944 km (allow 5% tolerance)
        self.assertAlmostEqual(distance, 3944, delta=200)
    
    def test_known_distance_london_to_paris(self):
        """Test distance between London and Paris (approximately 344 km)."""
        london_lat, london_lon = 51.5074, -0.1278
        paris_lat, paris_lon = 48.8566, 2.3522
        
        distance = haversine_distance(london_lat, london_lon, paris_lat, paris_lon)
        
        # Should be approximately 344 km
        self.assertAlmostEqual(distance, 344, delta=20)
    
    def test_antipodal_points(self):
        """Test distance between antipodal points (should be ~20,000 km)."""
        # North pole to south pole
        distance = haversine_distance(90, 0, -90, 0)
        
        # Should be approximately half Earth's circumference (~20,000 km)
        self.assertAlmostEqual(distance, 20015, delta=100)
    
    def test_symmetric(self):
        """Distance should be same regardless of direction."""
        dist1 = haversine_distance(40.7128, -74.0060, 34.0522, -118.2437)
        dist2 = haversine_distance(34.0522, -118.2437, 40.7128, -74.0060)
        
        self.assertEqual(dist1, dist2)


class TestFindClosestAirport(unittest.TestCase):
    """Test cases for the find_closest_airport function."""
    
    def test_location_near_jfk(self):
        """Test finding closest airport to a location near JFK."""
        # Manhattan coordinates
        lat, lon = 40.7580, -73.9855
        
        airport, distance = find_closest_airport(lat, lon)
        
        # JFK or LGA should be closest to Manhattan
        self.assertIn(airport['code'], ['JFK', 'LGA', 'EWR'])
    
    def test_location_near_lax(self):
        """Test finding closest airport to downtown LA."""
        lat, lon = 34.0522, -118.2437
        
        airport, distance = find_closest_airport(lat, lon)
        
        self.assertEqual(airport['code'], 'LAX')
    
    def test_location_in_london(self):
        """Test finding closest airport to central London."""
        lat, lon = 51.5074, -0.1278
        
        airport, distance = find_closest_airport(lat, lon)
        
        self.assertEqual(airport['code'], 'LHR')
    
    def test_location_in_tokyo(self):
        """Test finding closest airport to Tokyo."""
        lat, lon = 35.6762, 139.6503
        
        airport, distance = find_closest_airport(lat, lon)
        
        self.assertEqual(airport['code'], 'NRT')
    
    def test_distance_is_positive(self):
        """Distance should always be positive."""
        lat, lon = 0, 0  # Gulf of Guinea
        
        airport, distance = find_closest_airport(lat, lon)
        
        self.assertGreater(distance, 0)
    
    def test_returns_tuple(self):
        """Function should return a tuple of (airport, distance)."""
        result = find_closest_airport(40.7128, -74.0060)
        
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
    
    def test_airport_has_required_fields(self):
        """Returned airport should have all required fields."""
        airport, _ = find_closest_airport(40.7128, -74.0060)
        
        self.assertIn('code', airport)
        self.assertIn('name', airport)
        self.assertIn('lat', airport)
        self.assertIn('lon', airport)
    
    def test_custom_airport_list(self):
        """Test with a custom airport list."""
        custom_airports = [
            {"code": "TEST1", "name": "Test Airport 1", "lat": 0, "lon": 0},
            {"code": "TEST2", "name": "Test Airport 2", "lat": 10, "lon": 10},
        ]
        
        airport, _ = find_closest_airport(1, 1, airports=custom_airports)
        
        self.assertEqual(airport['code'], 'TEST1')
    
    def test_empty_airport_list_raises_error(self):
        """Should raise ValueError with empty airport list."""
        with self.assertRaises(ValueError):
            find_closest_airport(40.7128, -74.0060, airports=[])


class TestProcessCSVFile(unittest.TestCase):
    """Test cases for the process_csv_file function."""
    
    def setUp(self):
        """Create a temporary CSV file for testing."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_valid_csv_file(self):
        """Test processing a valid CSV file."""
        csv_path = os.path.join(self.temp_dir, 'test_locations.csv')
        
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['name', 'latitude', 'longitude'])
            writer.writerow(['New York', '40.7128', '-74.0060'])
            writer.writerow(['Los Angeles', '34.0522', '-118.2437'])
        
        results = process_csv_file(csv_path)
        
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['location_name'], 'New York')
        self.assertEqual(results[1]['location_name'], 'Los Angeles')
    
    def test_csv_results_have_required_fields(self):
        """Results should have all required fields."""
        csv_path = os.path.join(self.temp_dir, 'test_locations.csv')
        
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['name', 'latitude', 'longitude'])
            writer.writerow(['Test Location', '40.7128', '-74.0060'])
        
        results = process_csv_file(csv_path)
        
        self.assertIn('location_name', results[0])
        self.assertIn('latitude', results[0])
        self.assertIn('longitude', results[0])
        self.assertIn('closest_airport', results[0])
        self.assertIn('distance_km', results[0])
    
    def test_empty_csv_file(self):
        """Test processing an empty CSV file (header only)."""
        csv_path = os.path.join(self.temp_dir, 'empty.csv')
        
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['name', 'latitude', 'longitude'])
        
        results = process_csv_file(csv_path)
        
        self.assertEqual(len(results), 0)
    
    def test_file_not_found(self):
        """Should raise FileNotFoundError for non-existent file."""
        with self.assertRaises(FileNotFoundError):
            process_csv_file('/nonexistent/path/file.csv')
    
    def test_invalid_coordinates_skipped(self):
        """Rows with invalid coordinates should be skipped."""
        csv_path = os.path.join(self.temp_dir, 'invalid.csv')
        
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['name', 'latitude', 'longitude'])
            writer.writerow(['Valid', '40.7128', '-74.0060'])
            writer.writerow(['Invalid', 'not_a_number', '-74.0060'])
        
        results = process_csv_file(csv_path)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['location_name'], 'Valid')


class TestAirportData(unittest.TestCase):
    """Test cases for the airport data."""
    
    def test_airports_not_empty(self):
        """AIRPORTS list should not be empty."""
        self.assertGreater(len(AIRPORTS), 0)
    
    def test_all_airports_have_required_fields(self):
        """All airports should have required fields."""
        for airport in AIRPORTS:
            self.assertIn('code', airport)
            self.assertIn('name', airport)
            self.assertIn('lat', airport)
            self.assertIn('lon', airport)
    
    def test_airport_coordinates_valid(self):
        """Airport coordinates should be within valid ranges."""
        for airport in AIRPORTS:
            self.assertGreaterEqual(airport['lat'], -90)
            self.assertLessEqual(airport['lat'], 90)
            self.assertGreaterEqual(airport['lon'], -180)
            self.assertLessEqual(airport['lon'], 180)
    
    def test_airport_codes_unique(self):
        """Airport codes should be unique."""
        codes = [airport['code'] for airport in AIRPORTS]
        self.assertEqual(len(codes), len(set(codes)))


if __name__ == '__main__':
    unittest.main()
