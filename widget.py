#!/usr/bin/env python3
# coding: utf-8 -*-

def Createdatawidget(IEEE, _Name, _Type, opt):

    kwarg = {}

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

    elif _Type == 'Color Temperature dimmable light':
        kwarg['Type'] = 241
        kwarg['Subtype'] = 4
        kwarg['Switchtype'] = 7

    #Some device have unknow as type, but are full working.
    elif _Type == 'Unknown':
        Domoticz.Error("Unknow device : assume a light " + IEEE + " > " + _Name + ' (' + _Type +')' )
        kwarg['Type'] = 244
        kwarg['Subtype'] = 73
        kwarg['Switchtype'] = 0

    elif _Type == 'Window covering device' or _Type == 'Window covering controller' :
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
        kwarg['Subtype'] = 62
        kwarg['Switchtype'] = 18
        kwarg['Image'] = 13
        kwarg['Options'] = {"LevelActions": "|||", "LevelNames": "none|select|lselect|blink", "LevelOffHidden": "false", "SelectorStyle": "0"}

    #Sensors
    elif _Type == 'Daylight':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 73
        kwarg['Switchtype'] = 9

    elif _Type == 'ZHATemperature' or _Type == 'CLIPTemperature':
        kwarg['TypeName'] = 'Temperature'

    elif _Type == 'ZHAHumidity' or _Type == 'CLIPHumidity':
        kwarg['TypeName'] = 'Humidity'

    elif _Type == 'ZHAMoisture':
        kwarg['TypeName'] = 'Soil Moisture'

    elif _Type == 'ZHAPressure'or _Type == 'CLIPPressure':
        kwarg['TypeName'] = 'Barometer'

    elif _Type == 'ZHAAirQuality' or _Type == 'ZHAParticulateMatter':
        #kwarg['TypeName'] = 'Air Quality'
        kwarg['TypeName'] = 'Custom'
        if opt == 1:
            kwarg['Options'] = {"Custom": ("1;μg/m³")}
        else:
            kwarg['Options'] = {"Custom": ("1;ppb")}

    elif _Type == 'ZHAAirPurifier':
        kwarg['TypeName'] = 'Custom'
        kwarg['Image'] = 7
        kwarg['Options'] = {"Custom": ("1;m/s")}

    elif _Type == 'ZHAOpenClose' or _Type == 'CLIPOpenClose'  or _Type == 'ZHADoorLock':
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
        if opt == 0:
            kwarg['Type'] = 113
            kwarg['Subtype'] = 0
            kwarg['Switchtype'] = 0
        elif opt == 1:
            #Device with power and energy
            kwarg['TypeName'] = 'kWh'
        else:
            #Device with consumption_2
            kwarg['Type'] = 250
            kwarg['Subtype'] = 1

    elif _Type == 'ZHAPower':# in W
        kwarg['TypeName'] = 'Usage'
    elif _Type == 'ZHAPower_voltage':
            kwarg['Type'] = 243
            kwarg['Subtype'] = 8
    elif _Type == 'ZHAPower_current':
            kwarg['Type'] = 243
            kwarg['Subtype'] = 23

    elif _Type == 'ZHAAncillaryControl':
        kwarg['Type'] = 243
        kwarg['Subtype'] = 22

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
    elif _Type == 'Xiaomi_Opple_6_button_switch':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 62
        kwarg['Switchtype'] = 18
        kwarg['Image'] = 9
        kwarg['Options'] = {"LevelActions": "|||||||||||||||||", "LevelNames": "Off|B1|B2|B3|B4|B5|B6|B1L|B2L|B3L|B4L|B5L|B6L|B1RL|B2RL|B3RL|B4RL|B5RL|B6RL|B1D|B2D|B3D|B4D|B5D|B6D|B1T|B2T|B3T|B4T|B5T|B6T", "LevelOffHidden": "true", "SelectorStyle": "1"}
    elif _Type == 'Tuya_button_switch':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 62
        kwarg['Switchtype'] = 18
        kwarg['Image'] = 9
        kwarg['Options'] = {"LevelActions": "|||||||||||||", "LevelNames": "Off|B1|L1|D1|B2|L2|D2|B3|L3|D3|B4|L4|D4", "LevelOffHidden": "true", "SelectorStyle": "1"}
    elif _Type == 'Philips_button_switch':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 62
        kwarg['Switchtype'] = 18
        kwarg['Image'] = 9
        kwarg['Options'] = {"LevelActions": "|||||||||", "LevelNames": "Off|B1|L1|B2|L2|B3|L3|B4|L4", "LevelOffHidden": "true", "SelectorStyle": "1"}
    elif _Type == 'Binary_module':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 62
        kwarg['Switchtype'] = 18
        kwarg['Image'] = 9
        kwarg['Options'] = {"LevelActions": "|||", "LevelNames": "Unknow|On|Off", "LevelOffHidden": "true", "SelectorStyle": "1"}

    elif _Type == 'Styrbar_remote':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 62
        kwarg['Switchtype'] = 18
        kwarg['Image'] = 9
        kwarg['Options'] = {"LevelActions": "||||||||||||", "LevelNames": "V0|V1|V2|V3|V4|V5|V6|V7|V8|V9|V10|V11|V12", "LevelOffHidden": "true", "SelectorStyle": "0"}

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

    elif _Type == 'XCubeProT1_C':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 62
        kwarg['Switchtype'] = 18
        kwarg['Image'] = 9
        kwarg['Options'] = {"LevelActions": "||||||||||||", "LevelNames": "Off|F1|F2|F3|F4|F5|F6|Wake|Shake|Push|Tap|Drop", "LevelOffHidden": "true", "SelectorStyle": "0"}

    elif _Type == 'XCube_R':
        kwarg['TypeName'] = 'Custom'
        kwarg['Options'] = {"Custom": ("1;degree")}

    elif _Type == 'XCubeProT1_R':
        kwarg['TypeName'] = 'Custom'
        kwarg['Options'] = {"Custom": ("1;degree")}

    elif _Type == 'ZHARelativeRotary':
        kwarg['TypeName'] = 'Custom'
        kwarg['Options'] = {"Custom": ("1;degree")}

    elif _Type == 'Thermostat_Mode':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 62
        kwarg['Switchtype'] = 18
        kwarg['Options'] = {"LevelActions": "|||", "LevelNames": "Off|Heat|Auto", "LevelOffHidden": "false", "SelectorStyle": "0"}

    elif _Type == 'Purifier_Mode':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 62
        kwarg['Switchtype'] = 18
        kwarg['Image'] = 7
        kwarg['Options'] = {"LevelActions": "|||||||", "LevelNames": "Off|Auto|S1|S2|S3|S4|S5", "LevelOffHidden": "false", "SelectorStyle": "0"}

    elif _Type == 'Thermostat_Preset':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 62
        kwarg['Switchtype'] = 18
        kwarg['Options'] = {"LevelActions": "|||||||||", "LevelNames": "Off|holiday|auto|manual|comfort|eco|boost|complex|program", "LevelOffHidden": "true", "SelectorStyle": "1"}

    elif _Type == 'Chrismast_E':
        kwarg['Type'] = 244
        kwarg['Subtype'] = 62
        kwarg['Switchtype'] = 18
        kwarg['Image'] = 14
        kwarg['Options'] = {"LevelActions": "||||||||||||||||", "LevelNames": "off|none|steady|snow|rainbow|snake|twinkle|fireworks|flag|waves|updown|vintage|fading|collide|strobe|sparkles|carnival|glow", "LevelOffHidden": "true", "SelectorStyle": "1"}

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

    return kwarg
