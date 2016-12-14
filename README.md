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
![Image](https://github.com/honglongwei/pj-zabbix3.0/blob/master/images/warn2jpg) <br>

* 应用中心创建应用
可见范围还可以添加不同管理组，接受同一个应用推送的消息<br>
![Image](https://github.com/honglongwei/pj-zabbix3.0/blob/master/images/warn3jpg) <br>

* 给部门设置管理员
设置--->功能设置---->权限管理---->新建管理组<br>
管理员需要事先关注企业号，并且设置好邮箱地址<br>
![Image](https://github.com/honglongwei/pj-zabbix3.0/blob/master/images/warn4jpg) <br>
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
![Image](https://github.com/honglongwei/pj-zabbix3.0/blob/master/images/warn5jpg) <br>

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
![Image](https://github.com/honglongwei/pj-zabbix3.0/blob/master/images/warn6jpg) <br>

2. 创建用户
![Image](https://github.com/honglongwei/pj-zabbix3.0/blob/master/images/warn7jpg) <br>

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
![Image](https://github.com/honglongwei/pj-zabbix3.0/blob/master/images/warn8jpg) <br>
![Image](https://github.com/honglongwei/pj-zabbix3.0/blob/master/images/warn9jpg) <br>

* 测试微信告警发送
主动触发相关trigger告警，查看微信发送状态<br>
![Image](https://github.com/honglongwei/pj-zabbix3.0/blob/master/images/warn10jpg)

