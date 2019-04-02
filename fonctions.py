#!/usr/bin/env python3
# coding: utf-8 -*-

import Domoticz
buffercommand = {}

#****************************************************************************************************
# Global fonctions

def DecodeByteArray(stringStreamIn):
    # Turn string values into opererable numeric byte values
    byteArray = [ord(character) for character in stringStreamIn]
    datalength = byteArray[1] & 127
    indexFirstMask = 2

    if datalength == 126:
        indexFirstMask = 4
    elif datalength == 127:
        indexFirstMask = 10

    indexFirstDataByte = indexFirstMask

    #Data are masked ?
    if byteArray[1] & 128:
        # Extract masks
        masks = [m for m in byteArray[indexFirstMask : indexFirstMask+4]]
        indexFirstDataByte = indexFirstDataByte + 4
        print (str(masks))
    else:
        masks = [0,0,0,0]

    # List of decoded characters
    decodedChars = []
    i = indexFirstDataByte
    j = 0

    # Loop through each byte that was received
    while i < len(byteArray):

        # Unmask this byte and add to the decoded buffer
        decodedChars.append( chr(byteArray[i] ^ masks[j % 4]) )
        i += 1
        j += 1

    # Return the decoded string
    return  ''.join(decodedChars).strip()

def rgb_to_xy(rgb):
    ''' convert rgb tuple to xy tuple '''
    red, green, blue = rgb
    r = ((red + 0.055) / (1.0 + 0.055))**2.4 if (red > 0.04045) else (red / 12.92)
    g = ((green + 0.055) / (1.0 + 0.055))**2.4 if (green > 0.04045) else (green / 12.92)
    b = ((blue + 0.055) / (1.0 + 0.055))**2.4 if (blue > 0.04045) else (blue / 12.92)
    X = r * 0.664511 + g * 0.154324 + b * 0.162028
    Y = r * 0.283881 + g * 0.668433 + b * 0.047685
    Z = r * 0.000088 + g * 0.072310 + b * 0.986039
    cx = 0
    cy = 0
    if (X + Y + Z) != 0:
        cx = X / (X + Y + Z)
        cy = Y / (X + Y + Z)
    return (cx, cy)

def rgb_to_hsl(rgb):
    ''' convert rgb tuple to hls tuple '''
    r, g, b = rgb
    r = float(r/255)
    g = float(g/255)
    b = float(b/255)
    high = max(r, g, b)
    low = min(r, g, b)
    h, s, l = ((high + low) / 2,)*3

    if high == low:
        h = 0.0
        s = 0.0
    else:
        d = high - low
        s = d / (2 - high - low) if l > 0.5 else d / (high + low)
        h = {
            r: (g - b) / d + (6 if g < b else 0),
            g: (b - r) / d + 2,
            b: (r - g) / d + 4,
        }[high]
        h /= 6

    return h, s, l

def hsl_to_rgb(h, s, l):
    def hue_to_rgb(p, q, t):
        t += 1 if t < 0 else 0
        t -= 1 if t > 1 else 0
        if t < 1/6: return p + (q - p) * 6 * t
        if t < 1/2: return q
        if t < 2/3: p + (q - p) * (2/3 - t) * 6
        return p

    if s == 0:
        r, g, b = l, l, l
    else:
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        r = hue_to_rgb(p, q, h + 1/3)
        g = hue_to_rgb(p, q, h)
        b = hue_to_rgb(p, q, h - 1/3)

    return r, g, b

def xy_to_rgb(x, y, brightness = 1):

    x = float(x)
    y = float(y)
    z = 1.0 - x - y;

    Y = brightness
    X = (Y / y) * x
    Z = (Y / y) * z

    r =  X * 1.656492 - Y * 0.354851 - Z * 0.255038;
    g = -X * 0.707196 + Y * 1.655397 + Z * 0.036152;
    b =  X * 0.051713 - Y * 0.121364 + Z * 1.011530;

    r = 12.92 * r if r <= 0.0031308 else (1.0 + 0.055) * pow(r, (1.0 / 2.4)) - 0.055
    g = 12.92 * g if g <= 0.0031308 else (1.0 + 0.055) * pow(g, (1.0 / 2.4)) - 0.055
    b = 12.92 * b if b <= 0.0031308 else (1.0 + 0.055) * pow(b, (1.0 / 2.4)) - 0.055

    if (r > b) and (r > g):
        if (r > 1.0):
            g = g / r
            b = b / r
            r = 1.0

    elif (g > b) and (g > r):
        if (g > 1.0):
            r = r / g
            b = b / g
            g = 1.0

    elif (b > r) and (b > g):
        if (b > 1.0):
            r = r / b
            g = g / b
            b = 1.0

    return {'r': int(r * 255), 'g': int(g * 255), 'b': int(b * 255)}


