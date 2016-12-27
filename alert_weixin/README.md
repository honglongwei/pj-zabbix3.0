# 微信告警

### 配置微信企业号
1. 在组织架构中，新建二级组，并添加相关人员，注意添加人员的账号要记清楚。后期zabbix发送邮件时需要填写用户名（也可以填写@all发送给所有的人）
2. 点击"修改部门",获取ID
3. 去设置-->功能设置-->权限管理，最重要的是CorpID,Secret 两个密钥，后期脚本里会利用它俩生成一个token ，然后利用token 去发送消息

### 配置zabbix-server
将weixin.py放到/usr/local/zabbix/alertscripts/目录下<br>
```python
$vim zabbix_server.conf
 AlertScriptsPath=/usr/local/zabbix/alertscripts
$cd /usr/local/zabbix/alertscripts/weixin.py
$cat weixin.py

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib,urllib2,json
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )


class WeChat(object):
    __token_id = ''
    # init attribute
    def __init__(self,url):
        self.__url = url.rstrip('/')
        self.__corpid = ''    #微信企业号-设置-权限管理可查看
        self.__secret = ''    #微信企业号-设置-权限管理可查看 

    # Get TokenID
    def authID(self):
        params = {'corpid':self.__corpid, 'corpsecret':self.__secret}
        data = urllib.urlencode(params)
        content = self.getToken(data)
        try:
            self.__token_id = content['access_token']
            # print content['access_token']
        except KeyError:
            raise KeyError

    # Establish a connection
    def getToken(self,data,url_prefix='/'):
        url = self.__url + url_prefix + 'gettoken?'
        try:
            response = urllib2.Request(url + data)
        except KeyError:
            raise KeyError
        result = urllib2.urlopen(response)
        content = json.loads(result.read())
        return content

    # Get sendmessage url
    def postData(self,data,url_prefix='/'):
        url = self.__url + url_prefix + 'message/send?access_token=%s' % self.__token_id
        request = urllib2.Request(url,data)
        try:
            result = urllib2.urlopen(request)
        except urllib2.HTTPError as e:
            if hasattr(e,'reason'):
                print 'reason',e.reason
            elif hasattr(e,'code'):
                print 'code',e.code
            return 0
        else:
            content = json.loads(result.read())
            result.close()
        return content

    # send message
    def sendMessage(self,touser,message):
        self.authID()
        data = json.dumps({
                'touser':"@all",
                'toparty':"@all",
                'totag': "test",
                'msgtype':"text",
                'agentid':"2",
                'text':{
                        'content':message
                },
                'safe':"0"
        },ensure_ascii=False)
        response = self.postData(data)
        print response


if __name__ == '__main__':
        a = WeChat('https://qyapi.weixin.qq.com/cgi-bin')
        a.sendMessage(sys.argv[1],sys.argv[3])

$chmod +x /usr/local/zabbix/alertscripts/weixin.py
$chown zabbix:zabbix /usr/local/zabbix/alertscripts/weixin.py
$python zabbix test test  //$1联系人 $2主题  $3正文
 {u'errcode': 0, u'errmsg': u'ok'}
```

### 配置zabbix UI
1. 【管理】-【报警媒介类型】-【创建媒介类型】
![Image](https://github.com/honglongwei/pj-zabbix3.0/blob/master/images/zbx_a1.jpg)
2. 【管理】-【用户】-【admin】-【报警媒介】
![Image](https://github.com/honglongwei/pj-zabbix3.0/blob/master/images/zbx_a2.jpg)
3. 【配置】-【动作】-【触发器】-【创建动作】
![Image](https://github.com/honglongwei/pj-zabbix3.0/blob/master/images/zbx_a3.jpg)<br>
![Image](https://github.com/honglongwei/pj-zabbix3.0/blob/master/images/zbx_a4.jpg)



