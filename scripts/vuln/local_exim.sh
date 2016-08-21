#!/bin/bash

VULN_NAME=$1

check=`/usr/exim/bin/exim -bV -v | grep -i Perl`

if [[ ${check} == 'Support for: iconv() Perl DKIM PRDR OCSP' ]]; then
    echo "${VULN_NAME} successfully installed!"
    exit 0
else
    echo "${VULN_NAME} installation failed"
    exit 1
fi
