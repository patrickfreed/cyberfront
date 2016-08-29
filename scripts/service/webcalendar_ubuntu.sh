#!/bin/bash

SERVICE_NAME=$1

## Environment Variables
# webserver
# host_directory
##

# Extract files
cd ${CF_DIR}

wwwroot=`cat ${webserver}.json | python -c 'import sys, json; print json.load(sys.stdin)["options"]["wwwroot"]'`

tar -zxf ${SERVICE_NAME}.tar.gz
cd ${SERVICE_NAME}

cd defaults
tar -zxf WebCalendar.tar.gz
cp -r WebCalendar-1.2.4 ${wwwroot}${host_directory}

chmod -R 777 ${wwwroot}${host_directory}

echo "WebCalendar 1.2.4 setup complete. Manual configuration required to complete installation"
