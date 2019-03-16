# deCONZ Bridge
#
# Author: Smanar
#
"""
<plugin key="deCONZ" name="deCONZ plugin" author="Smanar" version="1.0.6" wikilink="https://github.com/Smanar/Domoticz-deCONZ" externallink="https://www.dresden-elektronik.de/funktechnik/products/software/pc-software/deconz/?L=1">
    <description>
        <br/><br/>
        <h2>deCONZ Bridge</h2><br/>
        It use the deCONZ rest api to make a bridge beetween your zigbee network and Domoticz (Using Conbee or Raspbee)
        <br/><br/>
        <h3>Remark</h3>
        <ul style="list-style-type:square">
            <li>You can use the file API_KEY.py if you have problems to get your API Key or your Websocket Port</li>
            <li>You can find updated files for deCONZ on their github : https://github.com/dresden-elektronik/deconz-rest-plugin</li>
            <li>If you want the plugin works without connexion, use as IP 127.0.0.1 (if deCONZ and domoticz are on same machine)</li>
            <li>If you are running the plugin for the first time, better to enable debug log (Take Debug info Only)</li>
        </ul>
        <h3>Supported Devices</h3>
        <ul style="list-style-type:square">
            <li>https://github.com/dresden-elektronik/deconz-rest-plugin/wiki/Supported-Devices</li>
        </ul>
        <h3>Configuration</h3>
        Gateway configuration
    </description>
    <params>
        <param field="Address" label="deCONZ IP" width="150px" required="true" default="127.0.0.1"/>
        <param field="Port" label="Port" width="150px" required="true" default="80"/>
        <param field="Mode1" label="Websocket port" width="75px" required="true" default="8088" />
        <param field="Mode2" label="API KEY" width="75px" required="true" default="1234567890" />
        <param field="Mode3" label="Debug" width="150px">
            <options>
                <option label="None" value="0"  default="true" />
                <option label="Debug info Only" value="2"/>
                <option label="Basic Debugging" value="62"/>
                <option label="Basic+Messages" value="126"/>
                <option label="Connections Only" value="16"/>
                <option label="Connections+Python" value="18"/>
                <option label="Connections+Queue" value="144"/>
                <option label="All" value="-1"/>
            </options>
        </param>
    </params>
</plugin>
"""

import Domoticz
import json,urllib, time
from fonctions import rgb_to_xy, rgb_to_hsl, xy_to_rgb
from fonctions import Count_Type, ProcessAllState, ProcessAllConfig, First_Json
from fonctions import ButtonconvertionXCUBE, ButtonconvertionXCUBE_R, ButtonconvertionTradfriRemote, ButtonconvertionGeneric

#Better to use 'localhost' ?
DOMOTICZ_IP = '127.0.0.1'

ANTIFLOOD = False
LIGHTLOG = True #To disable some activation, log will be lighter, but less informations.

#https://github.com/febalci/DomoticzEarthquake/blob/master/plugin.py
#https://stackoverflow.com/questions/32436864/raw-post-request-with-json-in-body

