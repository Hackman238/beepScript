===============================================================================
Zenoss beepScript
===============================================================================


About
-------------------------------------------------------------------------------
Script designed to test multiple Zenoss instances from a client machine and create an audible 'beep' from the client PC based on matching event criteria.

Prerequisites
-------------------------------------------------------------------------------

==================  =========================================================
Prerequisite        Restriction
==================  =========================================================
Product             Zenoss 4.0 or higher
Required ZenPacks   None
Other dependencies  None
==================  =========================================================


Usage
-------------------------------------------------------------------------------
Edit beepScript.pt

Configuration
-------------------------------------------------------------------------------
Severity - 5=Critical/Red, 4=Error/Orange, 3=Warning/Yellow, 2=Info/Blue, 1=Gray/Debug, 0=Green/Cleared
 Set the severity list to a list of severities you'd like to filter.
 Example:
     severity = [5,4]

EventState - 0=New, 1=Acked, 2=Suppressed, 3=Closed, 4=Cleared, 5=Aged
 Set the eventState list to a list of statuses you'd like to filter.
 Example:
     eventState = [0,1]

ProductionState - 1000=Production, 500=Pre-Production, 400=Test, 300=Maintenance, -1=Decommissioned
 Set the prodState list to a list of production states you'd like to filter.
 Example:
     prodState = [1000]

DeviceClass - Add * to include subclasses
 Set to a simple regex to include deviceClasses
 Example:
     deviceClass = '/Network*'

Query Config - Int
 Set to the number of seconds between each poll
 Example:
     cycleTime = 5

Zenoss authentication - user/password
 Set the user and password for the script to authenticate with. Requires only ZenUser role.
 Example:
     zenossUser = 'zenoss_beep'

     zenossPassword = 'myReallyBadPassword'

beepSound - File path
 Set to the patch of the beep sound you'd like to play. The default plays console-beep.mp3 from the beepScript folder.
 Example:
     beepSound = 'file://' + str(os.getcwd()) + '/console-beep.mp3'

Query targets - URLs
 Set add each target Zenoss instance you'd like to query for events
 Example:
     targetInstances = {'Dallas':{'targetInstance':'http://zen1.dallas.myDomain.net:8080'},'London':{'targetInstance':'http://zen1.ilondon.myDomain.net:8080'},'Chicago':{'targetInstance':'http://zen1.chicago.myDomain.net:8080'},}

Appendix Related Daemons
-------------------------------------------------------------------------------

============  ===============================================================
Type          Name
============  ===============================================================
None
============  ===============================================================
