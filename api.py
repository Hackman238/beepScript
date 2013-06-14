# Zenoss-4.x JSON API Example (python)
#
# To quickly explore, execute 'python -i api_example.py'
#
# >>> z = ZAPI()
# >>> events = z.get_events()
# etc.

import json
import urllib
import urllib2

ROUTERS = { 'MessagingRouter': 'messaging',
            'EventsRouter': 'evconsole',
            'ProcessRouter': 'process',
            'ServiceRouter': 'service',
            'DeviceRouter': 'device',
            'NetworkRouter': 'network',
            'TemplateRouter': 'template',
            'DetailNavRouter': 'detailnav',
            'ReportRouter': 'report',
            'MibRouter': 'mib',
            'ZenPackRouter': 'zenpack' }

class ZAPI():
    targetInstance='http://localhost:8080'
    def __init__(self, debug=False, targetInstance=targetInstance, zenossUser='admin', zenossPassword='zenoss'):
        """
        Initialize the API connection, log in, and store authentication cookie
        """
        self.targetInstance=targetInstance
        # Use the HTTPCookieProcessor as urllib2 does not save cookies by default
        self.urlOpener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        if debug: self.urlOpener.add_handler(urllib2.HTTPHandler(debuglevel=1))
        self.reqCount = 1

        # Contruct POST params and submit login.
        loginParams = urllib.urlencode(dict(
                        __ac_name = zenossUser,
                        __ac_password = zenossPassword,
                        submitted = 'true',
                        came_from = targetInstance + '/zport/dmd'))
        self.urlOpener.open(targetInstance + '/zport/acl_users/cookieAuthHelper/login',
                            loginParams)

    def _router_request(self, router, method, data=[]):
        if router not in ROUTERS:
            raise Exception('Router "' + router + '" not available.')

        # Contruct a standard URL request for API calls
        req = urllib2.Request(self.targetInstance + '/zport/dmd/' +
                              ROUTERS[router] + '_router')

        # NOTE: Content-type MUST be set to 'application/json' for these requests
        req.add_header('Content-type', 'application/json; charset=utf-8')

        # Convert the request parameters into JSON
        reqData = json.dumps([dict(
                    action=router,
                    method=method,
                    data=data,
                    type='rpc',
                    tid=self.reqCount)])

        # Increment the request count ('tid'). More important if sending multiple
        # calls in a single request
        self.reqCount += 1

        # Submit the request and convert the returned JSON to objects
        return json.loads(self.urlOpener.open(req, reqData).read())

    def get_devices(self, deviceClass='/zport/dmd/Devices'):
        return self._router_request('DeviceRouter', 'getDevices',
                                    data=[{'uid': deviceClass,
                                           'params': {} }])['result']

    def close_events(self, evids=None):
        return self._router_request('EventsRouter', 'close', data=[{'evids': evids,'params': {'severiy':[5,4,3,2]} }])['result']

    def get_events(self, device=None, component=None, deviceClass='/Server*', eventClass=None, severity=[5,4,3,2], eventState=[0,1], prodState=[1000]):
        data = dict(start=0, limit=100, dir='DESC', sort='severity')
        data['params'] = dict(severity=severity, eventState=eventState, DeviceClass=deviceClass)

        if device: data['params']['device'] = device
        if component: data['params']['component'] = component
        if prodState: data['params']['prodState'] = prodState

        return self._router_request('EventsRouter', 'query', [data])['result']

    def get_events_gen(self):
        data = dict(dir='DESC', sort='lastTime')
        data['params'] = dict(eventState=[])

        return self._router_request('EventsRouter', 'queryGenerator', [data])['result']

    def add_device(self, deviceName, deviceClass):
        data = dict(deviceName=deviceName, deviceClass=deviceClass)
        return self._router_request('DeviceRouter', 'addDevice', [data])

    def get_device_components(self, uid):
        if uid:
           return self._router_request('DeviceRouter', 'getComponents', data=[{'uid':uid}])


    def delete_device(self, uids):
        if uids:
            params={'productionState':['1000','500','400','300', '-1']}
            return self._router_request('DeviceRouter', 'removeDevices', data=[{'sort':'name', 'dir':'ASC', 'uids':uids, 'hashcheck':'0', 'action':'delete', 'deleteEvents':'true', 'deletePerf':'true', 'params': params }])['result']


    def create_event_on_device(self, device, severity, summary):
        if severity not in ('Critical', 'Error', 'Warning', 'Info', 'Debug', 'Clear'):
            raise Exception('Severity "' + severity +'" is not valid.')

        data = dict(device=device, summary=summary, severity=severity,
                    component='', evclasskey='', evclass='')
        return self._router_request('EventsRouter', 'add_event', [data])
