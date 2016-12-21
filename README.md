# Zabbix V3.0

### zabbix v3.0安装部署及使用

#### 关于zabbix及相关服务软件版本

```cmd
  Linux：centos 6.6
  nginx：1.9.15
  MySQL：5.5.49
  PHP：5.5.35
```


#### 安装nginx
* 安装依赖包
```cmd
$ yum -y install gcc gcc-c++ autoconf automake zlib zlib-devel openssl openssl-devel pcre* make gd-devel libjpeg-devel libpng-devel libxml2-devel bzip2-devel libcurl-devel
```

* 创建用户
```cmd
$ useradd nginx -s /sbin/nologin -M
```

* 下载nginx软件包并进入到目录中
```cmd
$ wget http://nginx.org/download/nginx-1.9.15.tar.gz && tar xvf nginx-1.9.15.tar.gz && cd nginx-1.9.15
```

* 编译安装
```cmd
$ ./configure --prefix=/usr/local/product/nginx1.9.14 --user=www --group=www --with-http_ssl_module --with-http_v2_module --with-http_stub_status_module --with-pcre
$ make && make install
$ ln -s /usr/local/product/nginx1.9.14 /usr/local/nginx    // 创建软链接
```

* 参数解释
```cmd
 --with-http_stub_status_module：支持nginx状态查询
 --with-http_ssl_module：支持https
 --with-http_spdy_module：支持google的spdy,想了解请百度spdy,这个必须有ssl的支持
 --with-pcre：为了支持rewrite重写功能，必须制定pcre
```


#### 安装PHP
* 下载PHP安装包
```cmd
$ wget http://cn2.php.net/get/php-5.5.35.tar.gz/from/this/mirror
```

* 解压并编译
```cmd
$ mv mirror php-5.5.35.tar.gz && tar xvf php-5.5.35.tar.gz && cd php-5.5.35
$ ./configure --prefix=/usr/local/product/php-5.5.35 --with-config-file-path=/usr/local/product/php-5.5.35/etc --with-bz2 --with-curl --enable-ftp --enable-sockets --disable-ipv6 --with-gd --with-jpeg-dir=/usr/local --with-png-dir=/usr/local --with-freetype-dir=/usr/local --enable-gd-native-ttf --with-iconv-dir=/usr/local --enable-mbstring --enable-calendar --with-gettext --with-libxml-dir=/usr/local --with-zlib --with-pdo-mysql=mysqlnd --with-mysqli=mysqlnd --with-mysql=mysqlnd --enable-dom --enable-xml --enable-fpm --with-libdir=lib64 --enable-bcmath
$ make && make install
$ ln -s /usr/local/product/php-5.5.35 /usr/local/php
$ cp php.ini-production /usr/local/php/etc/php.ini
$ cd /usr/local/php/etc/
$ cp php-fpm.conf.default php-fpm.conf
```

* 修改php.ini参数：（zabbix环境需要修改的参数）
```cmd
 max_execution_time = 300 
 memory_limit = 128M 
 post_max_size = 16M 
 upload_max_filesize = 2M 
 max_input_time = 300 
 date.timezone = PRC
```


#### 安装MySQL
* 添加mysql用户，创建mysql的数据目录
```cmd
$ groupadd mysql
$ mkdir -pv /data/mysql
$ useradd -r -g mysql -d /data/mysql -s /sbin/nologin mysql
$ chown -R mysql.mysql /data/mysql
```

* 安装cmake及依赖
```cmd
$ yum install cmake gcc* ncurses-devel -y 
```

* 下载MySQL安装包
```cmd
$ wget http://dev.mysql.com/get/Downloads/MySQL-5.5/mysql-5.5.49.tar.gz
```

* 编译安装MySQL
```cmd
$ tar -xvf mysql-5.5.49.tar.gz && cd mysql-5.5.49
$ cmake -DCMAKE_INSTALL_PREFIX=/usr/local/product/mysql5.5.49 -DDEFAULT_CHARSET=utf8 -DENABLED_LOCAL_INFILE=1 -DMYSQL_DATADIR=/data/mysql -DWITH_EXTRA_CHARSETS=all -DWITH_READLINE=1 -DWITH_INNOBASE_STORAGE_ENGINE=1 -DMYSQL_TCP_PORT=3306 -DDEFAULT_COLLATION=utf8_general_ci
$ make && make install
$ ln -s /usr/local/product/mysql5.5.49 /usr/local/mysql
$ chown -R mysql.mysql /usr/local/mysql
```

