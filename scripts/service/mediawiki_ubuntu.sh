#!/bin/bash

SERVICE_NAME=$1

## Environment Variables
# admin_username
# admin_password
# host_directory
# database
# webserver
##

# Extract files
cd ${CF_DIR}
# tar -zxf ${SERVICE_NAME}.tar.gz
cd ${SERVICE_NAME}

cd defaults
tar -zxf mediawiki.tar.gz
cd ..

python defaults/setup_mediawiki.py ${SERVICE_NAME}

service apache2 restart

echo "MediaWiki installed!"