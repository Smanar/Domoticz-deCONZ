Sorry for issue, but I m ATM on holidays for somes weeks.

# Domoticz-deCONZ
It's a python plugin for Domoticz (home automation application).   
It use the deCONZ REST API to make a bridge beetween your zigbee network and Domoticz using a Dresden Elektronik gateway.

## Description
To resume:
- you need a Dresden Elektronik gateway, a Raspbee (for raspberry) or Conbee (USB key), it support lot of Zigbee devices, Xiaomi, Heiman, Ikea, Philips, Osram, ect ....   
Official compatibility list https://github.com/dresden-elektronik/deconz-rest-plugin/wiki/Supported-Devices

- You need too deCONZ (their application to control and set up ZigBee network). It can work with an headless mode but you can use their GUI, for maintenance, support, look at traffic, set attributes, manage router, use command like identify https://www.dresden-elektronik.de/funktechnik/products/software/pc-software/deconz/?L=1

- You can use their Web app, for devices management, pairing, groups, scenes, events, ect ... https://phoscon.de/en/app/doc

- And use this plugin to make bridge beetween their webserver and domoticz.

## Requirement.
deCONZ : Last version.   
Domoticz : current stable version.   
Python : You need the requests library, if you have error message like "Module Import failed: ' Name: requests'", you probably miss it, to install it just type:
```
sudo -H pip3 install requests
sudo -H pip install requests
```

## Installation.
- Wtih command line, go to your plugins directory (domoticz/plugin).   
- Run:   
```git clone https://github.com/Smanar/Domoticz-deCONZ.git```
- (If needed) Make the plugin.py file executable:   
```chmod +x Domoticz-deCONZ/plugin.py```
- Restart Domoticz.   
- Enable the plugin in hardware page (hardware page, select deconz plugin, clic "update").   

You can later update the plugin
- With command line, go to the plugin directory (domoticz/plugin/Domoticz-deCONZ).   
- Run:   
```git pull```
- Just restart the plugin, (hardware page, select deconz plugin, clic "update").    

