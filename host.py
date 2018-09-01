import os
import shutil

import bson
from mongoengine import Document, StringField, ReferenceField, ListField, EmbeddedDocument, EmbeddedDocumentListField, DictField, \
    EmbeddedDocumentField, MapField, BooleanField, DynamicField, GenericReferenceField, DoesNotExist

import util


class OperatingSystem(Document):
    kernel = StringField(options=['WIN', 'LINUX', 'BSD'])  # TODO: ?
    name = StringField()

    # Built in users and services
    accounts = EmbeddedDocumentListField('Account')
    services = ListField(ReferenceField('Service'))

    version = StringField()
    box = StringField()


class ConfigurationOption(EmbeddedDocument):
    name = StringField()
    description = StringField()

    key = StringField()
    type = StringField(options=['STRING', 'FILE', 'INT', 'USER', 'BOOLEAN', 'SERVICE'], default='STRING')
    list = BooleanField(default=False)
    options = ListField()
    default = DynamicField()


class Module(EmbeddedDocument):
    name = StringField()
    options = DictField()
    files = StringField()
    install = StringField()
    source = GenericReferenceField(options=['Service', 'Vulnerability'])  # Bad


class Service(Document):
    install = util.SERVICES

    name = StringField()
    full_name = StringField()
    version = StringField()
    options = MapField(EmbeddedDocumentField(ConfigurationOption))
    vulnerabilities = ListField(ReferenceField('Vulnerability'))


class Vulnerability(Document):

    vuln_types = [
        'Remote Code Execution',
        'SQL Injection',
        'Directory Traversal',
        'Privilege Escalation',
        'File Inclusion'
    ]

    install = util.VULNERABILITIES

    name = StringField()
    full_name = StringField()
    category = StringField(options=vuln_types)
    cve = StringField()
    requirements = ListField()  # For now will just be service names, need to expand this to include kernel/os version
    options = MapField(EmbeddedDocumentField(ConfigurationOption))


class Account(EmbeddedDocument):
    name = StringField()
    password = StringField()
    groups = ListField()


class Host(EmbeddedDocument):
    hostname = StringField(required=True)
    os = ReferenceField('OperatingSystem')

    services = EmbeddedDocumentListField(Module)
    vulnerabilities = EmbeddedDocumentListField(Module)
    accounts = EmbeddedDocumentListField(Account)

    # In-Game stuff
    ip = StringField()
    owner = StringField()

    def __init__(self, **kwargs):
        super(Host, self).__init__(**kwargs)
    
    def to_json_old(self):
        mongo = self.to_mongo()
        mongo['os'] = self.os.to_mongo()
        return bson.json_util.dumps(mongo, indent=2)

    def install_os(self, install_dir):
        if self.os is None:
            return

        found = False
        for account in self.os.accounts:
            for input_account in self.accounts:
                if input_account.name == account.name:
                    found = True
                    break
            if found:
                found = False
                continue

            self.accounts.append(account)

        for service in self.os.services:
            self.install_module(service, install_dir)

    def install_module(self, ref, install_dir, files=dict(), options=dict()):
        host_dir = install_dir + '/'
        file_dir = host_dir + ref.name + '/'
        outfile = file_dir[:-1].encode('utf-8')

        if not os.path.isdir(host_dir):
            os.mkdir(host_dir)

        if not os.path.isdir(file_dir):
            os.mkdir(file_dir)

        opts = {}
        install = ref.install + '/' + ref.name + '.sh'

        if isinstance(ref, Service):
            out = self.services
        else:
            out = self.vulnerabilities

        for key, option in ref.options.items():
            if option.type == 'FILE':
                f = files.get(key)

                if f is None:
                    print "File not found: " + key
                    return False
                else:
                    path = file_dir + f.filename
                    config = f.filename
                    f.save(path)
            else:
                config = options.get(key, option.default)
                if config is None:
                    print "Missing configuration option " + key
                    return False
            opts[key] = config

        has_defaults = os.path.isdir(util.DEFAULTS + '/' + ref.name)
        if has_defaults and not os.path.isdir(file_dir + 'defaults'):
            ins = util.DEFAULTS + '/' + ref.name
            ous = file_dir + 'defaults'
            shutil.copytree(ins, ous)

        try:
            check = out.get(name=ref.name)
            check.options = opts

            if len(files) > 0 or has_defaults:
                check.files = outfile
        except DoesNotExist:
            module = Module(name=ref.name, options=opts, install=install, source=ref)

            if len(files) > 0 or has_defaults:
                module.files = outfile

            out.append(module)

            if isinstance(ref, Service):
                for v in ref.vulnerabilities:
                    self.install_module(v, install_dir)

        return True
