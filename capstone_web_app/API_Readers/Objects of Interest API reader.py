## Jonah Landry
# API Reader for Stargazer
#

import urllib.request
import json
import urllib.parse
import urllib.error
from datetime import datetime
from datetime import timedelta
from app.models import ObjectOfInterest
from app import app, db
import sys
from testing import *


# Class for each object of interest
class OOI:
    def __init__(self, name, riseTime, duration):
        self.name = name
        self.riseTime = riseTime
        self.duration = duration


# Subclass for ISS passes that adds a passnumber variable
class ISSPass(OOI):
    def __init__(self, passNum, duration, riseTime, name="ISS Pass"):
        super().__init__(name, riseTime, duration)
        self.passNum = passNum

    # String format of the class, mainly for debugging.
    def __str__(self):
        # Turns the raw seconds into a datetime type and the passNum into a string for concatenation
        datetimeDuration = datetime.fromtimestamp(self.duration)
        datetimeRiseTime = datetime.fromtimestamp(self.riseTime)
        strPassNum = str(self.passNum)

        # Gets a string from each datetime
        strRiseTime = datetimeRiseTime.strftime("%I:%M %p on %b %d %Y")
        strDuration = datetimeDuration.strftime("%M:%S")
        return "Pass number " + strPassNum + " will occur at " + strRiseTime + " over Ruston, LA for a duration of " + strDuration


# Grabs info from open-notify about when the ISS will pass over Ruston Louisiana.
def parseISS():
    #Checks that the oldest pass currently stored has already happened before parsing. If it has, continues to get five more
    #Otherwise it stops


    # Makes the request using Vienna Street in Ruston
    ISSURL = urllib.request.urlopen("http://api.open-notify.org/iss-pass.json?lat=32.532471&lon=-92.639061&n=5")

    # Takes the raw text and turns it into a json for easier reading.
    ISSText = ISSURL.read()  # text
    ISSData = json.loads(ISSText)  # json

    # A list for the various passes the ISS can make
    passes = []
    # The number of passes to be recorded as well as a counter and a temporary pass value
    passNum = int(ISSData['request']['passes'])
    passCount = 0
    currentPass = ISSPass(0, 0, 0)
    print("The ISS will pass over Ruston, LA ", passNum, " times.")

    # Iterates through each pass, recording them in the list 'passes'
    while (passCount < passNum):
        ### Debugging text
        print("Pass number ", passCount + 1, ": ", ISSData['response'][passCount], "\npassCount = ", passCount)
        ###
        #
        # Saves the pass number, duration, and risetime to a temporary pass variable
        currentPass.passNum = passCount + 1
        currentPass.duration = ISSData['response'][passCount]['duration']
        currentPass.riseTime = ISSData['response'][passCount]['risetime']

        # Adds the pass to the list
        passes.append(currentPass)

        # Debug text
        print(currentPass, "\n")

        # Iterate counter
        passCount = passCount + 1

        #reset current
        currentPass = ISSPass(0,0,0)

    #Counter for passes
    passDown = 4
    while(passDown >= 0):
        #Value manipulation in order to get the end time for visibility from the API's given duration
        comRise = datetime.fromtimestamp(passes[passDown].riseTime)
        print(comRise)
        temp_vis_end = comRise + timedelta(seconds= passes[passDown].duration)
        print(temp_vis_end)
        passCommit = ObjectOfInterest(id=passDown, type="ISSPass", vis_start=comRise, vis_end=temp_vis_end)
        db.session.add(passCommit)
        db.session.commit()


        passDown = passDown - 1



# Temporary, just for the purpose of getting the function up and running

if __name__ == "__main__":
    parseISS()