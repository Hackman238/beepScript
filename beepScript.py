#!/usr/bin/env python

from api import ZAPI
import os, time, thread
import sys
import glib, gobject
from sound import playSound
from time import gmtime, strftime
import logging
from datetime import datetime
import __main__
import logging.handlers

## Query Critiera for Beepable Events ##
# Severity 5=Critical/Red, 4=Error/Orange, 3=Warning/Yellow, 2=Info/Blue, 1=Gray/Debug, 0=Green/Cleared
severity = [5]
# EventState 0=New, 1=Acked, 2=Suppressed, 3=Closed, 4=Cleared, 5=Aged
eventState = [0]
#ProductionState 1000=Production, 500=Pre-Production, 400=Test, 300=Maintenance, -1=Decommissioned
prodState = [1000]
#DeviceClass - Add * to include subclasses
deviceClass = '/Network*'

# Query Config
cycleTime = 5
zenossUser = 'zenoss_beep'
zenossPassword = 'abc123'
beepSound = 'file://' + str(os.getcwd()) + '/console-beep.mp3'

# Query targets
targetInstances = {'Dallas':{'targetInstance':'http://zen1.dallas.myDomain.net:8080'},'London':{'targetInstance':'http://zen1.ilondon.myDomain.net:8080'},'Chicago':{'targetInstance':'http://zen1.chicago.myDomain.net:8080'},}

# Setup appPath
appPath=os.path.dirname(os.path.abspath(getattr(__main__,'__file__','__main__.py')))

# Setup Logging and SysLogger
levels = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}

logName = appPath + "/zenoss_beeps.log"
level = levels.get('debug', logging.NOTSET)
logging.basicConfig(filename=logName, level=level)

ZenBeep = logging.getLogger('ZenBeep')
ZenBeep.setLevel(logging.DEBUG)
handler = logging.handlers.SysLogHandler(address = '/dev/log')
ZenBeep.addHandler(handler)

run = 1

# Method for Playback
def playSoundMethod(uri):
    global loop
    loop = glib.MainLoop()
    playSoundClass = playSound(uri, loop=loop)
    thread.start_new_thread(playSoundClass.start, ())
    gobject.threads_init()
    loop.run()


# Main JSON query loop
def mainQuery(severity, eventState, prodState, deviceClass):
    overAllTotalEvents = 0
    totalCount = 0
    for target in targetInstances.iterkeys():
        targetInstance = targetInstances[target]['targetInstance']
        queryResult = None
        nowString = strftime("%a, %d %b %H:%M", gmtime())
        try:
            zapi = ZAPI(debug = False, targetInstance = targetInstance, zenossUser = zenossUser, zenossPassword = zenossPassword)
            queryResult = zapi.get_events(severity = severity, eventState = eventState, prodState = prodState, deviceClass = deviceClass)
            totalCount = int(queryResult['totalCount'])
            overAllTotalEvents = overAllTotalEvents + totalCount
            if totalCount > 0:
                print "%s events need to be ACK in %s at %s" % (str(totalCount), target, nowString)
                ZenBeep.critical("%s events need to be ACK in %s at %s" % (str(totalCount), target, nowString))
                playSoundMethod(beepSound)
            else:
                ZenBeep.info("All events in %s are ACK at %s" % (target, nowString))
        except:
            e = sys.exc_info()
            print "Failed to connect to %s at %s - ERROR %s" % (target, nowString, e)
            ZenBeep.critical("Failed to connect to %s at %s - ERROR %s" % (target, nowString, e))
            continue
        zapi = None

    if overAllTotalEvents == 0:
        print "All events are ACK at %s" % (nowString)
        ZenBeep.info("All events are ACK at %s" % (nowString))


# Main Loop
while(run == 1):
    try:
        os.system('clear')
        nowString = strftime("%a, %d %b %H:%M", gmtime())
        ZenBeep.info("Checking for events matching severity=%s, eventState=%s, prodState=%s, deviceClass=%s at %s" % (severity, eventState, prodState, deviceClass, nowString))
        mainQuery(severity, eventState, prodState, deviceClass)
        ZenBeep.info("Checking events at %s" % (cycleTime))
        time.sleep(cycleTime)
    except (KeyboardInterrupt, SystemExit):
        ZenBeep.info("Exited at %s" % (nowString))
        run = 0
    except:
        e = sys.exc_info()
        print "Failure at %s - ERROR %s" % (nowString, e)
        ZenBeep.critical("Failure at %s - ERROR %s" % (nowString, e))
