#!/bin/bash

# Cyberfront Service Install Script
# Name: apache_ubuntu.sh
# Description: Installs apache2 service via apt-get and configures based on user configuration
# Usage: apache_ubuntu.sh <service name>

SERVICE_NAME=$1

## Environment Variables
# files: name of file with server files in it
# php: whether to install php or not
# user: user to run server as
# group: group to run server as
# port: port to listen on
# wwwroot: root of webserver
##

# Extract files
cd ${CF_DIR}
tar -zxf ${SERVICE_NAME}.tar.gz
cd ${SERVICE_NAME}

# Install service
apt-get -y install apache2
service stop apache2

# Replace root web server
# Be careful...
if [ -d ${wwwroot} ]; then
    rm -r ${wwwroot}
fi

mkdir ${wwwroot}
tar -zxf ${files}
cd wwwroot
cp -r ./* ${wwwroot}

# Update root configuration
sed -i "s#DocumentRoot /var/www/html#DocumentRoot ${wwwroot}#g" /etc/apache2/sites-enabled/000-default.conf

# Change ports
sed -i "s/Listen 80/Listen ${port}/g" /etc/apache2/ports.conf
sed -i "s/<VirtualHost \*:80>/<VirtualHost \*:${port}>/g" /etc/apache2/sites-enabled/000-default.conf

# Change users
sed -i "s/APACHE_RUN_USER=www-data/APACHE_RUN_USER=${user}/g" /etc/apache2/envvars
sed -i "s/APACHE_RUN_GROUP=www-data/APACHE_RUN_GROUP=${user}/g" /etc/apache2/envvars

# Configure PHP
if [ ${php} == "true" ]; then
    apt-get -y install php5 libapache2-mod-php5 php5-mcrypt
else
    service apache2 start
fi
