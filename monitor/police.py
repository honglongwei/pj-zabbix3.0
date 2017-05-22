##/usr/local/zabbix/share/zabbix/alertscripts/police.py

#!/usr/bin/env python
#coding:utf-8
import redis
import sys
subject=sys.argv[1]
r = redis.StrictRedis(host='**.**.**.**', port=6379)
r.set(subject,subject)
