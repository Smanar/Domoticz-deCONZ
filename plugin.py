# deCONZ Bridge
#
# Author: Smanar
#
"""
<plugin key="deCONZ" name="deCONZ plugin" author="Smanar" version="1.0.15" wikilink="https://github.com/Smanar/Domoticz-deCONZ" externallink="https://www.dresden-elektronik.de/funktechnik/products/software/pc-software/deconz/?L=1">
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


# Combo for Heartbeat, disabled for the moment
#        <param field="Mode4" label="Refresh rate" width="150px" required="true">
#        <options>
#                <option label="1 second" value="1"  />
#                <option label="2 seconds" value="2"/>
#                <option label="5 seconds" value="5"/>
#                <option label="10 seconds" value="10" default="true"/>
#                <option label="20 seconds" value="20"/>
#            </options>
#        </param>


# All imports
import Domoticz

import urllib, time

try:
    import simplejson as json
except ImportError:
    import json

REQUESTPRESENT = True
try:
    import requests
except:
    REQUESTPRESENT = False

from fonctions import rgb_to_xy, rgb_to_hsl, xy_to_rgb
from fonctions import Count_Type, ProcessAllState, ProcessAllConfig, First_Json, JSON_Repair, get_JSON_payload
from fonctions import ButtonconvertionXCUBE, ButtonconvertionXCUBE_R, ButtonconvertionTradfriRemote, ButtonconvertionTradfriSwitch
from fonctions import ButtonConvertion, VibrationSensorConvertion
from fonctions import installFE, uninstallFE

#Better to use 'localhost' ?
DOMOTICZ_IP = '127.0.0.1'

LIGHTLOG = True #To disable some activation, log will be lighter, but less informations.
SETTODEFAULT = False #To set device in default state after a rejoin

#https://github.com/febalci/DomoticzEarthquake/blob/master/plugin.py
#https://stackoverflow.com/questions/32436864/raw-post-request-with-json-in-body

class BasePlugin:

    #enabled = False

    def __init__(self):
        self.Devices = {} # id, type, state (banned/missing/working) , model
        self.NeedToReset = []
        self.Ready = False
        self.Buffer_Command = []
        self.Buffer_Time = ''
        self.WebSocket = None
        self.WebsoketBuffer = ''
        self.Banned_Devices = []
        self.BufferReceive = ''
        self.BufferLenght = 0

        self.IDGateway = -1

        self.INIT_STEP = ['config','lights','sensors','groups']

        return

    def onStart(self):
        Domoticz.Debug("onStart called")
        #CreateDevice('zzzz','En test','Chrismast_E')

        #try:
        #    Domoticz.Log("Heartbeat set to: " + Parameters["Mode4"])
        #    Domoticz.Heartbeat(int(Parameters["Mode4"]))
        #except:
        #    pass

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
        try:
            with open(Parameters["HomeFolder"]+"banned_devices.txt", 'r') as myPluginConfFile:
                for line in myPluginConfFile:
                    if not line.startswith('#'):
                        Domoticz.Log("Adding banned device : " + line.strip())
                        self.Banned_Devices.append(line.strip())
        except (IOError,FileNotFoundError):
            #File not exist create it with example
            Domoticz.Status("Creating banned device file")
            with open(Parameters["HomeFolder"]+"banned_devices.txt", 'w') as myPluginConfFile:
                myPluginConfFile.write("#Alarm on Detector\n00:15:8d:00:02:36:c2:3f-01-0500")

        myPluginConfFile.close()

        #check and load Front end
        installFE()

        #Read and Set config
        #json = '{"websocketnotifyall":true}'
        #url = '/api/' + Parameters["Mode2"] + '/config/'
        #self.SendCommand(url,json)

        # Disabled, not working for selector ...
        #check for new icons
        #if 'bulbs_group' not in Images:
        #    try:
        #        Domoticz.Image('icons/bulbs_group.zip').Create()
        #    except:
        #        Domoticz.Error("Can't create new icons")

    def onStop(self):
        Domoticz.Debug("onStop called")
        if self.WebSocket:
            self.WebSocket.Disconnect()

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect called")

        if Connection.Name == 'deCONZ_WebSocket':

            if (Status != 0):
                Domoticz.Error("WebSocket connexion error : " + str(Connection))
                Domoticz.Error("Status : " + str(Status) + " Description : " + str(Description) )
                return

            Domoticz.Status("Launching websocket on port " + str(Connection.Port) )
            #Need to Add Sec-Websocket-Protocol : domoticz ????
            #Boring error > Socket Shutdown Error: 9, Bad file descriptor
            wsHeader = "GET / HTTP/1.1\r\n" \
                        "Host: "+ Parameters["Address"] + ':' + str(Connection.Port) + "\r\n" \
                        "User-Agent: Domoticz/1.0\r\n" \
                        "Sec-WebSocket-Version: 13\r\n" \
                        "Origin: http://" + DOMOTICZ_IP + "\r\n" \
                        "Sec-WebSocket-Key: qqMLBxyyjz9Tog1bll7K6A==\r\n" \
                        "Connection: keep-alive, Upgrade\r\n" \
                        "Upgrade: websocket\r\n\r\n"
                        #"Accept: Content-Type: text/html; charset=UTF-8\r\n" \
                        #"Pragma: no-cache\r\n" \
                        #"Cache-Control: no-cache\r\n" \
                        #"Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n" \
            self.WebSocket.Send(wsHeader)

        else:
            Domoticz.Error("Unknow connexion : " + str(Connection))
            Domoticz.Error("Status : " + str(Status) + " Description : " + str(Description) )
            return

    def onMessage(self, Connection, Data):
        Domoticz.Debug("onMessage called")

        _Data = []

        if self.WebsoketBuffer:
            Data = self.WebsoketBuffer + Data
            self.WebsoketBuffer = ''

        #Domoticz.Log("Data : " + str(Data))
        #Domoticz.Log("Connexion : " + str(Connection))
        #Domoticz.Log("Byte needed : " + str(Connection.BytesTransferred()) +  "ATM : " + str(len(Data)))
        #The max is 4096 so if the data size excess 4096 byte it will be cut

        #Websocket data ?
        if (Connection.Name == 'deCONZ_WebSocket'):
            #Data = b'\x81W{"e":"changed","id":"7","r":"groups","state":{"all_on":true,"any_on":true}}'
            #Data = b'\x81W{"e":"changed","id":"5","r":"groups","state":{"all_on":true,"any_on"'

            if Data.startswith(b'\x81'):
                while len(Data) > 0:
                    try:
                        payload, extra_data = get_JSON_payload(Data)
                    except:
                        if (Data[0:1] == b'\x81') and (len(str(Data)) < 300) :
                            self.WebsoketBuffer = Data
                            Domoticz.Log("Incomplete Json keep it for later : " + str(self.WebsoketBuffer) )
                        else:
                            Domoticz.Error("Malformed JSON response, can't repair : " + str(Data) )
                        break
                    _Data.append(payload)
                    Data = extra_data

                for js in _Data:
                    self.WebSocketConnexion(js)
            else:
                Domoticz.Log("Websocket Handshake : " + str(Data.decode("utf-8", "ignore").replace('\n','***')) )

        else:
            Domoticz.Log("Unknow Connection" + str(Connection))
            Domoticz.Log("Data : " + str(Data))
            return

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Log("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level) + ", Hue: " + str(Hue))

        if not self.Ready == True:
            Domoticz.Error("deCONZ not ready")
            return

        _type,deCONZ_ID = self.GetDevicedeCONZ(Devices[Unit].DeviceID)

        if not deCONZ_ID:
            Domoticz.Error("Device not ready : " + str(Unit) )
            return

        if _type == 'sensors':
            Domoticz.Error("This device don't support action")
            return

        IEEE = Devices[Unit].DeviceID

        _json = {}

        #on/off
        if Command == 'On':
            _json['on'] = True
            if Level:
                _json['bri'] = round(Level*254/100)
        if Command == 'Off':
            _json['on'] = False
            if _type == 'config':
                _json = {'mode':'off'}

        #level
        if Command == 'Set Level':
            #To prevent bug
            _json['on'] = True

            _json['bri'] = round(Level*254/100)

            #Special situation
            if _type == 'config':
                _json.clear()
                #Thermostat
                if Devices[Unit].DeviceID.endswith('_heatsetpoint'):
                    _json['mode'] = "auto"
                    _json['heatsetpoint'] = Level * 100
                elif Devices[Unit].DeviceID.endswith('_mode'):
                    if Level == 0:
                        _json['mode'] = "off"
                    if Level == 10:
                        _json['mode'] = "heat"
                    if Level == 20:
                        _json['mode'] = "auto"
                        #retreive previous value from domoticz
                        IEEE2 = Devices[Unit].DeviceID.replace('_mode','_heatsetpoint')
                        Hp = int(100*float(Devices[GetDomoDeviceInfo(IEEE2)].sValue))
                        _json['heatsetpoint'] = Hp
                #Chritsmas tree
                elif Devices[Unit].DeviceID.endswith('_effect'):
                    Domoticz.Log(">>>>>>>>" + str(Devices[Unit].sValue) + " / " + str(Devices[Unit]))
                    _json['effect'] = Devices[Unit].sValue
                    #_json['effectColours'] = [[255,0,0],[0,255,0],[0,0,255]]
                    #_json['effectSpeed' = 10
                    _type,deCONZ_ID = self.GetDevicedeCONZ(Devices[Unit].DeviceID.replace("_effect",""))


        #Pach for special device
        if 'NO DIMMER' in Devices[Unit].Description and 'bri' in _json:
            _json.pop('bri')
            _json['transitiontime'] = 0

        #Stop for shutter
        if Command == 'Stop':
            _json = {'bri_inc':0}

        #Special part for shutter
        #if self.Devices[IEEE]['model'] == 'Window covering device':
        #    previous_sate = Devices[Unit].nValue
        #    if _json['on'] == False and previous_sate == 0:
        #        _json = {'bri_inc':0}
        #    elif _json['on'] == True and previous_sate == 1:
        #        _json = {'bri_inc':0}

        #color
        if Command == 'Set Color':

            #To prevent bug
            _json['on'] = True

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
                _json['ct'] = TempMired
            #ColorModeRGB = 3    // Color. Valid fields: r, g, b.
            elif Hue_List['m'] == 3:
                if self.Devices[IEEE].get('colormode','Unknow') == 'hs':
                    h,l,s = rgb_to_hsl((int(Hue_List['r']),int(Hue_List['g']),int(Hue_List['b'])))
                    hue = int(h * 65535)
                    saturation = int(s * 254)
                    lightness = int(l * 254)
                    _json['hue'] = hue
                    _json['sat'] = saturation
                    _json['bri'] = lightness
                    _json['transitiontime'] = 0
                else:
                    x, y = rgb_to_xy((int(Hue_List['r']),int(Hue_List['g']),int(Hue_List['b'])))
                    x = round(x,6)
                    y = round(y,6)
                    _json['xy'] = [x,y]
            #ColorModeCustom = 4, // Custom (color + white). Valid fields: r, g, b, cw, ww, depending on device capabilities
            elif Hue_List['m'] == 4:
                ww = int(Hue_List['ww'])
                cw = int(Hue_List['cw'])
                x, y = rgb_to_xy((int(Hue_List['r']),int(Hue_List['g']),int(Hue_List['b'])))
                #TODO, Pas trouve de device avec ca encore ...
                Domoticz.Debug("Not implemented device color 2")

            #To prevent bug
            if 'bri' not in _json:
                _json['bri'] = round(Level*254/100)
                _json['transitiontime'] = 0

        url = '/api/' + Parameters["Mode2"] + '/' + _type + '/' + str(deCONZ_ID)
        if _type == 'lights':
            url = url + '/state'
        elif _type == 'config':
            url = '/api/' + Parameters["Mode2"] + '/sensors/' + str(deCONZ_ID) + '/config'
        elif _type == 'scenes':
            url = '/api/' + Parameters["Mode2"] + '/groups/' + deCONZ_ID.split('/')[0] + '/scenes/' + deCONZ_ID.split('/')[1] + '/recall'
            _json = {} # to force PUT
        else:
            url = url + '/action'

        #if 'Thermostat' in self.Devices[IEEE]['model']:
        #    Domoticz.Status("Thermostat debug : " + url + ' with ' + str(_json))

        self.SendCommand(url,_json)

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Status("onDisconnect called for " + str(Connection.Name) )

    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat called")

        #Check for freeze
        if len(self.Buffer_Command) > 0:
            self.UpdateBuffer()

        #Initialisation
        if self.Ready != True:
            if len(self.INIT_STEP) > 0:
                Domoticz.Debug("### Initialisation > " + str(self.INIT_STEP[0]))
                self.ManageInit()

                #Stop all here
                return
            else:
               self.Ready = True

        #Check websocket connexion
        if self.WebSocket:
            if not self.WebSocket.Connected():
                Domoticz.Error("WebSocket Disconnected, reconnexion !")
                self.WebSocket.Connect()

        #reset switchs
        if len(self.NeedToReset) > 0 :
            for IEEE in self.NeedToReset:
                _id = False
                for i in self.Devices:
                    if i == IEEE:
                        _id = self.Devices[i]['id']
                UpdateDevice(_id,'sensors', { 'nValue' : 0 , 'sValue' : 'Off' } )
            self.NeedToReset = []

        #Devices[27].Update(nValue=0, sValue='11;22' )

    def onDeviceRemoved(self,unit):
        Domoticz.Log("Device Removed")
        #TODO : Need to rescan all

#---------------------------------------------------------------------------------------

    def ManageInit(self,pop = False):

        if pop:
            self.INIT_STEP.pop(0)
        if len(self.INIT_STEP) < 1:
            self.Ready = True

            Domoticz.Status("### deCONZ ready")
            l,s,g,b,o,c = Count_Type(self.Devices)
            Domoticz.Status("### Found " + str(l) + " Operators, " + str(s) + " Sensors, " + str(g) + " Groups, " + str(c) + " Scenes and " + str(o) + " others, with " + str(b) + " Ignored")

            # Compare devices bases
            for i in Devices:
                if Devices[i].DeviceID not in self.Devices:
                    Domoticz.Status('### Device ' + Devices[i].DeviceID + '(' + Devices[i].Name + ') Not in deCONZ ATM, the device is deleted or not ready.')

            return

        #No flood during initialisation
        if len(self.Buffer_Command) > 0:
            u,d = self.Buffer_Command[-1]
            if "/" + self.INIT_STEP[0] + "/" in u:
                Domoticz.Log("### Still waiting")
                return

        Domoticz.Log("### Request " + self.INIT_STEP[0])
        self.SendCommand("/api/" + Parameters["Mode2"] + "/" + self.INIT_STEP[0] + "/")

    def InitDomoticzDB(self,key,_Data,Type_device):

        #Lights or sensors ?
        if not 'devicemembership' in _Data:

            IEEE = str(_Data['uniqueid'])
            Name = str(_Data['name'])
            Type = str(_Data['type'])
            Model = str(_Data.get('modelid',''))
            Manuf = str(_Data.get('manufacturername',''))
            if not Model:
                Model = ''

            Domoticz.Log("### Device > " + str(key) + ' Name:' + Name + ' Type:' + Type + ' Details:' + str(_Data['state']) + ' and ' + str(_Data.get('config','')) )

            #Skip useless devices
            if Type == 'Configuration tool':
                Domoticz.Log("Skipping Device (Useless) : " + str(IEEE) )
                self.IDGateway = key
                return
            if (Type == 'Unknown') and (len(_Data['state']) == 1) and ('reachable' in _Data['state']):
                Domoticz.Log("Skipping Device (Useless) : " + str(IEEE) )
                if self.IDGateway == -1:
                    self.IDGateway = key
                return

            self.Devices[IEEE] = {'id' : key , 'type' : Type_device , 'model' : Type , 'state' : 'working'}

            #Skip banned devices
            if IEEE in self.Banned_Devices:
                Domoticz.Log("Skipping Device (Banned) : " + str(IEEE) )
                self.Devices[IEEE]['state'] = 'banned'
                return

            #Get some infos
            kwarg = {}
            if 'state' in _Data:
                state = _Data['state']
                kwarg.update(ProcessAllState(state,Model))
                if 'colormode' in state:
                    self.Devices[IEEE]['colormode'] = state['colormode']

            if 'config' in _Data:
                config = _Data['config']
                kwarg.update(ProcessAllConfig(config))

            #It's a switch ? Need special process
            if Type == 'ZHASwitch' or Type == 'ZGPSwitch' or Type == 'CLIPSwitch':

                #Set it to off
                kwarg.update({'sValue': 'Off', 'nValue': 0})

                #ignore ZHASwitch if vibration sensor
                if 'sensitivity' in _Data['config']:
                    return
                if 'lumi.sensor_cube' in Model:
                    if IEEE.endswith('-03-000c'):
                        Type = 'XCube_R'
                    elif IEEE.endswith('-02-0012'):
                        Type = 'XCube_C'
                    else:
                        # Useless device
                        self.Devices[IEEE]['state'] = 'banned'
                        return
                elif 'TRADFRI remote control' in Model:
                    Type = 'Tradfri_remote'
                #elif 'RWL021' in Model:
                #    Type = 'Tradfri_remote'
                elif 'TRADFRI on/off switch' in Model:
                    Type = 'Tradfri_on/off_switch'
                elif 'lumi.remote.b186acn01' in Model:
                    Type = 'Xiaomi_single_gang'
                elif 'lumi.remote.b286acn01' in Model:
                    Type = 'Xiaomi_double_gang'
                #Used for all opple switches
                elif Model.endswith('86opcn01'):
                    Type = 'Xiaomi_Opple_6_button_switch'
                else:
                    Type = 'Switch_Generic'

                self.Devices[IEEE]['model'] = Type

            if self.Ready == True:
                Domoticz.Status("Adding missing device :" + str(key) + ' Type:' + str(Type))

            #lidl strip
            if Manuf == '_TZE200_s8gkrkxk':
                #Create a widget for effect
                self.Devices[IEEE + "_effect"] = {'id' : key , 'type' : 'config' , 'state' : 'working' , 'model' : 'Chrismast_E' }
                self.CreateIfnotExist(IEEE + "_effect",'Chrismast_E',Name)

            #Special devices
            if Type == 'ZHAThermostat':
                # Not working for cable outlet yet.
                if not Model == 'Cable outlet':
                    #Create a setpoint device
                    self.Devices[IEEE + "_heatsetpoint"] = {'id' : key , 'type' : 'config' , 'state' : 'working' , 'model' : 'ZHAThermostat' }
                    self.CreateIfnotExist(IEEE + "_heatsetpoint",'ZHAThermostat',Name)
                    #Create a mode device
                    self.Devices[IEEE + "_mode"] = {'id' : key , 'type' : 'config' , 'state' : 'working' , 'model' : 'Thermostat_Mode' }
                    self.CreateIfnotExist(IEEE + "_mode",'Thermostat_Mode',Name)
                    #Create the current device but as temperature device
                    self.CreateIfnotExist(IEEE,'ZHATemperature',Name)
            elif Type == 'ZHAVibration':
                #Create a Angle device
                self.Devices[IEEE + "_orientation"] = {'id' : key , 'type' : 'config' , 'state' : 'working' , 'model' : 'Vibration_Orientation' }
                self.CreateIfnotExist(IEEE + "_orientation",'Vibration_Orientation',Name)
                #Create the current device
                self.CreateIfnotExist(IEEE,'ZHAVibration',Name)
            else:
                self.CreateIfnotExist(IEEE,Type,Name)

            #update
            if kwarg:
                UpdateDevice(key,Type_device,kwarg)

        #groups
        else:

            Name = str(_Data['name'])
            Type = str(_Data['type'])
            Domoticz.Log("### Groupe > " + str(key) + ' Name:' + Name )
            Dev_name = 'GROUP_' + Name.replace(' ','_')
            self.Devices[Dev_name] = {'id' : key , 'type' : 'groups' , 'model' : 'groups', 'state' : 'working'}

            # Skip banned group
            if Dev_name in self.Banned_Devices:
                Domoticz.Log("Skipping Group (Banned) : " + str(Dev_name) )
                self.Devices[Dev_name]['state'] = 'banned'

            else:
                #Check for scene
                scenes = _Data.get('scenes',[])
                if len(scenes) > 0:
                    for j in scenes:
                        Domoticz.Log("### Scenes associated with group " + str(key) + " > ID:" + str(j['id']) + " Name:" + str(j['name']) )
                        Scene_name = 'SCENE_' + str(j['name']).replace(' ','_')
                        self.Devices[Scene_name] = {'id' : str(key) + '/' + str(j['id']) , 'type' : 'scenes' , 'model' : 'scenes'}
                        #^scene not exist > create
                        if GetDomoDeviceInfo(Scene_name) == False:
                            CreateDevice(Scene_name,str(j['name']),'Scenes')

                #Group not exist > create
                if GetDomoDeviceInfo(Dev_name) == False:
                    CreateDevice(Dev_name,Name,Type)

    def CreateIfnotExist(self,__IEEE,__Type,Name):
        if GetDomoDeviceInfo(__IEEE) == False:
            CreateDevice(__IEEE,Name,__Type)

    def NormalConnexion(self,_Data):

        Domoticz.Debug("Classic Data : " + str(_Data) )

        #JSON with data returned >> _Data = [{'success': {'/lights/2/state/on': True}}, {'success': {'/lights/2/state/bri': 251}}]
        if isinstance(_Data, list):
            self.ReadReturn(_Data)
        else:
            if (self.Ready != True):
                #JSON with config
                if 'bridgeid' in _Data:
                    if 'websocketnotifyall' in _Data:
                        self.ReadConfig(_Data)
                    else:
                        Domoticz.Error("Bad API KEY !")
                else:
                    #JSON with device info like {'1': {'data:1}}
                    for i in _Data:
                        self.InitDomoticzDB(i,_Data[i],self.INIT_STEP[0])

                    #Update initialisation
                    self.ManageInit(True)
            else:
                #JSON with device info like {'data:1}
                # Groups ?
                if 'devicemembership' in _Data:
                    _id = _Data.get('id','')
                    if _id:
                        self.InitDomoticzDB(_id,_Data,'groups')
                # simple device ?
                else:
                    typ,_id = self.GetDevicedeCONZ(_Data.get('uniqueid','') )
                    if _id:
                        self.InitDomoticzDB(_id,_Data,typ)


    def ReadReturn(self,_Data):
        kwarg = {}
        _id = False
        _type = False

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
                    pass
                else:
                    if not _id:
                        _id = dev[2]
                        _type = dev[1]

                    if dev[1] == 'config':
                        Domoticz.Status("Editing configuration : " + str(data) )

            else:
                Domoticz.Error("Not managed return JSON : " + str(_Data2) )

        if kwarg:
            UpdateDevice(_id,_type,kwarg)

    def ReadConfig(self,_Data):
        #trick to test is deconz is ready
        fw = _Data['fwversion']
        if fw == '0x00000000':
            Domoticz.Error("Wrong startup, retrying !!")
            #Cancel this part to restart it after 1 heartbeat (10s)
            return
        Domoticz.Status("Firmware version : " + _Data['fwversion'] )
        Domoticz.Status("Websocketnotifyall : " + str(_Data['websocketnotifyall']))
        if not _Data['websocketnotifyall'] == True:
            Domoticz.Error("Websocketnotifyall is not set to True")

        #Launch Web socket connexion
        self.WebSocket = Domoticz.Connection(Name="deCONZ_WebSocket", Transport="TCP/IP", Address=Parameters["Address"], Port=str(_Data['websocketport']) )
        self.WebSocket.Connect()

        self.ManageInit(True)

    def WebSocketConnexion(self,_Data):

        Domoticz.Debug("### WebSocket Data : " + str(_Data) )

        if not self.Ready == True:
            Domoticz.Error("deCONZ not ready")
            return

        if 'e' in _Data:
            if _Data['e'] == 'deleted':
                return
            if _Data['e'] == 'added':
                return
            if _Data['e'] == 'scene-called':
                Domoticz.Log("Playing scene > group:" + str(_Data['gid']) + " Scene:" + str(_Data['scid']) )
                return

        #Remove all uniqueid that can be have in group
        if 'r' in _Data:
            if _Data['r'] == 'groups' and 'uniqueid' in _Data:
                _Data.pop('uniqueid')

        #Take care, no uniqueid for groups
        IEEE,state = self.GetDeviceIEEE(_Data['id'],_Data['r'])

        #Patch for device with double UniqueID, can't be light
        if (not IEEE) and ('uniqueid' in _Data) and _Data['r'] != 'lights':
            typ,_id = self.GetDevicedeCONZ(_Data['uniqueid'] )
            if _id and (typ == _Data['r']):
                Domoticz.Log("Double UniqueID correction : " + _Data['id'] + ' > ' + str(_id) )
                _Data['id'] = _id
                IEEE,state = self.GetDeviceIEEE(_Data['id'],_Data['r'])

        if not IEEE:
            if 'uniqueid' in _Data:

                Domoticz.Error("Websocket error, unknow device > " + str(_Data['id']) + ' (' + str(_Data['r']) + ') Asking for information')
                IEEE = str(_Data['uniqueid'])
                #Try getting informations
                self.Devices[IEEE] = {'id' : str(_Data['id']) , 'type' : str(_Data['r']) , 'state' : 'missing'}
                self.SendCommand('/api/' + Parameters["Mode2"] + '/' + str(_Data['r']) + '/' + str(_Data['id']) )
            else:
                Domoticz.Error("Websocket error, unknow device > " + str(_Data['id']) + ' (' + str(_Data['r']) + ')')
                #Try getting informations
                if str(_Data['r']) == 'groups':
                    #Name = str(_Data['name'])
                    #Dev_name = 'GROUP_' + Name.replace(' ','_')
                    #self.Devices[Dev_name] = {'id' : str(_Data['id']) , 'type' : 'groups' , 'model' : 'groups', 'state' : 'missing'}
                    self.SendCommand('/api/' + Parameters["Mode2"] + '/groups/' + str(_Data['id']) )

            return
        if state == 'banned':
            Domoticz.Debug("Banned/Ignored device > " + str(_Data['id']) + ' (' + str(_Data['r']) + ')')
            return
        if state == 'missing':
            Domoticz.Error("Missing device > " + str(_Data['id']) + ' (' + str(_Data['r']) + ')')
            return

        model = self.Devices[IEEE].get('model','')

        #if 'Thermostat' in model:
        #    Domoticz.Status("Thermostat debug : " + str(_Data))

        kwarg = {}

        #MAJ State : _Data['e'] == 'changed'
        if 'state' in _Data:
            state = _Data['state']
            kwarg.update(ProcessAllState(state , model))

            if 'buttonevent' in state:
                if model == 'XCube_C':
                    kwarg.update(ButtonconvertionXCUBE( state['buttonevent'] ) )
                elif model == 'XCube_R':
                    kwarg.update(ButtonconvertionXCUBE_R( state['buttonevent'] ) )
                elif model == 'Tradfri_remote':
                    kwarg.update(ButtonconvertionTradfriRemote( state['buttonevent'] ) )
                elif model == 'Tradfri_on/off_switch':
                    kwarg.update(ButtonconvertionTradfriSwitch( state['buttonevent'] ) )
                elif model == 'Xiaomi_double_gang':
                    kwarg.update(ButtonConvertion( state['buttonevent'] , 1 ) )
                elif model == 'Xiaomi_Opple_6_button_switch':
                    kwarg.update(ButtonConvertion( state['buttonevent'] , 2) )
                elif model == 'Xiaomi_single_gang':
                    kwarg.update(ButtonConvertion( state['buttonevent'] , 3) )
                else:
                    kwarg.update(ButtonConvertion( state['buttonevent'] ) )
                if IEEE not in self.NeedToReset:
                    self.NeedToReset.append(IEEE)

            if 'vibration' in state:
                kwarg.update(VibrationSensorConvertion( state['vibration'] , state.get('tiltangle',None), state.get('orientation',None)) )

            if 'reachable' in state:
                if state['reachable'] == True:
                    Unit = GetDomoDeviceInfo(IEEE)
                    #Jump following action if Unit content is not valid
                    if Unit != False:
                        LUpdate = Devices[Unit].LastUpdate
                        LUpdate=time.mktime(time.strptime(LUpdate,"%Y-%m-%d %H:%M:%S"))
                        current = time.time()

                        if (SETTODEFAULT):
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

        #MAJ attr, not used yet
        elif 'attr' in _Data:
            attr = _Data['attr']

        else:
            Domoticz.Error("Unknow MAJ: " + str(_Data) )

        if kwarg:
            UpdateDevice(_Data['id'],_Data['r'],kwarg)

    def DeleteDeviceFromdeCONZ(self,_id):

        url = '/api/' + Parameters["Mode2"] + '/sensors/' + str(_id)

        self.Buffer_Command.append((url,'delete'))
        self.UpdateBuffer()

        Domoticz.Status("### Deleting device " + str(_id))

    def SendCommand(self,url,data=None):

        Domoticz.Debug("Send Command " + url + " with " + str(data) + ' (' + str(len(self.Buffer_Command)) + ' in buffer)')

        sendData = (url , data)
        self.Buffer_Command.append(sendData)
        self.UpdateBuffer()

    def GetDevicedeCONZ(self,IEEE):
        if IEEE in self.Devices:
            return self.Devices[IEEE]['type'],self.Devices[IEEE]['id']

        return False,False

    def UpdateBuffer(self):
        if len(self.Buffer_Command) == 0:
            return

        debut_time = time.time()

        while len(self.Buffer_Command) > 0:

            u , c = self.Buffer_Command.pop(0)

            _Data = MakeRequest('http://' + Parameters["Address"] + ':' + Parameters["Port"] + str(u) , c)

            #If not data usefull
            if len(_Data) == 0:
                return

            #Clean data
            #_Data = _Data.replace('true','True').replace('false','False').replace('null','None').replace('\n','***').replace('\00','')
            try:
                _Data = json.loads(_Data)
            except:
                #Sometime the connexion bug, trying to repair
                Domoticz.Error("Malformed JSON response, Trying to repair : " + str(_Data) )
                _Data = JSON_Repair(_Data)
                try:
                    _Data = json.loads(_Data)
                    Domoticz.Error("New Data repaired : " + str(_Data))
                except:
                    Domoticz.Error("Can't repair malformed JSON: " + str(_Data) )
                    _Data = None

            #traitement
            if not _Data == None: #WARNING None because can be {}
                self.NormalConnexion(_Data)

            fin_time = time.time()

            # if the process take more than 1s, skip all, not normal
            if fin_time - debut_time > 1 :
                Domoticz.Error("Process request take too much time : " + str(fin_time - debut_time) + ' s')
                break

        return

    def GetDeviceIEEE(self,_id,_type):
        if _id == self.IDGateway and _type == 'lights':
            return True, "banned"

        for IEEE in self.Devices:
            if (self.Devices[IEEE]['type'] == _type) and (self.Devices[IEEE]['id'] == _id):
                return IEEE,self.Devices[IEEE].get('state','unknow')

        return False,'unknow'

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

def MakeRequest(url,param=None):

    Domoticz.Debug("Making Request : " + url  + ' with params ' + str(param) )

    data = ''

    try:
        if not param == None:
            if param == 'delete':
                result=requests.delete(url, headers={'Content-Type': 'application/json' }, timeout=1)
            else:
                headers={'Content-Type': 'application/json' }
                result=requests.put(url , headers=headers, json = param, timeout=1)
                #result=requests.put(url , headers=headers, data = json.dumps(param), timeout=1)
        else :
            result=requests.get(url, headers={'Content-Type': 'application/json' }, timeout=1)

        if result.status_code  == 200 :
            data = result.content
        else:
            Domoticz.Error( "Connexion problem (1) with Gateway : " + str(result.status_code) )
            return ''
    except:
        if not REQUESTPRESENT:
            Domoticz.Error("Your pyton version miss requests library")
            Domoticz.Error("To install it, type : sudo -H pip3 install requests | sudo -H pip install requests")
        else:
            try:
                Domoticz.Error( "Connexion problem (2) with Gateway : " + str(result.status_code) )
            except:
                Domoticz.Error( "Connexion problem (3) with Gateway, check your API key, or Use Request lib > V2.4.2")
        return ''

    Domoticz.Debug('Request Return : ' + str(data.decode("utf-8", "ignore")) )

    return data.decode("utf-8", "ignore")

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
        IEEE,state = GetDeviceIEEE(_id,_type)

        if IEEE == False:
            Domoticz.Log("Device not in base, need resynchronisation ? > " + str(_id) + ' (' + str(_type) + ')')
            return False
        elif state == 'banned':
            Domoticz.Log("Banned device > " + str(_id) + ' (' + str(_type) + ')')
            return False
        elif state == 'missing':
            Domoticz.Log("missing device > " + str(_id) + ' (' + str(_type) + ')')
            return False

        return GetDomoDeviceInfo(IEEE)
    except:
        return False

    return False

def UpdateDevice_Special(_id,_type,kwarg, field):
    value = kwarg.get(field ,False)

    IEEE,dummy = GetDeviceIEEE(_id,_type)

    #select special device
    Unit2 = GetDomoDeviceInfo(IEEE + '_' + field)

    kwarg2 = kwarg.copy()

    if field == 'mode':
        kwarg2['nValue'] = value
    else:
        kwarg2['nValue'] = 0
    kwarg2['sValue'] = str(value)

    if not Unit2 :
        Domoticz.Error("Can't Update Unit > " + str(_id) + ' (' + str(_type) + ') Special part' )
        return

    #Update it
    UpdateDeviceProc(kwarg2,Unit2)

def UpdateDevice(_id,_type,kwarg):

    Unit = GetDomoUnit(_id,_type)

    if not Unit or not kwarg:
        Domoticz.Error("Can't Update Unit > " + str(_id) + ' (' + str(_type) + ') : ' + str(kwarg) )
        return

    #Check for special device, and remove special kwarg
    if 'orientation' in kwarg:
        UpdateDevice_Special(_id,_type,kwarg,"orientation")

    if 'heatsetpoint' in kwarg:
        UpdateDevice_Special(_id,_type,kwarg,"heatsetpoint")

    if 'mode' in kwarg:
        UpdateDevice_Special(_id,_type,kwarg,"mode")

    #Update the device
    UpdateDeviceProc(kwarg,Unit)

def UpdateDeviceProc(kwarg,Unit):
    #Do we need to update the sensor ?
    NeedUpdate = False

    if 'mode' in kwarg:
        kwarg.pop('mode')
    if 'heatsetpoint' in kwarg:
        kwarg.pop('heatsetpoint')
    if 'orientation' in kwarg:
        kwarg.pop('orientation')

    for a in kwarg:
        if kwarg[a] != getattr(Devices[Unit], a ):
            NeedUpdate = True
            break

    #Force update even there is no change, for exemple in case the user press a switch too fast, to not miss an event
    # Only for switch > 'LevelNames' in Devices[Unit].Options
    # Only sensors >  _type == 'sensors'
    if (('nValue' in kwarg) or ('sValue' in kwarg)) and ( ('LevelNames' in Devices[Unit].Options) and (kwarg['nValue'] != 0) ):
        NeedUpdate = True

    #Disabled because no update for battery or last seen for exemple
    #No need to trigger in this situation
    #if (kwarg['nValue'] == Devices[Unit].nValue) and (kwarg['nValue'] == Devices[Unit].nValue) and ('Color' not in kwarg):
    #    kwarg['SuppressTriggers'] = True

    #Alaways update for Color Bulb
    if 'Color' in kwarg:
        NeedUpdate = True

    #force update, at least 1 every 24h
    if not NeedUpdate:
        LUpdate = Devices[Unit].LastUpdate
        LUpdate=time.mktime(time.strptime(LUpdate,"%Y-%m-%d %H:%M:%S"))
        current = time.time()
        if (current-LUpdate) > 86400:
            NeedUpdate = True

    #Theses value are needed for Domoticz
    if 'nValue' not in kwarg:
        kwarg['nValue'] = Devices[Unit].nValue
    if 'sValue' not in kwarg:
        kwarg['sValue'] = Devices[Unit].sValue
    if Devices[Unit].TimedOut != 0 and kwarg.get('TimedOut',0) == 0:
        NeedUpdate = True
        kwarg['TimedOut'] = 0

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
    if _Type == 'Color light' or _Type == 'Color dimmable light':
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

    elif _Type == 'Dimmable light' or _Type == 'Dimmable plug-in unit' or _Type == 'Dimmer switch':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 73
        kwarg['Switchtype'] = 7

    elif _Type == 'Smart plug' or _Type == 'On/Off plug-in unit':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 73
        kwarg['Switchtype'] = 0
        kwarg['Image'] = 1

    elif _Type == 'On/Off light' or _Type == 'On/Off output' or _Type == 'On/Off light switch':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 73
        kwarg['Switchtype'] = 0

    elif _Type == 'Level control switch':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 73
        kwarg['Switchtype'] = 0

    #elif _Type == 'Color Temperature dimmable light':
    #    kwarg['Type'] = 241
    #    kwarg['Subtype'] = 4
    #    kwarg['Switchtype'] = 7

    #Some device have unknow as type, but are full working.
    elif _Type == 'Unknown':
        Domoticz.Error("Unknow device : assume a light " + IEEE + " > " + _Name + ' (' + _Type +')' )
        kwarg['Type'] = 244
        kwarg['Subtype'] = 73
        kwarg['Switchtype'] = 0

    elif _Type == 'Window covering device':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 73
        kwarg['Switchtype'] = 15

    elif _Type == 'Door Lock':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 73
        kwarg['Switchtype'] = 0

    elif _Type == 'Fan':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 73
        kwarg['Switchtype'] = 0
        kwarg['Image'] = 7

    elif _Type == 'Range extender':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 73
        kwarg['Switchtype'] = 0
        kwarg['Image'] = 17

    elif _Type == 'Warning device':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 73
        kwarg['Switchtype'] = 0
        kwarg['Image'] = 13

    #Sensors
    elif _Type == 'Daylight':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 73
        kwarg['Switchtype'] = 9

    elif _Type == 'ZHATemperature' or _Type == 'CLIPTemperature':
        kwarg['TypeName'] = 'Temperature'

    elif _Type == 'ZHAHumidity' or _Type == 'CLIPHumidity':
        kwarg['TypeName'] = 'Humidity'

    elif _Type == 'ZHAPressure'or _Type == 'CLIPPressure':
        kwarg['TypeName'] = 'Barometer'

    elif _Type == 'ZHAOpenClose' or _Type == 'CLIPOpenClose':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 73
        kwarg['Switchtype'] = 11

    elif _Type == 'ZHAPresence' or _Type == 'CLIPPresence':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 73
        kwarg['Switchtype'] = 8

    elif _Type == 'ZHALightLevel' or _Type == 'CLIPLightLevel' or _Type == 'ZHALight':
        kwarg['TypeName'] = 'Illumination'

    elif _Type == 'ZHAConsumption':# in kWh
        #Device with only comsumption
        if True: # if IEEE.endswith('0702'):
            kwarg['Type'] = 113
            kwarg['Subtype'] = 0
            kwarg['Switchtype'] = 0
        #Device with power and energy, not exist (yet)
        else:
            kwarg['TypeName'] = 'kWh'

    elif _Type == 'ZHAPower':# in W
        kwarg['TypeName'] = 'Usage'

    elif _Type == 'ZHAVibration':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 62
        kwarg['Switchtype'] = 18
        kwarg['Options'] = {"LevelActions": "|||", "LevelNames": "Off|Vibrate|Rotation|Drop", "LevelOffHidden": "true", "SelectorStyle": "0"}

    elif _Type == 'ZHAThermostat' or _Type == 'CLIPThermostat':
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

    elif _Type == 'ZHABattery':
        kwarg['TypeName'] = 'Percentage'

    elif _Type == 'CLIPGenericStatus':
        kwarg['TypeName'] = 'Text'

    elif _Type == 'CLIPGenericFlag':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 62
        kwarg['Switchtype'] = 0
        kwarg['Image'] = 9

    #Switch
    elif _Type == 'Xiaomi_single_gang':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 62
        kwarg['Switchtype'] = 18
        kwarg['Image'] = 9
        kwarg['Options'] = {"LevelActions": "||||", "LevelNames": "Off|single press|double press|hold", "LevelOffHidden": "true", "SelectorStyle": "0"}

    elif _Type == 'Switch_Generic' or _Type == 'Xiaomi_double_gang':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 62
        kwarg['Switchtype'] = 18
        kwarg['Image'] = 9
        kwarg['Options'] = {"LevelActions": "||||||", "LevelNames": "Off|B1|B2|B3|B4|B5|B6|B7|B8|B9", "LevelOffHidden": "true", "SelectorStyle": "0"}
    #eyal start
    elif _Type == 'Xiaomi_Opple_6_button_switch':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 62
        kwarg['Switchtype'] = 18
        kwarg['Image'] = 9
        kwarg['Options'] = {"LevelActions": "|||||||||||||||||", "LevelNames": "Off|B1|B2|B3|B4|B5|B6|B1L|B2L|B3L|B4L|B5L|B6L|B1RL|B2RL|B3RL|B4RL|B5RL|B6RL|B1D|B2D|B3D|B4D|B5D|B6D|B1T|B2T|B3T|B4T|B5T|B6T", "LevelOffHidden": "true", "SelectorStyle": "1"}
    #eyal end

    elif _Type == 'Tradfri_remote':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 62
        kwarg['Switchtype'] = 18
        kwarg['Image'] = 9
        kwarg['Options'] = {"LevelActions": "|||||||||", "LevelNames": "Off|On|+|-|<|>|L +|L -|L <|L >", "LevelOffHidden": "true", "SelectorStyle": "0"}

    elif _Type == 'Tradfri_on/off_switch':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 62
        kwarg['Switchtype'] = 18
        kwarg['Options'] = {"LevelActions": "|||||", "LevelNames": "Off|B1C|B1L|B2C|B2L", "LevelOffHidden": "true", "SelectorStyle": "0"}

    elif _Type == 'XCube_C':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 62
        kwarg['Switchtype'] = 18
        kwarg['Image'] = 9
        kwarg['Options'] = {"LevelActions": "||||||||", "LevelNames": "Off|Shak|Wake|Drop|90°|180°|Push|Tap", "LevelOffHidden": "true", "SelectorStyle": "0"}

    elif _Type == 'XCube_R':
        kwarg['TypeName'] = 'Custom'
        kwarg['Options'] = {"Custom": ("1;degree")}

    elif _Type == 'Thermostat_Mode':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 62
        kwarg['Switchtype'] = 18
        kwarg['Options'] = {"LevelActions": "|||", "LevelNames": "Off|Boost|Auto", "LevelOffHidden": "false", "SelectorStyle": "0"}

    elif _Type == 'Chrismast_E':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 62
        kwarg['Switchtype'] = 18
        kwarg['Image'] = 14
        kwarg['Options'] = {"LevelActions": "|||||||||||||||", "LevelNames": "none|steady|snow|rainbow|snake|tinkle|fireworks|flag|waves|updown|vintage|fading|collide|strobe|sparkles|carnival|glow", "LevelOffHidden": "false", "SelectorStyle": "1"}

    elif _Type == 'Vibration_Orientation':
        kwarg['Type'] = 243
        kwarg['Subtype'] = 19

    #groups
    elif _Type == 'LightGroup' or _Type == 'groups':
        if "_dim" in _Name:
            kwarg['Type'] = 244
            kwarg['Subtype'] = 62
            kwarg['Switchtype'] = 7
        else:
            kwarg['Type'] = 241
            kwarg['Subtype'] = 7
            kwarg['Switchtype'] = 7
        #if 'bulbs_group' in Images:
        #    kwarg['Image'] = Images['bulbs_group'].ID

    #Scenes
    elif _Type == 'Scenes':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 62
        kwarg['Switchtype'] = 9
        kwarg['Image'] = 9

    else:
        Domoticz.Error("Unknow device type " + _Type )
        return

    kwarg['DeviceID'] = IEEE
    kwarg['Name'] = _Name
    kwarg['Unit'] = Unit
    Domoticz.Device(**kwarg).Create()

    Domoticz.Status("### Create Device " + IEEE + " > " + _Name + ' (' + _Type +') as Unit ' + str(Unit) ) #Devices[Unit].ID
