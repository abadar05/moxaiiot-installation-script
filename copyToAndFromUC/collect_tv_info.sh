#!/bin/sh

# Check if run as root
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi




sn=$(fw_printenv |grep serialnu |cut -c14-)
infoFile=${sn}_TvInfo.log

rm ${sn}_TvInfo.log

deamon_val=$(teamviewer-iot-agent info |grep Daemon |cut -c8-)
echo "Deamon":"${deamon_val}" >> $infoFile

status_val=$(teamviewer-iot-agent info |grep Status |cut -c8-)
echo "Status":"${status_val}" >> $infoFile

conn_val=$(teamviewer-iot-agent info |grep Cloud |cut -c20-)
echo "Cloud Connectivity":"${conn_val}" >> $infoFile

file_val=$(teamviewer-iot-agent configure show |grep AccessControl |cut -c60-)
echo "File Transfer":"${file_val}" >> $infoFile

sn_val=$(fw_printenv |grep serialnu |cut -c14-)
echo "SN":"${sn_val}" >> $infoFile