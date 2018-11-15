# deCONZ Bridge
#
# Author: Smanar
#
"""
<plugin key="BasePlug" name="deCONZ plugin" author="xxx" version="1.0.0" wikilink="http://www.domoticz.com/wiki/plugins/plugin.html" externallink="https://www.google.com/">
    <description>
        <h2>deCONZ Bridge</h2><br/>
        Overview...
        <h3>Features</h3>
        <ul style="list-style-type:square">
            <li>Feature one...</li>
            <li>Feature two...</li>
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
                <option label="Python Only" value="2"/>
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
from fonctions import ReturnUpdateValue, Count_Type
from fonctions import ButtonconvertionXCUBE, ButtonconvertionXCUBE_R

#Better to use 'localhost' ?
DOMOTICZ_IP = '127.0.0.1'

#https://github.com/febalci/DomoticzEarthquake/blob/master/plugin.py
#https://stackoverflow.com/questions/32436864/raw-post-request-with-json-in-body

class BasePlugin:
    enabled = False
    def __init__(self):
        self.Devices = {}
        self.SelectorSwitch = {} #IEEE,update,model
        self.Ready = False
        self.Buffer_Command = []
        self.Request = None
        self.Banned_Devices = []

        return

    def onStart(self):
        Domoticz.Log("onStart called")
        
        if Parameters["Mode3"] != "0":
            Domoticz.Debugging(int(Parameters["Mode3"]))
            #DumpConfigToLog()
        
        #Read banned devices
        with open(Parameters["HomeFolder"]+"banned_devices.txt", 'r') as myPluginConfFile:
            self.Banned_Devices.append(myPluginConfFile.read())
        myPluginConfFile.close()
        
        #Web socket connexion
        self.WebSocket = Domoticz.Connection(Name="deCONZ_WebSocket", Transport="TCP/IP", Address=Parameters["Address"], Port=Parameters["Mode1"])
        self.WebSocket.Connect()

    def onStop(self):
        Domoticz.Log("onStop called")
        self.WebSocket.Disconnect()

    def onConnect(self, Connection, Status, Description):
        Domoticz.Log("onConnect called")
        
        ccc = str(Connection)
        
        if 'deCONZ_WebSocket' in ccc:
        
            if (Status != 0):
                Domoticz.Log("WebSocket connexion error : " + str(Connection))
                Domoticz.Log("Status : " + str(Status) + " Description : " + str(Description) )
                return
        
            Domoticz.Status("Laucnhing websocket")
            #Need to Add Sec-Websocket-Protocol : domoticz ????
            #Boring error > Socket Shutdown Error: 9, Bad file descriptor
            wsHeader = "GET / HTTP/1.1\r\n" \
                        "Host: "+ Parameters["Address"] + ':' + Parameters["Mode1"] + "\r\n" \
                        "User-Agent: Domoticz/1.0\r\n" \
                        "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n" \
                        "Sec-WebSocket-Version: 13\r\n" \
                        "Origin: http://" + DOMOTICZ_IP + "\r\n" \
                        "Sec-WebSocket-Key: qqMLBxyyjz9Tog1bll7K6A==\r\n" \
                        "Connection: keep-alive, Upgrade\r\n" \
                        "Pragma: no-cache\r\n" \
                        "Cache-Control: no-cache\r\n" \
                        "Upgrade: websocket\r\n\r\n"
            self.WebSocket.Send(wsHeader)

        elif 'deCONZ_Com' in ccc:
        
            if (Status != 0):
                Domoticz.Log("deCONZ connexion error : " + str(Connection))
                Domoticz.Log("Status : " + str(Status) + " Description : " + str(Description) )
                return

            if len(self.Buffer_Command) > 0:
                c = self.Buffer_Command.pop()
                self.Request.Send(c)

        else:
            Domoticz.Log("Unknow connexion : " + str(Connection))
            Domoticz.Log("Status : " + str(Status) + " Description : " + str(Description) )
            return

    def onMessage(self, Connection, Data):
        Domoticz.Debug("onMessage called")
        
        #Domoticz.Log("Data : " + str(Data))
        
        _Data = Data.decode("utf-8", "ignore")
        if _Data[-1] == ']':
            p = _Data.find('[')
        else:
            p = _Data.find('{')
        _Data = _Data[p:]
        _Data = _Data.replace('true','True').replace('false','False').replace('null','None')
        
        Domoticz.Debug("Data Cleaned : " + str(_Data))
            
        try:
            _Data = eval(_Data)
        except:
            Domoticz.Log("Data : " + str(Data))
            Domoticz.Error("Response not JSON format")
            return
        
        ccc = str(Connection)
        if 'deCONZ_WebSocket' in ccc:
            Domoticz.Log("###### WebSocket Data : " + str(_Data) )
            
            if not _Data:
                return
                
            if not self.Ready:
                Domoticz.Log("deCONZ not ready")
                return
            
            First_item = next(iter(_Data))
            
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
                if 'on' in state:
                    kwarg.update(ReturnUpdateValue( 'on' , state['on'] ) )
                if 'temperature' in state:
                    kwarg.update(ReturnUpdateValue( 'temperature' , state['temperature'] ) )
                if 'pressure' in state:
                    kwarg.update(ReturnUpdateValue( 'pressure' , state['pressure'] ) )
                if 'humidity' in state:
                    kwarg.update(ReturnUpdateValue( 'humidity' , state['humidity'] ) )
                if 'open' in state:
                    kwarg.update(ReturnUpdateValue( 'open' , state['open'] ) )
                if 'presence' in state:
                    kwarg.update(ReturnUpdateValue( 'presence' , state['presence'] ) )
                if 'lux' in state:
                    kwarg.update(ReturnUpdateValue( 'lux' , state['lux'] ) )
                if 'bri' in state:
                    kwarg.update(ReturnUpdateValue( 'bri' , state['bri'] ) )
                if 'buttonevent' in state:
                    IEEE = str(_Data['uniqueid'])
                    if IEEE in self.SelectorSwitch:
                        if self.SelectorSwitch[IEEE]['t'] == 'XCube_C':
                            kwarg.update(ButtonconvertionXCUBE( state['buttonevent'] ) )
                            self.SelectorSwitch[IEEE]['r'] = 1
                        if self.SelectorSwitch[IEEE]['t'] == 'XCube_R':
                            kwarg.update(ButtonconvertionXCUBE_R( state['buttonevent'] ) )
                            self.SelectorSwitch[IEEE]['r'] = 1
                    else:
                        kwarg.update(ReturnUpdateValue( 'buttonevent' , state['buttonevent'] ) )
                #if 'lastupdated' in state:
                #    kwarg.update(ReturnUpdateValue( 'lastupdated' , state['lastupdated'] ) )
                
                if 'reachable' in state:
                    if state['reachable'] == True:
                        IEEE = _Data['uniqueid']
                        Unit = GetDomoDeviceInfo(IEEE)
                        Domoticz.Status("###### Device just connected : " + str(_Data) )
                        LUpdate = Devices[Unit].LastUpdate
                        LUpdate=time.mktime(time.strptime(LUpdate,"%Y-%m-%d %H:%M:%S"))
                        current = time.time()
                        
                        #Check if the device has been see, at least 1 mn ago
                        if (current-LUpdate) > 10:
                            Domoticz.Status("###### Device just connected : " + str(_Data) )
                            self.SetDeviceDefautState(IEEE,_Data['r'])
                        else:
                            Domoticz.Status("###### Device just re-connected : " + str(_Data) + "But ignored")
                    else:
                        #Set red header
                        kwarg.update({'TimedOut':1})
                    
                #For groups
                if 'all_on' in state:
                    kwarg.update(ReturnUpdateValue( 'all_on' , state['all_on'] ) )
                if 'any_on' in state:
                    kwarg.update(ReturnUpdateValue( 'any_on' , state['any_on'] ) )

            #MAJ config
            elif 'config' in _Data:
                config = _Data['config']
                if 'battery' in config:
                    kwarg.update(ReturnUpdateValue( 'battery' , config['battery'] ) )
                
            else:
                Domoticz.Error("Unknow MAJ" + str(_Data) )
                
            #Domoticz.Log("###### "+ str(Unit) + str(kwarg) )
            if kwarg:
                UpdateDevice(_Data['id'],_Data['r'],kwarg)
            
        elif 'deCONZ_Com' in ccc:
        
            #Next command ?
            self.Request.Disconnect()
            self.UpdateBuffer()
            
            Domoticz.Log("Data : " + str(_Data) )
            
            if not _Data:
                return
        
            First_item = next(iter(_Data))

            if isinstance(First_item, str):
            
                #Read all devices
                if First_item.isnumeric():

                    #Lights or sensors ?
                    if 'uniqueid' in _Data[First_item]:
                        for i in _Data:
                        
                            IEEE = str(_Data[i]['uniqueid'])
                            Name = str(_Data[i]['name'])
                            Type = str(_Data[i]['type'])
                            
                            Domoticz.Log("### Device > " + str(i) + ' Name:' + Name + ' Type:' + Type + ' Details:' + str(_Data[i]['state']))
                            
                            self.Devices[IEEE] = {}
                            self.Devices[IEEE]['id'] = i
                            self.Devices[IEEE]['type'] = self.Ready
                            
                            
                            kwarg = {}
                            #Get some infos
                            if 'config' in _Data[i]:
                                config = _Data[i]['config']
                                if 'battery' in config:
                                    kwarg.update(ReturnUpdateValue( 'battery' , config['battery'] ) )
                                
                            #Create it in domoticz if not exist
                            if IEEE in self.Banned_Devices:
                                Domoticz.Log("Skipping Device (Banned) : " + str(IEEE) )
                                self.Devices[IEEE]['Banned'] = True
                                
                            else:
                                #It's a switch ? Need special process
                                if 'lumi.sensor_cube' in _Data[i]['modelid']:
                                    if IEEE.endswith('-03-000c'):
                                        self.SelectorSwitch[IEEE] = { 't': 'XCube_R', 'r': 0 }
                                    elif IEEE.endswith('-02-0012'):
                                        self.SelectorSwitch[IEEE] = { 't': 'XCube_C', 'r': 0 }
                                    else:
                                        #Useless
                                        #self.SelectorSwitch[IEEE] = { 't': 'XCube_R', 'r': 0 }
                                        self.Devices[IEEE]['Banned'] = True
                                        continue
                                        
                                #Not exist > create
                                if GetDomoDeviceInfo(IEEE) == False:
                                    if 'lumi.sensor_cube' in _Data[i]['modelid']:
                                        CreateDevice(IEEE,Name,self.SelectorSwitch[IEEE]['t'])
                                    else:
                                        CreateDevice(IEEE,Name,Type)
                                #Exist > update
                                else:
                                    if kwarg:
                                        Type_device = 'lights'
                                        if not 'hascolor' in _Data[i]:
                                            Type_device = 'sensors'
                                        UpdateDevice(i,Type_device,kwarg)

                    #groups
                    else:
                        for i in _Data:
                            Name = str(_Data[i]['name'])
                            Domoticz.Log("### Groupe > " + str(i) + ' Name:' + Name )
                            Dev_name = 'GROUP_' + Name
                            self.Devices[Dev_name] = {}
                            self.Devices[Dev_name]['id'] = i
                            self.Devices[Dev_name]['type'] = "groups"
                            
                            #Create it in domoticz if not exist
                            if Dev_name in self.Banned_Devices:
                                Domoticz.Log("Skipping Device (Banned) : " + str(Dev_name) )
                                self.Devices[Dev_name]['Banned'] = True
                                
                            else:
                                #Not exist > create
                                if GetDomoDeviceInfo(Dev_name) == False:
                                    CreateDevice(Dev_name,Name,'groups')
                            
                    #Update initialisation
                    if self.Ready == "groups":
                        self.Ready = True
                        Domoticz.Status("### deCONZ ready")
                        l,s,g = Count_Type(self.Devices)
                        Domoticz.Status("### Found " + str(l) + " Operators, " + str(s) + " Sensors and " + str(g) + " Groups")

                    if self.Ready == "sensors":
                        self.Ready = "groups"
                        Domoticz.Log("### Request Groups")
                        self.SendCommand("/api/" + Parameters["Mode2"] + "/groups/")
                            
                    if self.Ready == "lights":
                        self.Ready = "sensors"
                        Domoticz.Log("### Request sensors")
                        self.SendCommand("/api/" + Parameters["Mode2"] + "/sensors/")

                else:
                    Domoticz.Error("Not managed JSON : " + str(_Data) )
            
            else:
                kwarg = {}
                _id = False
                _type = False
                    
                for _Data2 in _Data:
                
                    First_item = next(iter(_Data2))
                    
                    #Error
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
                        #TODO : need to be sure of order color > level > on-off
                        data = _Data2['success']
                        dev = (list(data.keys())[0] ).split('/')
                        val = data[list(data.keys())[0]]
                        
                        if not _id:
                            _id = dev[2]
                            _type = dev[1]

                        kwarg.update(ReturnUpdateValue(dev[4],val))
                        
                    else:
                        Domoticz.Error("Not managed JSON : " + str(_Data2) )
                        
                if kwarg:
                    UpdateDevice(_id,_type,kwarg)

        else:
            Domoticz.Log("Unknow Connection" + str(Connection))
            Domoticz.Log("Data : " + str(Data))


    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Log("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level) + ", Hue: " + str(Hue))
        
        #Homemade json
        _json = '{'
        
        #on/off
        if Command == 'On':
            _json =_json + '"on":true,'
            _json = _json + '"bri":' + str(round(Level*254/100)) + ','
        if Command == 'Off':
            _json =_json + '"on":false,'
            
        #To prevent bug
        if Command == 'Set Level' or Command == 'Set Color':
            _json =_json + '"on":true,'

        #level
        if Command == 'Set Level':
            _json = _json + '"bri":' + str(round(Level*254/100)) + ','
        
        #color
        if Command == 'Set Color':
        
            _json = _json + '"bri":' + str(round(Level*254/100)) + ','
        
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
            #With saturation and hue, not seen in domoticz but present on deCONZ, and some device need it
            elif Hue_List['m'] == 9998:
                h,l,s = rgb_to_hsl((int(Hue_List['r']),int(Hue_List['g']),int(Hue_List['b'])))
                saturation = s * 100   #0 > 100
                hue = h *360           #0 > 360
                hue = int(hue*254//360)
                saturation = int(saturation*254//100)
                value = int(l * 254//100)
                _json = _json + '"hue":' + str(hue) + ',"sat":' + str(saturation) + ',"bri":' + str(value) + ','

        if _json[-1] == ',':
            _json = _json[:-1]
            
        _json = _json + '}'
                
        _type,deCONZ_ID = self.GetDevicedeCONZ(Devices[Unit].DeviceID)
        
        url = '/api/' + Parameters["Mode2"] + '/' + _type + '/' + str(deCONZ_ID)
        if _type == 'lights':
            url = url + '/state'
        else:
            url = url + '/action'
        self.SendCommand(url,_json)

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Debug("onDisconnect called for " + str(Connection) )
        ccc = str(Connection)
        if 'deCONZ_Com' in ccc:
            self.UpdateBuffer()

    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat called")
        if self.Ready != True:
            if self.Ready == False:
                self.Ready = "lights"
                Domoticz.Log("### Request lights")
                self.SendCommand("/api/" + Parameters["Mode2"] + "/lights/")
                
        #reset switch
        for IEEE in self.SelectorSwitch:
            if self.SelectorSwitch[IEEE]['r'] == 1:
                kwarg = {}
                kwarg['nValue'] = 0
                kwarg['sValue'] = 'Off'
                _id = False
                for i in self.Devices:
                    if i == IEEE:
                        _id = self.Devices[i]['id']
                UpdateDevice(_id,'sensors',kwarg)
                self.SelectorSwitch[IEEE]['r'] = 0
                
    def onDeviceRemoved(self,unit):
        Domoticz.Log("Device Removed")
        #TODO : Need to rescan all
        
    def SendCommand(self,url,data=None):
    
        Domoticz.Log("Send Command " + url + " with " + str(data))
    
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

        return False
        
    def UpdateBuffer(self):
        if len(self.Buffer_Command) == 0:
            return
            
        if (self.Request == None or not (self.Request.Connecting() or self.Request.Connected())):
            self.Request = Domoticz.Connection(Name="deCONZ_Com", Transport="TCP/IP", Address=Parameters["Address"] , Port=Parameters["Port"])
            self.Request.Connect()
            
    def GetDeviceIEEE(self,_id,_type):
        for IEEE in self.Devices:
            if (self.Devices[IEEE]['type'] == _type) and (self.Devices[IEEE]['id'] == _id):
                if self.Devices[IEEE].get('Banned',False) == True:
                    return False
                return IEEE

        return False

    def SetDeviceDefautState(self,IEEE,_type):
        # Set it off if bulb
        if _type == 'lights':
            _json = '{"on":false}'
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
        
        if IEEE == False:
            Domoticz.Log("Banned device > " + str(_id) + ' (' + str(_type) + ')')
            return False

        Unit = GetDomoDeviceInfo(IEEE)
    except:
        Domoticz.Error("Can't Update Unit > " + str(_id) + ' (' + str(_type) + ')' )
        return False
    return Unit
    
def UpdateDevice(_id,_type,kwarg):
        
    Unit = GetDomoUnit(_id,_type)
    
    if not Unit or not kwarg:
        return
        
    if 'nValue' not in kwarg:
        kwarg['nValue'] = Devices[Unit].nValue
    if 'sValue' not in kwarg:
        kwarg['sValue'] = Devices[Unit].sValue
    if Devices[Unit].TimedOut != 0:
        kwarg['TimedOut'] = 0

    Domoticz.Log("### Update  device ("+Devices[Unit].Name+") : " + str(kwarg))
    Devices[Unit].Update(**kwarg)

def CreateDevice(IEEE,_Name,_Type):
    kwarg = {}
    Unit = FreeUnit()
    TypeName = ''
    
    if _Type == 'Color light':
        kwarg['Type'] = 241
        kwarg['Subtype'] = 2
        kwarg['Switchtype'] = 7
        
    elif _Type == 'Dimmable light':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 73
        kwarg['Switchtype'] = 7
        
    elif _Type == 'Daylight':
        kwarg['TypeName'] = 'Illumination'
        
    elif _Type == 'ZHATemperature':
        kwarg['TypeName'] = 'Temperature'
        
    elif _Type == 'ZHAHumidity':
        kwarg['TypeName'] = 'Humidity'
        
    elif _Type == 'ZHAPressure':
        kwarg['TypeName'] = 'Pressure'
        
    elif _Type == 'ZHAOpenClose':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 73
        kwarg['Switchtype'] = 11
        
    elif _Type == 'ZHAPresence':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 73
        kwarg['Switchtype'] = 8
        
    elif _Type == 'ZHALightLevel':
        kwarg['TypeName'] = 'Illumination'
        
    elif _Type == 'ZHAAlarm':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 73
        kwarg['Switchtype'] = 2
        
    elif _Type == 'ZHASwitch':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 73
        kwarg['Switchtype'] = 9
        
    elif _Type == 'XCube_C':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 62
        kwarg['Switchtype'] = 18
        kwarg['Options'] = {"LevelActions": "||||||||", "LevelNames": "Off|Shak|Wake|Drop|90°|180°|Push|Tap", "LevelOffHidden": "true", "SelectorStyle": "0"}
        
    elif _Type == 'XCube_R':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 62
        kwarg['Switchtype'] = 18
        kwarg['Options'] = {"LevelActions": "|||", "LevelNames": "Off|Left Rot|Right Rot", "LevelOffHidden": "true", "SelectorStyle": "0"}
        
    elif _Type == 'groups':
        kwarg['Type'] = 241
        kwarg['Subtype'] = 2
        kwarg['Switchtype'] = 7

    else:
        Domoticz.Error("Unknow device type " + _Type )
        return

    kwarg['DeviceID'] = IEEE
    kwarg['Name'] = _Name
    kwarg['Unit'] = Unit
    Domoticz.Device(**kwarg).Create()
    
    Domoticz.Status("### Create Device " + IEEE + " > " + _Name )
