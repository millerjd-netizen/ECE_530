# Airport Finder

Find the closest airport to any location on Earth.

![Tests](https://github.com/millerjd-netizen/ECE_530/actions/workflows/tests.yml/badge.svg)

## Features

- Calculate distance using the Haversine formula (great-circle distance)
- Support for user input (interactive mode)
- Support for CSV file input (batch processing)
- Built-in database of 15 major international airports
- Comprehensive unit tests
- GitHub Actions CI/CD integration

## Usage

### Interactive Mode

```bash
python airport_finder.py
```

Select option 1, then enter your latitude and longitude when prompted.

### CSV File Mode

```bash
python airport_finder.py
```

Select option 2, then enter the path to your CSV file.

#### CSV Format

Your CSV file should have the following columns:

```csv
name,latitude,longitude
New York City,40.7128,-74.0060
Los Angeles,34.0522,-118.2437
```

A sample file `sample_locations.csv` is included.

## Running Tests

```bash
# Run all tests
python -m unittest test_airport_finder -v

# Run with coverage
coverage run -m unittest test_airport_finder
coverage report -m
```

## Project Structure

```
airport-finder/
├── .github/
│   └── workflows/
│       └── tests.yml          # GitHub Actions workflow
├── airport_finder.py          # Main module
├── test_airport_finder.py     # Unit tests
├── sample_locations.csv       # Sample input file
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## GitHub Actions

This project includes a GitHub Actions workflow that:

- Runs on every push and pull request to main/master
- Tests against Python 3.9, 3.10, 3.11, and 3.12
- Generates test coverage reports

## Algorithm

The distance calculation uses the **Haversine formula**, which determines the great-circle distance between two points on a sphere given their latitudes and longitudes. This is the shortest distance over the Earth's surface.

## Included Airports

The built-in database includes these major airports:
- JFK (New York)
- LAX (Los Angeles)
- ORD (Chicago O'Hare)
- DFW (Dallas/Fort Worth)
- DEN (Denver)
- SFO (San Francisco)
- SEA (Seattle)
- ATL (Atlanta)
- BOS (Boston)
- MIA (Miami)
- LHR (London Heathrow)
- CDG (Paris Charles de Gaulle)
- NRT (Tokyo Narita)
- SYD (Sydney)
- DXB (Dubai)

## License

MIT License
