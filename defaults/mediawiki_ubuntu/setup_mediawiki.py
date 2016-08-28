import os
import json
import shutil
import sys


name = sys.argv[1]
cf_dir = os.environ['CF_DIR']

wpath = cf_dir + '/' + os.environ['webserver'] + ".json"
with open(wpath) as f:
    webserver = json.load(f)

dbpath = cf_dir + '/' + os.environ['database'] + ".json"
with open(dbpath) as f:
    sqlserver = json.load(f)

wwwroot = webserver.get('options').get('wwwroot')
hd = os.environ['host_directory']
wikiroot = wwwroot + hd
install_sqlpass = sqlserver.get('options').get('password')
db_user = os.environ.get('db_username')
db_pass = os.environ.get('db_password')
admin_pass = os.environ['admin_password']
admin_username = os.environ['admin_username']

print wwwroot
print wikiroot

install = 'php install.php --installdbuser root --installdbpass ' + install_sqlpass + ' --confpath ' + wikiroot + \
          ' --scriptpath' + hd + ' --dbuser ' + db_user + ' --dbpass ' + db_pass + ' --pass ' + admin_pass + \
          ' wiki ' + admin_username

shutil.copytree(cf_dir + name + '/defaults/mediawiki', wikiroot)
os.system('cd ' + wikiroot + '/maintenance && ' + install)