def Count_Type(d):
    b = l = s = g = o = 0
    for i in d:
        if d[i]['type'] == 'lights':
            l += 1
        elif d[i]['type'] == 'sensors':
            s += 1
        elif d[i]['type'] == 'groups':
            g += 1
        else:
            o += 1

        if d[i].get('Banned',False) == True:
            b += 1
    return l,s,g,b,o

def First_Json(data):
    s = ''
    b = 0
    for c in data:
        s += c
        if c == '{':
            b += 1
        if c == '}':
            b -= 1
            if b == 0:
                return s
    return False

def JSON_Repair(data):
    s = e = p = 0
    c = 0
    b = ''

    while True:
        if c == 0:
            p = data.find('[',p)
            s = p
        else:
            p = data.find(']',p)
            e = p
        c = 1 - c
        if p == -1:
            break

        if e > s:
            if len(b) > 0:
                b += ','
            b += data[s + 1:e]

    return '[' + b + ']'

#**************************************************************************************************
# Domoticz fonctions
#
#https://github.com/dresden-elektronik/deconz-rest-plugin/wiki/Supported-Devices

def ProcessAllConfig(data):
    kwarg = {}

    if 'battery' in data:
        kwarg.update(ReturnUpdateValue( 'battery' , data['battery'] ) )
    if 'heatsetpoint' in data:
        kwarg.update(ReturnUpdateValue( 'heatsetpoint' , data['heatsetpoint'] ) )
    if 'reachable' in data:
        if data['reachable'] == False:
            kwarg.update({'TimedOut':1})

    return kwarg

def ProcessAllState(data,model):
    # Lux need to be > lightlevel > daylight > dark
    # xy > ct > bri > on/off
    # current > power > consumption
    # status > daylight > all

    kwarg = {}

    if 'status' in data:
        kwarg.update(ReturnUpdateValue( 'status' , data['status'] ) )
    if 'on' in data:
        kwarg.update(ReturnUpdateValue( 'on' , data['on'] , model) )
    if 'xy' in data:
        kwarg.update(ReturnUpdateValue( 'xy' , data['xy'] ) )
    if 'x' in data:
        kwarg.update(ReturnUpdateValue( 'x' , data['x'] ) )
    if 'y' in data:
        kwarg.update(ReturnUpdateValue( 'y' , data['y'] ) )
    if 'ct' in data:
        kwarg.update(ReturnUpdateValue( 'ct' , data['ct'] ) )
    if 'bri' in data:
        kwarg.update(ReturnUpdateValue( 'bri' , data['bri'] , model) )
    if 'temperature' in data:
        kwarg.update(ReturnUpdateValue( 'temperature' , data['temperature'] ) )
    if 'pressure' in data:
        kwarg.update(ReturnUpdateValue( 'pressure' , data['pressure'] ) )
    if 'humidity' in data:
        kwarg.update(ReturnUpdateValue( 'humidity' , data['humidity'] ) )
    if 'open' in data:
        kwarg.update(ReturnUpdateValue( 'open' , data['open'] ) )
    if 'presence' in data:
        kwarg.update(ReturnUpdateValue( 'presence' , data['presence'] ) )
    if 'daylight' in data:
        kwarg.update(ReturnUpdateValue( 'daylight' , data['daylight'] ) )
    #if 'lightlevel' in data:
    #    kwarg.update(ReturnUpdateValue( 'lightlevel' , data['lightlevel'] ) )
    if 'lux' in data:
        kwarg.update(ReturnUpdateValue( 'lux' , data['lux'] ) )
    if 'consumption' in data:
        kwarg.update(ReturnUpdateValue( 'consumption' , data['consumption'] ) )
    if 'power' in data:
        kwarg.update(ReturnUpdateValue( 'power' , data['power'] ) )
    if 'current' in data:
        kwarg.update(ReturnUpdateValue( 'current' , data['current'] ) )
    if 'battery' in data:
        kwarg.update(ReturnUpdateValue( 'battery' , data['battery'] ) )
    if 'buttonevent' in data:
        kwarg.update(ReturnUpdateValue( 'buttonevent' , data['buttonevent'] ) )
    if 'flag' in data:
        kwarg.update(ReturnUpdateValue( 'flag' , data['flag'] ) )
    if 'water' in data:
        kwarg.update(ReturnUpdateValue( 'water' , data['water'] ) )
    if 'fire' in data:
        kwarg.update(ReturnUpdateValue( 'fire' , data['fire'] ) )
    if 'alert' in data:
        kwarg.update(ReturnUpdateValue( 'alert' , data['alert'] ) )
    if 'carbonmonoxide' in data:
        kwarg.update(ReturnUpdateValue( 'carbonmonoxide' , data['carbonmonoxide'] ) )
    #if 'lastupdated' in data:
    #    kwarg.update(ReturnUpdateValue( 'lastupdated' , data['lastupdated'] ) )

    #For groups
    if 'all_on' in data:
        kwarg.update(ReturnUpdateValue( 'all_on' , data['all_on'] ) )
    if 'any_on' in data:
        kwarg.update(ReturnUpdateValue( 'any_on' , data['any_on'] ) )

    #Special
    if 'reachable' in data:
        if data['reachable'] == False:
            kwarg.update({'TimedOut':1})

    return kwarg

