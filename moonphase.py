'''
moonphase.py
Gets real time moon phase data and updates a 6 LED moon model accordingly
A project by Shawn Wilson and Ryan Wilson, May 2019
'''

import json, datetime, time
from urllib.request import urlopen

# user-adjustable variables
errorState = 0b001100 #LED sequence to show if there's an error (an impossible sequence is best)
errorRetry = datetime.timedelta(seconds=10) #how long to wait before trying to retrieve data after last failed attempt
errorLimit = 5 #how many times to try fetching data before giving up until updateDataTime or dark/light reset 
updateDataTime = datetime.timedelta(hours=24) #how often to check for phase change/update LEDs
darkUpperThres = 0 #upper threshold for darkness
darkLowerThres = 0 #lower threshold for darkness
userID = "moonLite" #up to 8 char username to allow USNO to estimate unique users

# script state variables
errorLevel = 0
lastActive = datetime.datetime.strptime("2000 1 1", "%Y %m %d")
lastError = datetime.datetime.strptime("2000 1 1", "%Y %m %d")
leds = errorState
darkState = True


#--------------------------------------------------------------------------------------
# retrieve JSON data from website
def get_jsonparsed_data(url):
    response = urlopen(url)
    data = response.read().decode("utf-8")
    return json.loads(data)

# rotate bits in num to left by bits bits
def rotl(num, bits):
    num = (num << bits & 0b111111111111) | num >> (12-bits)
    return num

# get sequence of LEDs representing 6 slices of visible moon
# 1=on, 0=off
# returns 6 bit number. Leftmost is moon's leftmost slice when viewed from Northern hemisphere
# upon error, returns 6 bit number corresponding to errorState
def getLEDSequence():
    #Rightmost 6 LEDs are visible. Start with new moon
    phases = 0b111111000000
    lunarmonth = datetime.timedelta(days=29, hours=12, minutes=44, seconds=3)
    curtime = datetime.datetime.now()
    url = ("https://api.usno.navy.mil/moon/phase?"
           "date="+curtime.strftime("%m/%d/%Y")+"&nump=5&ID="+userID)
    try: 
        data = get_jsonparsed_data(url)
    except:
        print("Error fetching data.")
        return errorState
    if data["error"] != False:
        print("Error with received data.")
        return errorState
    i=0
    while i<len(data['phasedata']):
        if data["phasedata"][i]["phase"] == 'New Moon':
            newmoon = datetime.datetime.strptime(data["phasedata"][i]["date"]+ " "+data["phasedata"][i]["time"], "%Y %b %d %H:%M")
            fraction = (newmoon - curtime).total_seconds()/lunarmonth.total_seconds()
            numMove = 12-int(round(fraction*12))
            phases = rotl(phases,numMove)
            print("Next new moon: "+data["phasedata"][i]['date'])
            print("Fraction of lunar month until new moon: " + str(fraction))
            print("Shifting LEDs left: "+str(numMove))
            return phases & 0b111111
        i+=1
    print("Error. New moon not found")
    return errorState

#returns true if dark, false if not
def isDark():
    thres = darkUpperThres if darkState else darkLowerThres
    
    return True

#update the LEDS with the 6 bit seq
def updateLEDs(seq):
    print("LED arrangement: "+format(seq, '06b'))
    return True

#reset counter variables to initial condition
def initializeVariables():
    errorLevel = 0
    lastActive = datetime.datetime.strptime("2000 1 1", "%Y %m %d")
    lastError = datetime.datetime.strptime("2000 1 1", "%Y %m %d")
    leds = errorState
    return True


#-------------------------------------------------------------
initializeVariables()

while True:
    if isDark():
        #update the data if there's an error or significant time has elapsed since data was fetched
        if (leds == errorState and errorLevel < errorLimit) or datetime.datetime.now() - lastActive > updateDataTime:
            if datetime.datetime.now() - lastError > errorRetry:
                leds = getLEDSequence()
                lastActive = datetime.datetime.now()
                if leds == errorState:
                    lasterror = datetime.datetime.now()
                    errorLevel+=1
                    time.sleep(1)
                    next
                else:
                    errorLevel = 0
                updateLEDs(leds)
    else:
        #turn off the LEDs if it's bright and reset everything
        updateLEDs(0)
        initializeVariables()
        time.sleep(1)






