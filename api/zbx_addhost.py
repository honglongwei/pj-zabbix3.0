#!/usr/bin/env python2.7
#coding=utf-8

import json
import urllib2
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )


# based url and required header
url = "http://10.0.0.1:8027/api_jsonrpc.php"
header = {"Content-Type": "application/json"}


def zbxauth():
    # auth user and password
    data = json.dumps(
    {
        "jsonrpc": "2.0",
        "method": "user.login",
        "params": {
                   "user": "admin",
                   "password": "123456"
        },
        "id": 0
    })
    # create request object
    request = urllib2.Request(url,data)
    for key in header:
        request.add_header(key,header[key])
    # auth and get authid
    try:
        result = urllib2.urlopen(request)
    except URLError as e:
        print "Auth Failed, Please Check Your Name And Password:",e.code
    else:
        response = json.loads(result.read())
        result.close()
       # return "Auth Successful. The Auth ID Is:",response['result']
        return response['result']


def add_host(ip):
    authid = zbxauth()
    # request json
    data = json.dumps(
    {
        "jsonrpc":"2.0",
        "method":"host.create",
        "params":{
        "host": ip,
        "interfaces": [
            {
                "type": 1,
                "main": 1,
                "useip": 1,
                "ip": ip,
                "dns": "",
                "port": "10050"
            }
        ],
        "groups": [{"groupid": 8}],
        "templates": [{"templateid":10108}],
        },
        "auth":"{0}".format(authid), # the auth id is what auth script returns, remeber it is string
        "id":0,
    })
    # create request object
    request = urllib2.Request(url,data)
    for key in header:
        request.add_header(key,header[key])
    # add host
    try:
        result = urllib2.urlopen(request)
    except URLError as e: 
        print "Error as ", e 
    else:
        response = json.loads(result.read()) 
        print response
        result.close() 
     #   print "Add host: {0} is ok.".format(ip) 


print add_host('8.8.8.8')
