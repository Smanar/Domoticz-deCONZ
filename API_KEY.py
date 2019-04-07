#!/usr/bin/env python3
# coding: utf-8 -*-

import sys
import urllib,json
try:
	from urllib import request, parse
except:
	print('This tool is for python 3, use instead "python3 API_KEY.py" !')
	sys.exit(0)

try:
    ip = sys.argv[1]
    action = sys.argv[2]
    data = sys.argv[3:]
except:
    action = 'error'

if action == 'create':
    query_args = '{"devicetype":"Domoticz"}'
    data = query_args.encode('utf-8')
    req = request.Request('http://' + ip + '/api',data)
    #request.add_header('Referer', 'http://www.python.org/')
    try:
        response = request.urlopen(req).read()
        response = response.decode("utf-8", "ignore")
        j = eval(response)
        print ("Your new API key is : " + j[0]["success"]['username'])

    except urllib.error.URLError as e:
        if e.code == 403:
            print('Please unlock the gateway first and retry !')

elif action == 'list':
    if len(data) < 1:
        print('Missing params !')
    else:
        req = request.Request('http://' + ip + '/api/' + data[0] + '/config')
        response = request.urlopen(req).read()
        response = response.decode("utf-8", "ignore")
        j = json.loads(response)
        j2 = j['whitelist']
        for i in j2:
            print ('KEY : ' + i + ' Name : ' + j2[i]['name'] + ' Last used : ' + j2[i]['last use date'] )

elif action == 'delete':
    if len(data) < 2:
        print('Missing params !')
    else:
        req = request.Request('http://' + ip + '/api/' + data[0] + '/config/whitelist/' + data[1] , method='DELETE')
        try:
            response = request.urlopen(req).read()
            print ('Key deleted')

        except urllib.error.URLError as e:
            print('Error : ' + str(e.code))
            print(e.read())

elif action == 'info':
    if len(data) < 1:
        print('Missing params!')
    else:
        req = request.Request('http://' + ip + '/api/' + data[0] + '/config')
        response = request.urlopen(req).read()
        response = response.decode("utf-8", "ignore")
        j = json.loads(response)
        print ("Webscoket Port : " + str(j['websocketport']) )
        print ("IP adress: " + j['ipaddress'] )
        print ("Firmware version : " + j['fwversion'] )


else:
    print('Exemples of use')
    print('python3 API_KEY.py <ip>:<port> <command> <Api key> <data>\n')
    print('python3 API_KEY.py 127.0.0.1:80 create')
    print('python3 API_KEY.py 127.0.0.1:80 info B4B018AA61')
    print('python3 API_KEY.py 127.0.0.1:80 list B4B018AA61')
    print('python3 API_KEY.py 127.0.0.1:80 delete B4B018AA61 CA606DA036')