* 拷贝mysql的配置文件
```cmd
$ cd /usr/local/mysql/support-files/
$ cp my-medium.cnf /data/mysql/my.cnf
$ cp mysql.server /etc/init.d/mysqld
$ chmod +x /etc/init.d/mysqld
```

* 初始化MySQL
```cmd
$ cd /usr/local/mysql/scripts
$ ./mysql_install_db --user=mysql --basedir=/usr/local/mysql/ --datadir=/data/mysql/
```

* 修改MySQL配置文件my.cnf中数据目录
```cmd
 datadir=/data/mysql/
```

* 启动MySQL
```cmd
$ /etc/init.d/mysqld start
```

* 登录数据库，创建zabbix数据库及用户名和密码
```cmd
mysql> create database zabbix default charset utf8;
Query OK, 1 row affected (0.00 sec)

mysql> grant all privileges on zabbix.* to zabbix@'localhost' identified by 'zabbix';
Query OK, 0 rows affected (0.03 sec)

mysql> flush privileges;
Query OK, 0 rows affected (0.00 sec)
```

* 如果登录数据库出现问题
```cmd
$ mysql 
ERROR 2002 (HY000): Can't connect to local MySQL server through socket '/var/lib/mysql/mysql.sock' (2)

解决办法：
$ ln -s /tmp/mysql.sock /var/lib/mysql/
```

* 为数据库的root创建密码
```cmd
$ mysqladmin -uroot password  "zabbix"
```


#### 安装zabbix server
* 下载安装包
```cmd
$ wget http://sourceforge.net/projects/zabbix/files/ZABBIX%20Latest%20Stable/3.0.3/zabbix-3.0.3.tar.gz
```

* 安装zabbix
```cmd
$ tar zxf zabbix-3.0.3.tar.gz && cd zabbix-3.0.3
$ ./configure --prefix=/usr/local/zabbix-3.0.3/ --enable-server --enable-agent --with-mysql --with-net-snmp --with-libcurl --with-libxml2
$ make && make install
```

* 编译过程中如果有报错
```cmd
故障1：
  checking for mysql_config... no
  configure: error: MySQL library not found

解决：
 $ yum install mysql-devel -y

故障2：
  checking for net-snmp-config... no
  configure: error: Invalid Net-SNMP directory - unable to find net-snmp-config

解决：
 $ yum install net-snmp-devel -y
```

* 创建zabbix用户
```cmd
$ groupadd zabbix
$ useradd zabbix -s /sbin/nologin -M -g zabbix
```

* zabbix server需要导入3个sql文件
```cmd
$ mysql -uroot -pzabbix zabbix < database/mysql/schema.sql 
$ mysql -uroot -pzabbix zabbix < database/mysql/images.sql
$ mysql -uroot -pzabbix zabbix < database/mysql/data.sql
```


#### zabbix管理网站配置（nginx）
* 创建项目目录
```cmd
$ mkdir /data/web/www.zabbix.com -p
$ mkdir /data/logs/zabbix -p
```

* 将前端文件拷贝到项目目录下
```cmd
$ cp -rp frontends/php/* /data/web/www.zabbix.com/
```

* 编辑nginx虚拟主机
```cmd
$ pwd
 /usr/local/nginx/conf
$ cd extra/
$ vim zabbix.conf
server {
listen 16888;
server_name www.zabbix.com;
access_log /data/logs/zabbix/zabbix.lifec.com.access.log main;
index index.html index.php index.html;
root /data/web/zabbix.lifec.com;

location /{
       try_files $uri $uri/ /index.php?$args;
}

location ~ ^(.+.php)(.*)$ {
       fastcgi_split_path_info ^(.+.php)(.*)$;
       include fastcgi.conf;
       fastcgi_pass 127.0.0.1:9000;
       fastcgi_index index.php;
       fastcgi_param PATH_INFO $fastcgi_path_info;
}

}
```

* 编辑nginx.conf配置文件
```cmd
$ vim nginx.conf
user  nginx;
worker_processes  1;

#error_log  logs/error.log warning;
#error_log  logs/error.log  notice;
#error_log  logs/error.log  info;

pid        logs/nginx.pid;


events {
    worker_connections  1024;
}


http {
    include       mime.types;
    default_type  application/octet-stream;

    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  logs/access.log  main;

    sendfile        on;
    #tcp_nopush     on;

    #keepalive_timeout  0;
    keepalive_timeout  65;

    #gzip  on;
    include extra/*.conf;

}
```

