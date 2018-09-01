import flask
import os

TMP = os.path.abspath('tmp/')
WORLDS = os.path.abspath('worlds/')
DEFAULTS = os.path.abspath('defaults/')
SERVICES = os.path.abspath('scripts/service/')
VULNERABILITIES = os.path.abspath('scripts/vuln/')


def fileize(string):
    return string.lower().replace(' ', '_')


def pretty_json(obj):
    return flask.jsonify(flask.json.loads(obj.to_json()))
