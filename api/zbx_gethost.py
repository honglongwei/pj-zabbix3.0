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


def get_host():
    authid = zbxauth()
    # request json
    data = json.dumps(
    {
        "jsonrpc":"2.0",
        "method":"host.get",
        "params":{
            "output":["hostid","name"],
            "filter":{"host":""}
        },
        "auth":"{0}".format(authid), # the auth id is what auth script returns, remeber it is string
        "id":0,
    })
    # create request object
    request = urllib2.Request(url,data)
    for key in header:
        request.add_header(key,header[key])
    # get host list
    try:
        result = urllib2.urlopen(request)
    except URLError as e:
        if hasattr(e, 'reason'):
            print 'We failed to reach a server.'
            print 'Reason: ', e.reason
        elif hasattr(e, 'code'):
            print 'The server could not fulfill the request.'
            print 'Error code: ', e.code
    else:
        response = json.loads(result.read())
        result.close()
        print "Number Of Hosts: ", len(response['result'])
        for host in response['result']:
            print "Host ID:",host['hostid'],"Host Name:",host['name']


print get_host()
