# WARNING !   
I m making the first official version ATM, so If you have already installed a previous version and install the new one (the 1.0.1), you will have an import error on log   
```
2019-01-11 20:13:35.441 Error: (BasePlug) failed to load 'plugin.py', Python Path used was ':/usr/lib/python35.zip:/usr/lib/python3.5:/usr/lib/python3.5/plat-arm-linux-gnueabihf:/usr/lib/python3.5/lib-dynload'.
2019-01-11 20:13:35.441 Error: (deCONZ) Module Import failed, exception: 'ImportError'
2019-01-11 20:13:35.441 Error: (deCONZ) Module Import failed: ' Name: plugin'
2019-01-11 20:13:35.441 Error: (deCONZ) Error Line details not available.
```
"Easy" to correct.   
- Go to Setting/Hardware
- Select deCONZ on hardware list, all will be empty at bottom.
- Select again "deCONZ plugin" in the selectbox "Type", all the bottom will be back.
- Reconfigure the plugin, all the editbox on the bottom was reset to defaut.

Your devices won't be reset. But your setting, yes, so remember your API key before updating the plugin. I m sorry for that, but I have used a generic name as key on my previous version.


# Domoticz-deCONZ
It's a python plugin for Domoticz (home automation application).   
It use the deCONZ REST API to make a bridge beetween your zigbee network and Domoticz using a Dresden Elektronik gateway.

# Description
To resume you need deCONZ (application to control and set up ZigBee network) https://www.dresden-elektronik.de/funktechnik/products/software/pc-software/deconz/?L=1

You need too a Dresden Elektronik gateway, a Raspbee (for raspberry) or Conbee (USB key), it support lot of Zigbee devices, Xiaomi, Heiman, Ikea, Philips, Osram, ect ....

Official compatibility list https://github.com/dresden-elektronik/deconz-rest-plugin/wiki/Supported-Devices


You can use their GUI, for maintenance, support, look at traffic, set attributes, manage router, use command like identify, update firmware, make RAZ, ect ....

![alt text](https://www.dresden-elektronik.de/typo3temp/pics/f0afa1a806.png)


You can use their Web app, for devices management, pairing, groups, scenes, events, ect ...
![alt text](https://user-images.githubusercontent.com/20152487/48567509-77dad480-e8fd-11e8-877d-2970ebb2c08c.png)


And use this plugin to make bridge beetween their webserver and domoticz.

# Requirement.
deCONZ 2.05.44, ATM, But there a new version every week, so I can't be sure the plugin don't use a special feature you don't have on your version if you use an older one.

Domoticz, current stable version.

# Installation.
- Wtih command line, go to your plugins directory (domoticz/plugin).   
- Run:
```git clone https://github.com/Smanar/Domoticz-deCONZ.git```
- Restart Domoticz.   
- Enable the plugin in hardware page.   

# Configuration.
The plugin don't use special configuration file, except the banned.txt file.   
At every start, it synchronise the deCONZ network with yours domoticz devices, so if you delete a device, at next startup, it will be re-created, so to prevent that, you can put the adress in the banned.txt file.   
Don't worry for name, the plugin never update name even you change it in deCONZ to prevent problems with scripts.

For theses ones who have problems with API Key, there is a file called API_KEY.py to help you to create/delete/get list with command line, informations and commands inside the file. It can too give somes informations like your used websocket port. To have all commands or parameters just use:   
```python3 API_KEY.py```

# Remark
- Take care if you have too much devices, at startup, the plugin add ALL your devices from deCONZ in domoticz (except these one in banned file).

- The plugin works fine, but I haven't tested all possibles devices, so not finished, for group I m using group name from deCONZ, and I don't know yet if it's a good method.

- At final, you can have more devices you have in reality, it's normal, deCONZ can create more than 1 device for 1 real, and it can create for exemple 1 bulb + 2 switches just for 1 physical switch.


# Known issues
- Don't take care about the error message   
```Error: (deCONZ): Socket Shutdown Error: 9, Bad file descriptor```   
I know where is the problem the problem, but I haven't find a way to avoid it, But it change nothing on working mode.

- If you add devices or change devices name for exemple in Phoscon after the plugin have started, the plugin will de desynchronized, and you will have this kind of error message   
```2018-12-29 20:49:32.807 Error: (deConz) Unknow MAJ{'name': 'TRÅDFRI Motion sensor', 'uniqueid': '00:0b:57:ff:xx:xx:xx:xx', 'id': '2', 'r': 'sensors', 't': 'event', 'e': 'changed'}```   
or   
```2018-12-29 20:54:04.979 (deConz) Banned device > 2 (sensors)```   
To solve them, no need to reboot, just restart the plugin, it ynchronise at every start.
To restart plugin : Tab "Harware" > select the hardware "deCONZ" then clic "Update"   

# Versions
- 11/01/19 : 1.0.1 > First official version, The Xiaomi cube now use custom sensor for Rotation, it send now numeric value, so you can use it to vary a light or a volume speaker.
