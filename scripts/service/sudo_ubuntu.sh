#!/bin/bash

# Cyberfront Service Install Script
# Name: sudo_ubuntu.sh
# Description: Configures users to be sudoers or not
# Usage: sudo_ubuntu.sh <service_name>

SERVICE_NAME=$1

users_arr=(${users})

for user in ${users_arr[@]}; do
    echo "Adding ${user} to sudoers file."
    echo "${user} ALL=(ALL) ALL" >> /etc/sudoers
done

exit 0