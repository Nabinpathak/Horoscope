from flask import Flask, render_template, request
import sqlite3
import random
import os
import ephem
from datetime import datetime
import pytz # New: for timezone handling
import geopy # New: for geocoding city names
from geopy.geocoders import Nominatim # New: specific geocoder

app = Flask(__name__)

DATABASE_FILE = "predictions.db"

# Initialize geolocator for city coordinates
geolocator = Nominatim(user_agent="horoscope_app_agent")

# --- Database Initialization (from previous code, ensures table exists) ---
def init_db():
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sign TEXT NOT NULL,
                category TEXT NOT NULL,
                text TEXT NOT NULL
            )
        """)
        conn.commit()
        print("Database table 'predictions' ensured to exist.")
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")
    finally:
        if conn:
            conn.close()

# --- Prediction Retrieval from Database (will be modified later for ML) ---
def get_prediction_from_db(sign, category):
    conn = None
    prediction_text = "Sorry, something went wrong fetching your prediction. Please try again later."
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT text FROM predictions WHERE sign=? AND category=?", (sign.lower(), category.lower()))
        results = cursor.fetchall()

        if not results:
            prediction_text = "No prediction found for that sign and category."
        else:
            prediction_text = random.choice(results)[0]
    except sqlite3.Error as e:
        print(f"Database error during prediction retrieval: {e}")
        prediction_text = "Error accessing horoscope data. Please try again."
    finally:
        if conn:
            conn.close()
    return prediction_text

# --- Helper: Get Zodiac Sign from Ecliptic Longitude ---
def get_zodiac_sign(ecliptic_longitude_degrees):
    # Ensure longitude is normalized to 0-360
    lon = ecliptic_longitude_degrees % 360
    zodiac_signs = [
        ("aries", 0), ("taurus", 30), ("gemini", 60), ("cancer", 90),
        ("leo", 120), ("virgo", 150), ("libra", 180), ("scorpio", 210),
        ("sagittarius", 240), ("capricorn", 270), ("aquarius", 300), ("pisces", 330)
    ]
    for sign, start_degree in zodiac_signs:
        if lon >= start_degree and lon < start_degree + 30:
            return sign
    return "unknown" # Should not be reached with proper longitude

# --- NEW: Function to calculate a full birth chart ---
def calculate_birth_chart(birth_dt_utc, lat, lon):
    observer = ephem.Observer()
    observer.lat = str(lat) # ephem expects strings for lat/lon
    observer.lon = str(lon)
    observer.date = birth_dt_utc

    chart_info = {}

    # Sun
    sun = ephem.Sun(observer)
    sun.compute(observer)
    chart_info['sun_sign'] = get_zodiac_sign(ephem.degrees(sun.hlong).norm * 180 / ephem.pi)

    # Moon
    moon = ephem.Moon(observer)
    moon.compute(observer)
    chart_info['moon_sign'] = get_zodiac_sign(ephem.degrees(moon.hlong).norm * 180 / ephem.pi)

    # Mercury
    mercury = ephem.Mercury(observer)
    mercury.compute(observer)
    chart_info['mercury_sign'] = get_zodiac_sign(ephem.degrees(mercury.hlong).norm * 180 / ephem.pi)

    # Venus
    venus = ephem.Venus(observer)
    venus.compute(observer)
    chart_info['venus_sign'] = get_zodiac_sign(ephem.degrees(venus.hlong).norm * 180 / ephem.pi)

    # Mars
    mars = ephem.Mars(observer)
    mars.compute(observer)
    chart_info['mars_sign'] = get_zodiac_sign(ephem.degrees(mars.hlong).norm * 180 / ephem.pi)

    # Jupiter
    jupiter = ephem.Jupiter(observer)
    jupiter.compute(observer)
    chart_info['jupiter_sign'] = get_zodiac_sign(ephem.degrees(jupiter.hlong).norm * 180 / ephem.pi)

    # Saturn
    saturn = ephem.Saturn(observer)
    saturn.compute(observer)
    chart_info['saturn_sign'] = get_zodiac_sign(ephem.degrees(saturn.hlong).norm * 180 / ephem.pi)

    # Ascendant (Rising Sign) - Requires calculating Sidereal Time
    # Get sidereal time at the location
    sidereal_time_at_birth = observer.sidereal_time()

    # Convert sidereal time to degrees (15 degrees per hour)
    # The Ascendant is the sign on the eastern horizon at the time of birth.
    # It's the longitude of the point where the ecliptic intersects the eastern horizon.
    # Ephem can provide house cusps, from which we derive the Ascendant.
    # The first house cusp is the Ascendant.
    # observer.asc_obliq and observer.ecl_obliq can help, but a direct Ascendant calc
    # isn't as straightforward as planets in ephem without going into house calculations.
    # For a simple approximate Ascendant without full house calculations:
    # A common method uses the Local Sidereal Time (LST) and latitude.
    # Let's approximate by setting the observer date again and using ephem's internal house calculation
    # to get the first house cusp, which is the Ascendant.
    # This requires using the `horizon` and `house` module's functionality or manually using LST.
    # A more common astrological library would have a direct ascendant method.
    # For now, let's use a common approximation based on LST and try to derive it.
    # This might require some more complex ephem usage or a different library like Astropy.
    # For simplicity, if a direct "Ascendant" isn't immediately obvious, let's skip
    # full Ascendant calculation for now and focus on planets.
    # Or, a simplified way: Ephem doesn't directly give you ascendant sign easily from an observer.
    # Many users might calculate it using 1st house cusp, which isn't directly a simple `.hlong`.
    # Let's comment it out for now to ensure working code.
    # chart_info['ascendant_sign'] = "Feature pending"

    # Alternative approach for ascendant: using `ephem.Equatorial` and converting to ecliptic
    # This is more involved and typically requires a full astrological library.
    # For now, let's stick to planet signs.

    # Example: You can get right ascension (RA) and declination (Dec)
    # This part is more for advanced use, getting RA/Dec of a body
    # observer.date = birth_dt_utc
    # equ = ephem.Equatorial(ephem.degrees('0:0:0'), ephem.degrees('0:0:0'), observer) # Dummy for context
    # chart_info['mc_ra'] = ephem.degrees(observer.mc_ra).norm * 180 / ephem.pi # Midheaven Right Ascension
    # chart_info['asc_ra'] = ephem.degrees(observer.asc_ra).norm * 180 / ephem.pi # Ascendant Right Ascension (not its sign yet)

    # Let's ensure a basic Ascendant derivation is available or we add a note.
    # For now, we'll leave ascendant_sign as None if not explicitly calculated in a simple way.
    # A robust Ascendant calc usually involves more than just ephem.Sun/Moon setup directly.
    # It needs to compute the ecliptic point rising on the eastern horizon.
    # For this current scope, let's stick to planets in signs.

    return chart_info

# --- Flask Web Routes ---
@app.route('/', methods=['GET', 'POST'])
def home():
    prediction = ""
    astrological_info = {} # To store calculated astrological details

    valid_categories = ["love", "career", "health", "finance", "general"]

    if request.method == 'POST':
        birth_date_str = request.form.get('birth_date')
        birth_time_str = request.form.get('birth_time')
        birth_city = request.form.get('birth_city', '').strip() # New: get city from form
        birth_timezone = request.form.get('birth_timezone', 'UTC').strip() # New: get timezone

        category = request.form.get('category', '').strip().lower()

        if birth_date_str and birth_time_str and birth_city and category:
            if category in valid_categories:
                try:
                    # 1. Geocode City to get Latitude and Longitude
                    location = geolocator.geocode(birth_city)
                    if not location:
                        prediction = f"Could not find coordinates for {birth_city}. Please enter a valid city."
                        return render_template('index.html', prediction=prediction, astrological_info=astrological_info)

                    lat = location.latitude
                    lon = location.longitude

                    # 2. Parse Birth Date and Time
                    local_birth_dt = datetime.strptime(f"{birth_date_str} {birth_time_str}", "%Y-%m-%d %H:%M")

                    # 3. Convert Local Birth Time to UTC
                    try:
                        local_tz = pytz.timezone(birth_timezone)
                        local_dt = local_tz.localize(local_birth_dt)
                        birth_dt_utc = local_dt.astimezone(pytz.utc)
                    except pytz.UnknownTimeZoneError:
                        prediction = f"Unknown timezone: '{birth_timezone}'. Please enter a valid timezone identifier (e.g., 'Asia/Kathmandu', 'America/New_York')."
                        return render_template('index.html', prediction=prediction, astrological_info=astrological_info)


                    # 4. Calculate Birth Chart
                    astrological_info = calculate_birth_chart(birth_dt_utc, lat, lon)
                    astrological_info['birth_city'] = birth_city
                    astrological_info['birth_timezone'] = birth_timezone
                    # Add current time for context (can be used for daily transits later)
                    astrological_info['current_utc_time'] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")


                    print(f"Calculated Astrological Info: {astrological_info}")

                    # --- This is where your ML/smarter logic will go ---
                    # For now, let's use the calculated sun sign for the prediction.
                    # In future steps, you'll use all of 'astrological_info' to generate a more detailed prediction.
                    prediction = get_prediction_from_db(astrological_info["sun_sign"], category)

                except ValueError:
                    prediction = "Invalid date or time format. Please use YYYY-MM-DD and HH:MM."
                except Exception as e:
                    prediction = f"An unexpected error occurred: {e}"
                    print(f"Error during astrological calculation or geocoding: {e}")
            else:
                prediction = "Invalid category selected. Please choose from the available options."
        else:
            prediction = "Please provide your birth date, time, city, timezone, and select a category."

    return render_template('index.html', prediction=prediction, astrological_info=astrological_info)

# --- Run the Flask Application ---
if __name__ == '__main__':
    init_db() # Ensure DB table exists
    app.run(debug=True)