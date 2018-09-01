#!/bin/bash

# Environment Variables
# webserver
# mediawiki

# Metasploit: https://www.rapid7.com/db/modules/exploit/multi/http/mediawiki_thumb
# CVE: https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2014-1610
# See: https://www.mediawiki.org/wiki/Extension:PdfHandler

cd ${CF_DIR}

# Install dependencies
apt-get install -y imagemagick
apt-get install -y xpdf-utils

# get info from other services
wwwroot=`cat ${webserver}.json | python -c 'import sys, json; print json.load(sys.stdin)["options"]["wwwroot"]'`
wikiroot=`cat ${mediawiki}.json | python -c 'import sys, json; print json.load(sys.stdin)["options"]["host_directory"]'`

# Update configuration
sed -i "s/\$wgEnableUploads = false;/\$wgEnableUploads = true;/g" "${wwwroot}${wikiroot}/LocalSettings.php"

echo '$wgUseImageMagick = "true";' >> "${wwwroot}${wikiroot}/LocalSettings.php"
echo '$wgImageMagickConvertCommand = "/usr/bin/convert";' >> "${wwwroot}${wikiroot}/LocalSettings.php"
echo 'require_once "$IP/extensions/PdfHandler/PdfHandler.php";' >> "${wwwroot}${wikiroot}/LocalSettings.php"
echo '$wgFileExtensions[] = "pdf";' >> "${wwwroot}${wikiroot}/LocalSettings.php"

echo "mediawiki vulnerability installation"