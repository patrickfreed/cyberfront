#!/bin/bash

SERVICE_NAME=$1

## Environment Variables
# user: run server as this user
# port: listen on this port
# password: mysql root password
##

# Extract files
cd ${CF_DIR}
tar -zxf ${SERVICE_NAME}.tar.gz
cd ${SERVICE_NAME}

# Install server
dpkg -i defaults/mysql-server_5.0.15-1_amd64.deb

# Setup configuration
cp defaults/my.cnf /etc/
sed -i "s/port = PLACEHOLDER_PORT/port = ${port}/g" /etc/my.cnf
sed -i "s/user = PLACEHOLDER_USER/user = ${user}/g" /etc/my.cnf
chown ${user} /etc/my.cnf
chgrp ${user} /etc/my.cnf

# Assign proper permissions
chown -R ${user} /var/lib/mysql
chgrp -R ${user} /var/lib/mysql

# Setup db
mysql_install_db

# Do it again
chown -R ${user} /var/lib/mysql
chgrp -R ${user} /var/lib/mysql

# Install client
apt-get install -y mysql-client-core-5.5
apt-get install -y libmysqlclient15-dev

# Start up, set password
service mysql start
mysql -u root -Bse "use mysql;update user set password=PASSWORD('${password}') where User='root';flush privileges;";

# chmod a+r /var/run/mysqld
# chmod a=rwx /var/run/mysqld/mysqld.sock
# chmod a+r /var/run/mysqld/mysqld.pid

# TODO: not this
chmod -R 777 /var/run/mysqld

echo "mysql installed!"

