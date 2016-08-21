#!/bin/bash

SERVICE_NAME=$1

# Extract files
cd ${CF_DIR}
tar -zxf ${SERVICE_NAME}.tar.gz
cd ${SERVICE_NAME}

# Install dependencies
apt-get install -y libpcre3-dev
apt-get install -y libdb5.1-dev

# create exim user
useradd -r -s /sbin/nologin exim

# extract source
tar -zxf defaults/exim.tar.gz
cd exim-4.85/build-Linux-x86_64
bash ../scripts/exim_install
