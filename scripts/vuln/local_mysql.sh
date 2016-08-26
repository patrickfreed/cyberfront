#!/bin/bash

# MySQL local UDF vulnerability check script

VULN_NAME=$1

# Just check if mysql is running as root
ps aux | grep mysql | grep -e "--user=root" > /dev/null

if [ $? -eq 0 ]; then
        echo "host is vulnerable to ${VULN_NAME}"
else
        echo "host is not vulnerable to ${VULN_NAME}"
fi
