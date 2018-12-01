#!/usr/bin/env python3
# coding: utf-8 -*-


#Exemple command
#
# python3 API_KEY.py 127.0.0.1:80 create
# python3 API_KEY.py 127.0.0.1:80 list B4B018AA61
# python3 API_KEY.py 127.0.0.1:80 delete A2615C25A6 CA606DA036

import sys
import urllib,json
from urllib import request, parse

ip = sys.argv[1]
action = sys.argv[2]
data = sys.argv[3:]


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
        print('Missing params!')
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
        print('Missing params!')
    else:
        req = request.Request('http://' + ip + '/api/' + data[0] + '/config/whitelist/' + data[1] , method='DELETE')
        try:
            response = request.urlopen(req).read()
            print ('Key deleted')
            
        except urllib.error.URLError as e:
            print('Error : ' + str(e.code))
            print(e.read())
