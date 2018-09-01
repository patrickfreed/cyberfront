from flask import Flask, request, jsonify
from flask import json
from mongoengine import *
from mongoengine.base import TopLevelDocumentMetaclass
import os

import util
from host import Host, OperatingSystem, Account, Service, ConfigurationOption, Vulnerability
from world import World
import setup

app = Flask(__name__)
connect('cyberfront')


# routing decorator
# parses arguments/their types from url path and request body
def route(path, method='GET', params=None, url_params=[], files=False):
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

            for i, url_param in enumerate(url_params):
                key = kwargs.keys()[i]

                if isinstance(url_param, TopLevelDocumentMetaclass):
                    f_kwargs[key] = url_param.objects(id=kwargs[key]).first()
                else:
                    f_kwargs[key] = url_param(kwargs[key])
                    
                if f_kwargs.get(key) is None:
                    return "invalid " + key, 400
                
            return f(**f_kwargs)

        app.add_url_rule(path, f.__name__, decorated, methods=[method])
        return decorated
    return decorator


@route('/')
def index():
    return app.send_static_file('index.html')


@route('/api/debug/<host>', method='POST', params=['action', 'dog'], url_params=[Host])
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
    os.mkdir(util.WORLDS + '/' + name)
    os.mkdir(util.TMP + '/' + name)
    return w.to_json()


@route('/api/worlds/<world>', url_params=[World])
def get_world(world):
    return util.pretty_json(world)
    # return jsonify(world.to_mongo())


@route('/api/worlds/<world>', method='POST', params=['action'], url_params=[World])
def post_world(action, world):
    if action == 'START':
        world.start()
    elif action == 'STOP':
        world.stop()

    return world.to_json()


@route('/api/worlds/<world>/add_host', method='POST', params=['hostname', 'os_id'], url_params=[World])
def add_host_to_world(world, hostname, os_id):
    ops = OperatingSystem.objects(id=os_id).first()

    if hostname in world.hosts:
        return 'Duplicate hostname in World'

    if ops is None:
        return 'Invalid Operating System id'

    h = Host(hostname=hostname, os=ops)
    h.install_os(util.TMP + '/' + world.name)

    world.hosts[hostname] = h
    world.save()

    return h.to_json()


@route('/api/worlds/<world>/hosts/<host>', url_params=[World, str])
def get_host_in_world(world, host):
    check = World.objects(name=world.name, hosts__name=host).only('hosts__$').first()

    if check is None:
        return 'No such host'

    return util.pretty_json(check.hosts[0])


@route('/api/worlds/<world>/hosts/<hostname>/module', method='POST', params=['module_id', 'options'], url_params=[World, str], files=True)
def install_module(world, hostname, files, module_id, options):
    host = world.hosts.get(hostname)

    if host is None:
        return 'No such host', 400

    service = Service.objects(id=module_id).first()
    vuln = Vulnerability.objects(id=module_id).first()

    if service is None and vuln is None:
        return 'invalid service id', 400

    ref = service if service else vuln

    if host.install_module(ref, util.TMP + '/' + world.name, files=files, options=options):
        world.save()
        return host.to_json()
    else:
        return 'installation failed', 400


@route('/api/worlds/<world>/hosts/<hostname>/account', method='POST', params=['name', 'password', 'groups'], url_params=[World, str])
def setup_account(world, hostname, name, password, groups):
    host = world.hosts.get(hostname)

    if host is None:
        return "Error, no such host"

    try:
        check = host.accounts.get(name=name)
        check.groups = groups
        check.password = password
        host.save()
    except DoesNotExist:
        mongo_account = Account(name=name, groups=groups, password=password)
        host.accounts.append(mongo_account)
        world.save()

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


print "setup starting"
setup.populate_database()

print "web server starting"
app.run(port=8080, host='localhost', debug=True)
