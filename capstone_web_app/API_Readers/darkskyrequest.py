# API Reader for Dark Sky
import urllib.request
import urllib.parse
import urllib.error
import json
from datetime import datetime
from app import app, db
from app.models import Weather
from testing import *
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

        # Retrieve current conditions before getting daily
        clouds = (weatherjson["currently"]["cloudCover"])  # 0-1, needs to be converted to a percent
        vis = (weatherjson["currently"]["visibility"])  # Visibility in Miles
        wind = (weatherjson["currently"]["windSpeed"])  # MPH
        wind_dir = (weatherjson["currently"]["windBearing"])  # Compass direction of which the wind is blowing FROM
        highTemp = (weatherjson["currently"]["temperature"])  # Fahrenheit
        lowTemp = 0 #Arbitrary value since current shows the temperature read at the last update.
        time = (weatherjson["currently"]["time"])  # UNIX format current time (as of call)
        current = (weatherjson["currently"]["icon"]) # string value that corresponds to an image

        # Retrieve sunset and sunrise times in UNIX format
        sunrise = (weatherjson["daily"]["data"][0]["sunriseTime"])
        sunset = (weatherjson["daily"]["data"][0]["sunsetTime"])

        # Converting to datetime type
        time = datetime.fromtimestamp(time)
        sunrise = datetime.fromtimestamp(sunrise)
        sunset = datetime.fromtimestamp(sunset)

        # Converting clouds to percentage
        clouds = clouds * 100

        # retrieve Moon Phase data and convert it
        m_phase = (weatherjson["daily"]["data"][0]["moonPhase"])

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
        currentWeather = Weather(id=0, date_stored=time, sunset=sunset, sunrise=sunrise, high=highTemp, low = lowTemp,
                                 m_phase=m_phase,clouds=clouds, wind=wind, wind_dir=wind_dir, vis=vis, current=current)
        db.session.add(currentWeather)
        db.session.commit()

        #Parses the next seven days' conditions.
        dayCount = 1
        while (dayCount <= 7 ):
            clouds = (weatherjson["daily"]["data"][dayCount]["cloudCover"])
            vis = (weatherjson["daily"]["data"][dayCount]["visibility"])  # Visibility in Miles
            wind = (weatherjson["daily"]["data"][dayCount]["windSpeed"])  # MPH
            wind_dir = (weatherjson["daily"]["data"][dayCount]["windBearing"])  # Compass direction of which the wind is blowing FROM
            highTemp = (weatherjson["daily"]["data"][dayCount]["temperatureHigh"])  # Fahrenheit
            lowTemp = (weatherjson["daily"]["data"][dayCount]["temperatureLow"]) # float value for the predicted low temperature
            current = (weatherjson["daily"]["data"][dayCount]["icon"])  # string value that corresponds to an image

            # Retrieve sunset and sunrise times in UNIX format
            sunrise = (weatherjson["daily"]["data"][dayCount]["sunriseTime"])
            sunset = (weatherjson["daily"]["data"][dayCount]["sunsetTime"])

            # Converting to datetime type
            sunrise = datetime.fromtimestamp(sunrise)
            sunset = datetime.fromtimestamp(sunset)

            # Converting clouds to percentage
            clouds = clouds * 100

            # retrieve Moon Phase data and convert it
            m_phase = (weatherjson["daily"]["data"][dayCount]["moonPhase"])

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
            currentWeather = Weather(id=dayCount , date_stored=time, sunset=sunset, sunrise=sunrise, high=highTemp,
                                     low=lowTemp, m_phase=m_phase,clouds=clouds, wind=wind, wind_dir=wind_dir, vis=vis,
                                     current=current)
            db.session.add(currentWeather)
            db.session.commit()

            dayCount = dayCount + 1


    else:
        print(weather)


if __name__ == "__main__":
    # logfile for errors and unit testing
    sys.stdout = open("log.txt", "w")
    # if true, runs unit testing on calls
    parseRequest()
    sys.stdout = sys.__stdout__
