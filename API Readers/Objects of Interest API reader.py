# Jonah Landry
# API Reader for Stargazer
# 

import urllib.request
import json
import urllib.parse
from datetime import datetime

#Class for each object of interest
class OOI:
    def __init__(name, riseTime):
        self.name = name
        self.riseTime = riseTime

#Subclass for ISS passes that adds a passnumber variable
class ISSPass(OOI):
    def __init__(self,passNum,duration, riseTime):
        self.passNum = passNum
        self.duration = duration
        self.riseTime = riseTime
        self.name = "ISS Pass"
        
    #String format of the class, mainly for debugging.
    def __str__(self):
        #Turns the raw seconds into a datetime type and the passNum into a string for concatanation
        datetimeDuration = datetime.fromtimestamp(self.duration)
        datetimeRiseTime = datetime.fromtimestamp(self.riseTime)
        strPassNum = str(self.passNum)

        #Gets a string from each datetime
        strRiseTime = datetimeRiseTime.strftime("%I:%M %p on %b %d %Y")
        strDuration = datetimeDuration.strftime("%M:%S")
        return "Pass number " + strPassNum + " will occur at " + strRiseTime + " over Ruston, LA for a duration of " + strDuration
     
#Grabs info from open-notify about when the ISS will pass over Ruston Louisiana.
def parseISS ():
    #Makes the request
    ISSURL = urllib.request.urlopen("http://api.open-notify.org/iss-pass.json?lat=32.532471&lon=-92.639061")

    #Takes the raw text and turns it into a json for easier reading.
    ISSText = ISSURL.read() #text
    ISSData = json.loads(ISSText) #json

    #A list for the various passes the ISS can make
    passes = []
    #The number of passes to be recorded as well as a counter and a temporary pass value
    passNum = int(ISSData['request']['passes'])
    passCount = 0
    currentPass = ISSPass(0,0,0)

    #Iterates through each pass, recording them in the list 'passes'
    while (passCount < passNum):
        ### Debugging text
        print( "The ISS will pass over Ruston, LA ", passNum ," times.")
        print("Pass number ", passCount + 1, ": ",ISSData['response'][passCount])
        ###
        #
        #Saves the pass number, duration, and risetime to a temporary pass variable
        currentPass.passNum = passCount + 1
        currentPass.duration = ISSData['response'][passCount]['duration']
        currentPass.riseTime = ISSData['response'][passCount]['risetime']
        
        #Adds the pass to the list 
        passes.append(currentPass)
        
        #Debug text
        print(currentPass, "\n")
        
        #Iterate counter
        passCount = passCount+1

    return passes
    

# Declares a list for the function and fills it. Temporary, just for the purpose of getting the function up and running
ISSPassList = {}
ISSPassList = parseISS()
