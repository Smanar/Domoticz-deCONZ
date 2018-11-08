# Basic Python Plugin Example
#
# Author: Smanar
#
"""
<plugin key="BasePlug" name="deCONZ plugin" author="xxx" version="1.0.0" wikilink="http://www.domoticz.com/wiki/plugins/plugin.html" externallink="https://www.google.com/">
    <description>
        <h2>Plugin Title</h2><br/>
        Overview...
        <h3>Features</h3>
        <ul style="list-style-type:square">
            <li>Feature one...</li>
            <li>Feature two...</li>
        </ul>
        <h3>Devices</h3>
        <ul style="list-style-type:square">
            <li>Device Type - What it does...</li>
        </ul>
        <h3>Configuration</h3>
        Configuration options...
    </description>
    <params>
        <param field="Address" label="deCONZ IP" width="150px" required="true" default="127.0.0.1"/>
        <param field="Port" label="Port" width="150px" required="true" default="80"/>
        <param field="Mode1" label="Websocket port" width="75px" required="true" default="8088" />
        <param field="Mode2" label="API KEY" width="75px" required="true" default="1234567890" />
    </params>
</plugin>
"""
import Domoticz
import json,urllib
from fonctions import rgb_to_xy, rgb_to_hsl, xy_to_rgb
from fonctions import ReturnUpdateValue


LIGHT = 10
SENSOR = 11
GROUP = 12

#https://github.com/febalci/DomoticzEarthquake/blob/master/plugin.py
#https://stackoverflow.com/questions/32436864/raw-post-request-with-json-in-body

def GetResponse(url):
    #html = urllib.request.urlopen(url, timeout=5)
    return 'ok'#html.decode("utf8")


