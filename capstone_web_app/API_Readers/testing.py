import urllib.request
import urllib.parse
import urllib.error
import json
from datetime import datetime
from app import app, db
from app.models import Weather
import unittest
import sys

#logfile for errors and unit testing
sys.stdout = open("log.txt", "w")

class DarkSkyTesting(unittest.TestCase):

    def test_API_Response(self):
        weather = urllib.request.urlopen(
            "https://api.darksky.net/forecast/9b4b1b1398764e02d892ee09dca2328e/32.5314,-92.6379")
        self.assertEqual(weather.getcode(), 200)

    def test_case2(self):
        #self.assertEqual()
        pass

    #@unittest.expectedFailure
    def test_case3(self):
        #self.assertEqual()
        pass


if __name__ == '__main__':
    print(unittest.main())
