# Basic Python Plugin Example
#
# Author: GizMoCuz
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
from fonctions import test

LIGHT = 10
SENSOR = 20

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
        self.Init = False
        self.Buffer_Command = []
        self.Request = None
        return

    def onStart(self):
        Domoticz.Log("onStart called")
        
        #Domoticz.Debugging(62+64)
        
        #Web socket connexion
        #self.WebSocket = Domoticz.Connection(Name="deCONZ_WebSocket", Transport="TCP/IP", Address=Parameters["Address"], Port=Parameters["Mode1"])
        #self.WebSocket.Connect()
        
        # Scan devices
        # light
        url = "http://127.0.0.1:8010/api/3E62E09612/lights/"
        #test()

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
        
        Domoticz.Log("Data : " + str(Data))
        
        _Data = Data.decode("utf-8", "ignore")
        _Data = _Data[_Data.find('{'):]
        if _Data[-1] == ']':
            _Data = _Data[:-1]
        _Data = _Data.replace('true','True').replace('false','False') 
        Domoticz.Log("Data Cleaned : " + str(_Data))
            
        try:
            _Data = eval(_Data)
        except:
            _Data = {}
            Domoticz.Error("Response not JSON format")
            return
        
        ccc = str(Connection)
        if 'deCONZ_WebSocket' in ccc:
            Domoticz.Log("Data : " + str(_Data) )
        elif 'deCONZ_Com' in ccc:
        
            #Next command ?
            self.Request.Disconnect()
            self.UpdateBuffer()
            
            Domoticz.Log("Data : " + str(_Data) )
            
            for _Data2 in _Data:
            
                if isinstance(_Data2, str):
                    #merde rattage
                    _Data2 =_Data
            
                First_item = next(iter(_Data2))
                #Error
                if First_item == 'error':
                    Domoticz.Error("deCONZ error :" + str(_Data2))
                    
                #Command sucess
                elif First_item == 'success':
                    UpdateDomoticz(_Data2['success'])
                
                #Read all devices
                elif First_item.isnumeric():

                    for i in _Data2:
                    
                        IEEE = str(_Data2[i]['uniqueid'])
                        Name = str(_Data2[i]['name'])
                        Type = str(_Data2[i]['type'])
                        
                        Domoticz.Log("Device > " + str(i) + ' Name:' + Name + ' Type:' + Type + ' Details:' + str(_Data2[i]['state']))
                        
                        if self.Init == LIGHT:
                            self.ListLights[i] = IEEE
                        if self.Init == SENSOR:
                            self.ListSensors[i] = IEEE
                            
                        #Create it in domoticz if not exist
                        if GetDomoDeviceInfo(IEEE) == False:
                            CreateDevice(IEEE,Name,Type)
                            
                    if self.Init == SENSOR:
                        self.Init = True
                            
                    if self.Init == LIGHT:
                        self.Init = SENSOR
                        Domoticz.Log("### Request sensors")
                        self.SendCommand("/api/" + Parameters["Mode2"] + "/sensors/")

                else:
                    Domoticz.Error("Not managed JSON : " + str(_Data2) )
            
        else:
            Domoticz.Log("Unknow Connection" + str(Connection))
            Domoticz.Log("Data : " + str(Data))


    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Log("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level) + "', Hue: " + str(Hue))
        
        if Command == 'On':
            on_off = 'true'
        if Command == 'Off':
            on_off = 'false'

        #Homemade json
        _json = '{"on":' + on_off + ',"bri":' + str(Level) + '}'
                
        deCONZ_ID = self.GetDevicedeCONZ(Devices[Unit].DeviceID)
        
        url = '/api/' + Parameters["Mode2"] + '/lights/' + str(deCONZ_ID) + '/state'
        #self.SendCommand(url,urllib.parse.urlencode(_json))
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
        
    def SendCommand(self,url,data=None):
    
        Domoticz.Log("Send Command " + url + "with " + str(data))
    
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
                return i

        for i in self.ListSensors:
            if self.ListSensors[i] == IEEE:
                return i

        return False
        
    def UpdateBuffer(self):
        if len(self.Buffer_Command) == 0:
            return
            
        if (self.Request == None or not (self.Request.Connecting() or self.Request.Connected())):
            self.Request = Domoticz.Connection(Name="deCONZ_Com", Transport="TCP/IP", Address=Parameters["Address"] , Port=Parameters["Port"])
            self.Request.Connect()
            
    def GetDeviceIEEE(self,id,type):
        if type == 'lights':
            return self.ListLights[id]
        elif type == 'sensors':
            self.ListSensors[id]
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

def UpdateDomoticz(data):
    dev = list(data.keys())[0].split['/']
    val = data[list(data.keys())[0]]
    
    IEEE = GetDeviceIEEE(dev[2],dev[3])
    dummy,Unit = GetDomoDeviceInfo(IEEE)
    
    kwarg = []
    
    if dev[4] == 'on':
        if val == 'True':
            kwarg['nValue'] = 1
            kwarg['sValue'] = 'on'
        else:
            kwarg['nValue'] = 1
            kwarg['sValue'] = 'off'
            
    if dev[4] == 'bri':
        kwarg['nValue'] = 1
        kwarg['sValue'] = str(val)
        
    Devices[Unit].Update(**kwarg)
    Domoticz.Log("Update  ("+Devices[Unit].Name+") : " + str(kwarg))

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
        
    else:
        Domoticz.Error("Unknow device type " + _Type )
        return

    if TypeName:
        Domoticz.Device(DeviceID=IEEE, Name=_Name, Unit=Unit, TypeName=TypeName).Create()
    else:
        Domoticz.Device(DeviceID=IEEE, Name=_Name, Unit=Unit, Type=Type, Subtype=Subtype, Switchtype=Switchtype).Create()
    
    Domoticz.Status("Create Device " + IEEE + " > " + _Name )
