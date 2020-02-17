#API Reader for Dark Sky
import urllib.request
import urllib.parse
import urllib.error
import json
from datetime import datetime
from app.models import Weather

#Class to hold the weather data object
class CurrentWeatherData:

    def __init__(self, sunset, sunrise, temp, m_phase, clouds, wind, wind_dir, vis, current):
        self.sunset = sunset
        self.sunrise = sunrise
        self.temp = temp
        self.m_phase = m_phase
        
        #Convert decimal to percent
        self.clouds = (clouds*100)
        self.wind = wind
        self.wind_dir = wind_dir
        self.vis = vis
        self.current = current

    def __str__(self):
        #Convert the UNIX time values to datetime values
        DTsunset = datetime.fromtimestamp(self.sunset)
        DTsunrise = datetime.fromtimestamp(self.sunrise)

        #Turn datetime values into strings
        strSunset = DTsunset.strftime("%I:%M %p")
        strSunrise = DTsunrise.strftime("%I:%M %p")

        #Return all the weather data as a string
        return "Current Conditions for Ruston, LA:" + "\n" + str(self.current) + ", " + str(self.temp) + "F" + "\n" + "Sunrise: " + strSunrise + "\n" + "Sunset: " + strSunset + "\n" + "Moon Phase: " + str(self.m_phase) + "\n" + "Cloud Cover: " + str(self.clouds) + "%" + "\n" + "Wind: " + str(self.wind) + " mph from " + str(self.wind_dir) + " degrees" + "\n" + "Visibility: " + str(self.vis) + " miles"

#Class to hold the next day's weather object (unfinished)
class Forecast(CurrentWeatherData):

    def __init__(self, CurrentWeatherData, rain_chance):
        self.rain_chance = rain_chance

    def __str__(self):
        return "NEXT DAY FORECAST:" + super(Forecast, self) + "\n" + "Chance of Rain: " + str(self.rain_chance*100)

def parseRequest():
    
    #Error handling
    weather_error = False
    
    #Using Vienna Street in Ruston as the location, try to pull from the API
    try:
        weather = urllib.request.urlopen("https://api.darksky.net/forecast/9b4b1b1398764e02d892ee09dca2328e/32.5314,-92.6379")
    #Exception, get the error
    except:
        urllib.error.URLError as e: weather = e.read().decode("utf8", 'ignore')
        weather_error = True
    
    #If not False (True):
    if not weather_error:    
        #(For consistency)
        weathertxt = weather.read()
        weatherjson = json.loads(weathertxt)

        #Retreive basic weather data needed for Stargazer App
        cloud = (weatherjson["currently"]["cloudCover"]) #0-1, needs to be converted to a percent
        vis = (weatherjson["currently"]["visibility"]) #Visibility in Miles
        wind = (weatherjson["currently"]["windSpeed"]) #MPH
        wind_dir = (weatherjson["currently"]["windBearing"]) #Compass direction of which the wind is blowing FROM
        temp = (weatherjson["currently"]["temperature"]) #Fahrenheit

        #Retrieve sunset and sunrise times in UNIX format
        sunrise = (weatherjson["daily"]["data"][0]["sunriseTime"])
        sunset = (weatherjson["daily"]["data"][0]["sunsetTime"])

        #retrieve Moon Phase data and convert it 
        m_phase = (weatherjson["daily"]["data"][0]["moonPhase"])

        #Moon phase data is returned as a decimal 0-1.
        if m_phase < 0.25:
            m_phase = "Waxing Crescent"
        elif m_phase == 0.25:
            m_phase = "First Quarter"
        elif m_phase > 0.25 and m_phase < 0.5:
            m_phase = "Waxing Gibbous"
        elif m_phase == 0.5:
            m_phase = "Full Moon"
        elif m_phase > 0.5 and m_phase < 0.75:
            m_phase = "Waning Gibbous"
        elif m_phase == 0.75:
            m_phase = "Last Quarter"
        elif m_phase > 0.75:
            m_phase = "Waning Crescent"
        elif m_phase == 0:
            m_phase = "New Moon"

        #Current conditions
        current = (weatherjson["currently"]["summary"])
        #Temporary format
        currentWeather = CurrentWeatherData(sunset, sunrise, temp, m_phase, cloud, wind, wind_dir, vis, current)
        print(currentWeather)
    else:
        print("Error retrieving weather data")
"""
In the future, we will encapsulate this program within a while loop that will make calls based on comparing the current time value to the last known sunset/sunrise values for the current day.
For example (psuedocode):

#if time is between the sunrise and sunset (daytime)
If time > sunrise and time < sunset:
    call once an hour
else: (anything not in the current day, ie night)
    call once every 5 or 10 minutes 
"""
parseRequest()
    
