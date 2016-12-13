# Zabbix V3.0

### zabbix v3.0安装部署

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
  	 如果是MysqlServer，你可以把value设置为Mysql，并且让它链接Mysql和普通的模板。<br>

* 自动发现
  1.	 主机自动发现
  2.	 端口自动发现
