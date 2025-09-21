# Solarius

**Solarius** is a Python library for calculating your precise solar return — the exact moment the Sun returns to the same ecliptic longitude it occupied at your birth — according to the Gregorian calendar. This *real* birthday and can differ from your *civil* birthday in a given future year due to leap years, etc.

To give you accurate results anywhere in the world, Solarius uses:

- [skyfield](https://pypi.org/project/skyfield/) to compute precise positions of celestial bodies.
- [geopy](https://pypi.org/project/geopy/) to map the names of cities and countries to coordinates.
- [timezonefinder](https://pypi.org/project/timezonefinder/) for mapping geographical coordinates to timezones.
- [pytz](https://pypi.org/project/pytz/) to convert between UTC and local times using regional daylight-saving rules.

## Installation

```bash
pip install solarius
```

## API Documentation

See [here](https://github.com/ckstash/solarius/blob/main/API.md)

## Example Usage

```Python
from solarius.model import SolarReturnCalculator

calc = SolarReturnCalculator(ephemeris_file="de421.bsp")

# Predict without printing
date_str, time_str, tz_name = calc.predict(
    official_birthday="18-01-1996",
    official_birth_time="02:30",
    birth_country="France",
    birth_city="Paris",
    current_country="France",
    current_city="Paris",
    target_year="2026"
)
print(date_str, time_str, tz_name)

# Or use the convenience printer
calc.print_real_birthday(
    official_birthday="18-01-1996",
    official_birth_time="02:30",
    birth_country="France",
    birth_city="Paris",
    current_country="France",
    current_city="Paris",
    target_year="2026"
)
```