def ReturnUpdateValue(command,val,model = None):

    if not val:
        val = 0

    val = str(val)
    command = str(command)

    kwarg = {}

    #operator
    if command == 'on':
        if val == 'True':
            kwarg['nValue'] = 1
            if model == 'Window covering device':
                kwarg['sValue'] = '100'
            else:
                kwarg['sValue'] = 'on'
        else:
            kwarg['nValue'] = 0
            if model == 'Window covering device':
                kwarg['sValue'] = '0'
            else:
                kwarg['sValue'] = 'off'

    if command == 'bri':
        #kwarg['nValue'] = 1
        val = int(int(val) * 100 / 255 )
        if model == 'Window covering device':
            if val < 2:
                kwarg['sValue'] = '0'
                kwarg['nValue'] = 0
            elif val > 99:
                kwarg['sValue'] = '100'
                kwarg['nValue'] = 1
            else:
                kwarg['sValue'] = str(val)
                kwarg['nValue'] = 2
        else:
            kwarg['sValue'] = str(val)

    if command == 'x' or command == 'y':
        buffercommand[command] = val
        if buffercommand.get('x') and buffercommand.get('y'):
            rgb = xy_to_rgb(int(buffercommand['x']),int(buffercommand['y']),1)
            kwarg['Color'] = '{"b":' + str(rgb['b']) + ',"cw":0,"g":' + str(rgb['g']) + ',"m":3,"r":' + str(rgb['r']) + ',"t":0,"ww":0}'
            buffercommand.clear()

    if command == 'xy':
        x,y = eval(str(val))
        rgb = xy_to_rgb(x,y,1)
        #kwarg['nValue'] = 1
        #kwarg['sValue'] = str(255)
        kwarg['Color'] = '{"b":' + str(rgb['b']) + ',"cw":0,"g":' + str(rgb['g']) + ',"m":3,"r":' + str(rgb['r']) + ',"t":0,"ww":0}'

    if command == 'ct':
        #Correct values are from 153 (6500K) up to 588 (1700K) so uselss if < 1
        if int(val) > 1:
            ct = 1000000  // int(val)
            ct = -((ct - 1700) / ((6500.0-1700.0)/255.0) - 255 )
            ct = int(ct)
            if ct < 0:
                ct = 0
            if ct > 255:
                ct = 255
            #kwarg['nValue'] = 1
            #kwarg['sValue'] = str(255)
            kwarg['Color'] = '{"ct":' + str(ct) + ',"t":0,"ww":0}'

    #groups
    if command == 'all_on' or command == 'any_on':
        if val == 'True':
            kwarg['nValue'] = 1
            kwarg['sValue'] = 'on'
        else:
            kwarg['nValue'] = 0
            kwarg['sValue'] = 'off'

    #sensor
    if command == 'open':
        if val == 'True':
            kwarg['nValue'] = 1
            kwarg['sValue'] = 'Open'
        else:
            kwarg['nValue'] = 0
            kwarg['sValue'] = 'Closed'

    if command == 'flag' or command == 'water' or command == 'fire' or command == 'presence' or command == 'alert' or command == 'carbonmonoxide':
        if val == 'True':
            kwarg['nValue'] = 1
            kwarg['sValue'] = 'On'
        else:
            kwarg['nValue'] = 0
            kwarg['sValue'] = 'Off'

    if command == 'temperature':
        kwarg['nValue'] = 0
        val = round( int(val) / 100 , 2  )
        kwarg['sValue'] = str(val)

    if command == 'heatsetpoint':
        val = round( int(val) / 100 , 2  )
        kwarg['heatsetpoint'] = str(val)

    if command == 'status':
        if int(val) == 0:
            kwarg['nValue'] = 0
            kwarg['sValue'] = str(val)
        else:
            kwarg['nValue'] = 1
            kwarg['sValue'] = str(val)

    if command == 'pressure':
        kwarg['nValue'] = 0
        kwarg['sValue'] = str(val)

    if command == 'humidity':
        val = int( int(val) / 100)
        kwarg['nValue'] = val
        kwarg['sValue'] = '0'

    if command == 'lightlevel':
        kwarg['nValue'] = 0
        kwarg['sValue'] = str(val)

    if command == 'lux':
        kwarg['nValue'] = 0
        kwarg['sValue'] = str(val)

    if command == 'consumption':
        kwarg['nValue'] = 0
        kwarg['sValue'] = str(val)

    if command == 'power':
        kwarg['nValue'] = 0
        kwarg['sValue'] = str(val)

    if command == 'current':
        kwarg['nValue'] = 0
        kwarg['sValue'] = str(val)

    if command == 'daylight':
        if val == 'True':
            kwarg['nValue'] = 1
            kwarg['sValue'] = 'On'
        else:
            kwarg['nValue'] = 0
            kwarg['sValue'] = 'Off'

    #switch
    if command == 'buttonevent':
        kwarg['nValue'] = int(val)
        kwarg['sValue'] = str(val)

    # other
    if command == 'battery':
        if not val.isdigit():
            kwarg['BatteryLevel'] = 255
        else:
            kwarg['BatteryLevel'] = int(val)

    if command == 'xxxx':
        kwarg['SignalLevel'] = 100

    #if command == 'lastupdated':
    #    kwarg['LastUpdate'] = val.replace('T',' ')

    return kwarg

