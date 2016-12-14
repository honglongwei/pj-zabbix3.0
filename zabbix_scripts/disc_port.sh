#!/bin/bash 
# function:monitor tcp connect status from zabbix 
# 
# Zline


K="[[:blank:]]+"
IP="[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}"
PORT="[0-9]{1,5}"

> /etc/zabbix/zabbix_scripts/dport_check.d/.all.txt
for i in `cat /etc/zabbix/zabbix_scripts/dport_check.d/*.conf`
do

    if [[ "$i" =~ ($IP):($PORT):(.+) ]]
    then 
        echo $i >> /etc/zabbix/zabbix_scripts/dport_check.d/.all.txt
    fi
done

sort -u  /etc/zabbix/zabbix_scripts/dport_check.d/.all.txt  > /etc/zabbix/zabbix_scripts/disc_port.txt

WEB_SITE=($(cat /etc/zabbix/zabbix_scripts/disc_port.txt|grep -v "^#" |awk -F: '{print $1}'))
WEB_SITE1=($(cat /etc/zabbix/zabbix_scripts/disc_port.txt|grep -v "^#"|awk -F: '{print $2}'))
WEB_SITE2=($(cat /etc/zabbix/zabbix_scripts/disc_port.txt|grep -v "^#"|awk -F: '{print "["$3"]"}'))

[ "$WEB_SITE" ] || {
echo \{
echo       \"data\":'[]'
echo \}
exit
}


        printf '{\n' 
        printf '\t"data":[\n' 
for((i=0;i<${#WEB_SITE[@]};++i)) 

{ 
num=$(echo $((${#WEB_SITE[@]}-1))) 
        if [ "$i" != ${num} ]; 
                then 
        printf "\t\t{ \n" 
        printf "\t\t\t\"{#IP}\":\"${WEB_SITE[$i]}\",\"{#PORT}\":\"${WEB_SITE1[$i]}\",\"{#APP}\":\"${WEB_SITE2[$i]}\"},\n" 
                else 
                        printf  "\t\t{ \n" 
                        printf  "\t\t\t\"{#IP}\":\"${WEB_SITE[$num]}\",\"{#PORT}\":\"${WEB_SITE1[$i]}\",\"{#APP}\":\"${WEB_SITE2[$i]}\"}]}\n" 
        fi 
}
