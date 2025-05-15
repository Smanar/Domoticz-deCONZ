# deCONZ bridge, a Zigbee plugin for Domoticz.   
It's a python plugin for Domoticz (home automation application).   
It uses the deCONZ REST API to make a bridge beetween your zigbee network and Domoticz using a Dresden Elektronik gateway and their application.   

## Description
To resume:
- you need a Dresden Elektronik gateway, a Raspbee (for raspberry) or Conbee (USB key), it support a lot of Zigbee devices, Xiaomi, Heiman, Ikea, Philips, Osram, Tuya, ect ....   
Official compatibility list https://github.com/dresden-elektronik/deconz-rest-plugin/wiki/Supported-Devices

- You also need deCONZ (their application to control and set up ZigBee network). It can work with an headless mode but you can use their GUI, for maintenance, support, look at traffic, set attributes, manage router, use command like identify:

![deconz](https://user-images.githubusercontent.com/20152487/73596164-37766f00-4520-11ea-8101-05a102bd6bdf.jpg)


- You can use their Web app, for devices management, pairing, groups, scenes, events, ect ... https://phoscon.de/en/app/doc

![phoscon](https://user-images.githubusercontent.com/20152487/73598455-f3439880-4538-11ea-9c56-0fb18576a44b.png)


- You can use too some android application like Hue essential compatible with deconz ... https://play.google.com/store/apps/dev?id=7433470895643453779

![hue](https://user-images.githubusercontent.com/20152487/189486132-bf16261f-e4d3-40c1-bc9e-23f909c2b166.png)


- And use this plugin to bridge between the deCONZ server and domoticz. The plugin have now a Frontend for some actions (thx to @JayPearlman). To use it, just go in "Custom"/"DeCONZ".   

![domoticz](https://user-images.githubusercontent.com/20152487/102008804-7e81e300-3d33-11eb-8ad4-5949f1eb189e.jpg)   


## Requirement.
deCONZ : Last version.   
Domoticz : current stable version.   
Python : You need the requests library, if you have error message like "Module Import failed: ' Name: requests'", you probably miss it, to install it just type:
```
sudo -H pip3 install requests
sudo -H pip install requests
```

## Installation.
- With command line, go to your plugins directory (domoticz/plugins).   
- Run:   
```git clone https://github.com/Smanar/Domoticz-deCONZ.git```
- (If needed) Make the plugin.py file executable:   
```chmod +x Domoticz-deCONZ/plugin.py```
- Restart Domoticz.   
- Enable the plugin in hardware page (hardware page, select deconz plugin, click "update").   

You can later update the plugin
- With command line, go to the plugin directory (domoticz/plugin/Domoticz-deCONZ).   
- Run:   
```git pull```
- Restart Domoticz.    

To test the beta branch :
```
git pull
git checkout beta
git pull
```


## Configuration.
- The plugin works better with websocketnotifyall option set to true (it's the configuration by default).   
```curl -H 'Content-Type: application/json' -X PUT -d '{"websocketnotifyall": true}' http://IP_DECONZ:80/api/API_KEY/config```
- The plugin doesn't use a special configuration file, except the banned.txt file.   
- At every start, it synchronises the deCONZ network with yours domoticz devices, so if you delete a device, at next startup, it will be re-created, so to prevent that, you can put the adress in the banned.txt file.   
- If you have problem to find your IP or the used port, take a look at https://phoscon.de/discover (Remember better to use 127.0.0.1 if domoticz and deconz are on the same machine).   
- Don't worry about the name, the plugin never updates name even you change it in deCONZ to prevent problems with scripts.   
- If you create a group, it's not possible to identify the type of device they are inside, so the type will be by defaut RGBWWZ to have all options, if you want to create only a dimmer group for exemple add "_dim" at the group name.   
- For those who have problems with API Key, there is a file called API_KEY.py to help you to create/delete/get list with command line, informations and commands inside the file. It can also give some information like your used websocket port. To show all commands or parameters just use:   
```
python3 API_KEY.py
``` 
If using default settings you might be able to obtain the API key using:
```
python3 API_KEY.py 127.0.0.1:80 create
```
And for those who don't know where to find the API key and don't wana use the tool: https://dresden-elektronik.github.io/deconz-rest-doc/getting_started/#acquire-an-api-key    
Or you can just use the Front End in Domoticz/Custom/Deconz.   

- By defaut the plugin use standard setting, you can use special one in the field "specials settings" on the hardware panel, available setting are :   

| Option 	| action |
|---	|---	|
| ENABLEMORESENSOR | enable tension and current sensors	|
| ENABLEBATTERYWIDGET	| create a  special widget by device just for battery |


## Remark.
- There is a deconz Discord channel https://discord.gg/QFhTxqN

- Take care if you have too many devices, at startup, the plugin adds ALL your devices from deCONZ in domoticz (except those who are in banned file).

- Finally, you can see more devices than you have in reality. This is normal, deCONZ can create more than 1 device for 1 real, and it can create for example 1 bulb + 2 switches just for 1 physical switch.

- If you haven't github acount, the support in domoticz forum is here https://www.domoticz.com/forum/viewtopic.php?f=68&t=25631

- You can't use the native function in domoticz for switch (activation devices), because this plugin trigger device event for useless information, like battery level. So instead of using trigger event, you need to use button detected. You have some LUA examples here : [Use LUA for switch](https://github.com/Smanar/Domoticz-deCONZ/wiki/Examples-to-use-LUA-script-for-switch).   

- You have some others examples here :
>[Some LUA examples for sensors](https://github.com/Smanar/Domoticz-deCONZ/wiki/Examples-to-use-LUA-script-for-various-sensors).   
[Using LUA to change setting on the fly](https://github.com/Smanar/Domoticz-deCONZ/wiki/Examples-to-use-LUA-to-change-setting-on-the-fly.).   
[Create a color loop effect with zigbee bulb](https://github.com/Smanar/Domoticz-deCONZ/wiki/Example-to-make-a-color-loop-effect).   
[Mix temperature/humidity/barometer on the same sensor](https://github.com/Smanar/Domoticz-deCONZ/wiki/Example-to-make-a-LUA-script-to-mix-temperature-humidity-barometer-on-the-same-sensor).   

## Known issues.
- Don't take care about the error message   
```Error: (deCONZ): Socket Shutdown Error: 9, Bad file descriptor```   
I know where is the problem the problem, but I haven't find a way to avoid it, But it change nothing on working mode.

- If you add devices or change devices name for example in Phoscon after the plugin have started, the plugin will de desynchronized, and you will have this kind of error message   
```2018-12-29 20:49:32.807 Error: (deConz) Unknow MAJ{'name': 'TRÅDFRI Motion sensor', 'uniqueid': '00:0b:57:ff:xx:xx:xx:xx', 'id': '2', 'r': 'sensors', 't': 'event', 'e': 'changed'}```   
or   
```2018-12-29 20:54:04.979 (deConz) Banned device > 2 (sensors)```   
To solve them, no need to reboot, just restart the plugin, it synchronises at every start.
To restart plugin : Tab "Hardware" > select the hardware "deCONZ" then click "Update"   
- If your system doesn't support python "Request" lib, you can try older version < 1.0.9.    

## Changelog.
- 15/05/25 : 1.0.34 > Make custom page working again, improve Aqara Cube Pro T1 support, thx @Sumd84 .    
- 17/03/25 : 1.0.33 > Solve issue for air quality sensor again.   
- 20/10/24 : 1.0.32 > Solve issue during installation for dockers users (thx to @RneeJ), solve issue for air quality sensor.   
- 27/04/24 : 1.0.31 > Solve issue about "invalid literal", solve issue about CLIPDaylightOffset, solve issue if you use ENABLEBATTERYWIDGET.   
- 10/02/24 : 1.0.30 > Solve issue with "mode" widget for thermostat, improve air quality sensor support.   
- 28/10/23 : 1.0.29 > Add support for moisture sensor, add support for double consumption, add an error widget about deconz status.   
- 24/05/23 : 1.0.28 > Add support for New Xiaomi Cube T1/ T1 pro thx @Sumd84 , the widget created by the option "ENABLEBATTERYWIDGET" have now different icons according to batery level, thx @BabaIsYou , remove error about "capabilities".   
- 17/02/23 : 1.0.27 > Add special support for the Ikea Starkvind thx @arjannv , add support for the Alarm System, and the support for keypad, see https://github.com/Smanar/Domoticz-deCONZ/wiki/How-to-add-keypad-to-domoticz thx @BabaIsYou , add new option ENABLEBATTERYWIDGET ,remove "capabilities" error message.   
- 12/11/22 : 1.0.26 > Make the widget for covering work again, following the Domoticz update. Create a widget with consumption and power for some devices that are able to support it, (thx @BabaIsYou)
- 10/09/22 : 1.0.25 > It's now possible to clean the unused API key used for Hue Essentials, add support for binary module, with the develco one, add "pulseconfiguration" as possible setting in the GUI, thx @Jemand .   
- Correct an issue for thermostat with "mode" not updated.
- 08/05/22 : 1.0.24 > This version contain various correctives for consumption/power sensors.   
- 15/03/22 : 1.0.23 > Can create tension and current widget (need to be enabled in hardware panel), new path system for docker installation (to correct front end issue), Add new field in config, to be used as special setting later, somes change on covering support.
- 29/12/21 : 1.0.22 > Add specific widget for the Ikea Styrbar, optimisation/update for covering, some devices correctives, thx to @veitk, @RDols and @sonar98.   
- 20/09/21 : 1.0.21 > Warning device use now a selector switch instead of a 2 position one, add some new value for ZGP switches, repair the front end to be able to set "0" value, add a tool to clean the API key list.    
- 03/07/21 : 1.0.20 > add primary support for ZHAAirQuality, repair of frontend, now it s possible again to configure device.   
- 15/06/21 : 1.0.19 > Make special widget for Tuya switches and philips RWL02 one. Starting to repair siren. Increase Websocket buffer to prevent message "Incomplete JSON keep it for later". Add the possibility to see the deconz config on the front-end.    
- 18/04/21 : 1.0.18 > Set light state to off if detected off line (thx @nonolk), starting to implement ZHADoorlock.   
- 14/03/21 : 1.0.17 > Grammar corrections, corrective for power sensor, can retreive raw data from Xiaomi cube (to get side), improve widget for extended color light, adding remote covering devices.
- 13/12/20 : 1.0.16 > Correction to support Ally thermostat (@johnsprogs), the Xiaomi sensor return the 3 angles (@flopp999), the xiaomi cube can give complete information (@kispalsz ), Color correction for devices that don't support XY, the frontend (@JayPearlman), support of the Lidl Melinera Smart XMAS LED string lights (@sonar98), can specify type for group (@Plantje).   
- 01/08/20 : 1.0.15 > Better support for Friend of HUE device. Disable error message about the gateway.
- 25/06/20 : 1.0.14 > Handle the new websocket "attr", special widget for Xiaomi Aqara single gang (thx to @markiboy2all).
- 28/05/20 : 1.0.13 > Delete banned_devices.txt from github, it will be created by the plugin, create specific widget for Aquara Opple and Xiaomi double gang (thx to @eserero), critic bug correction for Xiaomi plug (thx to @xxLeoxx93).
- 27/01/20 : 1.0.12 > Correction for some Philips hue, correction for thermostat devices, change consumption widget for some devices, remove domoticz batterie alert if device have bad return for battery level, patch for group with UniqueId.
- 09/11/19 : 1.0.11 > All unknows devices will be recognized as on/off controler, because some working device have "Unknow" as type. Improving detection for fan and range extender. Adding Thermostat support (thx to @salopette). Adding support for long press on ikea remote. Reparation for Shutter control.   
- 23/08/19 : 1.0.10 > Add message information for missing requests lib, make special device for "Tradfri on/off_switch" (thx @erwan2345). The plugin can now add itself missing groups after the starting. Another division by zero correction. Patch for virtual devices with same UniqueId.  
- 20/06/19 : 1.0.9 > Compare database to check deleted devices. Code clean up. The plugin can now add itself missing devices after the starting. Trying to synchronise at start only if the gateway seem ready. Change request code (cf remark). Change Websocket code (thx @salopette).      
- 03/05/19 : 1.0.8 > Adding a tool to delete all useless key created everytime launching Phoscon. Setting Websocket port is now useless. Change switches icon for button instead of bulb. Prevent the system be freezed if the gateway don't answer at a request and using queue list for request to prevent collision. Adding scenes control.Adding some missing bulbs.   
- 14/04/19 : 1.0.7 > Special version, because of a problem in a feature I have make and a deconz version >= 2.05.62, bulb will be set to off just after set to on.
- 07/04/19 : 1.0.6 > starting to implement vibration sensor/Carbonmonoxide sensor/Window covering/thermostat/door lock. Trying to correct bad JSON data on normal connexion. Enable timeout display for no rechables devices. Devices Units correction (thx @fswmlu). Corrections for initialisation device on plugin start and bug on banning groups (Thx @dobber81).
- 04/03/19 : 1.0.5 > improve the case deCONZ is not on same machine than Domoticz. Groups reparation, now you can send for example a color level to a complete group with only 1 device. Device update modification, for fast event, like if you press a switch too fast.
- 02/02/19 : 1.0.4 > Modification the way the plugin receive data. Decrease the device update amount, less logs, less notifications, but at least 1 update every 24h to see if the device is still alive.
- 22/01/19 : 1.0.3 > Division by zero bug correction, adding some missing devices, and Xiaomi water leak update (thx to @stefan1957 and @AdamWeglarz)
- 12/01/19 : 1.0.2 > Correction in the situation the user don't have a device category, for example, no bulbs.
- 11/01/19 : 1.0.1 > First official version, The Xiaomi cube now use custom sensor for Rotation, it send now numeric value, so you can use it to vary a light or a volume speaker.