* 编辑zabbix_server.conf文件
```cmd
$ vim etc/zabbix_server.conf
LogFile=/tmp/zabbix_server.log
PidFile=/tmp/zabbix_server.pid
DBHost=localhost
DBName=zabbix
DBUser=zabbix
DBPassword=zabbix
```


#### 启动服务
* 启动nginx
```cmd
$ /usr/local/nginx/sbin/nginx
```

* 启动PHP
```cmd
$ /usr/local/php/sbin/php-fpm
```

* 启动zabbix server
```cmd
$ /usr/local/zabbix-3.0.3/sbin/zabbix_server

如果启动的时候报错：
$ /usr/local/zabbix-3.0.2/sbin/zabbix_server
 /usr/local/zabbix-3.0.2/sbin/zabbix_server: error while loading shared libraries: libmysqlclient.so.18: cannot open shared object file: No such file or directory

$ ln -s /usr/local/mysql/lib/libmysqlclient.so.18 /usr/lib64/
```

* 添加/etc/hosts文件
```cmd
10.0.0.1 www.zabbix.com
```

* 将服务加入开机自启动
```cmd
$ echo "/usr/local/nginx/sbin/nginx" >>/etc/rc.local
$ echo "/usr/local/php/sbin/php-fpm" >>/etc/rc.local 
$ echo "/etc/init.d/mysqld start" >>/etc/rc.local
$ echo "/usr/local/zabbix-3.0.3/sbin/zabbix_server" >>/etc/rc.local
```


