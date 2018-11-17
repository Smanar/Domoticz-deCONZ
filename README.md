# Domoticz-deCONZ
deCONZ plugin for Domoticz  in python, waiting for native hardware support https://www.domoticz.com/forum/viewtopic.php?f=68&t=25179&p=195222&hilit=deconz#p195222

Official compatibility list https://github.com/dresden-elektronik/deconz-rest-plugin/wiki/Supported-Devices


# Requirement
deCONZ 2.05.44

# Information
WIP project, To resume you need deCONZ (application to control and set up ZigBee network) https://www.dresden-elektronik.de/funktechnik/products/software/pc-software/deconz/?L=1&cHash=c9c902ccdb43164696acccf81b62b2bd

Use a deCONZ device (Raspbee or Conbee)

You can use their GUI, for maintenance, support, look traffic, set attributes, manage router, ect ....
![alt text](https://www.dresden-elektronik.de/typo3temp/pics/f0afa1a806.png)


You can use their Web app, for devices management, pairing, groups, ect ...
![alt text](https://user-images.githubusercontent.com/20152487/48567509-77dad480-e8fd-11e8-877d-2970ebb2c08c.png)


And use this plugin to make bridge beetween their webserver and domoticz.

# Remark
Take care if you have too much devices, at startup, the plugin add ALL your devices from deCONZ in domoticz (except these one in banned file).