## Configuration.
- The plugin works better with websocketnotifyall option set to true (it's the configuration by default).   
```curl -H 'Content-Type: application/json' -X PUT -d '{"websocketnotifyall": true}' http://IP_DECONZ:80/api/API_KEY/config```
- The plugin don't use special configuration file, except the banned.txt file.   
- At every start, it synchronise the deCONZ network with yours domoticz devices, so if you delete a device, at next startup, it will be re-created, so to prevent that, you can put the adress in the banned.txt file.   
- Don't worry for name, the plugin never update name even you change it in deCONZ to prevent problems with scripts.
- For theses ones who have problems with API Key, there is a file called API_KEY.py to help you to create/delete/get list with command line, informations and commands inside the file. It can too give somes informations like your used websocket port. To have all commands or parameters just use:   
```python3 API_KEY.py```   
And for theses ones who don't know where to find the API key and don't wana use the tool: https://dresden-elektronik.github.io/deconz-rest-doc/configuration/#aquireapikey

## Remark.
- Take care if you have too much devices, at startup, the plugin add ALL your devices from deCONZ in domoticz (except these one in banned file).

- At final, you can have more devices you have in reality, it's normal, deCONZ can create more than 1 device for 1 real, and it can create for exemple 1 bulb + 2 switches just for 1 physical switch.

- If you haven't github acount, the support in domoticz forum is here https://www.domoticz.com/forum/viewtopic.php?f=68&t=25631

- You can't use the native fonction in domoticz for switch (activation devices), because this plugin trigger device event for useless information, like battery level. So instead of using trigger event, you need to use button detected. You have some LUA exemples here : [Use LUA for switch](https://github.com/Smanar/Domoticz-deCONZ/wiki/Examples-to-use-LUA-script-for-switch).   

- You have some others exemples here :
>[Some LUA exemples for sensors](https://github.com/Smanar/Domoticz-deCONZ/wiki/Examples-to-use-LUA-script-for-various-sensors).   
[Using LUA to change setting on the fly](https://github.com/Smanar/Domoticz-deCONZ/wiki/Examples-to-use-LUA-to-change-setting-on-the-fly.).   
[Create a color loop effect with zigbee bulb](https://github.com/Smanar/Domoticz-deCONZ/wiki/Example-to-make-a-color-loop-effect).   
[Mix temperature/humidity/barometer on the same sensor](https://github.com/Smanar/Domoticz-deCONZ/wiki/Example-to-make-a-LUA-script-to-mix-temperature-humidity-barometer-on-the-same-sensor).   

## Known issues.
- Don't take care about the error message   
```Error: (deCONZ): Socket Shutdown Error: 9, Bad file descriptor```   
I know where is the problem the problem, but I haven't find a way to avoid it, But it change nothing on working mode.

- If you add devices or change devices name for exemple in Phoscon after the plugin have started, the plugin will de desynchronized, and you will have this kind of error message   
```2018-12-29 20:49:32.807 Error: (deConz) Unknow MAJ{'name': 'TRÅDFRI Motion sensor', 'uniqueid': '00:0b:57:ff:xx:xx:xx:xx', 'id': '2', 'r': 'sensors', 't': 'event', 'e': 'changed'}```   
or   
```2018-12-29 20:54:04.979 (deConz) Banned device > 2 (sensors)```   
To solve them, no need to reboot, just restart the plugin, it ynchronise at every start.
To restart plugin : Tab "Harware" > select the hardware "deCONZ" then clic "Update"   
- If your system don't support python "Request" lib, you can try older version < 1.0.9.    

## Changelog.
- xx/xx/xx : 1.0.11 (Beta) > All unknows devices will be reconized as on/off controler, because some working device have "Unknow" as type.   
- 23/08/19 : 1.0.10 > Add message information for missing requests lib, make special device for "Tradfri on/off_switch" (thx @erwan2345). The plugin can now add itself missing groups after the starting. Another division by zero correction. Patch for virtual devices with same UniqueId.  
- 20/06/19 : 1.0.9 > Compare database to check deleted devices. Code clean up. The plugin can now add itself missing devices after the starting. Trying to synchronise at start only if the gateway seem ready. Change request code (cf remark). Change Websocket code (thx @salopette).      
- 03/05/19 : 1.0.8 > Adding a tool to delete all useless key created everytime launching Phoscon. Setting Websocket port is now useless. Change switches icon for button instead of bulb. Prevent the system be freezed if the gateway don't answer at a request and using queue list for request to prevent collision. Adding scenes control.Adding some missing bulbs.   
- 14/04/19 : 1.0.7 > Special version, because of a problem in a feature I have make and a deconz version >= 2.05.62, bulb will be set to off just after set to on.
- 07/04/19 : 1.0.6 > starting to implement vibration sensor/Carbonmonoxide sensor/Window covering/thermostat/door lock. Trying to correct bad JSON data on normal connexion. Enable timeout display for no rechables devices. Devices Units correction (thx @fswmlu). Corrections for initialisation device on plugin start and bug on banning groups (Thx @dobber81).
- 04/03/19 : 1.0.5 > improve the case deCONZ is not on same machine than Domoticz. Groups reparation, now you can send for exemple a color level to a complete group with only 1 device. Device update modification, for fast event, like if you press a switch too fast.
- 02/02/19 : 1.0.4 > Modification the way the plugin receive data. Decrease the device update amount, less logs, less notifications, but at least 1 update every 24h to see if the device is still alive.
- 22/01/19 : 1.0.3 > Division by zero bug correction, adding some missing devices, and Xiaomi water leak update (thx to @stefan1957 and @AdamWeglarz)
- 12/01/19 : 1.0.2 > Correction in the situation the user don't have a device category, for exemple, no bulbs.
- 11/01/19 : 1.0.1 > First official version, The Xiaomi cube now use custom sensor for Rotation, it send now numeric value, so you can use it to vary a light or a volume speaker.
