import flask
from flask import json

TMP = '/cyberfront/tmp/'
WORLDS  = '/cyberfront/worlds/'
DEFAULTS = '/cyberfront/defaults/'
SERVICES = '/cyberfront/scripts/service/'
VULNERABILITIES = '/cyberfront/scripts/vuln/'


def fileize(string):
    return string.lower().replace(' ', '_')


def pretty_json(obj):
    return flask.jsonify(json.loads(obj.to_json()))
