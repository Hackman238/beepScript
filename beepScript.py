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
from optparse import OptionParser

severity = '[5]'
eventState = '[0]'
prodState = '[1000]'
deviceClass = '/Network*'
cycleTime = '10'
zenossUser = 'zenoss_beep'
zenossPassword = 'password'
beepSound = 'file://' + str(os.getcwd()) + '/console-beep.mp3'
targetInstances = '{}'

# Option Parser
parser = OptionParser()

parser.add_option('-s', '--severity', dest='severity',
 help='Severity filter. 5=Critical/Red, 4=Error/Orange, 3=Warning/Yellow, 2=Info/Blue, 1=Gray/Debug, 0=Green/Cleared Ex. \"[5,4]\"', default=severity)
parser.add_option('-q', '--eventstate', dest='eventState',
 help='EventState filter. 0=New, 1=Acked, 2=Suppressed, 3=Closed, 4=Cleared, 5=Aged Ex. \"[0]\"', default=eventState)
parser.add_option('-y', '--prodstate', dest='prodState',
 help='ProdState filter. 1000=Production, 500=Pre-Production, 400=Test, 300=Maintenance, -1=Decommissioned Ex. \"[1000]\"', default=prodState)
parser.add_option('-k', '--deviceclass', dest='deviceClass',
 help='DeviceClass filter. Ex. \"/Network*\"', default=deviceClass)
parser.add_option('-t', '--cycletime', dest='cycleTime',
 help='Cycle time parameter.', default=cycleTime)
parser.add_option('-u', '--user', dest='zenossUser',
 help='Zenoss user for reading from ZEP.', default=zenossUser)
parser.add_option('-p', '--pass', dest='zenossPassword',
 help='Zenoss password for reading from ZEP.', default=zenossPassword)
parser.add_option('-b', '--beepsound', dest='beepSound',
 help='MP3 or WAV to play.', default=beepSound)
parser.add_option('-o', '--targetinstances', dest='targetInstances',
 help='Dictionary of target Zenoss instances to poll. Ex. \"{'Dallas':{'targetInstance':'http://zen1.dallas.myDomain.net:8080'},'London':{'targetInstance':'http://zen1.ilondon.myDomain.net:8080'},'Chicago':{'targetInstance':'http://zen1.chicago.myDomain.net:8080'},}\"', default=targetInstances)

(options, args) = parser.parse_args()

severity = eval(options.severity)
eventState = eval(options.eventState)
prodState = eval(options.prodState)
deviceClass = options.deviceClass
cycleTime = float(options.cycleTime)
zenossUser = options.zenossUser
zenossPassword = options.zenossPassword
beepSound = options.beepSound
targetInstances = eval(options.targetInstances)

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
            totalCount = -1
            zapi = ZAPI(debug = False, targetInstance = targetInstance, zenossUser = zenossUser, zenossPassword = zenossPassword)
            queryResult = zapi.get_events(severity = severity, eventState = eventState, prodState = prodState, deviceClass = deviceClass)
            totalCount = int(queryResult['totalCount'])
            overAllTotalEvents = overAllTotalEvents + totalCount
            if totalCount > 0:
                print "%s events need to be ACK in %s at %s" % (str(totalCount), target, nowString)
                ZenBeep.critical("%s events need to be ACK in %s at %s" % (str(totalCount), target, nowString))
                playSoundMethod(beepSound)
            elif totalCount == 0:
                ZenBeep.info("All events in %s are ACK at %s" % (target, nowString))
            elif totalCount == -1:
                ZenBeep.critical("Problem eith query against  %s at %s" % (target, nowString))
        except (KeyboardInterrupt, SystemExit):
            ZenBeep.info("Exited at %s" % (nowString))
            run = 0
            sys.exit(0)
        except:
            e = sys.exc_info()[:2]
            print "Failed to connect to %s at %s - ERROR %s" % (target, nowString, str(e))
            ZenBeep.critical("Failed to connect to %s at %s - ERROR %s" % (target, nowString, e))
            continue
        zapi = None
    if overAllTotalEvents == 0:
        print "All events are ACK at %s" % (nowString)
        ZenBeep.info("All events are ACK at %s" % (nowString))

if len(targetInstances) == 0:
   print "No targets specified"
   ZenBeep.info("No targets specified")
   run = 0
   sys.exit(0)

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
        sys.exit(0)
    except:
        e = sys.exc_info()[:2]
        print "Failure at %s - ERROR %s" % (nowString, e)
        ZenBeep.critical("Failure at %s - ERROR %s" % (nowString, e))

