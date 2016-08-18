#!/bin/bash

# Cyberfront Utility Script
# Name: user.sh
# Description: Sets up user accounts based on arguments
# Usage: user.sh <user>:<pass> [user1]:[pass1] ...

if [ "$#" -lt 1 ]; then
	exit 1
fi

for PAIR; do
	user=$(echo ${PAIR} | cut -d':' -f1)
	pass=$(echo ${PAIR} | cut -d':' -f2)
	
	cat /etc/passwd | grep ${user} > /dev/null
	if [ $? -ne 0 ]; then
		adduser --disabled-password --gecos "" ${user}
	fi

	echo ${PAIR} | chpasswd
done
