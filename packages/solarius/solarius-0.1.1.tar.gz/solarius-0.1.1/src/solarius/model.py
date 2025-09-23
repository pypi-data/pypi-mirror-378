from datetime import datetime, timedelta
from skyfield.api import load, wgs84
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import pytz
import calendar
import time


class SolarReturnCalculator:
    """A calculator for predicting the precise solar return date and time.

    This class computes the "real" birthday (solar return) for a given year,
    accounting for the time zone at the birth location and the time zone
    at the current location. It uses astronomical calculations from the
    Skyfield library and geolocation/timezone lookups.

    Attributes:
        eph: The loaded ephemeris data from a BSP file.
    """

    def __init__(self, ephemeris_file: str = "de421.bsp"):
        """Initializes the SolarReturnCalculator with ephemeris data.

        Args:
            ephemeris_file (str): Path to the BSP ephemeris file. Defaults to "de421.bsp", which is downloaded to the current working directory.
        """
        self.eph = load(ephemeris_file)

    def predict(
        self,
        official_birthday: str,
        official_birth_time: str,
        birth_country: str,
        birth_city: str,
        current_country: str,
        current_city: str,
        target_year: str = None
    ):
        """Predict the precise solar return date and time.

        Args:
            official_birthday (str): Birth date in 'dd-mm-yyyy' format.
            official_birth_time (str): Birth time in 'hh:mm' 24-hour format.
            birth_country (str): Country of birth.
            birth_city (str): City of birth.
            current_country (str): Current country of residence.
            current_city (str): Current city of residence.
            target_year (str, optional): Year for which to calculate the solar return.
                Defaults to the current year.

        Returns:
            tuple: (date_str, time_str, current_tz_name) where:
                - date_str (str): Date of solar return in 'dd/mm' format.
                - time_str (str): Time of solar return in 'HH:MM' format.
                - current_tz_name (str): Time zone name of the current location.

        Raises:
            ValueError: If inputs are invalid or locations/timezones cannot be determined.
        """
        # Determine target year
        if target_year is None:
            target_year = datetime.now().year
        else:
            try:
                target_year = int(target_year)
            except ValueError:
                raise ValueError(f"Invalid target year '{target_year}'. Please use 'yyyy' format.")

        # Validate and parse birth date
        try:
            birth_date = datetime.strptime(official_birthday, "%d-%m-%Y")
        except ValueError:
            raise ValueError(
                f"Invalid birth date '{official_birthday}'. "
                "Please use 'dd-mm-yyyy' format with a valid calendar date."
            )

        # Validate and parse birth time
        try:
            birth_hour, birth_minute = map(int, official_birth_time.split(":"))
        except ValueError:
            raise ValueError(
                f"Invalid birth time '{official_birth_time}'. "
                "Please use 'hh:mm' 24-hour format."
            )

        if not (0 <= birth_hour <= 23):
            raise ValueError(f"Hour '{birth_hour}' is out of range (0-23).")
        if not (0 <= birth_minute <= 59):
            raise ValueError(f"Minute '{birth_minute}' is out of range (0-59).")

        geolocator = Nominatim(user_agent="birthday_tz_lookup", timeout=10)

        def safe_geocode(query, retries=3, delay=1):
            """Safely geocode a location with retries."""
            for attempt in range(retries):
                try:
                    return geolocator.geocode(query)
                except GeocoderTimedOut:
                    if attempt < retries - 1:
                        time.sleep(delay)
                    else:
                        raise RuntimeError(
                            f"Could not retrieve location for '{query}' after {retries} attempts. "
                            "The geocoding service may be slow or unavailable. Please try again later."
                        )

        birth_location = safe_geocode(f"{birth_city}, {birth_country}")
        current_location = safe_geocode(f"{current_city}, {current_country}")

        if not birth_location or not current_location:
            raise ValueError("Could not find coordinates for one of the locations. Please check spelling.")

        # Get time zones
        tf = TimezoneFinder()
        birth_tz_name = tf.timezone_at(lng=birth_location.longitude, lat=birth_location.latitude)
        current_tz_name = tf.timezone_at(lng=current_location.longitude, lat=current_location.latitude)

        if not birth_tz_name or not current_tz_name:
            raise ValueError("Could not determine timezone for one of the locations.")

        birth_tz = pytz.timezone(birth_tz_name)
        current_tz = pytz.timezone(current_tz_name)

        # Handle leap year birthdays
        birth_month, birth_day = birth_date.month, birth_date.day
        if (birth_month, birth_day) == (2, 29):
            if not calendar.isleap(birth_date.year):
                raise ValueError(f"{birth_date.year} is not a leap year, so February 29 is invalid.")
            civil_anniversary_month, civil_anniversary_day = (
                (3, 1) if not calendar.isleap(target_year) else (2, 29)
            )
        else:
            civil_anniversary_month, civil_anniversary_day = birth_month, birth_day

        # Parse birth datetime in birth location's local time
        birth_local_dt = birth_tz.localize(datetime(
            birth_date.year, birth_month, birth_day,
            birth_hour, birth_minute
        ))
        birth_dt_utc = birth_local_dt.astimezone(pytz.utc)

        # Load timescale and planetary bodies
        ts = load.timescale()
        sun = self.eph["sun"]
        earth = self.eph["earth"]

        t_birth = ts.utc(
            birth_dt_utc.year, birth_dt_utc.month, birth_dt_utc.day,
            birth_dt_utc.hour, birth_dt_utc.minute, birth_dt_utc.second
        )

        # Birth longitude in tropical frame
        birth_observer = earth + wgs84.latlon(birth_location.latitude, birth_location.longitude)
        ecl = birth_observer.at(t_birth).observe(sun).apparent().ecliptic_latlon(epoch='date')
        birth_longitude = ecl[1].degrees

        # Initial guess for target year solar return
        approx_dt_local_birth_tz = birth_tz.localize(datetime(
            target_year, civil_anniversary_month, civil_anniversary_day,
            birth_hour, birth_minute
        ))
        approx_dt_utc = approx_dt_local_birth_tz.astimezone(pytz.utc)

        # Current observer
        current_observer = earth + wgs84.latlon(current_location.latitude, current_location.longitude)

        def sun_longitude_at(dt):
            t = ts.utc(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
            ecl = current_observer.at(t).observe(sun).apparent().ecliptic_latlon(epoch='date')
            return ecl[1].degrees

        def angle_diff(a, b):
            return (a - b + 180) % 360 - 180

        # Binary search for exact solar return
        dt1 = approx_dt_utc - timedelta(days=2)
        dt2 = approx_dt_utc + timedelta(days=2)
        old_angle_diff = 999
        for _ in range(50):
            mid = dt1 + (dt2 - dt1) / 2
            curr_angle_diff = angle_diff(sun_longitude_at(mid), birth_longitude)
            if old_angle_diff == curr_angle_diff:
                break
            if curr_angle_diff > 0:
                dt2 = mid
            else:
                dt1 = mid
            old_angle_diff = curr_angle_diff

        real_dt_utc = dt1 + (dt2 - dt1) / 2

        # Convert to current location's local time
        real_dt_local_current = real_dt_utc.astimezone(current_tz)
        date_str = real_dt_local_current.strftime("%d/%m")
        time_str = real_dt_local_current.strftime("%H:%M")

        return date_str, time_str, current_tz_name

    def print_real_birthday(
        self,
        official_birthday: str,
        official_birth_time: str,
        birth_country: str,
        birth_city: str,
        current_country: str,
        current_city: str,
        target_year: str = None
    ):
        """Print the predicted solar return date and time in a human-readable format.

        This is a convenience method that calls `predict()` internally and
        prints the result to stdout in a friendly format.

        Args:
            official_birthday (str): Birth date in 'dd-mm-yyyy' format.
            official_birth_time (str): Birth time in 'hh:mm' 24-hour format.
            birth_country (str): Country of birth.
            birth_city (str): City of birth.
            current_country (str): Current country of residence.
            current_city (str): Current city of residence.
            target_year (str, optional): Year for which to calculate the solar return.
                Defaults to the current year.

        Returns:
            None: This method prints the result directly and does not return a value.

        Raises:
            ValueError: If inputs are invalid or locations/timezones cannot be determined.
        """
        print("Official birthday and time:", official_birthday, "at", official_birth_time)
        try:
            date_str, time_str, current_tz_name = self.predict(
                official_birthday,
                official_birth_time,
                birth_country,
                birth_city,
                current_country,
                current_city,
                target_year
            )
            year_display = target_year if target_year is not None else datetime.now().year
            print(f"In year {year_display}, your real birthday is on {date_str} at {time_str} ({current_tz_name})")
        except Exception as e:
            print("Error calculating real birthday:", str(e))