class BasePlugin:

    enabled = False

    def __init__(self):
        self.Devices = {} # id, type, banned
        self.SelectorSwitch = {} #IEEE,update,model
        self.Ready = False
        self.Buffer_Command = []
        self.Request = None
        self.Banned_Devices = []
        self.NeedWaitForCon = False
        self.BufferReceive = ''
        self.BufferLenght = 0

        self.bug = ''

        return

    def onStart(self):
        Domoticz.Debug("onStart called")
        #Domoticz.Error("xx : " + str('--a ---a \x01 \xFF \ua000 -a --  a\xac\u1234\u20ac\U00008000 -- - ---a '))
        #PyArg_ParseTuple
        #CreateDevice('1111','sensors','ZHAThermostat')
        self.bug = Parameters["Mode2"]

        #Check Domoticz IP
        if Parameters["Address"] != '127.0.0.1' and Parameters["Address"] != 'localhost':
            global DOMOTICZ_IP
            DOMOTICZ_IP = get_ip()
            Domoticz.Log("Your haven't use 127.0.0.1 as IP, so I suppose deCONZ and Domoticz aren't on same machine")
            Domoticz.Log("Taking " + DOMOTICZ_IP + " as Domoticz IP")

            if DOMOTICZ_IP == Parameters["Address"]:
                Domoticz.Status("Your have same IP for deCONZ and Domoticz why don't use 127.0.0.1 as IP")
        else:
            Domoticz.Log("Domoticz and deCONZ are on same machine")

        if Parameters["Mode3"] != "0":
            Domoticz.Debugging(int(Parameters["Mode3"]))
            #DumpConfigToLog()

        #Read banned devices
        with open(Parameters["HomeFolder"]+"banned_devices.txt", 'r') as myPluginConfFile:
            for line in myPluginConfFile:
                if not line.startswith('#'):
                    self.Banned_Devices.append(line.strip())
        myPluginConfFile.close()

        #Web socket connexion
        self.WebSocket = Domoticz.Connection(Name="deCONZ_WebSocket", Transport="TCP/IP", Address=Parameters["Address"], Port=Parameters["Mode1"])
        self.WebSocket.Connect()

        # Disabled, not working for selector ...
        #check for new icons
        #if 'bulbs_group' not in Images:
        #    try:
        #        Domoticz.Image('icons/bulbs_group.zip').Create()
        #    except:
        #        Domoticz.Error("Can't create new icons")

    def onStop(self):
        Domoticz.Debug("onStop called")
        self.WebSocket.Disconnect()

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect called")

        if Connection.Name == 'deCONZ_WebSocket':

            if (Status != 0):
                Domoticz.Error("WebSocket connexion error : " + str(Connection))
                Domoticz.Error("Status : " + str(Status) + " Description : " + str(Description) )
                return

            Domoticz.Status("Launching websocket on port " + str(Parameters["Mode1"]) )
            #Need to Add Sec-Websocket-Protocol : domoticz ????
            #Boring error > Socket Shutdown Error: 9, Bad file descriptor
            #"Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n" \
            wsHeader = "GET / HTTP/1.1\r\n" \
                        "Host: "+ Parameters["Address"] + ':' + Parameters["Mode1"] + "\r\n" \
                        "User-Agent: Domoticz/1.0\r\n" \
                        "Accept: Content-Type: text/html; charset=UTF-8\r\n" \
                        "Sec-WebSocket-Version: 13\r\n" \
                        "Origin: http://" + DOMOTICZ_IP + "\r\n" \
                        "Sec-WebSocket-Key: qqMLBxyyjz9Tog1bll7K6A==\r\n" \
                        "Connection: keep-alive, Upgrade\r\n" \
                        "Pragma: no-cache\r\n" \
                        "Cache-Control: no-cache\r\n" \
                        "Upgrade: websocket\r\n\r\n"
            self.WebSocket.Send(wsHeader)

        elif Connection.Name == 'deCONZ_Com':

            self.NeedWaitForCon = False

            if (Status != 0):
                Domoticz.Error("deCONZ connexion error : " + str(Connection))
                Domoticz.Error("Status : " + str(Status) + " Description : " + str(Description) )
                return

            if len(self.Buffer_Command) > 0:
                c = self.Buffer_Command.pop(0)
                #Domoticz.Log("### Send" + str(c))
                self.Request.Send(c)
                self.BufferReceive = ''

        else:
            Domoticz.Error("Unknow connexion : " + str(Connection))
            Domoticz.Error("Status : " + str(Status) + " Description : " + str(Description) )
            return

    def onMessage(self, Connection, Data):
        Domoticz.Debug("onMessage called")

        _Data = ''

        #Domoticz.Log("Data : " + str(Data))
        #Domoticz.Log("Connexion : " + str(Connection))
        #Domoticz.Log("Byte needed : " + str(Connection.BytesTransferred()) +  "ATM : " + str(len(Data)))
        #The max is 4096 so if the data size excess 4096 byte it will be cut

        #Websocket data ?
        if (Connection.Name == 'deCONZ_WebSocket'):
            if Data.startswith(b'\x81'):
                Data = Data.decode("utf-8", "ignore")
                p = Data.find('{')
                _Data = Data[p:]
            else:
                Domoticz.Debug("Websocket Http data : " + str(Data.decode("utf-8", "ignore").replace('\n','')) )
        #Normal connexion
        elif Connection.Name == 'deCONZ_Com':
            #New frame
            if Data.startswith(b'HTTP'):
                self.BufferLenght = len(Data)
                self.BufferReceive = ''
                Data = Data.decode("utf-8", "ignore")
                if Data[-1] == ']':
                    p = Data.find('[')
                else:
                    p = Data.find('{')
                _Data = Data[p:]
            else:
                self.BufferLenght += len(Data)
                _Data = Data.decode("utf-8", "ignore")

            self.BufferReceive = self.BufferReceive + _Data

            #Frame is completed ?
            l = Connection.BytesTransferred() - self.BufferLenght
            if l > 0:
                #Not complete frame
                Domoticz.Debug("Incomplete trame, miss " + str(l) + " bytes" )
                return

            _Data = self.BufferReceive
        else:
            Domoticz.Log("Unknow Connection" + str(Connection))
            Domoticz.Log("Data : " + str(Data))
            return

        #Clean data
        _Data = _Data.replace('true','True').replace('false','False').replace('null','None').replace('\n','').replace('\00','')
        #Domoticz.Debug("Data Cleaned : " + _Data)

        if not _Data:
            if Connection.Name == 'deCONZ_Com':
                self.Request.Disconnect()
            return

        if Connection.Name == 'deCONZ_Com':
            try:
                _Data = eval(_Data)
            except:
                Domoticz.Error("INVALID JSON Normal Connexion : " + str(_Data) )
                return

            #Complete frame, force disconnexion
            self.Request.Disconnect()

            #traitement
            self.NormalConnexion(_Data)

            #Next command ?
            self.UpdateBuffer()

        elif Connection.Name == 'deCONZ_WebSocket':
            try:
                _Data = eval(_Data)
            except:
                #Sometime the socket bug, trying to repair
                Domoticz.Log("Malformed JSON response, Trying to repair : " + str(_Data) )
                try:
                    last = ''
                    p = _Data.find('{')
                    while p != -1:
                        b = First_Json(_Data[p:])
                        if b:
                            _Data = _Data[len(b):]
                            p = _Data.find('{')
                            if last != b:
                                _Data2 = eval(b)
                                Domoticz.Log("New Data repaired : " + str(_Data2))
                                self.WebSocketConnexion(_Data2)
                                last = b
                        else:
                            break
                    return
                except:
                    Domoticz.Error("Can't repair malformed JSON: " + str(_Data) )
                    return

            self.WebSocketConnexion(_Data)
        else:
            Domoticz.Log("Unknow Connection" + str(Connection))
            Domoticz.Log("Data : " + str(Data))

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Log("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level) + ", Hue: " + str(Hue))

        if not self.Ready == True:
            Domoticz.Error("deCONZ not ready")
            return

        _type,deCONZ_ID = self.GetDevicedeCONZ(Devices[Unit].DeviceID)

        if _type == 'sensors':
            Domoticz.Error("This device don't support action")
            return

        #Homemade json
        _json = '{'

        #on/off
        if Command == 'On':
            _json += '"on":true,'
            if Level:
                _json += '"bri":' + str(round(Level*254/100)) + ','
        if Command == 'Off':
            _json += '"on":false,'

        #level
        if Command == 'Set Level':
            #To prevent bug
            _json += '"on":true,'

            _json += '"bri":' + str(round(Level*254/100)) + ','

            #thermostat situation
            if True == False:
                _json = '{"mode": "auto","heatsetpoint":' + Level

        #color
        if Command == 'Set Color':

            #To prevent bug
            _json += '"on":true,'

            Hue_List = json.loads(Hue)

            #ColorModeNone = 0   // Illegal
            #ColorModeNone = 1   // White. Valid fields: none
            if Hue_List['m'] == 1:
                ww = int(Hue_List['ww']) # Can be used as level for monochrome white
                #TODO : Jamais vu un device avec ca encore
                Domoticz.Debug("Not implemented device color 1")
            #ColorModeTemp = 2   // White with color temperature. Valid fields: t
            if Hue_List['m'] == 2:
                #Value is in mireds (not kelvin)
                #Correct values are from 153 (6500K) up to 588 (1700K)
                # t is 0 > 255
                TempKelvin = int(((255 - int(Hue_List['t']))*(6500-1700)/255)+1700);
                TempMired = 1000000 // TempKelvin
                #if previous not working
                #TempMired = round(float(Hue_List['t'])*(500.0f - 153.0f) / 255.0f + 153.0f)
                _json = _json + '"ct":' + str(TempMired) + ','
            #ColorModeRGB = 3    // Color. Valid fields: r, g, b.
            elif Hue_List['m'] == 3:
                IEEE = Devices[Unit].DeviceID
                if self.Devices[IEEE]['colormode'] == 'hs':
                    h,l,s = rgb_to_hsl((int(Hue_List['r']),int(Hue_List['g']),int(Hue_List['b'])))
                    hue = int(h * 65535)
                    saturation = int(s * 254)
                    value = int(l * 254/100)
                    _json = _json + '"hue":' + str(hue) + ',"sat":' + str(saturation) + ',"bri":' + str(value) + ',"transitiontime":0,'
                else:
                    x, y = rgb_to_xy((int(Hue_List['r']),int(Hue_List['g']),int(Hue_List['b'])))
                    x = round(x,6)
                    y = round(y,6)
                    _json = _json + '"xy":[' + str(x) + ','+ str(y) + '],'
            #ColorModeCustom = 4, // Custom (color + white). Valid fields: r, g, b, cw, ww, depending on device capabilities
            elif Hue_List['m'] == 4:
                ww = int(Hue_List['ww'])
                cw = int(Hue_List['cw'])
                x, y = rgb_to_xy((int(Hue_List['r']),int(Hue_List['g']),int(Hue_List['b'])))
                #TODO, Pas trouve de device avec ca encore ...
                Domoticz.Debug("Not implemented device color 2")

            #To prevent bug
            if '"bri":' not in _json:
                _json += '"bri":' + str(round(Level*254/100)) + ',"transitiontime":0,'

        if _json[-1] == ',':
            _json = _json[:-1]

        _json += '}'

        url = '/api/' + Parameters["Mode2"] + '/' + _type + '/' + str(deCONZ_ID)
        if _type == 'lights':
            url = url + '/state'
        elif _type == 'config':
            url = url + '/config'
        else:
            url = url + '/action'

        self.SendCommand(url,_json)

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        #Domoticz.Debug("onDisconnect called for " + str(Connection) )
        if Connection.Name == 'deCONZ_Com':
            self.UpdateBuffer()
        else:
            Domoticz.Status("onDisconnect called for " + str(Connection) )

    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat called")

        #Just to debug
        try:
            aa = Parameters["Mode2"]
        except Exception as inst:
            Domoticz.Error("Exception detail: '"+str(inst)+"'")
            Domoticz.Error("**** " + str(self.bug) + ' ' + str(Parameters))
            raise

        #Initialisation
        if self.Ready != True:
            Domoticz.Debug("### Initialisation > " + str(self.Ready))
            if ((self.Ready == False) or (self.Ready == 'lights')):
                self.Ready = "lights"
                Domoticz.Log("### Request lights")
                self.SendCommand("/api/" + Parameters["Mode2"] + "/lights/")

        #Check websocket connexion
        if not self.WebSocket.Connected():
            Domoticz.Error("WebSocket Disconnected, reconnexion !")
            self.WebSocket.Connect()

        #reset switchs
        for IEEE in self.SelectorSwitch:
            if self.SelectorSwitch[IEEE]['r'] == 1:
                _id = False
                for i in self.Devices:
                    if i == IEEE:
                        _id = self.Devices[i]['id']
                UpdateDevice(_id,'sensors', { 'nValue' : 0 , 'sValue' : 'Off' } )
                self.SelectorSwitch[IEEE]['r'] = 0

    def onDeviceRemoved(self,unit):
        Domoticz.Log("Device Removed")
        #TODO : Need to rescan all

#---------------------------------------------------------------------------------------

    def InitDeconz(self,_Data,First_item):
        #Read all devices

        if First_item:
            #Lights or sensors ?
            if 'uniqueid' in _Data[First_item]:
                for i in _Data:

                    IEEE = str(_Data[i]['uniqueid'])
                    Name = str(_Data[i]['name'])
                    Type = str(_Data[i]['type'])
                    Model = str(_Data[i].get('modelid',''))
                    if not Model:
                        Model = ''

                    #Type_device = 'lights'
                    #if not 'hascolor' in _Data[i]:
                    #    Type_device = 'sensors'
                    Type_device = self.Ready

                    Domoticz.Log("### Device > " + str(i) + ' Name:' + Name + ' Type:' + Type + ' Details:' + str(_Data[i]['state']))

                    self.Devices[IEEE] = {'id' : i , 'type' : Type_device }

                    #Skip banned device
                    if IEEE in self.Banned_Devices:
                        Domoticz.Log("Skipping Device (Banned) : " + str(IEEE) )
                        self.Devices[IEEE]['Banned'] = True
                        continue

                    #Get some infos
                    kwarg = {}
                    if 'state' in _Data[i]:
                        state = _Data[i]['state']
                        kwarg.update(ProcessAllState(state))
                        if 'colormode' in state:
                            self.Devices[IEEE]['colormode'] = state['colormode']

                    if 'config' in _Data[i]:
                        config = _Data[i]['config']
                        kwarg.update(ProcessAllConfig(config))

                    #hack
                    if Type == 'ZHAPower':
                        try:
                            if _Data[i]['manufacturername'] == 'OSRAM':
                                #This device not working
                                dummy,deCONZ_ID = self.GetDevicedeCONZ(IEEE)
                                if deCONZ_ID:
                                    self.DeleteDeviceFromdeCONZ(deCONZ_ID)
                                continue
                        except:
                            Domoticz.Log("### Can't disable unworking device : Osram plug")

                    #It's a switch ? Need special process
                    if Type == 'ZHASwitch' or Type == 'ZGPSwitch' or Type == 'CLIPSwitch':

                        #Set it to off
                        kwarg.update({'sValue': 'Off', 'nValue': 0})

                        if 'lumi.sensor_cube' in Model:
                            if IEEE.endswith('-03-000c'):
                                self.SelectorSwitch[IEEE] = { 't': 'XCube_R', 'r': 0 }
                            elif IEEE.endswith('-02-0012'):
                                self.SelectorSwitch[IEEE] = { 't': 'XCube_C', 'r': 0 }
                            else:
                                #Useless
                                #self.SelectorSwitch[IEEE] = { 't': 'XCube_R', 'r': 0 }
                                self.Devices[IEEE]['Banned'] = True
                                continue
                        elif 'TRADFRI remote control' in Model:
                            self.SelectorSwitch[IEEE] = { 't': 'Tradfri_remote', 'r': 0 }
                        else:
                            self.SelectorSwitch[IEEE] = { 't': 'Switch_Generic', 'r': 0 }

                    #Special device
                    if Type == 'ZHAPressure':#ZHAThermostat
                        self.Devices[IEEE + "_heatsetpoint"] = {'id' : i , 'type' : 'config'}

                    #Not exist > create
                    if GetDomoDeviceInfo(IEEE) == False:
                        if Type == 'ZHAThermostat':
                            CreateDevice(IEEE,Name,'ZHATemperature') #Temperature device
                            CreateDevice(IEEE + "_heatsetpoint" ,Name,'ZHAThermostat') #Setpoint device
                        elif self.SelectorSwitch.get(IEEE,False):
                            CreateDevice(IEEE,Name,self.SelectorSwitch[IEEE]['t'])
                        else:
                            CreateDevice(IEEE,Name,Type)

                    #update
                    if kwarg:
                        UpdateDevice(i,Type_device,kwarg)

            #groups
            else:
                for i in _Data:
                    Name = str(_Data[i]['name'])
                    Type = str(_Data[i]['type'])
                    Domoticz.Log("### Groupe > " + str(i) + ' Name:' + Name )
                    Dev_name = 'GROUP_' + Name.replace(' ','_')
                    self.Devices[Dev_name] = {'id' : i , 'type' : 'groups' }

                    #Create it in domoticz if not exist
                    if Dev_name in self.Banned_Devices:
                        Domoticz.Log("Skipping Group (Banned) : " + str(Dev_name) )
                        self.Devices[Dev_name]['Banned'] = True

                    else:
                        #Not exist > create
                        if GetDomoDeviceInfo(Dev_name) == False:
                            CreateDevice(Dev_name,Name,Type)

        #Update initialisation
        if self.Ready == "groups":
            self.Ready = True
            Domoticz.Status("### deCONZ ready")
            l,s,g,b,o = Count_Type(self.Devices)
            Domoticz.Status("### Found " + str(l) + " Operators, " + str(s) + " Sensors, " + str(g) + " Groups and " + str(o) + " others, with " + str(b) + " Ignored")

        elif self.Ready == "sensors":
            self.Ready = "groups"
            Domoticz.Log("### Request Groups")
            self.SendCommand("/api/" + Parameters["Mode2"] + "/groups/")

        elif self.Ready == "lights":
            self.Ready = "sensors"
            Domoticz.Log("### Request sensors")
            self.SendCommand("/api/" + Parameters["Mode2"] + "/sensors/")


    def NormalConnexion(self,_Data):

        Domoticz.Debug("Classic Data : " + str(_Data) )

        try:
            First_item = next(iter(_Data))
        except:
            #Special case, if the user don't have this kind of device >> _Data = {}
            if (self.Ready != True) and ( len(_Data) == 0) :
                self.InitDeconz(_Data,None)
            else:
                Domoticz.Error("Bad JSON response (or empty): " + str(_Data) )
            return

        # JSON with device list >  {'1': {'data:1}}
        if isinstance(First_item, str):
            if First_item.isnumeric():
                self.InitDeconz(_Data,First_item)
            else:
                Domoticz.Error("Not managed JSON : " + str(_Data) )

        else:
        #JSON with data returned >> _Data = [{'success': {'/lights/2/state/on': True}}, {'success': {'/lights/2/state/bri': 251}}]
            kwarg = {}
            _id = False
            _type = False
            _FakeJson = {}

            for _Data2 in _Data:

                First_item = next(iter(_Data2))

                #Command Error
                if First_item == 'error':
                    Domoticz.Error("deCONZ error :" + str(_Data2))
                    if _Data2['error']['type'] == 3:
                        dev = _Data2['error']['address'].split('/')
                        _id = dev[2]
                        _type = dev[1]
                        #Set red header
                        kwarg.update({'TimedOut':1})

                #Command sucess
                elif First_item == 'success':
                    data = _Data2['success']
                    dev = (list(data.keys())[0] ).split('/')
                    val = data[list(data.keys())[0]]

                    if len(dev) < 3:
                        Domoticz.Error("Not managed JSON : " + str(_Data2) )
                    else:
                        if not _id:
                            _id = dev[2]
                            _type = dev[1]

                        _FakeJson.update( { dev[4] : val } )

                else:
                    Domoticz.Error("Not managed JSON : " + str(_Data2) )

            if _FakeJson:
                kwarg.update(ProcessAllState( _FakeJson ))
            if kwarg:
                UpdateDevice(_id,_type,kwarg)

    def WebSocketConnexion(self,_Data):

        Domoticz.Debug("###### WebSocket Data : " + str(_Data) )

        if not self.Ready == True:
            Domoticz.Error("deCONZ not ready")
            return

        if 'e' in _Data:
            #Device just deleted ?
            if _Data['e'] == 'deleted':
                return
            if _Data['e'] == 'added':
                return

        kwarg = {}

        #MAJ State : _Data['e'] == 'changed'
        if 'state' in _Data:
            state = _Data['state']
            kwarg.update(ProcessAllState(state))

            if 'buttonevent' in state:
                IEEE = str(_Data['uniqueid'])
                if IEEE in self.SelectorSwitch:
                    if self.SelectorSwitch[IEEE]['t'] == 'XCube_C':
                        kwarg.update(ButtonconvertionXCUBE( state['buttonevent'] ) )
                        self.SelectorSwitch[IEEE]['r'] = 1
                    elif self.SelectorSwitch[IEEE]['t'] == 'XCube_R':
                        kwarg.update(ButtonconvertionXCUBE_R( state['buttonevent'] ) )
                        self.SelectorSwitch[IEEE]['r'] = 1
                    elif self.SelectorSwitch[IEEE]['t'] == 'Tradfri_remote':
                        kwarg.update(ButtonconvertionTradfriRemote( state['buttonevent'] ) )
                        self.SelectorSwitch[IEEE]['r'] = 1
                    else:
                        kwarg.update(ButtonconvertionGeneric( state['buttonevent'] ) )
                        self.SelectorSwitch[IEEE]['r'] = 1

            if 'reachable' in state:
                if state['reachable'] == True:
                    IEEE = _Data['uniqueid']
                    Unit = GetDomoDeviceInfo(IEEE)
                    LUpdate = Devices[Unit].LastUpdate
                    LUpdate=time.mktime(time.strptime(LUpdate,"%Y-%m-%d %H:%M:%S"))
                    current = time.time()

                    #Check if the device has been see, at least 10 s ago
                    if (current-LUpdate) > 10:
                        Domoticz.Status("###### Device just re-connected : " + str(_Data) + "Set to defaut state")
                        self.SetDeviceDefautState(IEEE,_Data['r'])
                    else:
                        Domoticz.Status("###### Device just re-connected : " + str(_Data) + "But ignored")

            if ('tampered' in state) or ('lowbattery' in state):
                tampered = state.get('tampered',False)
                lowbattery = state.get('lowbattery',False)
                if tampered or lowbattery:
                    kwarg.update({'TimedOut':1})
                    Domoticz.Error("###### Device with hardware defaut : " + str(_Data))


        #MAJ config
        elif 'config' in _Data:
            config = _Data['config']
            kwarg.update(ProcessAllConfig(config))

        else:
            Domoticz.Error("Unknow MAJ" + str(_Data) )

        if kwarg:
            UpdateDevice(_Data['id'],_Data['r'],kwarg)

    def DeleteDeviceFromdeCONZ(self,_id):
        url = '/api/' + Parameters["Mode2"] + '/sensors/' + str(_id)

        sendData = "DELETE " + url + " HTTP/1.1\r\n" \
                    "Host: " + Parameters["Address"] + ':' + Parameters["Port"] + "\r\n" \
                    "Connection: keep-alive\r\n\r\n"

        self.Buffer_Command.append(sendData)
        self.UpdateBuffer()

        Domoticz.Status("### Deleting device " + str(_id))

    def SendCommand(self,url,data=None):

        Domoticz.Debug("Send Command " + url + " with " + str(data))

        if data == None:
            sendData = "GET " + url + " HTTP/1.1\r\n" \
                        "Host: " + Parameters["Address"] + ':' + Parameters["Port"] + "\r\n" \
                        "User-Agent: Domoticz/1.0\r\n" \
                        "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n" \
                        "Connection: keep-alive\r\n\r\n"
        else:
            sendData = "PUT " + url + " HTTP/1.1\r\n" \
                        "Host: " + Parameters["Address"] + ':' + Parameters["Port"] + "\r\n" \
                        "User-Agent: Domoticz/1.0\r\n" \
                        "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n" \
                        "Content-Type: application/x-www-form-urlencoded\r\n" \
                        "Content-Length: " + str(len(data)) + "\r\n" \
                        "Connection: keep-alive\r\n\r\n"
            sendData = sendData + data + "\r\n"

        self.Buffer_Command.append(sendData)
        self.UpdateBuffer()

    def GetDevicedeCONZ(self,IEEE):
        for i in self.Devices:
            if i == IEEE:
                return self.Devices[IEEE]['type'],self.Devices[IEEE]['id']

        return False,False

    def UpdateBuffer(self):
        if len(self.Buffer_Command) == 0:
            return

        if ANTIFLOOD == False:
            self.NeedWaitForCon = False

        if (self.NeedWaitForCon == False) and (self.Request == None or not (self.Request.Connecting() or self.Request.Connected())):
            self.Request = Domoticz.Connection(Name="deCONZ_Com", Transport="TCP/IP", Address=Parameters["Address"] , Port=Parameters["Port"])
            self.Request.Connect()
            self.NeedWaitForCon = True

    def GetDeviceIEEE(self,_id,_type):
        for IEEE in self.Devices:
            if (self.Devices[IEEE]['type'] == _type) and (self.Devices[IEEE]['id'] == _id):
                if self.Devices[IEEE].get('Banned',False) == True:
                    return 'banned'
                return IEEE

        return False

    def SetDeviceDefautState(self,IEEE,_type):
        # Set bulb on same state than in domoticz
        if _type == 'lights':
            Unit = GetDomoDeviceInfo(IEEE)
            if Devices[Unit].nValue == 0:
                _json = '{"on":false}'
            else:
                _json = '{"on":true}'
            dummy,deCONZ_ID = self.GetDevicedeCONZ(IEEE)
            url = '/api/' + Parameters["Mode2"] + '/lights/' + str(deCONZ_ID) + '/state'
            self.SendCommand(url,_json)

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

def onDeviceRemoved(unit):
    global _plugin
    _plugin.onDeviceRemoved(unit)

    # Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return

def GetDeviceIEEE(id,type):
    global _plugin
    return _plugin.GetDeviceIEEE(id,type)

#*****************************************************************************************************

def get_ip():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def GetDomoDeviceInfo(IEEE):
    for x in Devices:
        if Devices[x].DeviceID == str(IEEE) :
            return x
    return False

def FreeUnit() :
    FreeUnit = ""
    for x in range(1,256):
        if x not in Devices :
            FreeUnit=x
            return FreeUnit
    if FreeUnit == "" :
        FreeUnit=len(Devices)+1
    return FreeUnit

def GetDomoUnit(_id,_type):
    try:
        IEEE = GetDeviceIEEE(_id,_type)

        if IEEE == 'banned':
            Domoticz.Log("Banned device > " + str(_id) + ' (' + str(_type) + ')')
            return False
        elif IEEE == False:
            Domoticz.Log("Device not in base, need resynchronisation ? > " + str(_id) + ' (' + str(_type) + ')')
            return False

        return GetDomoDeviceInfo(IEEE)
    except:
        return False

    return False

def UpdateDevice(_id,_type,kwarg):

    Unit = GetDomoUnit(_id,_type)

    if not Unit or not kwarg:
        Domoticz.Error("Can't Update Unit > " + str(_id) + ' (' + str(_type) + ')' )
        return

    #Check for special device.
    if 'heatsetpoint' in kwarg:
        v = kwarg.pop('heatsetpoint')
        IEEE = GetDeviceIEEE(_id,_type)
        Unit = GetDomoDeviceInfo(IEEE + '_heatsetpoint')
        kwarg['nValue'] = 0
        kwarg['nValue'] = str(v)

    NeedUpdate = False

    #Force update even there is no change, for exemple in case the user press a switch too fast, to not miss an event, But only for switch
    if (('nValue' in kwarg) or ('sValue' in kwarg)) and ('LevelNames' in Devices[Unit].Options):
        NeedUpdate = True

    if 'nValue' not in kwarg:
        kwarg['nValue'] = Devices[Unit].nValue
    if 'sValue' not in kwarg:
        kwarg['sValue'] = Devices[Unit].sValue
    if Devices[Unit].TimedOut != 0:
        kwarg['TimedOut'] = 0

    #Disabled because no update for battery or last seen for exemple
    #No need to trigger in this situation
    #if (kwarg['nValue'] == Devices[Unit].nValue) and (kwarg['nValue'] == Devices[Unit].nValue) and ('Color' not in kwarg):
    #    kwarg['SuppressTriggers'] = True

    for a in kwarg:
        if kwarg[a] != getattr(Devices[Unit], a ):
            NeedUpdate = True
            break
    if 'Color' in kwarg:
        NeedUpdate = True

    #force update, at least 1 every 24h
    if not NeedUpdate:
        LUpdate = Devices[Unit].LastUpdate
        LUpdate=time.mktime(time.strptime(LUpdate,"%Y-%m-%d %H:%M:%S"))
        current = time.time()
        if (current-LUpdate) > 86400:
            NeedUpdate = True

    if NeedUpdate or not LIGHTLOG:
        Domoticz.Debug("### Update  device ("+Devices[Unit].Name+") : " + str(kwarg))
        Devices[Unit].Update(**kwarg)
    else:
        Domoticz.Debug("### Update  device ("+Devices[Unit].Name+") : " + str(kwarg) + ", IGNORED , no changes !")

def CreateDevice(IEEE,_Name,_Type):
    kwarg = {}
    Unit = FreeUnit()
    TypeName = ''

    #Operator
    if _Type == 'Color light':
        kwarg['Type'] = 241
        kwarg['Subtype'] = 2
        kwarg['Switchtype'] = 7

    elif _Type == 'Extended color light':
        kwarg['Type'] = 241
        kwarg['Subtype'] = 7
        kwarg['Switchtype'] = 7

    elif _Type == 'Color temperature light':
        kwarg['Type'] = 241
        kwarg['Subtype'] = 8
        kwarg['Switchtype'] = 7

    elif _Type == 'Dimmable light':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 73
        kwarg['Switchtype'] = 7

    elif _Type == 'Smart plug' or _Type == 'On/Off plug-in unit':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 73
        kwarg['Switchtype'] = 0
        kwarg['Image'] = 1

    elif _Type == 'Window covering device':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 73
        kwarg['Switchtype'] = 16

    elif _Type == 'Door Lock':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 73
        kwarg['Switchtype'] = 0

    #Sensors
    elif _Type == 'Daylight':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 73
        kwarg['Switchtype'] = 9

    elif _Type == 'ZHATemperature' or _Type == 'CLIPTemperature':
        kwarg['TypeName'] = 'Temperature'

    elif _Type == 'ZHAHumidity' or _Type == 'CLIPHumidity':
        kwarg['TypeName'] = 'Humidity'

    elif _Type == 'ZHAPressure':
        kwarg['TypeName'] = 'Pressure'

    elif _Type == 'ZHAOpenClose' or _Type == 'CLIPOpenClose':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 73
        kwarg['Switchtype'] = 11

    elif _Type == 'ZHAPresence' or _Type == 'CLIPPresence':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 73
        kwarg['Switchtype'] = 8

    elif _Type == 'ZHALightLevel':
        kwarg['TypeName'] = 'Illumination'

    elif _Type == 'ZHAConsumption':
        kwarg['TypeName'] = 'Usage'

    elif _Type == 'ZHAPower':
        kwarg['TypeName'] = 'Usage'

    elif _Type == 'ZHAVibration':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 62
        kwarg['Switchtype'] = 2

    elif _Type == 'ZHAThermostat':
        kwarg['Type'] = 242
        kwarg['Subtype'] = 1

    elif _Type == 'ZHAAlarm':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 73
        kwarg['Switchtype'] = 2

    elif _Type == 'ZHAWater':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 62
        kwarg['Switchtype'] = 5
        kwarg['Image'] = 11 # Visible only on floorplan

    elif _Type == 'ZHAFire' or _Type == 'ZHACarbonMonoxide':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 62
        kwarg['Switchtype'] = 5

    elif _Type == 'CLIPGenericStatus':
        kwarg['TypeName'] = 'Text'

    elif _Type == 'CLIPGenericFlag':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 62
        kwarg['Switchtype'] = 2

    #Switch
    elif _Type == 'Switch_Generic':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 62
        kwarg['Switchtype'] = 18
        kwarg['Options'] = {"LevelActions": "||||||", "LevelNames": "Off|B1|B2|B3|B4|B5|B6|B7|B8", "LevelOffHidden": "true", "SelectorStyle": "0"}

    elif _Type == 'Tradfri_remote':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 62
        kwarg['Switchtype'] = 18
        kwarg['Options'] = {"LevelActions": "|||||", "LevelNames": "Off|On|More|Less|Right|Left", "LevelOffHidden": "true", "SelectorStyle": "0"}

    elif _Type == 'XCube_C':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 62
        kwarg['Switchtype'] = 18
        kwarg['Options'] = {"LevelActions": "||||||||", "LevelNames": "Off|Shak|Wake|Drop|90°|180°|Push|Tap", "LevelOffHidden": "true", "SelectorStyle": "0"}

    elif _Type == 'XCube_R':
        kwarg['TypeName'] = 'Custom'
        kwarg['Options'] = {"Custom": ("1;degree")}

    #groups
    elif _Type == 'LightGroup' or _Type == 'groups':
        kwarg['Type'] = 241
        kwarg['Subtype'] = 7
        kwarg['Switchtype'] = 7
        #if 'bulbs_group' in Images:
        #    kwarg['Image'] = Images['bulbs_group'].ID

    else:
        Domoticz.Error("Unknow device type " + _Type )
        return

    kwarg['DeviceID'] = IEEE
    kwarg['Name'] = _Name
    kwarg['Unit'] = Unit
    Domoticz.Device(**kwarg).Create()

    Domoticz.Status("### Create Device " + IEEE + " > " + _Name + ' (' + _Type +') as Unit ' + str(Unit) )