#### web端配置zabbix
* 浏览器安装:http://10.0.0.1:16888
![Image](https://github.com/honglongwei/pj-zabbix3.0/blob/master/images/zab1.jpg) <br>
![Image](https://github.com/honglongwei/pj-zabbix3.0/blob/master/images/zab2.jpg) <br>
![Image](https://github.com/honglongwei/pj-zabbix3.0/blob/master/images/zab3.jpg) <br>
![Image](https://github.com/honglongwei/pj-zabbix3.0/blob/master/images/zab4.jpg) <br>
![Image](https://github.com/honglongwei/pj-zabbix3.0/blob/master/images/zab5.jpg) <br>
![Image](https://github.com/honglongwei/pj-zabbix3.0/blob/master/images/zab6.jpg) <br>

* 需要下载文件，上传到指定的服务器目录中并修改属组
```cmd
$ pwd
 /data/web/www.zabbix.com/conf
$ chown 1000:1000 zabbix.conf.php
```
![Image](https://github.com/honglongwei/pj-zabbix3.0/blob/master/images/zab7.jpg) <br>

* 使用用户名(Admin)和密码(zabbix)登录

* 修改界面为中文界面
```cmd
$ vim /data/web/www.zabbix.com/include/locales.inc.php
'zh_CN' => ['name' => _('Chinese (zh_CN)'), 'display' => true],

$ unzip yaheiFont_CHS.zip //文件在git的fonts目录里 
$ rz msyh.ttf
$ cd /data/web/www.zabbix.com/fonts
$ mv DejaVuSans.ttf DejaVuSans_bak
$ mv msyh.ttf DejaVuSans.ttf
$ chown 1000:1000 DejaVuSans.ttf
//重启服务即可
```


#### zabbix-agent 安装
* 下载
```cmd
$ rpm -Uvh http://repo.zabbix.com/zabbix/3.0/rhel/6/x86_64/zabbix-agent-3.0.3-1.el6.x86_64.rpm
```

* 问题报错
```cmd
error: Failed dependencies:
    libodbc.so.2()(64bit) is needed by zabbix-agent-3.0.3-1.el6.x86_64

解决办法:
$ yum -y install unixODBC
```

* 修改配置配置文件
```cmd
$ vim /etc/zabbix/zabbix_agentd.conf   
PidFile=/var/run/zabbix/zabbix_agentd.pid
LogFile=/var/log/zabbix/zabbix_agentd.log
LogFileSize=0
Server=10.0.0.1
ServerActive=10.0.0.1
Hostname=8.8.8.8
Include=/etc/zabbix/zabbix_agentd.d/
```


#### 自动注册和自动发现
* 区别
  1.	 自动发现： 
	 适用于提供相同服务的Server群组，因为自动发现是批量添加Discovery Host的，你可以让所有主机链接同一个模板，并且让他们提供相同的服务。没错，如果你学过Shell，并且能写出批量部署服务的脚本，那么这个自动发现再适合你不过了。

  2.	 自动注册： 
  	 自动注册呢，它是比较灵活的，根据HostMetadata的value来匹配规则，并且通过不同的值来执行不同的操作。 <br>
  	 也就是说，如果是普通Server，你只要把value设置为Linux，并且让它链接普通的模板 <br>
  	 如果是MysqlServer，你可以把value设置为Mysql，并且让它链接Mysql和普通的模板。

* 自动发现
  1.	 主机自动发现

![Image](https://github.com/honglongwei/pj-zabbix3.0/blob/master/images/disc_host1.jpg) <br>
![Image](https://github.com/honglongwei/pj-zabbix3.0/blob/master/images/disc_host2.jpg) <br>
![Image](https://github.com/honglongwei/pj-zabbix3.0/blob/master/images/disc_host3.jpg) <br>
![Image](https://github.com/honglongwei/pj-zabbix3.0/blob/master/images/disc_host4.jpg) <br>
![Image](https://github.com/honglongwei/pj-zabbix3.0/blob/master/images/disc_host5.jpg) <br>
![Image](https://github.com/honglongwei/pj-zabbix3.0/blob/master/images/disc_host6.jpg) 

  2.	 端口自动发现
  
   	 先创建自动发现脚本：vim /etc/zabbix/zabbix_scripts/disc_port.sh <br>
   	 自定义key值：vim /etc/zabbix/zabbix_agentd.d/disc_port.conf <br>
   	 添加需要自动发现的端口描述文件：vim /etc/zabbix/zabbix_scripts/dport_check.d/tes.conf
```cmd
$ cat /etc/zabbix/zabbix_scripts/dport_check.d/tes.conf
127.0.0.1:12066:docker_tes
//#IP:#PORT:#DESC
```
  	  
![Image](https://github.com/honglongwei/pj-zabbix3.0/blob/master/images/disc_port1.jpg) <br>
![Image](https://github.com/honglongwei/pj-zabbix3.0/blob/master/images/disc_port2.jpg) <br>
![Image](https://github.com/honglongwei/pj-zabbix3.0/blob/master/images/disc_port3.jpg) <br>
![Image](https://github.com/honglongwei/pj-zabbix3.0/blob/master/images/disc_port4.jpg) <br>
![Image](https://github.com/honglongwei/pj-zabbix3.0/blob/master/images/disc_port5.jpg) 

* 自动注册
(跟自动发现异曲同工，这里就不做详情说明)


#### 微信告警
* 微信企业号注册与使用
企业号注册：https://qy.weixin.qq.com/

* 企业号使用教程
1. 通讯录添加企业员工
登录新建的企业号，通过提前把企业成员信息添加到组织或者部门，需要填写手机号、微信号或邮箱，通过这样方式让别人扫码关注企业公众号，为了后面企业号推送消息给企业成员。<br>
![Image](https://github.com/honglongwei/pj-zabbix3.0/blob/master/images/warn1.jpg) <br>

2. 新增账户，填写信息<br>
![Image](https://github.com/honglongwei/pj-zabbix3.0/blob/master/images/warn2.jpg) <br>

* 应用中心创建应用
可见范围还可以添加不同管理组，接受同一个应用推送的消息<br>
![Image](https://github.com/honglongwei/pj-zabbix3.0/blob/master/images/warn3.jpg) <br>

* 给部门设置管理员
设置--->功能设置---->权限管理---->新建管理组<br>
管理员需要事先关注企业号，并且设置好邮箱地址<br>
![Image](https://github.com/honglongwei/pj-zabbix3.0/blob/master/images/warn4.jpg) <br>
```cmd
#需要确定管理员有权限使用应用发送消息，需要管理员的CorpID和Sercrt。（重要）
#准备事项：
微信企业号
企业号已经被部门成员关注
企业号有一个可以发送消息的应用（test-msg），一个授权管理员（test-msg），可以使用应用给成员发送消息
#需要先添加管理员信息，然后使其关注企业号
#需要得到的信息
成员账号
组织部门ID
应用ID
CorpID和Secret
```

* 微信接口调用
调用微信接口需要一个调用接口的凭证：access_token<br>
通过CorpID和Secret可以获得access_token<br>
微信企业号接口调试地址： http://qydev.weixin.qq.com/debug<br>
![Image](https://github.com/honglongwei/pj-zabbix3.0/blob/master/images/warn5.jpg) <br>

* 脚本调用原理
设置脚本执行路径，编辑zabbix_server.conf文件，添加一行<br>
AlertScriptsPath=/opt/zabbix/share/zabbix/alertscripts<br>
1. Shell脚本使用
```cmd
获取 AccessToken

curl -s -G url
传送凭证调用企业号接口

curl --data  url
[root@zabbix alertscripts]# cat wechat.sh
#!/bin/bash
#########################################################################
# File Name: wechat.sh
#########################################################################
# Functions: send messages to wechat app
# set variables
CropID='xxxxxx'
Secret='M3FMhnFh8nTI6SxLAEbbLLZaj-1BpZIyqkJRskeMMUXObGx4mfQsAg7Jw-nUMXe9'
GURL="https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=$CropID&corpsecret=$Secret"
#get acccess_token
Gtoken=$(/usr/bin/curl -s -G $GURL | awk -F\" '{print $4}')
PURL="https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=$Gtoken"
#
function body() {
local int AppID=10                        #企业号中的应用id
local UserID="touser"                        #部门成员id，zabbix中定义的微信接收者
local PartyID=8                           #部门id，定义了范围，组内成员都可接收到消息
local Msg=$(echo "$@" | cut -d" " -f3-)   #过滤出zabbix传递的第三个参数
printf '{\n'
printf '\t"touser": "'"$UserID"\"",\n"
printf '\t"toparty": "'"$PartyID"\"",\n"
printf '\t"msgtype": "text",\n'
printf '\t"agentid": "'" $AppID "\"",\n"
printf '\t"text": {\n'
printf '\t\t"content": "'"$Msg"\""\n"
printf '\t},\n'
printf '\t"safe":"0"\n'
printf '}\n'
}
/usr/bin/curl --data-ascii "$(body $! $2 $3)" $PURL
#http://qydev.weixin.qq.com/wiki/index.php?title=消息类型及数据格式
#测试：

bash wechat.sh test hello.world!
{"errcode":0,"errmsg":"ok","invaliduser":"all user invalid"}
```
2. python脚本
安装simplejson<br>
```cmd
$ wget https://pypi.python.org/packages/f0/07/26b519e6ebb03c2a74989f7571e6ae6b82e9d7d81b8de6fcdbfc643c7b58/simplejson-3.8.2.tar.gz
$ tar zxvf simplejson-3.8.2.tar.gz && cd simplejson-3.8.2
$ python setup.py build
$ python setup.py install
```
下载wechat.py脚本<br>
```cmd
$ git clone https://github.com/X-Mars/Zabbix-Alert-WeChat.git
$ cp Zabbix-Alert-WeChat/wechat.py /opt/zabbix/share/zabbix/alertscripts/
$ chmod +x wechat.py && chown zabbix:zabbix wechat.py
```
脚本修改<br>
```cmd
#!/usr/bin/python
#_*_coding:utf-8 _*_
 
import urllib,urllib2
import json
import sys
import simplejson
 
def gettoken(corpid,corpsecret):
	gettoken_url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=' + corpid + '&corpsecret=' + corpsecret
	print  gettoken_url
	try:
		token_file = urllib2.urlopen(gettoken_url)
	except urllib2.HTTPError as e:
		print e.code
		print e.read().decode("utf8")
		sys.exit()
	token_data = token_file.read().decode('utf-8')
	token_json = json.loads(token_data)
	token_json.keys()
	token = token_json['access_token']
	return token
 
def senddata(access_token,user,subject,content):
	send_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + access_token
	send_values = {
								"touser":"touser",      #企业号中的用户帐号，在zabbix用户Media中配置，如果配置不正常，将按部门发送。
								"toparty":"8",          #企业号中的部门id。
								"msgtype":"text",       #消息类型。
								"agentid":"10",         #企业号中的应用id。
								"text":{
								"content":subject + '\n' + content
								},
							"safe":"0"
						}
	#    send_data = json.dumps(send_values, ensure_ascii=False)
	send_data = simplejson.dumps(send_values, ensure_ascii=False).encode('utf-8')
	send_request = urllib2.Request(send_url, send_data)
	response = json.loads(urllib2.urlopen(send_request).read())
	print str(response)

if __name__ == '__main__':
	user = str(sys.argv[1])     #zabbix传过来的第一个参数
	subject = str(sys.argv[2])  #zabbix传过来的第二个参数
	content = str(sys.argv[3])  #zabbix传过来的第三个参数
	corpid =  'xxxxxx'   #CorpID是企业号的标识
	corpsecret = 'M3FMhnFh8nTI6SxLAEbbLLZaj-1BpZIyqkJRskeMMUXObGx4mfQsAg7Jw-nUMXe9'  #corpsecretSecret是管理组凭证密钥
	accesstoken = gettoken(corpid,corpsecret)
	senddata(accesstoken,user,subject,content)
```
脚本测试<br>
28,29,31行分别改为用户账号，部门ID，和应用ID<br>
48,49 改为CropID和Secret<br>
文中使用的用户为，test-msg,部门iD为8，应用ID为10.<br>
```cmd
$ ./wechat.py test-msg test hello
https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=wx11ac451376ae0e98&corpsecret=M3FMhnFh8nTI6SxLAEbbLLZaj-1BpZIyqkJRskeMMUXObGx4mfQsAg7Jw-nUMXe9
{u'invaliduser': u'all user invalid', u'errcode': 0, u'errmsg': u'ok'}
```


* 脚本路径设置
将脚本放到zabbix默认执行的路径下<br>
```cmd
$ mv wechat.php wechat.sh /opt/zabbix/share/zabbix/alertscripts/
$ chown zabbix:zabbix /opt/zabbix/share/zabbix/alertscripts/wechat.php
$ chmod +x /opt/zabbix/share/zabbix/alertscripts/wechat.php
或
$ chown zabbix:zabbix /opt/zabbix/share/zabbix/alertscripts/wechat.sh
$ chmod +x /opt/zabbix/share/zabbix/alertscripts/wechat.sh
```

设置脚本的启动用户为zabbix，并给脚本可执行权限<br>
修改zabbix_server.conf文件，添加脚本执行目录<br>
```cmd
AlertScriptsPath=/opt/zabbix/share/zabbix/alertscripts
```
修改完成重启zabbix_server<br>
```cmd
$ /etc/init.d/zabbix_server restart
```


* Zabbix-web前端设置
1. 设置通知媒介
![Image](https://github.com/honglongwei/pj-zabbix3.0/blob/master/images/warn6.jpg) <br>

2. 创建用户
![Image](https://github.com/honglongwei/pj-zabbix3.0/blob/master/images/warn7.jpg) <br>

3. 创建触发动作及发送内容
告警主题<br>：

Default subject：{TRIGGER.STATUS}: {TRIGGER.NAME}<br>
 
Trigger host:{HOSTNAME}<br>
Trigger ip:{HOST.IP}<br>
Trigger time:{EVENT.DATE}:{EVENT.TIME}<br>
Trigger: {TRIGGER.NAME}<br>
Trigger status: {TRIGGER.STATUS}<br>
Trigger severity: {TRIGGER.SEVERITY}<br>
Trigger URL: {TRIGGER.URL}<br>
 
Item values:<br>
{ITEM.NAME1} ({HOST.NAME1}:{ITEM.KEY1}): {ITEM.VALUE1}<br>
{ITEM.NAME2} ({HOST.NAME2}:{ITEM.KEY2}): {ITEM.VALUE2}<br>
 
Original event ID: {EVENT.ID}<br>
恢复主题：<br>

Default subject：{TRIGGER.STATUS}: {TRIGGER.NAME}<br>
Trigger host:{HOSTNAME}<br>
Trigger ip:{HOST.IP}<br>
Trigger time:{EVENT.DATE}:{EVENT.TIME}<br>
Trigger: {TRIGGER.NAME}<br>
Trigger status: {TRIGGER.STATUS}<br>
Trigger severity: {TRIGGER.SEVERITY}<br>
Trigger URL: {TRIGGER.URL}<br>
 
Item values:<br>
{ITEM.NAME1} ({HOST.NAME1}:{ITEM.KEY1}): {ITEM.VALUE1}<br>
{ITEM.NAME2} ({HOST.NAME2}:{ITEM.KEY2}): {ITEM.VALUE2}<br>
Original event ID: {EVENT.ID}<br>
![Image](https://github.com/honglongwei/pj-zabbix3.0/blob/master/images/warn8.jpg) <br>
![Image](https://github.com/honglongwei/pj-zabbix3.0/blob/master/images/warn9.jpg) <br>

* 测试微信告警发送
主动触发相关trigger告警，查看微信发送状态<br>
![Image](https://github.com/honglongwei/pj-zabbix3.0/blob/master/images/warn10.jpg)


#### Zabbix Api
* API简介
Zabbix API开始扮演着越来越重要的角色，尤其是在集成第三方软件和自动化日常任务时。很难想象管理数千台服务器而没有自动化是多么的困难。Zabbix API为批量操作、第三方软件集成以及其他作用提供可编程接口。<br>

Zabbix API是在1.8版本中开始引进并且已经被广泛应用。所有的Zabbix移动客户端都是基于API，甚至原生的WEB前端部分也是建立在它之上。Zabbix API 中间件使得架构更加模块化也避免直接对数据库进行操作。它允许你通过JSONRPC协议来创建、更新和获取Zabbix对象并且做任何你喜欢的操作【当然前提是你拥有认证账户】。<br>
Zabbix API提供两项主要功能：<br>
   远程管理Zabbix配置 <br>
   远程检索配置和历史数据<br>

* 使用JSON
API 采用JSON-RPC实现。这意味着调用任何函数，都需要发送POST请求，输入输出数据都是以JSON格式。大致工作流如下：<br>
1. 准备JSON对象，它描述了你想要做什么（创建主机，获取图像，更新监控项等）。<br>
2. 采用POST方法向 http://example.com/zabbix/api_jsonrpc.php发送此JSON对象，http://example.com/zabbix/是Zabbix前端地址 ，api_jsonrpc.php是调用API的PHP脚本。可在安装可视化前端的目录下找到。<br>
3. 获取JSON格式响应。<br>
4. 注：请求除了必须是POST方法之外，HTTP Header Content-Type必须为【application/jsonrequest，application/json-rpc，application/json】其中之一。<br>
可以采用脚本或者任何"手动"支持JSON RPC的工具来使用API。而首先需要了解的就是如何验证和如何使用验证ID来获取想要的信息。后面的演示会以Python脚本和基于Curl的例子来呈现API的基本使用。

* 基本请求格式
Zabbix API 简化的JSON请求如下：<br>
```cmd
 {
        "jsonrpc": "2.0",
        "method": "method.name",
        "params": {
        "param_1_name": "param_1_value",
        "param_2_name": "param_2_value"
        },
        "id": 1,
        "auth": "159121b60d19a9b4b55d49e30cf12b81",
}
```

下面一行一行来看：<br>
1. "jsonrpc": "2.0"-这是标准的JSON RPC参数以标示协议版本。所有的请求都会保持不变。
2. "method": "method.name"-这个参数定义了真实执行的操作。例如：host.create、item.update等等
3. "params"-这里通过传递JSON对象来作为特定方法的参数。如果你希望创建监控项，"name"和"key-"参数是需要的，每个方法需要的参数在Zabbix API文档中都有描述。
4. "id": 1-这个字段用于绑定JSON请求和响应。响应会跟请求有相同的"id"。在一次性发送多个请求时很有用，这些也不需要唯一或者连续
5. "auth": "159121b60d19a9b4b55d49e30cf12b81"-这是一个认证令牌【authentication token】用以鉴别用户、访问API。这也是使用API进行相关操作的前提-获取认证ID。

* API 使用
1. 环境准备
Zabbix API是基于JSON-RPC 2.0规格，具体实现可以选择任何你喜欢的编程语言或者手动方式。这里我们采用的Python和基于Curl的方式来做示例。Python 2.7版本已经支持JSON，所以不再需要其他模块组件。当然可以采用Perl、Ruby、PHP之类的语言，使用前先确保相应JSON模块的安装。

2. 身份验证
任何Zabbix API客户端在真正工作之前都需要验证它自身。在这里是采用User.login方法。这个方法接受一个用户名和密码作为参数并返回验证ID，一个安全哈希串用于持续的API调用（在使用User.logout之前该验证ID均有效）。具体Python代码auth.py如下：
```cmd
#!/usr/bin/env python2.7
#coding=utf-8
import json
import urllib2
# based url and required header
url = "http://172.20.0.233/zabbix/api_jsonrpc.php"
header = {"Content-Type": "application/json"}
# auth user and password
data = json.dumps(
{
    "jsonrpc": "2.0",
    "method": "user.login",
    "params": {
    "user": "admin",
    "password": "zabbix"
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
    print "Auth Successful. The Auth ID Is:",response['result']
```
确保用户名密码正确，执行结果如下：
```cmd
$ python auth.py
Auth Successful. The Auth ID Is: 9a8ade34ea5af0c8bfe7331975492c3c
```

可以看到，auth.py成功连接并认证。现在有了验证ID，它能够在新的API调用中被重用。下面再来看基于CURL的方式来进行验证是如何实现的：
```cmd
$ curl -i -X POST -H 'Content-Type:application/json' -d'{"jsonrpc": "2.0","method":"user.authenticate","params":{"user":"Admin","password":"zabbix"},"auth": null,"id":0}' "http://172.20.0.233/zabbix/api_jsonrpc.php"
HTTP/1.1 200 OK
Date: Mon, 30 Jun 2014 09:28:56 GMT
Server: Apache/2.2.15 (CentOS)
X-Powered-By: PHP/5.3.3
Content-Length: 68
Connection: close
Content-Type: application/json
{"jsonrpc":"2.0","result":"359d57f0392df5a7de7c4b6807f7d2d4","id":0}
```
3. 一般操作
这里举例说明如何获取监控主机列表【host list】。这段脚本需要采用auth.py中获取的验证ID并执行host.get方法来获取主机列表。来看具体代码get_host.py:
```cmd
#!/usr/bin/env python2.7
#coding=utf-8
import json
import urllib2
# based url and required header
url = "http://172.20.0.233/zabbix/api_jsonrpc.php"
header = {"Content-Type": "application/json"}
# request json
data = json.dumps(
{
    "jsonrpc":"2.0",
    "method":"host.get",
    "params":{
        "output":["hostid","name"],
        "filter":{"host":""}
    },
    "auth":"9a8ade34ea5af0c8bfe7331975492c3c", # the auth id is what auth script returns, remeber it is string
    "id":1,
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
```

执行结果如下：
```cmd
$ python get_host.py
Number Of Hosts:  5
Host ID: 10084 Host Name: Zabbix server
Host ID: 10105 Host Name: ubuntu
Host ID: 10108 Host Name: mongodb-0-45
Host ID: 10111 Host Name: redis-172-20
Host ID: 10129 Host Name: hosts39
```
对于基于curl 的访问方式，执行结果如下：
```cmd
$ curl -i -X POST -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","method":"host.get","params":{"output":["hostid","name"],"filter":{"host":""}},"auth":"9a8ade34ea5af0c8bfe7331975492c3c","id":1}' "http://172.20.0.233/zabbix/api_jsonrpc.php"
HTTP/1.1 200 OK
Date: Mon, 30 Jun 2014 09:35:58 GMT
Server: Apache/2.2.15 (CentOS)
X-Powered-By: PHP/5.3.3
Content-Length: 230
Connection: close
Content-Type: application/json
{"jsonrpc":"2.0","result":[{"hostid":"10084","name":"Zabbix server"},{"hostid":"10105","name":"ubuntu"},{"hostid":"10108","name":"mongodb-0-45"},{"hostid":"10111","name":"redis-172-20"},{"hostid":"10129","name":"hosts39"}],"id":1}
```

比较来看，采用脚本可以有更多的灵活性，而基于CURL的方式，对结果的处理不是很方便。原理则都是相通的。<br>
除了这些获取信息以外，采用API调用同样可以进行创建操作，更新操作和删除操作等等。这也很容易让我们联想起数据库操作，当然比较这些采用API调用获取结果的方式，也不能忘掉这种最直接而危险的方式。在开始讨论中已经提到，Zabbix现在自带的前端实现部分是采用数据库操作，部分是基于API调用。在API还不是很成熟的现在，具体采用哪种方式，需要根据业务需求再来确定。

4. 数据流程
下面的流程图代表了Zabbix API<br>
工作的典型工作流。验证（方法user.login）是获取验证ID的强制步骤。这个ID又允许我们调用API提供的任何权限允许的方法来进行操作。在之前的例子中没有提到user.logout方法，这也是一次验证ID能够重复使用的原因所在。使用user.logout方法后将会使验证ID失效，后面的操作将不能再使用此ID。<br>
![Image](https://github.com/honglongwei/pj-zabbix3.0/blob/master/images/zbxapi01.jpg)
