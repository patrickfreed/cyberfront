#!/bin/bash

SERVICE_NAME=$1

## Environment Variables
# host_directory
# database
# webserver
##

# Extract files
cd ${CF_DIR}

# Get dependencies
wwwroot=`cat ${webserver}.json | python -c 'import sys, json; print json.load(sys.stdin)["options"]["wwwroot"]'`
dbpass=`cat ${database}.json | python -c 'import sys, json; print json.load(sys.stdin)["options"]["password"]'`
dbuser='root'

tar -zxf ${SERVICE_NAME}.tar.gz
cd ${SERVICE_NAME}

# Install service
cd defaults
tar -zxf vcms.tar.gz
cp -r vcms ${wwwroot}${host_directory}

# Setup configuration
cd ${wwwroot}${host_directory}
mv includes/config.dist.php includes/config.php
sed -i "s/define(\"ENCRYPTION_SALT\", \"987654321SalT\");/define(\"ENCRYPTION_SALT\", \"BadSalt\");/g" includes/config.php # TODO: ...
sed -i "s/define(\"ENCRYPTION_PASSWORD\", \"PassWord123456789\");/define(\"ENCRYPTION_PASSWORD\", \"!!!not_default_password12345\");/g" includes/config.php
sed -i "s/define(\"DB_USER\", \"user\");/define(\"DB_USER\", \"${dbuser}\");/g" includes/config.php
sed -i "s/define(\"DB_PASS\", \"password\");/define(\"DB_PASS\", \"${dbpass}\");/g" includes/config.php
sed -i "s/define(\"USE_SSL\", \"1\");/define(\"USE_SSL\", \"0\");/g" includes/config.php

# Set permissions
chmod -R 777 ${wwwroot}${host_directory}

# Setup db (assuming mysql)
mysql -u root "-p${dbpass}" -Bse "create database vcms;";
curl -s "localhost${host_directory}/index.php?page=install" > /dev/null
curl -s "localhost${host_directory}/index.php?page=install2" > /dev/null

echo "V-CMS installation complete!"