# API Reader for Dark Sky
import urllib.request
import urllib.parse
import urllib.error
from app import create_app, db
from app.models import Weather
from app.API_Readers.testing import *
import sys

DEBUG_MODE = False


def parseRequest():
    if DEBUG_MODE:
        # logfile for errors and unit testing
        sys.stdout = open("log.txt", "w")

        with open("log.txt", "w") as sys.stdout:
            DarkSky_Test = unittest.TestLoader().loadTestsFromTestCase(DarkSkyTesting)
            unittest.TextTestRunner(stream=sys.stdout).run(DarkSky_Test)

            sys.stdout.close()
            sys.stdout = sys.__stdout__

    # Attempts to delete any pre-existing weather data before updating the database.
    try:
        Weather.query.delete()
        db.session.commit()
    except Exception as err:
        print("Unable to find Weather object for deletion (Perhaps one hasn't been created?)")

    # Error handling
    weather_error = False

    # Using Vienna Street in Ruston as the location, try to pull from the API
    try:
        weather = urllib.request.urlopen(
            "https://api.darksky.net/forecast/9b4b1b1398764e02d892ee09dca2328e/32.5314,-92.6379")
    # Exception, get the error
    except urllib.error.URLError as e:
        weather = e.read().decode("utf8", 'ignore')
        weather_error = True

    # If not False (True):
    if not weather_error:
        # (For consistency)
        weathertxt = weather.read()
        weatherjson = json.loads(weathertxt)

        day_num = 1
        weather_data = weatherjson["daily"]["data"]
        # Parses the next seven days' conditions.
        for day in weather_data:
            clouds = day["cloudCover"]
            vis = day["visibility"]  # Visibility in Miles
            wind = day["windSpeed"]  # MPH
            wind_dir = day["windBearing"]  # Compass direction of which the wind is blowing FROM
            highTemp = day["temperatureHigh"]  # Fahrenheit
            lowTemp = day["temperatureLow"]  # float value for the predicted low temperature
            current = day["icon"]  # string value that corresponds to an image

            # Retrieve sunset and sunrise times in UNIX format
            sunrise = day["sunriseTime"]
            sunset = day["sunsetTime"]

            # Converting to datetime type
            sunrise = datetime.fromtimestamp(sunrise)
            sunset = datetime.fromtimestamp(sunset)

            # Converting clouds to percentage
            clouds = clouds * 100

            # retrieve Moon Phase data and convert it
            m_phase = day["moonPhase"]

            # Moon phase data is returned as a decimal 0-1.
            if m_phase < 0.25:
                m_phase = "Waxing Crescent"
            elif m_phase == 0.25:
                m_phase = "First Quarter"
            elif 0.25 < m_phase < 0.5:
                m_phase = "Waxing Gibbous"
            elif m_phase == 0.5:
                m_phase = "Full Moon"
            elif 0.5 < m_phase < 0.75:
                m_phase = "Waning Gibbous"
            elif m_phase == 0.75:
                m_phase = "Last Quarter"
            elif m_phase > 0.75:
                m_phase = "Waning Crescent"
            elif m_phase == 0:
                m_phase = "New Moon"

            # Take the parsed data and send it to the Weather class in "models" and save it to the database
            weather = Weather(id=day_num, sunset=sunset, sunrise=sunrise, high=highTemp, low=lowTemp, m_phase=m_phase,
                              clouds=clouds, wind=wind, wind_dir=wind_dir, vis=vis, current=current)
            db.session.add(weather)
            day_num += 1

        db.session.commit()



    else:
        print(weather)


if __name__ == "__main__":
    # logfile for errors and unit testing
    sys.stdout = open("log.txt", "w")
    # if true, runs unit testing on calls
    parseRequest()
    sys.stdout = sys.__stdout__
