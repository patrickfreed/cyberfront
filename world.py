from mongoengine import Document, StringField, EmbeddedDocumentListField, DictField, EmbeddedDocumentField, MapField

import subprocess

import util


class World(Document):
    name = StringField(unique=True)
    status = StringField(options=['STARTING', 'RUNNING', 'STOPPED', 'CLEAN'])
    hosts = MapField(EmbeddedDocumentField('Host'))

    def __init__(self, **kwargs):
        super(World, self).__init__(**kwargs)
        self.dir = util.WORLDS + '/' + self.name + '/'

    def start(self):
        if self.status == 'CLEAN':
            print "Creating world " + self.name + "..."
            self.update(status='STARTING')
            subprocess.Popen(["vagrant", "up"], cwd=self.dir)
            return True
        else:
            print "world already running"
            return False

    def stop(self):
        if self.status == 'RUNNING':
            print "stop here"
        elif self.status == 'STARTING':
            print "can't stop while starting"
        elif self.status == 'STOPPED' or self.status == 'CLEAN':
            print "world not started yet, can't stop."
