# Domoticz-deCONZ
deCONZ plugin for Domoticz in python, waiting for native hardware support https://www.domoticz.com/forum/viewtopic.php?f=68&t=25179&p=195222&hilit=deconz#p195222.

It use the deCONZ rest api to make a bridge beetween your zigbee network and Domoticz.

# WIP Project

# Requirement.
deCONZ 2.05.44

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

For theses ones who have problems with API Key, there is a file called API_KEY.py to help you to create/delete/get list with command line, informations and commands inside the file.

# Information.
To resume you need deCONZ (application to control and set up ZigBee network) https://www.dresden-elektronik.de/funktechnik/products/software/pc-software/deconz/?L=1

You need too a Dresden Elektronik gateway, a Raspbee (for raspberry) or Conbee (USB key), it support lot of Zigbee devices, XIAOMI, Heiman, IKEA, PHILIPS, ect ....

Official compatibility list https://github.com/dresden-elektronik/deconz-rest-plugin/wiki/Supported-Devices


You can use their GUI, for maintenance, support, look at traffic, set attributes, manage router, use command like identify, update firmware, make RAZ, ect ....

![alt text](https://www.dresden-elektronik.de/typo3temp/pics/f0afa1a806.png)


You can use their Web app, for devices management, pairing, groups, scenes, events, ect ...
![alt text](https://user-images.githubusercontent.com/20152487/48567509-77dad480-e8fd-11e8-877d-2970ebb2c08c.png)


And use this plugin to make bridge beetween their webserver and domoticz.

# Remark
Take care if you have too much devices, at startup, the plugin add ALL your devices from deCONZ in domoticz (except these one in banned file).

The plugin works fine, but I haven't tested all possibles devices, so not finished, for group I m using group name from deCON, so not realy robust

Don't take care about the error message   
```Error: (deCONZ): Socket Shutdown Error: 9, Bad file descriptor```   
I can't find the problem, but it change nothing on working mode.