class BasePlugin:
    enabled = False
    def __init__(self):
        self.ListLights = {}
        self.ListSensors = {}
        self.ListGroups = {}
        self.Init = False
        self.Buffer_Command = []
        self.Request = None
        self.Banned_Devices = []
        return

    def onStart(self):
        Domoticz.Log("onStart called")
        
        #Domoticz.Debugging(62+64)
        
        #Read banned devices
        with open(Parameters["HomeFolder"]+"banned_devices.txt", 'r') as myPluginConfFile:
            self.Banned_Devices.append(myPluginConfFile.read())
        myPluginConfFile.close()
        
        #Web socket connexion
        self.WebSocket = Domoticz.Connection(Name="deCONZ_WebSocket", Transport="TCP/IP", Address=Parameters["Address"], Port=Parameters["Mode1"])
        self.WebSocket.Connect()

    def onStop(self):
        Domoticz.Log("onStop called")

    def onConnect(self, Connection, Status, Description):
        Domoticz.Log("onConnect called")
        
        ccc = str(Connection)
        
        if 'deCONZ_WebSocket' in ccc:
        
            if (Status != 0):
                Domoticz.Log("WebSocket connexion error : " + str(Connection))
                Domoticz.Log("Status : " + str(Status) + " Description : " + str(Description) )
                return
        
            Domoticz.Status("Laucnhing websocket")
            wsHeader = "GET / HTTP/1.1\r\n" \
                        "Host: "+ Parameters["Address"] + "\r\n" \
                        "User-Agent: Domoticz/1.0\r\n" \
                        "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n" \
                        "Sec-WebSocket-Version: 13\r\n" \
                        "Origin: http://" + Parameters["Address"] + "\r\n" \
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
        Domoticz.Log("onMessage called")
        
        #Domoticz.Log("Data : " + str(Data))
        
        _Data = Data.decode("utf-8", "ignore")
        if _Data[-1] == ']':
            p = _Data.find('[')
        else:
            p = _Data.find('{')
        _Data = _Data[p:]
        _Data = _Data.replace('true','True').replace('false','False').replace('null','None')
        
        Domoticz.Log("Data Cleaned : " + str(_Data))
            
        try:
            _Data = eval(_Data)
        except:
            Domoticz.Log("Data : " + str(Data))
            Domoticz.Error("Response not JSON format")
            return
        
        ccc = str(Connection)
        if 'deCONZ_WebSocket' in ccc:
            Domoticz.Log("###### WebSocket Data : " + str(_Data) )
            First_item = next(iter(_Data))
            
            kwarg = {}

            #MAJ State
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
                #if 'lastupdated' in state:
                #    kwarg.update(ReturnUpdateValue( 'lastupdated' , state['lastupdated'] ) )
                
                if 'reachable' in state and state['reachable'] == True:
                    Domoticz.Status("###### Device just connected : " + str(_Data) )
                    
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
                            
                            if self.Init == LIGHT:
                                self.ListLights[i] = IEEE
                            if self.Init == SENSOR:
                                self.ListSensors[i] = IEEE
                            
                            kwarg = {}
                            #Get some infos
                            if 'config' in _Data[i]:
                                config = _Data[i]['config']
                                if 'battery' in config:
                                    kwarg.update(ReturnUpdateValue( 'battery' , config['battery'] ) )
                                
                            #Create it in domoticz if not exist
                            if IEEE in self.Banned_Devices:
                                Domoticz.Log("Skipping Device (Banned) : " + str(IEEE) )
                                
                            else:
                                #Not exist > create
                                if GetDomoDeviceInfo(IEEE) == False:
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
                            
                            self.ListGroups[i] = Dev_name
                            
                            #Create it in domoticz if not exist
                            if Dev_name in self.Banned_Devices:
                                Domoticz.Log("Skipping Device (Banned) : " + str(Dev_name) )
                                
                            else:
                                #Not exist > create
                                if GetDomoDeviceInfo(Dev_name) == False:
                                    CreateDevice(Dev_name,Name,'groups')
                            
                    #Update initialisation
                    if self.Init == GROUP:
                        self.Init = True
                            
                    if self.Init == SENSOR:
                        self.Init = GROUP
                        Domoticz.Log("### Request Groups")
                        self.SendCommand("/api/" + Parameters["Mode2"] + "/groups/")
                            
                    if self.Init == LIGHT:
                        self.Init = SENSOR
                        Domoticz.Log("### Request sensors")
                        self.SendCommand("/api/" + Parameters["Mode2"] + "/sensors/")

                else:
                    Domoticz.Error("Not managed JSON : " + str(_Data) )
            
            else:
                kwarg = {}
                Unit = False
                    
                for _Data2 in _Data:
                
                    First_item = next(iter(_Data2))
                    
                    #Error
                    if First_item == 'error':
                        Domoticz.Error("deCONZ error :" + str(_Data2))
                        
                    #Command sucess
                    elif First_item == 'success':
                        #TODO : need to be sure of order color > level > on-off
                        data = _Data2['success']
                        dev = (list(data.keys())[0] ).split('/')
                        val = data[list(data.keys())[0]]
                        
                        if not Unit:
                            IEEE = GetDeviceIEEE(dev[2],dev[1])
                            dummy,Unit = GetDomoDeviceInfo(IEEE)
                            
                        kwarg.update(ReturnUpdateValue(dev[4],val))
                        
                    else:
                        Domoticz.Error("Not managed JSON : " + str(_Data2) )
                        
                if kwarg and Unit:
                    Devices[Unit].Update(**kwarg)
                    Domoticz.Log("Update  ("+Devices[Unit].Name+") : " + str(kwarg))

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
            _json = _json + '"bri":' + str(round(Level*255/100)) + ','
        if Command == 'Off':
            _json =_json + '"on":false,'
            
        #To prevent bug
        if Command == 'Set Level' or Command == 'Set Color':
            _json =_json + '"on":true,'

        #level
        if Command == 'Set Level':
            _json = _json + '"bri":' + str(round(Level*255/100)) + ','
        
        #color
        if Command == 'Set Color':
        
            _json = _json + '"bri":' + str(round(Level*255/100)) + ','
        
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
                _json = _json + '"ct":' + str(TempMired) + ','
            #ColorModeRGB = 3    // Color. Valid fields: r, g, b.
            elif Hue_List['m'] == 3:
                x, y = rgb_to_xy((int(Hue_List['r']),int(Hue_List['g']),int(Hue_List['b'])))
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
        Domoticz.Log("onDisconnect called for " + str(Connection) )
        ccc = str(Connection)
        if 'deCONZ_Com' in ccc:
            self.UpdateBuffer()

    def onHeartbeat(self):
        Domoticz.Log("onHeartbeat called")
        if self.Init != True:
            if self.Init == False:
                self.Init = LIGHT
                Domoticz.Log("### Request lights")
                self.SendCommand("/api/" + Parameters["Mode2"] + "/lights/")
                
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
        for i in self.ListLights:
            if self.ListLights[i] == IEEE:
                return 'lights',i

        for i in self.ListSensors:
            if self.ListSensors[i] == IEEE:
                return 'sensors',i
                
        for i in self.ListGroups:
            if self.ListGroups[i] == IEEE:
                return 'groups',i

        return False
        
    def UpdateBuffer(self):
        if len(self.Buffer_Command) == 0:
            return
            
        if (self.Request == None or not (self.Request.Connecting() or self.Request.Connected())):
            self.Request = Domoticz.Connection(Name="deCONZ_Com", Transport="TCP/IP", Address=Parameters["Address"] , Port=Parameters["Port"])
            self.Request.Connect()
            
    def GetDeviceIEEE(self,id,type):
        if type == 'lights':
            return self.ListLights.get(id,False)
        elif type == 'sensors':
            return self.ListSensors.get(id,False)
        elif type == 'groups':
            return self.ListGroups.get(id,False)
        return False

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
    _plugin.onDeviceRemoved()

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
            return Devices[x],x
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
    