#https://github.com/dresden-elektronik/deconz-rest-plugin/issues/138
def ButtonconvertionXCUBE_R(val):
    kwarg = {}

    kwarg['nValue'] = int(val)

    if kwarg['nValue'] == 0:
        kwarg['sValue'] = 'Off'
    else:
        kwarg['sValue'] = str( kwarg['nValue'] )

    return kwarg

def ButtonconvertionXCUBE(val):
    kwarg = {}
    val = str(val)
    if val == '0':# off
        kwarg['nValue'] = 0
    elif val == '7007':# shake
        kwarg['nValue'] = 10
    elif val == '7000': # wake
        kwarg['nValue'] = 20
    elif val == '7008':# drop
        kwarg['nValue'] = 30
    elif int(val[3]) == (7 - int(val[0])) :# 180 flip
        kwarg['nValue'] = 50
    elif val[1:] == '000':# push
        kwarg['nValue'] = 60
    elif val[0] == val[3]:# double tap
        kwarg['nValue'] = 70
    else:# 90 flip
        kwarg['nValue'] = 40

    if kwarg['nValue'] == 0:
        kwarg['sValue'] = 'Off'
    else:
        kwarg['sValue'] = str( kwarg['nValue'] )

    return kwarg

def ButtonconvertionTradfriRemote(val):
    kwarg = {}
    val = str(val)

    if val == '1002':
        kwarg['nValue'] = 10
    elif val == '2002':
        kwarg['nValue'] = 20
    elif val == '3002':
        kwarg['nValue'] = 30
    elif val == '4002':
        kwarg['nValue'] = 40
    elif val == '5002':
        kwarg['nValue'] = 50
    else:
        kwarg['nValue'] = 0

    if kwarg['nValue'] == 0:
        kwarg['sValue'] = 'Off'
    else:
        kwarg['sValue'] = str( kwarg['nValue'] )

    return kwarg

def ButtonconvertionGeneric(val):
    kwarg = {}
    val = "%04d" % val
    Button_Number = val[0]
    Button_Action = val[3]

    v = 0

    if Button_Action == '2': #  Release (after press)
        v = 10
    if Button_Action == '3': # Release (after hold)
        v = 20
    if Button_Action == '4': # Double press
        v = 30
    if Button_Action == '5': # Triple press
        v = 40
    if Button_Action == '6': # Quadruple press
        v = 50
    if Button_Action == '7': # shake
        v = 60

    kwarg['nValue'] = v * int(Button_Number)

    if kwarg['nValue'] == 0:
        kwarg['sValue'] = 'Off'
    else:
        kwarg['sValue'] = str( kwarg['nValue'] )

    return kwarg

#https://github.com/dresden-elektronik/deconz-rest-plugin/issues/748
def VibrationSensorConvertion(val_v,val_t):
    kwarg = {}

    v = 0

    kwarg['nValue'] = v

    if kwarg['nValue'] == 0:
        kwarg['sValue'] = 'Off'
    else:
        kwarg['sValue'] = str( kwarg['nValue'] )

    return kwarg
