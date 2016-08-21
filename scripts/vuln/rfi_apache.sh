#!/bin/bash

SERVICE_NAME=$1

# Extract files
cd ${CF_DIR}
tar -zxf ${SERVICE_NAME}.tar.gz
cd ${SERVICE_NAME}

sed -i "s/allow_url_include=Off/allow_url_include=On/g" /etc/php5/apache2/php.ini

python defaults/setup_files.py ${service} ${file}