def UpdateDevice(id,type,kwarg):

    if not kwarg:
        return

    try:
        IEEE = GetDeviceIEEE(id,type)
        dummy,Unit = GetDomoDeviceInfo(IEEE)
    except:
        Domoticz.Error("Can't find Unit > " + id + ' ' + type )
        return
        
    if 'nValue' not in kwarg:
        kwarg['nValue'] = Devices[Unit].nValue
    if 'sValue' not in kwarg:
        kwarg['sValue'] = Devices[Unit].sValue

    Domoticz.Log("### Update  device ("+Devices[Unit].Name+") : " + str(kwarg))
    Devices[Unit].Update(**kwarg)


def CreateDevice(IEEE,_Name,_Type):
    Unit = FreeUnit()
    TypeName = ''
    
    if _Type == 'Color light':
        Type = 241
        Subtype = 2
        Switchtype = 7
        
    elif _Type == 'Dimmable light':
        Type = 244
        Subtype = 73
        Switchtype = 7
        
    elif _Type == 'Daylight':
        TypeName = 'Illumination'
        
    elif _Type == 'ZHATemperature':
        TypeName = 'Temperature'
        
    elif _Type == 'ZHAHumidity':
        TypeName = 'Humidity'
        
    elif _Type == 'ZHAPressure':
        TypeName = 'Pressure'
        
    elif _Type == 'ZHAOpenClose':
        Type = 244
        Subtype = 73
        Switchtype = 11
        
    elif _Type == 'ZHAPresence':
        Type = 244
        Subtype = 73
        Switchtype = 8
        
    elif _Type == 'ZHALightLevel':
        TypeName = 'Illumination'
        
    elif _Type == 'ZHAAlarm':
        Type = 244
        Subtype = 73
        Switchtype = 2
        
    elif _Type == 'ZHASwitch':
        TypeName = 'Switch'
        
    elif _Type == 'groups':
        Type = 241
        Subtype = 2
        Switchtype = 7

    else:
        Domoticz.Error("Unknow device type " + _Type )
        return

    if TypeName:
        Domoticz.Device(DeviceID=IEEE, Name=_Name, Unit=Unit, TypeName=TypeName).Create()
    else:
        Domoticz.Device(DeviceID=IEEE, Name=_Name, Unit=Unit, Type=Type, Subtype=Subtype, Switchtype=Switchtype).Create()
    
    Domoticz.Status("### Create Device " + IEEE + " > " + _Name )
